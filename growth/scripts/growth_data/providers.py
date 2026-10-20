"""Read-only adapters. Fetch never creates report subscriptions or changes settings."""
import base64
import datetime as dt
import hashlib
import json
from .auth import apple_token, google_token
from .core import HTTP, DataError, apple_list, canonical, date, days, fail, quote
from .reports import deduplicate, normalize, number

APPLE_BASE = "https://api.appstoreconnect.apple.com/v1"
APPLE_NAMES = {"discovery": "App Store Discovery and Engagement", "downloads": "App Store Downloads"}


def transport(source, s):
    if source == "apple":
        return HTTP(apple_token(s), "api.appstoreconnect.apple.com")
    scope = "webmasters.readonly" if source == "gsc" else "devstorage.read_only"
    host = "www.googleapis.com" if source == "gsc" else "storage.googleapis.com"
    return HTTP(google_token("https://www.googleapis.com/auth/" + scope), host)


def describe(source, s):
    if source == "gsc":
        return {"identity": {"site_url": s["site_url"]}, "report": "search_analytics",
                "dimensions": s.get("dimensions", ["date", "page"]), "timezone": "America/Los_Angeles",
                "filters": s.get("filter_groups", []), "search_type": s.get("search_type", "web"),
                "aggregation": "auto", "data_state": "final"}
    if source == "apple":
        from .reports import APPLE_DIMENSIONS
        return {"identity": {"app_id": s["app_id"]}, "report": s["report"],
                "dimensions": APPLE_DIMENSIONS[s["report"]], "timezone": s["timezone"],
                "filters": {}, "aggregation": "standard daily report; latest processing revision per event date"}
    return {"identity": {"package_name": s["package_name"], "bucket": s["bucket"]},
            "report": "store_performance", "dimensions": s["breakdown"], "timezone": s["timezone"],
            "filters": {}, "aggregation": "daily counts at the selected breakdown; not period-unique users"}


def limitations(source):
    return {
        "gsc": ["Final data only. Search Analytics returns top rows and can omit anonymized or internally limited rows; pagination cannot recover all data.",
                "Page/query breakdowns must not be treated as property-wide totals. Position is impression-weighted, not an arithmetic average."],
        "apple": ["Privacy thresholds and late corrections can leave gaps. A newer processing instance replaces a whole event-date partition.",
                  "Unique Counts are not additive across dates or dimensions. Discovery engagement is not installs; download types must remain separate.",
                  "App Store search may include paid Search Ads. Timezone is a project-verified report assumption."],
        "play": ["Monthly exports can lag event dates by 3 to 7 days and may be revised; missing months are not zero.",
                 "Daily visitors and acquisitions are not period-unique users. Country and traffic-source exports cannot be added together.",
                 "Timezone is a project-verified report assumption; this adapter does not provide keyword search volume or organic rank."],
    }[source]


