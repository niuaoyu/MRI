import json, os, sys, time, urllib.parse, urllib.request

ROOT = r"C:\nay\github\MRI\searchpaper"
RAW = os.path.join(ROOT, "_raw")
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (research; mailto:qoder@example.com)"


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def search_title(q, n=5):
    url = ("https://api.openalex.org/works?search=" + urllib.parse.quote(q) +
           "&per-page=%d&select=id,doi,title,publication_year,cited_by_count,type,primary_location" % n)
    d = get(url)
    return d.get("results", [])


if __name__ == "__main__":
    queries = json.loads(sys.argv[1])
    out = {}
    for q in queries:
        res = search_title(q)
        out[q] = res
        print("### " + q)
        for w in res:
            loc = (w.get("primary_location") or {}).get("source") or {}
            print("  %s | %s | cites=%s | %s" % (w["id"], w.get("publication_year"), w.get("cited_by_count"), (w.get("title") or "")[:100]))
        time.sleep(0.3)
    json.dump(out, open(os.path.join(RAW, "resolved.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
