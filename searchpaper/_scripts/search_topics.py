import json, os, time, urllib.parse, urllib.request

ROOT = r"C:\nay\github\MRI\searchpaper"
RAW = os.path.join(ROOT, "_raw")
UA = "Mozilla/5.0 (research; mailto:qoder@example.com)"
SELECT = ("id,doi,title,publication_year,publication_date,cited_by_count,"
          "abstract_inverted_index,authorships,primary_location,type")


def get(url, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))


def abstract(inv):
    if not inv:
        return ""
    pos = [(i, w) for w, idxs in inv.items() for i in idxs]
    pos.sort()
    return " ".join(w for _, w in pos)


def slim(w):
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
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
        "pdf": loc.get("pdf_url"),
    }


QUERIES = [
    "cardiac dense correspondence",
    "cardiac template implicit",
    "cardiac shape correspondence",
    "cardiac implicit neural representation template",
    "cardiac mesh reconstruction sparse MRI",
    "heart dense correspondence",
    "heart implicit template",
    "bijective shape correspondence",
    "homeomorphism shape correspondence",
    "point identity shape correspondence",
    "bijective deformation neural field",
    "diffeomorphic shape template",
    "non-rigid shape matching 3D",
    "correspondence uncertainty 3D shape",
    "cardiac digital twin mesh",
]

if __name__ == "__main__":
    out = {}
    for q in QUERIES:
        url = ("https://api.openalex.org/works?filter=title_and_abstract.search:%s,"
               "from_publication_date:2024-01-01&sort=cited_by_count:desc&per-page=200&select=%s"
               % (urllib.parse.quote(q), SELECT))
        d = get(url)
        recs = [slim(w) for w in d.get("results", [])]
        out[q] = recs
        print("%-52s %d" % (q, len(recs)))
        time.sleep(0.3)
    json.dump(out, open(os.path.join(RAW, "topic_search.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
