#!/usr/bin/env python3
"""Agent-facing SEO/ASO data CLI. See README.md for the result contract."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
from growth_data.core import (DataError, EXIT_CODES, MAX_BYTES, canonical, coverage, fail,
                              load_config, result, save_snapshot, source_config, window)
from growth_data.providers import FETCHERS, describe, doctor, limitations, transport
from growth_data.reports import deduplicate, normalize

GROWTH = Path(__file__).resolve().parent.parent


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's message can echo arbitrary CLI values. Return a safe, stable error.
        fail("invalid_arguments", "Invalid command arguments; use --help for usage.")


def parser():
    p = Parser(description=__doc__)
    p.add_argument("--config", type=Path, default=GROWTH / "config.local.json", help="Project JSON configuration (no secrets)")
    p.add_argument("--env-file", type=Path, help="Optional dotenv path; defaults to this workspace's growth/.env")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("doctor", "fetch", "import"):
        command = sub.add_parser(name)
        command.add_argument("source", choices=("apple", "play") if name == "import" else ("gsc", "apple", "play", "all"))
        if name != "doctor":
            command.add_argument("--start", required=True, help="Inclusive YYYY-MM-DD event date")
            command.add_argument("--end", required=True, help="Inclusive YYYY-MM-DD event date")
        if name == "doctor":
            command.add_argument("--online", action="store_true", help="Also check read access against enabled sources")
        if name == "import":
            command.add_argument("--file", type=Path, required=True, action="append", help="One snapshot's CSV/TSV(.gz); repeat for segments")
            command.add_argument("--processing-date", help="Required for Apple: processing date of this one report instance")
    comparison = sub.add_parser("compare")
    comparison.add_argument("--before", type=Path, required=True)
    comparison.add_argument("--after", type=Path, required=True)
    return p


def run_source(args, config, source, w, http=None):
    out = result(source, config["project"], w)
    try:
        s = source_config(config, source)
        out["definition"] = describe(source, s)
        out["limitations"] = limitations(source)
        if args.command == "doctor":
            out["operation"] = "doctor"
            out["access_verified"] = False
            out["message"] = "Configuration is valid; credentials and live access have not been checked."
            if args.online:
                out["message"] = doctor(http or transport(source, s), source, s)
                out["access_verified"] = True
            return out
        if args.command == "import":
            if source == "apple":
                from growth_data.core import date
                if not args.processing_date:
                    fail("invalid_arguments", "Apple import requires --processing-date; import all segments from one instance together.")
                processing = date(args.processing_date).isoformat()
            raw_parts, rows = [], []
            for path in args.file:
                with path.open("rb") as stream:
                    raw = stream.read(MAX_BYTES + 1)
                rows.extend(normalize(raw, source, s, w))
                raw_parts.append(raw)
            rows = deduplicate(rows)
            provenance = {"method": "local_import", "revision_policy": "Caller supplied one complete snapshot; no merging with earlier imports."}
            if source == "apple":
                if any(row["date"] > processing for row in rows):
                    fail("invalid_revision", "Apple processing date cannot precede an event date.")
                provenance["processing_date"] = processing
            errors = []
            out["limitations"].append("Local import cannot verify that all provider segments or export rows were supplied.")
        else:
            rows, raw_parts, provenance, errors = FETCHERS[source](http or transport(source, s), s, w)
        out["operation"] = args.command
        out["provenance"] = provenance
        out["errors"] = errors
        coverage(out, rows, w)
        # Explicitly surface publication lag; successful HTTP is not completeness.
        from zoneinfo import ZoneInfo
        today = dt.datetime.now(ZoneInfo(out["definition"]["timezone"])).date()
        from growth_data.core import date
        lag = {"gsc": 3, "apple": 3, "play": 7}[source]
        if (today - date(w["end"])).days < lag:
            out["status"] = "partial"
            out["limitations"].append(f"Window reaches the most recent {lag} days; report completeness is not established.")
        if source == "apple":
            lag = 2 if s["report"] == "downloads" else 3
            revision_dates = provenance.get("event_date_revisions", {})
            immature = [row["date"] for row in rows if (date(revision_dates.get(row["date"], {}).get("processing_date", provenance.get("processing_date", row["date"]))) - date(row["date"])).days < lag]
            if immature:
                out["status"] = "partial"
                out["limitations"].append("At least one Apple event date lacks a revision beyond its report completeness threshold.")
        if errors:
            out["status"] = "partial"
        if any(value is None for row in rows for value in row["metrics"].values()):
            out["status"] = "partial"
            out["limitations"].append("Some metrics are suppressed or unavailable and remain null.")
        return save_snapshot(GROWTH, out, rows, raw_parts)
    except DataError as error:
        out.update(status=error.status, error_code=error.code, message=error.message)
        return out
    except OSError:
        out.update(status="error", error_code="file_error", message="Unable to read input or write local evidence files.")
        return out
    except (KeyError, TypeError, ValueError, AttributeError):
        out.update(status="error", error_code="invalid_schema", message="Configuration or provider response did not match the supported schema.")
        return out


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        if args.command == "compare":
            from growth_data.compare import compare
            out = compare(args.before, args.after)
        else:
            from growth_data.environment import load_environment
            load_environment(args.env_file if args.env_file is not None else GROWTH / ".env", required=args.env_file is not None)
            config = load_config(args.config)
            w = window(args.start, args.end) if args.command != "doctor" else None
            if args.source == "all":
                sources = [source for source in FETCHERS if isinstance(config["sources"].get(source), dict) and config["sources"][source].get("enabled") is True]
                if not sources:
                    fail("no_enabled_sources", "No sources are enabled in configuration.", "unavailable")
                results = [run_source(args, config, source, w) for source in sources]
                statuses = {item["status"] for item in results}
                status = "ok" if statuses == {"ok"} else "partial" if "ok" in statuses or "partial" in statuses else "error" if "error" in statuses else "unavailable"
                out = {"schema_version": 1, "status": status, "project": config["project"], "results": results}
            else:
                out = run_source(args, config, args.source, w)
    except DataError as error:
        out = {"schema_version": 1, "status": error.status, "error_code": error.code, "message": error.message}
    except (OSError, ValueError, KeyError, TypeError):
        out = {"schema_version": 1, "status": "error", "error_code": "invalid_input", "message": "Unable to process the supplied input."}
    print(json.dumps(out, indent=2, ensure_ascii=False, allow_nan=False))
    return EXIT_CODES[out["status"]]


if __name__ == "__main__":
    sys.exit(main())
