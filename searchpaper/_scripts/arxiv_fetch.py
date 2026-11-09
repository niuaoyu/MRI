import json, os, re, sys, time, urllib.parse, urllib.request, html
import xml.etree.ElementTree as ET

ROOT = r"C:\nay\github\MRI\searchpaper"
RAW = os.path.join(ROOT, "_raw")
UA = "Mozilla/5.0 (research; mailto:qoder@example.com)"
NS = {"a": "http://www.w3.org/2005/Atom"}
KEY = r"limitat|future work|future direction|we do not|we cannot|fail(?:s|ed)? to|assum(?:e|es|ption)|remains? (?:un|a )|challeng|not (?:yet )?(?:able|possible)|open problem"


def get(url, timeout=25, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(5 * (i + 1))


def arxiv_by_id(aid):
    raw = get("https://export.arxiv.org/api/query?id_list=" + aid)
    if not raw:
        return None
    try:
        root = ET.fromstring(raw)
    except Exception:
        return None
    for e in root.findall("a:entry", NS):
        return {
            "title": e.find("a:title", NS).text.strip(),
            "arxiv_id": e.find("a:id", NS).text.strip().split("/abs/")[-1],
            "abstract": re.sub(r"\s+", " ", e.find("a:summary", NS).text.strip()),
            "published": e.find("a:published", NS).text[:10],
        }
    return None


def arxiv_search(title, doi=""):
    m = re.search(r"arxiv\.([0-9]{4}\.[0-9]{4,5})", (doi or "").lower())
    if m:
        hit = arxiv_by_id(m.group(1))
        if hit:
            return hit
    words = re.sub(r"[^A-Za-z0-9 ]", " ", title).split()
    q = 'ti:"%s"' % " ".join(words[:12])
    for query in (q, "all:" + " AND ".join(words[:8])):
        url = "https://export.arxiv.org/api/query?search_query=%s&max_results=3" % urllib.parse.quote(query)
        raw = get(url)
        if not raw:
            continue
        try:
            root = ET.fromstring(raw)
        except Exception:
            continue
        for e in root.findall("a:entry", NS):
            t = e.find("a:title", NS).text.strip().lower()
            common = len(set(words[:6]) & set(re.sub(r"[^a-z0-9 ]", " ", t).split()))
            if common < 3:
                continue
            return {
                "title": e.find("a:title", NS).text.strip(),
                "arxiv_id": e.find("a:id", NS).text.strip().split("/abs/")[-1],
                "abstract": re.sub(r"\s+", " ", e.find("a:summary", NS).text.strip()),
                "published": e.find("a:published", NS).text[:10],
            }
    return None


def clean(h):
    h = re.sub(r"<script.*?</script>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<style.*?</style>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h)
    return re.sub(r"\s+", " ", h).strip()


def split_sents(t):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", t)
    return [p.strip() for p in parts if p.strip()]


def analyse(arxiv_id):
    h = get("https://arxiv.org/html/" + arxiv_id)
    if not h:
        return None, []
    secs = []
    for m in re.finditer(r"<(h[1-6])[^>]*>(.*?)</\1>", h, flags=re.S | re.I):
        head = clean(m.group(2))
        if re.search(r"limitation|future work|discussion|conclusion|outlook", head, re.I):
            start = m.end()
            nxt = re.search(r"<h[1-6][^>]*>", h[start:], flags=re.I)
            end = start + (nxt.start() if nxt else 20000)
            body = clean(h[start:end])
            if len(body) > 60:
                secs.append({"heading": head, "text": body[:6000]})
    # paragraph-level hits anywhere in the paper
    paras = []
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", h, flags=re.S | re.I):
        t = clean(m.group(1))
        if len(t) > 60 and re.search(KEY, t, re.I):
            paras.append(t)
    # dedupe paragraphs contained in sections
    sents = []
    for t in paras:
        for s in split_sents(t):
            if re.search(KEY, s, re.I) and 40 < len(s) < 600:
                if s not in sents:
                    sents.append(s)
    return secs, sents[:12]


if __name__ == "__main__":
    d = json.load(open(os.path.join(RAW, "details.json"), encoding="utf-8"))
    out = json.load(open(os.path.join(RAW, "arxiv.json"), encoding="utf-8")) if os.path.exists(os.path.join(RAW, "arxiv.json")) else {}
    keys = json.loads(sys.argv[1]) if len(sys.argv) > 1 else list(d.keys())
    for k in keys:
        v = d[k]
        if k in out and out[k].get("found") and out[k].get("sections"):
            continue
        time.sleep(3.5)
        hit = arxiv_search(v["title"], v.get("doi") or "")
        rec = {"openalex": k, "title": v["title"], "found": bool(hit)}
        if hit:
            rec.update(hit)
            secs, sents = analyse(hit["arxiv_id"])
            rec["sections"] = secs or []
            rec["limitation_sentences"] = sents
            print("OK ", k, hit["arxiv_id"], "secs=%d sent=%d" % (len(rec["sections"]), len(sents)), v["title"][:48], flush=True)
        else:
            print("---", k, v["title"][:55], flush=True)
        out[k] = rec
        time.sleep(3.5)
    json.dump(out, open(os.path.join(RAW, "arxiv.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
