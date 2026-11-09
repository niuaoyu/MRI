import json, io, re, sys

d = json.load(io.open(r"C:\nay\github\MRI\searchpaper\_raw\arxiv.json", encoding="utf-8"))
bad = re.compile(r"math|mathcal|theta|sigma|mathbf|equation|\\\\")
out = []
for k, v in d.items():
    if not v.get("found"):
        out.append("## %s | NOT FOUND | %s" % (k, v["title"]))
        continue
    ls = [s for s in v.get("limitation_sentences", []) if not bad.search(s) and 50 < len(s) < 420]
    out.append("## %s | %s | %s" % (k, v["arxiv_id"], v["title"]))
    for s in ls[:7]:
        out.append("   - " + s)
txt = "\n".join(out)
io.open(r"C:\nay\github\MRI\searchpaper\_raw\limits.txt", "w", encoding="utf-8").write(txt)
print(len(out), "lines")
