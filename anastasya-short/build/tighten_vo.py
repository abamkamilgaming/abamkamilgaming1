"""Buang awkward pause dalam setiap line VO: gap antara perkataan > MAXGAP dipotong ke KEEP,
senyap depan/belakang dibuang. assets/voice/raw/<id>.wav -> assets/voice/<id>.wav + build/vo_words_tight.json"""
import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "assets", "voice"); RAW = os.path.join(V, "raw")
MAXGAP, KEEP, HEAD, TAIL = 0.22, 0.12, 0.03, 0.12
words = json.load(open(os.path.join(ROOT, "build", "vo_words.json")))
out = {}; tot = 0
for vid, d in words.items():
    W = d["words"]
    segs, cur = [], max(0.0, W[0][1] - HEAD)
    for a, b in zip(W, W[1:]):
        if b[1] - a[2] > MAXGAP:
            segs.append((cur, a[2] + KEEP / 2)); cur = b[1] - KEEP / 2
    segs.append((cur, min(d["dur"], W[-1][2] + TAIL)))
    def remap(t):
        acc = 0.0
        for s, e in segs:
            if t <= e: return round(acc + max(0.0, t - s), 3)
            acc += e - s
        return round(acc, 3)
    parts = "".join(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,"
                    f"afade=t=out:st={max(0, e - s - 0.012):.3f}:d=0.012[p{i}];" for i, (s, e) in enumerate(segs))
    fc = parts + "".join(f"[p{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1,loudnorm=I=-15:TP=-1.5:LRA=7[a]"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", os.path.join(RAW, vid + ".wav"),
                    "-filter_complex", fc, "-map", "[a]", "-ar", "48000", os.path.join(V, vid + ".wav")], check=True)
    dur = sum(e - s for s, e in segs); tot += dur
    out[vid] = {"dur": round(dur, 3), "words": [[w, remap(s), remap(e)] for w, s, e in W], "cuts": len(segs) - 1}
    print(vid, f"{d['dur']:.2f} -> {dur:.2f} ({len(segs)-1} pause dipotong)")
json.dump(out, open(os.path.join(ROOT, "build", "vo_words_tight.json"), "w"), ensure_ascii=False, indent=0)
print("total", round(tot, 2))
