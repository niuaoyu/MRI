import io, json, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

OUT = r"C:\nay\github\MRI\searchpaper\_raw\crossdomain_arxiv.json"
NS = {"a": "http://www.w3.org/2005/Atom"}
UA = "Mozilla/5.0 (research; mailto:qoder@example.com)"

QUERIES = [
    'abs:"shape correspondence" AND abs:bijective',
    'abs:"shape matching" AND abs:homeomorphism',
    'abs:"dense correspondence" AND abs:"point identity"',
    'abs:injective AND abs:deformation AND abs:mesh',
    'abs:"cycle consistency" AND abs:correspondence',
    'abs:"partial shape matching"',
    'abs:"shape matching" AND abs:topology',
    'abs:"neural deformation field" AND abs:correspondence',
    'abs:"template" AND abs:"dense correspondence" AND abs:3D',
    'abs:"correspondence" AND abs:"evaluation" AND abs:shape',
]


def fetch(q):
    url = ("https://export.arxiv.org/api/query?search_query=" + urllib.parse.quote(q)
           + "&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending")
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            print("retry", i, e)
            time.sleep(5 * (i + 1))
    return None


res = {}
for q in QUERIES:
    raw = fetch(q)
    items = []
    if raw:
        try:
            root = ET.fromstring(raw)
        except Exception as e:
            print("parse fail", q, e)
            root = None
        if root is not None:
            for e in root.findall("a:entry", NS):
                pub = e.find("a:published", NS).text[:10]
                if pub < "2024-01-01":
                    continue
                aid = e.find("a:id", NS).text.split("/abs/")[-1]
                items.append({
                    "arxiv": aid,
                    "title": re.sub(r"\s+", " ", e.find("a:title", NS).text.strip()),
                    "published": pub,
                    "abstract": re.sub(r"\s+", " ", e.find("a:summary", NS).text.strip()),
                    "cats": [c.get("term") for c in e.findall("a:category", NS)],
                })
    res[q] = items
    print(q, len(items))
    time.sleep(3.5)

io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
pool = {}
for q, items in res.items():
    for it in items:
        pool.setdefault(it["arxiv"], it).setdefault("q", [])
        pool[it["arxiv"]]["q"].append(q)
print("pool", len(pool))

lines = []
for it in sorted(pool.values(), key=lambda x: x["published"], reverse=True):
    lines.append("%s | %s | %s | %s" % (it["arxiv"], it["published"], ",".join(it["cats"][:2]), it["title"]))
    lines.append("    " + it["abstract"][:420])
io.open(r"C:\nay\github\MRI\searchpaper\_raw\crossdomain_arxiv.txt", "w", encoding="utf-8").write("\n".join(lines))
