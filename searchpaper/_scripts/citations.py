import json, os, time, urllib.parse, urllib.request

ROOT = r"C:\nay\github\MRI\searchpaper"
RAW = os.path.join(ROOT, "_raw")
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (research; mailto:qoder@example.com)"
SELECT = ("id,doi,title,publication_year,publication_date,cited_by_count,"
          "abstract_inverted_index,authorships,primary_location,type,referenced_works_count")


def get(url, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))


def abstract(inv):
    if not inv:
        return ""
    pos = []
    for w, idxs in inv.items():
        for i in idxs:
            pos.append((i, w))
    pos.sort()
    return " ".join(w for _, w in pos)


def citing(work_id, since="2024-01-01", per_page=200):
    out, cursor = [], "*"
    while cursor:
        url = ("https://api.openalex.org/works?filter=cites:%s,from_publication_date:%s"
               "&per-page=%d&cursor=%s&select=%s" %
               (work_id, since, per_page, urllib.parse.quote(cursor), SELECT))
        d = get(url)
        out.extend(d.get("results", []))
        cursor = d.get("meta", {}).get("next_cursor")
        if not d.get("results"):
            break
        time.sleep(0.2)
    return out


def slim(w):
    loc = w.get("primary_location") or {}
    src = (loc.get("source") or {})
    return {
        "id": w["id"].split("/")[-1],
        "doi": w.get("doi"),
        "title": w.get("title"),
        "year": w.get("publication_year"),
        "date": w.get("publication_date"),
        "cites": w.get("cited_by_count"),
        "venue": src.get("display_name"),
        "type": w.get("type"),
        "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])][:4],
        "abstract": abstract(w.get("abstract_inverted_index")),
        "landing": loc.get("landing_page_url"),
        "oa": (w.get("primary_location") or {}).get("pdf_url"),
    }


if __name__ == "__main__":
    seeds = json.load(open(os.path.join(RAW, "seeds.json"), encoding="utf-8"))
    allrec = {}
    for name, wid in seeds.items():
        recs = [slim(w) for w in citing(wid)]
        allrec[name] = recs
        print("%-28s %d citing works (>=2024)" % (name, len(recs)))
    json.dump(allrec, open(os.path.join(RAW, "citations_2024plus.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
