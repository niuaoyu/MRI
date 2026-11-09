import json, io, re

d = json.load(io.open(r"C:\nay\github\MRI\searchpaper\_raw\crossdomain.json", encoding="utf-8"))
pool = {}
for q, items in d.items():
    for it in items:
        it.setdefault("queries", []).append(q)
        if it["id"] in pool:
            pool[it["id"]]["queries"].append(q)
        else:
            pool[it["id"]] = it

KEY = re.compile(r"biject|homeomorph|injectiv|point identity|dense correspondence|"
                 r"cycle consistency|topolog|functional map|diffeomorph|partial|"
                 r"canonical|template|correspondence", re.I)
rows = []
for it in pool.values():
    txt = (it["title"] or "") + " " + (it["abstract"] or "")
    hits = len(set(m.group(0).lower() for m in KEY.finditer(txt)))
    it["score"] = hits * 3 + min(it["cites"], 60) / 10.0 + len(it["queries"])
    rows.append(it)
rows.sort(key=lambda x: -x["score"])

out = []
for it in rows[:70]:
    out.append("%s | %s | %s | cites=%d | %s | %s" % (
        it["id"], it["year"], it["title"], it["cites"], it["venue"][:40],
        " / ".join(sorted(set(it["queries"])))[:90]))
out.append("\n===== ABSTRACTS (top 40) =====")
for it in rows[:40]:
    out.append("\n## %s | %s | %s" % (it["id"], it["year"], it["title"]))
    out.append((it["abstract"] or "")[:700])

io.open(r"C:\nay\github\MRI\searchpaper\_raw\crossdomain_ranked.txt", "w", encoding="utf-8").write("\n".join(out))
print("pool", len(pool))
