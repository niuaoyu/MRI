# -*- coding: utf-8 -*-
"""Last-45-day arXiv sweep: cardiac mesh / correspondence / implicit template."""
import io, json, re, time, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

OUT = r"C:\nay\github\MRI\searchpaper\_raw\newest.json"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

QUERIES = [
    'abs:"cardiac" AND abs:"mesh"',
    'abs:"cardiac" AND abs:"correspondence"',
    'abs:"heart" AND abs:"reconstruction" AND abs:"magnetic resonance"',
    'abs:"dense correspondence" AND cat:cs.CV',
    'abs:"shape correspondence" AND cat:cs.CV',
    'abs:"template" AND abs:"deform" AND abs:"implicit"',
    'abs:"4D" AND abs:"heart"',
    'abs:"cine" AND abs:"MRI"',
    'abs:"point identity"',
    'abs:"diffeomorphic" AND abs:"correspondence"',
    'abs:"cardiac" AND abs:"implicit neural"',
    'abs:"ventricle" AND abs:"reconstruction"',
]


def fetch(q, maxr=60):
    url = ("http://export.arxiv.org/api/query?search_query="
           + urllib.parse.quote(q)
           + "&start=0&max_results=%d&sortBy=submittedDate&sortOrder=descending" % maxr)
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-sweep/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if i == 2:
                print("FAIL", q, e)
                return None
            time.sleep(5 * (i + 1))


def parse(xml):
    root = ET.fromstring(xml)
    out = []
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.rsplit("/", 1)[-1]
        pub = e.find("a:published", NS).text[:10]
        title = re.sub(r"\s+", " ", e.find("a:title", NS).text or "").strip()
        summ = re.sub(r"\s+", " ", e.find("a:summary", NS).text or "").strip()
        cats = [c.get("term") for c in e.findall("a:category", NS)]
        out.append({"id": aid, "date": pub, "title": title, "abs": summ, "cats": cats})
    return out


if __name__ == "__main__":
    seen = {}
    for q in QUERIES:
        xml = fetch(q)
        if not xml:
            continue
        items = parse(xml)
        n = 0
        for it in items:
            if it["date"] < "2026-09-15":
                continue
            if it["id"] not in seen:
                it["q"] = [q]
                seen[it["id"]] = it
                n += 1
            else:
                seen[it["id"]]["q"].append(q)
        print("%-55s +%d  (total %d)" % (q[:55], n, len(seen)), flush=True)
        time.sleep(3.2)
    rows = sorted(seen.values(), key=lambda x: x["date"], reverse=True)
    json.dump(rows, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("SAVED", len(rows))
