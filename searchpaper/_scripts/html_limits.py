import json, os, re, time, urllib.request, html

ROOT = r"C:\nay\github\MRI\searchpaper"
RAW = os.path.join(ROOT, "_raw")
UA = "Mozilla/5.0 (research; mailto:qoder@example.com)"
KEY = r"limitat|future work|future direction|we do not|we cannot|fail(?:s|ed)? to|assum(?:e|es|ption)|remains? (?:un|a )|challeng|not (?:yet )?(?:able|possible)|open problem"


def get(url, timeout=30, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(4 * (i + 1))


def clean(h):
    h = re.sub(r"<script.*?</script>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<style.*?</style>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h)
    return re.sub(r"\s+", " ", h).strip()


def split_sents(t):
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", t) if p.strip()]


def analyse(aid):
    h = get("https://arxiv.org/html/" + aid)
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
                secs.append({"heading": head, "text": body[:8000]})
    paras = []
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", h, flags=re.S | re.I):
        t = clean(m.group(1))
        if len(t) > 60 and re.search(KEY, t, re.I):
            paras.append(t)
    sents = []
    for t in paras:
        for s in split_sents(t):
            if re.search(KEY, s, re.I) and 40 < len(s) < 700 and s not in sents:
                sents.append(s)
    return secs, sents[:14]


if __name__ == "__main__":
    d = json.load(open(os.path.join(RAW, "details.json"), encoding="utf-8"))
    idmap = json.load(open(os.path.join(RAW, "idmap.json"), encoding="utf-8"))
    out = json.load(open(os.path.join(RAW, "arxiv.json"), encoding="utf-8")) if os.path.exists(os.path.join(RAW, "arxiv.json")) else {}
    for k, v in d.items():
        aid = (idmap.get(k) or {}).get("arxiv")
        if not aid:
            m = re.search(r"arxiv\.([0-9]{4}\.[0-9]{4,5})", (v.get("doi") or "").lower())
            if m:
                aid = m.group(1)
        if not aid:
            continue
        if k in out and out[k].get("arxiv_id", "").split("v")[0] == aid and out[k].get("sections"):
            continue
        secs, sents = analyse(aid)
        out[k] = {"openalex": k, "title": v["title"], "found": secs is not None,
                  "arxiv_id": aid, "abstract": (idmap.get(k) or {}).get("s2abs") or v.get("abstract"),
                  "sections": secs or [], "limitation_sentences": sents}
        print(("OK  " if secs else "--- "), k, aid, "secs=%d sent=%d" % (len(secs or []), len(sents)), v["title"][:45], flush=True)
        json.dump(out, open(os.path.join(RAW, "arxiv.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(2)
