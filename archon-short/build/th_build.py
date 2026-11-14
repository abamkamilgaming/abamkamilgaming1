"""Cut the talking-head take into one tight clip per script line.
- pauses longer than MAXGAP (from silencedetect) are cut down to KEEP
- loudness brought down to about -14 LUFS with a limiter
- word timings (whisper) remapped onto each tightened clip
Usage: python3 build/th_build.py <talking_head.mp4> <th_tx.json>
Writes assets/th/<id>.mp4 and build/th_words.json"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, TX = sys.argv[1], sys.argv[2]
OUT = os.path.join(ROOT, "assets", "th"); os.makedirs(OUT, exist_ok=True)
MAXGAP, KEEP = 0.18, 0.10
SPEED = 1.15
# filler words removed: (line, raw word text, occurrence)
DROP = {("c1b", "lepas", 0), ("c1b", "tu", 0), ("n1", "ni", 0), ("n1", "dengar", 0), ("n1", "ni.", 0),
        ("e1", "Kawan", 0), ("e1", "akan", 0), ("e1", "dapat", 0), ("e1", "reward", 0), ("s1", "yang", 0)}

# line windows in the raw take (seconds), set from silencedetect + transcript
LINES = [
    ("h1", 0.70, 7.12), ("h2", 7.92, 11.66), ("d1", 13.15, 22.14), ("s1", 22.88, 29.62),
    ("r1", 30.02, 36.45), ("r2", 36.45, 39.36), ("z1", 39.74, 42.60), ("z2", 43.06, 49.56),
    ("c1a", 50.02, 52.10), ("c1b", 52.10, 56.25), ("n1", 56.25, 62.94), ("e1", 63.95, 72.80),
    ("e2", 72.80, 74.95),
]
# whisper slips -> what was actually said
FIX = {"Wee,": "Weh,", "Wee": "Weh", "Noi.": "Noy!", "45": "paling", "remang": "meremang",
       "bergamung": "bergabung", "Kawan": "Korang", "Celestial,": "Celestia,", "Eternity.": "eternity.",
       "time": "time", "babe.": "babe!", "Gila.": "Gila!"}

sil = subprocess.run(["ffmpeg", "-nostdin", "-i", SRC, "-af", "highpass=f=80,silencedetect=noise=-38dB:d=0.22",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", sil)]
ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", sil)]
SIL = list(zip(starts, ends))
words = [w for seg in json.load(open(TX)) for w in seg["w"]]

out = {}
for lid, a, b in LINES:
    lw = [w for w in words if (a - 0.8 if lid == "h1" else a - 0.05) <= w[0] < b - 0.02]
    # regions to remove: long silences + dropped filler words
    rm = [(s + KEEP / 2, e - KEEP / 2) for s, e in SIL if s > a + 0.05 and e < b - 0.05 and e - s > MAXGAP]
    seen = {}
    for i, (ws, we, wt) in enumerate(lw):
        k = (lid, wt); n = seen.get(k, 0); seen[k] = n + 1
        if (lid, wt, n) in DROP:
            nxt = lw[i + 1][0] if i + 1 < len(lw) else we
            rm.append((max(a, ws - 0.04), min(b, nxt - 0.04)))
    rm.sort(); merged = []
    for r in rm:
        if merged and r[0] <= merged[-1][1]: merged[-1] = (merged[-1][0], max(merged[-1][1], r[1]))
        else: merged.append(r)
    keep, cur = [], a
    for s, e in merged:
        if s > cur: keep.append((cur, s))
        cur = max(cur, e)
    keep.append((cur, b))
    def remap(t):
        acc = 0.0
        for s, e in keep:
            if t <= e: return round(acc + max(0.0, t - s), 3)
            acc += e - s
        return round(acc, 3)
    cuts, acc = [], 0.0
    for s, e in keep[:-1]:
        acc += e - s; cuts.append(round(acc, 3))
    dropped = set()
    seen = {}
    for i, (ws, we, wt) in enumerate(lw):
        k = (lid, wt); n = seen.get(k, 0); seen[k] = n + 1
        if (lid, wt, n) in DROP: dropped.add(i)
    W = [[FIX.get(w, w), round(remap(max(s, a)) / SPEED, 3), round(remap(e) / SPEED, 3)]
         for i, (s, e, w) in enumerate(lw) if i not in dropped]
    cuts = [round(c / SPEED, 3) for c in cuts]
    fc = ""
    for i, (s, e) in enumerate(keep):
        fc += (f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS,fps=60[v{i}];"
               f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,"
               f"afade=t=out:st={max(0, e - s - 0.015):.3f}:d=0.015[a{i}];")
    n = len(keep)
    fc += "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a0];"
    fc = fc.replace("concat=n=%d:v=1:a=1[v][a0];" % n, "concat=n=%d:v=1:a=1[v0][a0];[v0]setpts=PTS/%s[v];" % (n, SPEED))
    fc += f"[a0]atempo={SPEED},volume=-5.5dB,alimiter=limit=0.89:level=false[a]"
    dst = os.path.join(OUT, lid + ".mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[v]",
                    "-map", "[a]", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", dst], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
                               capture_output=True, text=True).stdout)
    out[lid] = {"dur": round(dur, 3), "words": W, "cuts": cuts, "raw": [a, b]}
    print(f"{lid:4s} {b - a:5.2f} -> {dur:5.2f}  cuts={len(cuts)}  " + " ".join(w[0] for w in W))
json.dump(out, open(os.path.join(ROOT, "build", "th_words.json"), "w"), ensure_ascii=False, indent=0)
print("total speech", round(sum(v["dur"] for v in out.values()), 2))
