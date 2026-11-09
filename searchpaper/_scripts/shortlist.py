import json, os, re

ROOT = r"C:\nay\github\MRI\searchpaper"
RAW = os.path.join(ROOT, "_raw")

CARDIAC = ["cardiac", "heart", "ventric", "myocard", "atrial", "cine", "cmr", "mri", "echocardiogra", "4d flow"]
CORR = ["correspond", "registrat", "matching", "template", "deform", "point identity", "landmark"]
IMPL = ["implicit", "sdf", "signed distance", "neural field", "neural representation", "template", "mesh", "surface"]

recs = {}

def add(r, src):
    rid = r["id"]
    if rid not in recs:
        r = dict(r)
        r["_src"] = [src]
        recs[rid] = r
    else:
        recs[rid]["_src"].append(src)
        for k, v in r.items():
            if v and not recs[rid].get(k):
                recs[rid][k] = v

for name, lst in json.load(open(os.path.join(RAW, "citations_2024plus.json"), encoding="utf-8")).items():
    for r in lst:
        add(r, "cite:" + name)

for q, lst in json.load(open(os.path.join(RAW, "topic_search.json"), encoding="utf-8")).items():
    for r in lst:
        add(r, "q:" + q)


def text(r):
    return ((r.get("title") or "") + " " + (r.get("abstract") or "")).lower()


out = []
for r in recs.values():
    t = text(r)
    y = r.get("year") or 0
    if y < 2024:
        continue
    ncard = sum(1 for k in CARDIAC if k in t)
    ncorr = sum(1 for k in CORR if k in t)
    nimpl = sum(1 for k in IMPL if k in t)
    # cardiac gate: must mention heart anatomy or cardiac imaging
    strong_cardiac = any(k in t for k in ["cardiac", "heart", "ventric", "myocard", "atrial", "cine mri", "cmr"])
    score = 3 * ncard + 2 * ncorr + nimpl + min(r.get("cites") or 0, 50) / 25.0
    if strong_cardiac:
        score += 8
    r["_score"] = round(score, 1)
    r["_tags"] = ("CARD " if strong_cardiac else "") + ("CORR " if ncorr >= 2 else "") + ("IMPL" if nimpl >= 2 else "")
    out.append(r)

out.sort(key=lambda r: -r["_score"])
json.dump(out, open(os.path.join(RAW, "pool.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("pool:", len(out))
print("\n=== cardiac candidates ===")
for r in out:
    if "CARD" in r["_tags"]:
        print("%5.1f | %s | c=%-3s | %-30s | %s" % (
            r["_score"], r["year"], r["cites"], (r["venue"] or "")[:30], (r["title"] or "")[:110]))