def gsc_fetch(http, s, w):
    dimensions = s.get("dimensions", ["date", "page"])
    url = "https://www.googleapis.com/webmasters/v3/sites/" + quote(s["site_url"]) + "/searchAnalytics/query"
    rows, raw_parts, aggregations = [], [], set()
    # Query daily to avoid letting high-volume days displace other days' rows.
    for day in days(w):
        start, page_fingerprints = 0, set()
        while True:
            body = {"startDate": day, "endDate": day, "dimensions": dimensions,
                    "type": s.get("search_type", "web"), "dataState": "final", "aggregationType": "auto",
                    "rowLimit": 25000, "startRow": start}
            if s.get("filter_groups"):
                body["dimensionFilterGroups"] = s["filter_groups"]
            page = http.json(url, method="POST", body=body)
            batch = page.get("rows", [])
            if not isinstance(batch, list):
                fail("invalid_response", "GSC rows must be an array.")
            fingerprint = canonical(batch)
            if batch and fingerprint in page_fingerprints:
                fail("pagination_loop", "GSC repeated a nonempty page.")
            page_fingerprints.add(fingerprint)
            raw_parts.append(canonical(page).encode())
            if batch:
                aggregation = page.get("responseAggregationType")
                if aggregation not in ("byPage", "byProperty", "byNewsShowcasePanel"):
                    fail("invalid_response", "GSC did not identify its response aggregation.")
                aggregations.add(aggregation)
            for item in batch:
                keys = item.get("keys")
                if not isinstance(keys, list) or len(keys) != len(dimensions) or not all(isinstance(v, str) for v in keys):
                    fail("invalid_response", "GSC row keys do not match configured dimensions.")
                values = dict(zip(dimensions, keys))
                event_date = values.pop("date")
                if event_date != day:
                    fail("invalid_response", "GSC returned a date outside its daily query.")
                if not all(name in item for name in ("clicks", "impressions", "ctr", "position")):
                    fail("invalid_response", "GSC row is missing required metrics.")
                clicks, impressions = number(item["clicks"]), number(item["impressions"])
                ctr = number(item["ctr"], rate=True)
                position = item["position"]
                import math
                if isinstance(position, bool) or not isinstance(position, (int, float)) or not math.isfinite(position) or position < 0:
                    fail("invalid_metric", "GSC position must be a finite, nonnegative number.")
                if clicks is None or impressions is None or ctr is None:
                    fail("invalid_metric", "GSC returned null metrics.")
                rows.append({"date": event_date, "dimensions": values,
                             "metrics": {"clicks": clicks, "impressions": impressions, "ctr": ctr, "position": position}})
            if len(batch) < 25000:
                break
            start += len(batch)
    if len(aggregations) > 1:
        fail("mixed_aggregation", "GSC changed aggregation within the requested window.")
    return deduplicate(rows), raw_parts, {"response_aggregation": next(iter(aggregations), None)}, []


def apple_report(http, s):
    requests = apple_list(http, f"{APPLE_BASE}/apps/{quote(s['app_id'])}/analyticsReportRequests?limit=200")
    requests = [r for r in requests if r.get("attributes", {}).get("accessType") == "ONGOING"
                and not r.get("attributes", {}).get("stoppedDueToInactivity", False)]
    if s.get("request_id"):
        requests = [r for r in requests if r["id"] == s["request_id"]]
    if not requests:
        fail("report_setup_required", "No active ONGOING Apple analytics request. An authorized admin must enable report generation; initial availability may take 1-2 days.", "unavailable")
    if len(requests) != 1:
        fail("ambiguous_report", "Configure request_id to select one active Apple analytics request.")
    reports = apple_list(http, f"{APPLE_BASE}/analyticsReportRequests/{quote(requests[0]['id'])}/reports?limit=200")
    names = {APPLE_NAMES[s["report"]], APPLE_NAMES[s["report"]] + " Standard"}
    if s["report"] == "downloads":
        names.update({"App Downloads", "App Downloads Standard"})
    matches = [r for r in reports if r.get("attributes", {}).get("name") in names]
    if s.get("report_id"):
        matches = [r for r in matches if r["id"] == s["report_id"]]
    if len(matches) != 1:
        fail("report_unavailable", "The selected standard Apple report is not uniquely available yet.", "unavailable")
    return matches[0]["id"]


