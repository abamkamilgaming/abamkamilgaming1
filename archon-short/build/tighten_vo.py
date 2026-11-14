"""Remove awkward pauses inside each VO line: any gap between words longer
than MAXGAP is cut down to KEEP seconds. Rewrites assets/voice/<id>.wav
(from assets/voice/raw/<id>.wav) and build/vo_words_tight.json."""
import json, subprocess, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "assets", "voice")
RAW = os.path.join(V, "raw")
MAXGAP, KEEP = 0.30, 0.20

words = json.load(open(os.path.join(ROOT, "build", "vo_words.json")))
os.makedirs(RAW, exist_ok=True)
out = {}
for vid, d in words.items():
    raw = os.path.join(RAW, vid + ".wav")
    if not os.path.exists(raw):
        shutil.move(os.path.join(V, vid + ".wav"), raw)
    W = d["words"]
    # keep-segments in source time
    segs, cur_s = [], 0.0
    for a, b in zip(W, W[1:]):
        gap = b[1] - a[2]
        if gap > MAXGAP:
            cut_s = a[2] + KEEP / 2
            cut_e = b[1] - KEEP / 2
            segs.append((cur_s, cut_s))
            cur_s = cut_e
    segs.append((cur_s, d["dur"]))
    # map word times
    def remap(t):
        acc = 0.0
        for s, e in segs:
            if t <= e:
                return round(acc + max(0.0, t - s), 3)
            acc += e - s
        return round(acc, 3)
    nw = [[w, remap(s), remap(e)] for w, s, e in W]
    parts = "".join(
        f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0,e-s-0.012):.3f}:d=0.012[p{i}];"
        for i, (s, e) in enumerate(segs))
    fc = parts + "".join(f"[p{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[a]"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw, "-filter_complex", fc,
                    "-map", "[a]", "-ar", "48000", os.path.join(V, vid + ".wav")], check=True)
    dur = sum(e - s for s, e in segs)
    out[vid] = {"dur": round(dur, 3), "words": nw, "cuts": len(segs) - 1}
    print(vid, f"{d['dur']:.2f} -> {dur:.2f}  ({len(segs)-1} pause cut)")
json.dump(out, open(os.path.join(ROOT, "build", "vo_words_tight.json"), "w"), ensure_ascii=False, indent=0)
