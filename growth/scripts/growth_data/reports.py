"""Strict parsers for the documented English aggregate report formats."""
import csv
import gzip
import io
from decimal import Decimal, InvalidOperation
from .core import MAX_BYTES, canonical, date, fail

APPLE_DIMENSIONS = {
    "discovery": ["Event", "Page Type", "Source Type", "Engagement Type", "Device", "Platform Version", "Territory"],
    "downloads": ["Download Type", "App Version", "Device", "Platform Version", "Source Type", "Page Type", "Pre-Order", "Territory"],
}
PLAY_METRICS = {"Store listing acquisitions": "acquisitions", "Store listing visitors": "visitors",
                "Store listing conversion rate": "conversion_rate"}


def number(value, rate=False):
    if value is None or str(value).strip() in ("", "-", "--", "N/A", "null"):
        return None
    text = str(value).strip()
    percent = text.endswith("%")
    try:
        n = Decimal(text[:-1] if percent else text)
    except InvalidOperation:
        fail("invalid_metric", "Report contains a nonnumeric metric; localized exports are not supported.")
    if not n.is_finite() or n < 0 or (percent and not rate):
        fail("invalid_metric", "Report metrics must be finite, nonnegative numbers.")
    if percent:
        n /= 100
    if rate:
        if n > 1:
            fail("invalid_metric", "Conversion rates must be fractions or explicitly marked percentages.")
        return float(n)
    if n != n.to_integral_value():
        fail("invalid_metric", "Count metrics must be integers.")
    return int(n)


def table(raw):
    if len(raw) > MAX_BYTES:
        fail("size_limit", "Report exceeds the 50 MiB limit.")
    if raw.startswith(b"\x1f\x8b"):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(MAX_BYTES + 1)
        except (OSError, EOFError):
            fail("invalid_report", "Unable to decompress the report.")
    if len(raw) > MAX_BYTES:
        fail("size_limit", "Decompressed report exceeds the 50 MiB limit.")
    try:
        encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
        text = raw.decode(encoding)
    except UnicodeError:
        fail("invalid_encoding", "Use UTF-8 or BOM-marked UTF-16 reports.")
    if "\x00" in text:
        fail("invalid_encoding", "UTF-16 reports require a byte-order mark.")
    header = text.splitlines()[0] if text.splitlines() else ""
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter="\t" if "\t" in header else ",")
    fields = reader.fieldnames or []
    if not fields or len(fields) != len(set(fields)):
        fail("invalid_schema", "Report headers are empty or duplicated.")
    try:
        rows = list(reader)
    except csv.Error:
        fail("invalid_report", "Malformed delimited report.")
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        fail("invalid_schema", "Report rows do not match the header width.")
    return fields, rows


def normalize(raw, source, settings, w):
    fields, original = table(raw)
    if source == "apple":
        dimensions = APPLE_DIMENSIONS[settings["report"]]
        metrics = {"Counts": "counts"}
        if settings["report"] == "discovery":
            metrics["Unique Counts"] = "unique_counts"
        identity, expected = "App Apple Identifier", settings["app_id"]
        required = {"Date", "App Name", identity, *dimensions, *metrics}
        # Detailed reports have a different grain. Never silently combine them.
        if set(fields) - required:
            fail("invalid_schema", "Unsupported Apple report columns; use the standard aggregate report, not Detailed.")
    else:
        identity, expected = "Package name", settings["package_name"]
        dimensions = ["Country"] if settings["breakdown"] == "country" else ["Traffic source", "Search term", "UTM source", "UTM campaign"]
        if "Country/region" in fields and "Country" not in fields:
            fields = ["Country" if key == "Country/region" else key for key in fields]
            original = [{("Country" if key == "Country/region" else key): value for key, value in row.items()} for row in original]
        metrics = PLAY_METRICS
        required = {"Date", identity, *dimensions, *metrics}
        if set(fields) - required:
            fail("invalid_schema", "Unsupported Play columns; verify the current Store Performance export schema.")
    if not required <= set(fields):
        fail("invalid_schema", "Missing required report columns; verify source, report type, and export language.")
    rows = []
    for row in original:
        if row[identity] != expected:
            fail("source_mismatch", "Report contains an app or package other than the configured source.")
        event_date = date(row["Date"]).isoformat()
        values = {name: number(row[column], rate=name == "conversion_rate") for column, name in metrics.items()}
        if w["start"] <= event_date <= w["end"]:
            rows.append({"date": event_date, "dimensions": {key: row[key] for key in dimensions}, "metrics": values})
    return deduplicate(rows)


def deduplicate(rows):
    seen = {}
    for row in rows:
        key = canonical([row["date"], row["dimensions"]])
        if key in seen and seen[key] != row:
            fail("conflicting_rows", "Conflicting values at the same report grain; import one revision or fetch a fresh snapshot.")
        seen[key] = row
    return sorted(seen.values(), key=lambda row: canonical([row["date"], row["dimensions"]]))