def apple_fetch(http, s, w):
    report_id = apple_report(http, s)
    instances = apple_list(http, f"{APPLE_BASE}/analyticsReports/{quote(report_id)}/instances?filter%5Bgranularity%5D=DAILY&limit=200")
    selected = []
    for item in instances:
        attrs = item["attributes"]
        if attrs.get("granularity") != "DAILY":
            fail("invalid_response", "Apple returned an unexpected granularity.")
        processing = date(attrs["processingDate"]).isoformat()
        if processing >= w["start"]:
            selected.append((processing, item["id"]))
    if not selected:
        fail("report_unavailable", "No retained daily Apple instances cover this window.", "unavailable")
    partitions, revisions, raw_parts = {}, {}, []
    for processing, instance_id in sorted(selected):
        segments = apple_list(http, f"{APPLE_BASE}/analyticsReportInstances/{quote(instance_id)}/segments?limit=200")
        if not segments:
            fail("incomplete_instance", "An Apple instance has no segments; no partial revision was accepted.", "partial")
        instance_rows = []
        for segment in segments:
            attrs = segment["attributes"]
            # Download immediately; signed URLs expire. Never persist the segment API response.
            raw = http.request(attrs["url"], authenticated=False)
            checksum = attrs.get("checksum")
            if checksum and hashlib.md5(raw).hexdigest().lower() != checksum.lower():
                fail("checksum_mismatch", "An Apple segment failed its MD5 integrity check.")
            if attrs.get("sizeInBytes") is not None and len(raw) != int(attrs["sizeInBytes"]):
                fail("size_mismatch", "An Apple segment size did not match its metadata.")
            instance_rows.extend(normalize(raw, "apple", s, w))
            raw_parts.append(raw)
        grouped = {}
        for row in deduplicate(instance_rows):
            grouped.setdefault(row["date"], []).append(row)
        for event_date, event_rows in grouped.items():
            if revisions.get(event_date, {}).get("processing_date") == processing and partitions[event_date] != event_rows:
                fail("ambiguous_revision", "Apple returned conflicting revisions with the same processing date.")
            partitions[event_date] = event_rows
            revisions[event_date] = {"processing_date": processing, "instance_id": instance_id}
    rows = deduplicate([row for partition in partitions.values() for row in partition])
    return rows, raw_parts, {"report_id": report_id, "event_date_revisions": revisions}, []


def play_fetch(http, s, w):
    months = sorted({day[:7].replace("-", "") for day in days(w)})
    rows, raw_parts, objects, errors = [], [], [], []
    for month in months:
        name = f"stats/store_performance/store_performance_{s['package_name']}_{month}_{s['breakdown']}.csv"
        url = f"https://storage.googleapis.com/storage/v1/b/{quote(s['bucket'])}/o/{quote(name)}"
        try:
            meta = http.json(url)
            generation = meta.get("generation")
            if not isinstance(generation, str) or not generation.isdigit():
                fail("invalid_response", "GCS did not return a valid object generation.")
            raw = http.request(url + "?alt=media&generation=" + generation)
            if meta.get("md5Hash") and base64.b64encode(hashlib.md5(raw).digest()).decode() != meta["md5Hash"]:
                fail("checksum_mismatch", "A Play report failed its GCS MD5 integrity check.")
            parsed = normalize(raw, "play", s, w)
            if any(row["date"][:7].replace("-", "") != month for row in parsed):
                fail("source_mismatch", "A monthly Play object contained another month's rows.")
            rows.extend(parsed)
            raw_parts.append(raw)
            objects.append({"name": name, "generation": generation})
        except DataError as error:
            errors.append({"month": month, "code": error.code, "message": error.message})
    if errors and not objects:
        fail(errors[0]["code"], "No requested Play monthly reports could be read.", "unavailable" if all(e["code"].startswith("http_") for e in errors) else "error")
    return deduplicate(rows), raw_parts, {"objects": objects}, errors


def doctor(http, source, s):
    if source == "gsc":
        response = http.json("https://www.googleapis.com/webmasters/v3/sites/" + quote(s["site_url"]))
        if response.get("siteUrl") != s["site_url"] or response.get("permissionLevel") not in ("siteOwner", "siteFullUser", "siteRestrictedUser"):
            fail("property_access_unverified", "GSC did not confirm the configured property and permission.", "unavailable")
        return "Property access succeeded; run fetch to verify query coverage."
    if source == "apple":
        apple_report(http, s)
        return "Report discovery succeeded; run fetch to verify instances and segments."
    # A narrow prefix list checks the configured app without downloading account-wide data.
    prefix = f"stats/store_performance/store_performance_{s['package_name']}_"
    response = http.json(f"https://storage.googleapis.com/storage/v1/b/{quote(s['bucket'])}/o?maxResults=1&prefix={quote(prefix)}")
    if not response.get("items"):
        fail("report_unavailable", "Bucket access succeeded but no Store Performance objects match this app.", "unavailable")
    return "Report prefix access succeeded; run fetch to verify the chosen months and breakdown."


FETCHERS = {"gsc": gsc_fetch, "apple": apple_fetch, "play": play_fetch}
