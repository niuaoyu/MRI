import json, os, re, time, urllib.parse, urllib.request, html

ROOT = r"C:\nay\github\MRI\searchpaper"
RAW = os.path.join(ROOT, "_raw")
UA = "Mozilla/5.0 (research; mailto:qoder@example.com)"
SELECT = ("id,doi,title,publication_year,publication_date,cited_by_count,"
          "abstract_inverted_index,authorships,primary_location,type")


def get(url, tries=4, timeout=60):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def abstract(inv):
    if not inv:
        return ""
    pos = [(i, w) for w, idxs in inv.items() for i in idxs]
    pos.sort()
    return " ".join(w for _, w in pos)


IDS = """W4401437780 W4403071569 W4403071497 W4391452647 W4405468760 W4409865654
W4414602808 W7155184131 W7161324349 W7167226951 W7214391406 W7131086421 W7220676654
W7167829670 W7160327394 W7162287616 W7196949058 W4405303959 W4411996531 W7138869125
W4403649766 W7134047657 W7214158550 W7147237246 W4415089519 W4417137794 W4414687007
W4394929009 W7151509712 W4417358728 W7148874316 W4402727307 W4399563522 W4403878288
W4408519784 W4402716356 W4402716382 W4402753754 W4402951670 W7160140527 W4394625900
W4404965629 W4400817548 W4417125790 W4400582074 W4397049055 W4417000834 W7138255617
W7137992698 W4402619788""".split()

if __name__ == "__main__":
    out = {}
    for wid in IDS:
        url = "https://api.openalex.org/works/%s?select=%s" % (wid, SELECT)
        try:
            w = json.loads(get(url))
        except Exception as e:
            print("ERR", wid, e)
            continue
        loc = w.get("primary_location") or {}
        out[wid] = {
            "id": wid,
            "title": w.get("title"),
            "year": w.get("publication_year"),
            "date": w.get("publication_date"),
            "doi": w.get("doi"),
            "cites": w.get("cited_by_count"),
            "venue": (loc.get("source") or {}).get("display_name"),
            "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])][:4],
            "abstract": abstract(w.get("abstract_inverted_index")),
            "landing": loc.get("landing_page_url"),
            "pdf": loc.get("pdf_url"),
        }
        time.sleep(0.15)
    json.dump(out, open(os.path.join(RAW, "details.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("saved", len(out))
