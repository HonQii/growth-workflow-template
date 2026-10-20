"""Bounded transport, configuration, and immutable local evidence snapshots."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

MAX_BYTES = 50 * 1024 * 1024
EXIT_CODES = {"ok": 0, "partial": 2, "unavailable": 3, "error": 1}


class DataError(Exception):
    def __init__(self, code, message, status="error"):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


def fail(code, message, status="error"):
    raise DataError(code, message, status)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def date(value):
    try:
        parsed = dt.date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError()
        return parsed
    except (ValueError, TypeError):
        fail("invalid_date", "Use calendar dates in YYYY-MM-DD format.")


def window(start, end):
    first, last = date(start), date(end)
    if first > last or (last - first).days > 365:
        fail("invalid_window", "The inclusive window must contain 1 to 366 days.")
    return {"start": start, "end": end}


def days(w):
    first, last = date(w["start"]), date(w["end"])
    return [(first + dt.timedelta(days=n)).isoformat() for n in range((last-first).days+1)]


def load_config(path):
    try:
        config = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        fail("invalid_config", "Cannot read the JSON config; copy config.example.json and fill it in.")
    if not isinstance(config, dict) or not isinstance(config.get("sources"), dict):
        fail("invalid_config", "Config requires project and sources fields.")
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", str(config.get("project", ""))):
        fail("invalid_config", "project must be a stable identifier containing letters, digits, '-' or '_'.")
    return config


def source_config(config, source):
    s = config["sources"].get(source)
    if not isinstance(s, dict) or s.get("enabled") is not True:
        fail("source_disabled", "The requested source is not enabled in project configuration.", "unavailable")
    fields = {"gsc": ["site_url"], "apple": ["app_id", "report", "timezone"],
              "play": ["package_name", "bucket", "breakdown", "timezone"]}
    for key in fields[source]:
        if not isinstance(s.get(key), str) or not s[key].strip():
            fail("invalid_config", f"Missing required {source} configuration field: {key}.")
    if source == "apple":
        if not s["app_id"].isdigit() or s["report"] not in ("discovery", "downloads"):
            fail("invalid_config", "Apple requires a numeric app_id and report discovery or downloads.")
    if source == "play":
        if s["breakdown"] not in ("country", "traffic_source"):
            fail("invalid_config", "Play breakdown must be country or traffic_source.")
        if not re.fullmatch(r"[a-zA-Z0-9_.]+", s["package_name"]) or not re.fullmatch(r"[a-z0-9_.-]+", s["bucket"]):
            fail("invalid_config", "Invalid Play package or bucket identifier.")
    if source == "gsc":
        if not (s["site_url"].startswith("sc-domain:") or urllib.parse.urlsplit(s["site_url"]).scheme in ("http", "https")):
            fail("invalid_config", "Use an exact Search Console property ID.")
        dimensions = s.get("dimensions", ["date", "page"])
        if not isinstance(dimensions, list) or "date" not in dimensions or not all(isinstance(d, str) for d in dimensions) or len(dimensions) != len(set(dimensions)) or not set(dimensions) <= {"date", "page", "query", "country", "device", "searchAppearance"}:
            fail("invalid_config", "GSC dimensions must be unique supported dimensions and include date.")
        if s.get("search_type", "web") not in ("web", "image", "video", "news", "discover", "googleNews"):
            fail("invalid_config", "Unsupported GSC search_type.")
        filters = s.get("filter_groups", [])
        if not isinstance(filters, list):
            fail("invalid_config", "filter_groups must be an array of GSC dimension filter groups.")
        for group in filters:
            if not isinstance(group, dict) or group.get("groupType", "and") != "and" or not isinstance(group.get("filters"), list):
                fail("invalid_config", "GSC filter groups require an AND filter array.")
            for rule in group["filters"]:
                if not isinstance(rule, dict) or rule.get("dimension") not in ("country", "device", "page", "query", "searchAppearance") or rule.get("operator", "equals") not in ("equals", "notEquals", "contains", "notContains", "includingRegex", "excludingRegex") or not isinstance(rule.get("expression"), str):
                    fail("invalid_config", "Unsupported GSC dimension filter.")
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    try:
        ZoneInfo("America/Los_Angeles" if source == "gsc" else s["timezone"])
    except (ZoneInfoNotFoundError, ValueError):
        fail("invalid_config", "Provide an IANA source timezone verified against the report definition.")
    return s


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HTTP:
    def __init__(self, token=None, host=None, timeout=30, retries=2, budget=200):
        self.token, self.host = token, host
        self.timeout, self.retries, self.budget = timeout, retries, budget
        self.opener = urllib.request.build_opener(NoRedirect())
        self.remaining_bytes = 256 * 1024 * 1024

    def request(self, url, method="GET", body=None, authenticated=True, retry=True):
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None, 443):
            fail("unsafe_url", "Only HTTPS provider URLs are supported.")
        if authenticated and parsed.hostname != self.host:
            fail("unsafe_url", "Refusing to forward credentials to another host.")
        attempts = self.retries + 1 if retry else 1
        for attempt in range(attempts):
            if self.budget <= 0:
                fail("request_budget", "Request budget exhausted; narrow the window or resume later.", "partial")
            self.budget -= 1
            headers = {"Accept": "application/json", "User-Agent": "growth-workflow-template/0.3.0"}
            if authenticated and self.token:
                headers["Authorization"] = "Bearer " + self.token()
            data = None if body is None else canonical(body).encode()
            if data is not None:
                headers["Content-Type"] = "application/json"
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with self.opener.open(req, timeout=self.timeout) as response:
                    raw = response.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    fail("size_limit", "Response exceeds the 50 MiB limit; narrow the query.")
                self.remaining_bytes -= len(raw)
                if self.remaining_bytes < 0:
                    fail("size_limit", "Run exceeds the 256 MiB download limit; narrow the query.")
                return raw
            except urllib.error.HTTPError as error:
                code = error.code
                # Never print response bodies or URLs, which may contain signed credentials.
                error.close()
                if code in (429, 500, 502, 503, 504) and attempt+1 < attempts:
                    time.sleep(min(2 ** attempt, 4))
                    continue
                fail(f"http_{code}", f"Provider returned HTTP {code}.", "unavailable" if code in (401,403,404,429,503) else "error")
            except (urllib.error.URLError, TimeoutError, socket.timeout, OSError):
                if attempt+1 < attempts:
                    time.sleep(min(2 ** attempt, 4))
                    continue
                fail("network_error", "Provider request failed or timed out.", "unavailable")

    def json(self, url, **kwargs):
        try:
            data = json.loads(self.request(url, **kwargs))
        except (ValueError, UnicodeError):
            fail("invalid_response", "Provider returned invalid JSON.")
        if not isinstance(data, dict):
            fail("invalid_response", "Expected a JSON object from the provider.")
        return data


def quote(value):
    return urllib.parse.quote(str(value), safe="")


def apple_list(http, url):
    result, visited = [], set()
    while url:
        if url in visited:
            fail("pagination_loop", "Provider pagination repeated a page.")
        visited.add(url)
        page = http.json(url)
        if not isinstance(page.get("data"), list):
            fail("invalid_response", "Provider list response is missing data.")
        result.extend(page["data"])
        url = page.get("links", {}).get("next")
    return result


def result(source, project, w=None):
    return {"schema_version": 1, "status": "ok", "source": source, "project": project,
            "requested_window": w, "actual_coverage": {"start": None, "end": None},
            "extracted_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "row_count": None, "limitations": [], "artifacts": [], "error_code": None}


def coverage(out, rows, w):
    dates = sorted({row["date"] for row in rows})
    out["row_count"] = len(rows)
    out["actual_coverage"] = {"start": dates[0] if dates else None, "end": dates[-1] if dates else None}
    missing = sorted(set(days(w)) - set(dates))
    out["dates_without_rows"] = missing
    if missing:
        out["limitations"].append("Dates without rows may mean no activity, suppression, or unavailable data; they are not automatically zero.")


def save_snapshot(root, out, rows, raw_parts):
    # Each invocation is an independent snapshot, never an append to previous metrics.
    folder = root / ".local-data" / out["source"] / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:12])
    folder.mkdir(parents=True, mode=0o700)
    artifacts = []
    for number, raw in enumerate(raw_parts):
        path = folder / f"raw-{number:04d}.bin"
        path.write_bytes(raw)
        artifacts.append({"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()})
    normalized = folder / "rows.json"
    normalized.write_text(canonical(rows)+"\n", encoding="utf-8")
    artifacts.append({"path": str(normalized), "sha256": hashlib.sha256(normalized.read_bytes()).hexdigest()})
    out["artifacts"] = artifacts
    out["rows_path"] = str(normalized)
    manifest = folder / "manifest.json"
    out["manifest_path"] = str(manifest)
    manifest.write_text(json.dumps(out, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")
    return out
