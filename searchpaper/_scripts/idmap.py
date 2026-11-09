import json, os, time, urllib.request

ROOT = r"C:\nay\github\MRI\searchpaper"
RAW = os.path.join(ROOT, "_raw")
UA = {"User-Agent": "Mozilla/5.0 (research; mailto:qoder@example.com)", "Content-Type": "application/json"}


def batch(ids):
    body = json.dumps({"ids": ids}).encode()
    for i in range(4):
        try:
            req = urllib.request.Request(
                "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,externalIds,openAccessPdf,abstract",
                data=body, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print("retry", i, e, flush=True)
            time.sleep(10 * (i + 1))
    return []


if __name__ == "__main__":
    d = json.load(open(os.path.join(RAW, "details.json"), encoding="utf-8"))
    ids_out = json.load(open(os.path.join(RAW, "idmap.json"), encoding="utf-8")) if os.path.exists(os.path.join(RAW, "idmap.json")) else {}
    todo = [(k, v) for k, v in d.items() if k not in ids_out and v.get("doi")]
    for start in range(0, len(todo), 20):
        chunk = todo[start:start + 20]
        res = batch(["DOI:" + v["doi"].split("doi.org/")[-1] for _, v in chunk])
        for (k, v), r in zip(chunk, res):
            ax = ((r or {}).get("externalIds") or {}).get("ArXiv")
            ids_out[k] = {"arxiv": ax, "pdf": ((r or {}).get("openAccessPdf") or {}).get("url"),
                          "s2abs": (r or {}).get("abstract")}
            print(("OK  " if ax else "--- "), k, ax, v["title"][:55], flush=True)
        json.dump(ids_out, open(os.path.join(RAW, "idmap.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(4)
    print("done", sum(1 for x in ids_out.values() if x.get("arxiv")), "/", len(ids_out))
