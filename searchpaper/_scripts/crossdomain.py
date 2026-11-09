import json, io, time, urllib.parse, urllib.request

OUT = r"C:\nay\github\MRI\searchpaper\_raw\crossdomain.json"
BASE = "https://api.openalex.org/works"
UA = "Mozilla/5.0 (research; mailto:qoder@example.com)"
MAIL = "mailto=qoder@example.com"

QUERIES = [
    "shape correspondence bijective",
    "shape matching homeomorphism",
    "point identity 3D shape",
    "injective deformation neural",
    "dense correspondence cycle consistency",
    "non-rigid shape matching partial",
    "topology adaptive shape matching",
    "canonical space correspondence 3D",
    "functional map bijectivity",
    "diffeomorphic shape template learning",
    "3D semantic correspondence foundation model",
    "shape correspondence evaluation benchmark",
]

FIELDS = (
    "id,doi,title,publication_year,publication_date,primary_location,"
    "authorships,cited_by_count,abstract_inverted_index,type"
)


def get(url):
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == 2:
                print("FAIL", url, e)
                return None
            time.sleep(2 * (i + 1))


def abstract(inv):
    if not inv:
        return ""
    pos = []
    for w, idxs in inv.items():
        for i in idxs:
            pos.append((i, w))
    pos.sort()
    return " ".join(w for _, w in pos)


res = {}
for q in QUERIES:
    url = (BASE + "?search=" + urllib.parse.quote(q)
           + "&filter=from_publication_date:2024-01-01,type:article"
           + "&sort=cited_by_count:desc&per-page=25&mailto=qoder@example.com"
           + "&select=" + FIELDS)
    d = get(url)
    items = []
    if d:
        for w in d.get("results", []):
            pl = w.get("primary_location") or {}
            src = (pl.get("source") or {}).get("display_name") or ""
            items.append({
                "id": w["id"].split("/")[-1],
                "title": w.get("title"),
                "year": w.get("publication_year"),
                "date": w.get("publication_date"),
                "venue": src,
                "doi": w.get("doi"),
                "cites": w.get("cited_by_count"),
                "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])][:6],
                "abstract": abstract(w.get("abstract_inverted_index")),
            })
    res[q] = items
    print(q, len(items))
    time.sleep(1)

io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
print("written", OUT)
