import json, os, re, time, urllib.request

ROOT = r"C:\nay\github\MRI\searchpaper"
RAW = os.path.join(ROOT, "_raw")
UA = "Mozilla/5.0 (research; mailto:qoder@example.com)"


def get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()


d = json.load(open(os.path.join(RAW, "details.json"), encoding="utf-8"))
for k, v in d.items():
    if v.get("abstract") or not v.get("doi"):
        continue
    try:
        c = json.loads(get("https://api.crossref.org/works/" + v["doi"].split("doi.org/")[-1]))
        ab = strip_tags(c.get("message", {}).get("abstract", ""))
        if ab:
            v["abstract"] = ab
            v["abstract_src"] = "crossref"
            print("OK ", k, len(ab), v["title"][:55])
        else:
            print("---", k, v["title"][:55])
    except Exception as e:
        print("ERR", k, e)
    time.sleep(0.2)

json.dump(d, open(os.path.join(RAW, "details.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
