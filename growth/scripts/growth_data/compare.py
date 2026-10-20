"""Comparable-period arithmetic at the original dimension grain; no causal claims."""
import hashlib
import json
from pathlib import Path
from .core import canonical, date, fail, result


def read_snapshot(path):
    try:
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
        rows_path = Path(manifest["rows_path"])
        raw = rows_path.read_bytes()
        expected = next(a["sha256"] for a in manifest["artifacts"] if a["path"] == str(rows_path))
        if hashlib.sha256(raw).hexdigest() != expected:
            fail("integrity_error", "Normalized rows have changed since the snapshot was saved.")
        rows = json.loads(raw)
    except (OSError, ValueError, KeyError, StopIteration, TypeError):
        fail("invalid_snapshot", "Cannot read a valid snapshot manifest and its normalized rows.")
    if manifest.get("schema_version") != 1 or manifest.get("status") != "ok":
        fail("incomparable", "Comparison requires successful schema-version-1 snapshots.")
    if not rows or manifest.get("dates_without_rows"):
        fail("incomplete_coverage", "Both periods need rows on every date; resolve missing-date ambiguity before comparison.")
    if any(value is None for row in rows for value in row["metrics"].values()):
        fail("suppressed_metrics", "Suppressed or unavailable metrics prevent a complete comparison.")
    return manifest, rows


def summarize(source, rows):
    # Never sum across report dimensions. Each group is a fixed country, event,
    # source, device, etc. Play totals are daily count sums, not unique users.
    groups = {}
    for row in rows:
        key = canonical(row["dimensions"])
        group = groups.setdefault(key, {"dimensions": row["dimensions"], "metrics": {}, "dates": set()})
        group["dates"].add(row["date"])
        sums = group["metrics"]
        metrics = row["metrics"]
        additive = {"gsc": ["clicks", "impressions"], "apple": ["counts"], "play": ["acquisitions", "visitors"]}[source]
        for name in additive:
            sums[name] = sums.get(name, 0) + metrics[name]
        if source == "gsc":
            sums["position_numerator"] = sums.get("position_numerator", 0) + metrics["position"] * metrics["impressions"]
    for group in groups.values():
        sums = group["metrics"]
        if source == "gsc":
            denominator = sums["impressions"]
            sums["ctr"] = sums["clicks"] / denominator if denominator else None
            numerator = sums.pop("position_numerator")
            sums["position"] = numerator / denominator if denominator else None
        group["observed_days"] = len(group.pop("dates"))
    return groups


def compare(before_path, after_path):
    before, before_rows = read_snapshot(before_path)
    after, after_rows = read_snapshot(after_path)
    if any(before.get(key) != after.get(key) for key in ("project", "source", "definition")):
        fail("incomparable", "Project, source, identity, filters, timezone, and report grain must match.")
    if before.get("provenance", {}).get("response_aggregation") != after.get("provenance", {}).get("response_aggregation"):
        fail("incomparable", "GSC response aggregations differ.")
    bw, aw = before["requested_window"], after["requested_window"]
    count = (date(bw["end"]) - date(bw["start"])).days + 1
    if count != (date(aw["end"]) - date(aw["start"])).days + 1 or bw["end"] >= aw["start"]:
        fail("incomparable", "Use equal-length, non-overlapping periods in chronological order.")
    old, new = summarize(before["source"], before_rows), summarize(after["source"], after_rows)
    groups = []
    for key in sorted(set(old) | set(new)):
        left, right = old.get(key), new.get(key)
        complete = bool(left and right and left["observed_days"] == count and right["observed_days"] == count)
        metrics = {}
        for name in sorted(set((left or {}).get("metrics", {})) | set((right or {}).get("metrics", {}))):
            a, b = (left or {}).get("metrics", {}).get(name), (right or {}).get("metrics", {}).get(name)
            metrics[name] = {"before": a, "after": b, "absolute_change": b-a if complete and a is not None and b is not None else None,
                             "relative_change": (b-a)/a if complete and a not in (None, 0) and b is not None else None}
        groups.append({"dimensions": (right or left)["dimensions"], "coverage_comparable": complete, "metrics": metrics})
    out = result(before["source"], before["project"])
    out.update({"operation": "compare", "before": str(Path(before_path).resolve()), "after": str(Path(after_path).resolve()),
                "groups": groups, "definition": before["definition"],
                "limitations": list(dict.fromkeys(before["limitations"] + after["limitations"] + [
                    "Arithmetic only; no causal, significance, or growth-quality conclusion is implied.",
                    "Changes are null for groups without daily coverage in both periods. A zero baseline has no relative change.",
                    "Apple Unique Counts are excluded. Play counts are sums of daily observations; no period-unique conversion rate is calculated."]))})
    if any(not group["coverage_comparable"] for group in groups):
        out["status"] = "partial"
    return out
