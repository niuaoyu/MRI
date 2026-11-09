import io, json, os, time
import html_limits as hl

IDS = [
    ("2601.04494", "Differential Locally Injective Grid Deformation and Optimization"),
    ("2605.18039", "SGSoft: Template-Guided Soft Signals for 3D Shape Correspondence"),
    ("2609.04202", "TokenMatch: 3D Mesh Correspondence Transformer"),
    ("2411.03511", "Beyond Complete Shapes: benchmark for 3D shape surface matching"),
    ("2610.22325", "Dense4D: Pixel-Level 4D Human Correspondence"),
    ("2606.29167", "Geometry-Grounded Articulation and Test-Time Adaptation"),
    ("2602.06590", "ILP Geometrically Consistent Partial-Partial Shape Matching"),
    ("2607.03330", "GrowFields: Topology-Changing Plant Growth"),
    ("2507.18677", "HeartUnloadNet: Cycle-Consistent Graph Network"),
]

OUT = r"C:\nay\github\MRI\searchpaper\_raw\arxiv_cross.json"
out = {}
for aid, title in IDS:
    secs, sents = hl.analyse(aid)
    out[aid] = {"title": title, "found": secs is not None, "sections": secs or [],
                "limitation_sentences": sents}
    print(("OK  " if secs else "--- "), aid, "secs=%d sent=%d" % (len(secs or []), len(sents)))
    time.sleep(3)

json.dump(out, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("written", OUT)
