"""Tighten every script line using the demucs vocal stem, then cut cam + game crops.
- speech = vocal RMS (10 ms) above max(-42 dBFS, peak-32 dB); gaps < 0.12 s bridged
- head/tail trimmed to speech (+0.05 / +0.10 s); inner gaps > MAXGAP cut to KEEP
- audio = vocals + game stem at GAME_GAIN (cleaner voice, game still audible)
Usage: python3 build/cut.py <source.mp4>
Writes assets/clips/<id>_cam.mp4, <id>_game.mp4 (game carries audio), build/lines.json"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
SRC = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEP = "/home/user/work/stems/sep/htdemucs"; PAD = 0.5
OUT = os.path.join(ROOT, "assets", "clips"); TMP = "/home/user/work/cut"; os.makedirs(TMP, exist_ok=True)
MAXGAP, KEEP, GAME_GAIN, SPEED = 0.20, 0.09, 0.32, 1.06
CAM = "crop=392:225:582:948,scale=1080:620:flags=lanczos,unsharp=5:5:0.7"
words = [w for s in json.load(open("/home/user/work/main_tx.json")) for w in s["w"]]
OFF = json.load(open("/home/user/work/stems/offsets.json"))
S = json.load(open(os.path.join(ROOT, "build", "script.json")))["lines"]

def speech(v, sr):
    hop = int(sr * 0.01); n = len(v) // hop
    rms = np.sqrt((v[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12); db = 20 * np.log10(rms)
    thr = max(-42.0, db.max() - 32.0); on = db > thr
    regs, i = [], 0
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]: j += 1
            regs.append([i * 0.01, j * 0.01]); i = j
        else: i += 1
    out = []
    for r in regs:
        if out and r[0] - out[-1][1] < 0.12: out[-1][1] = r[1]
        else: out.append(r)
    return [r for r in out if r[1] - r[0] >= 0.06]

lines = []
for ln in S:
    keep = []  # source-time intervals
    gains = []
    for k, (a, b) in enumerate(ln["pieces"]):
        d = f"{SEP}/{ln['id']}_{k}"
        v, sr = sf.read(d + "/vocals.wav"); v = v.mean(1)
        regs = [[r[0] - PAD + a, r[1] - PAD + a] for r in speech(v, sr)]
        regs = [r for r in regs if r[1] > a - 0.1 and r[0] < b + 0.1]  # stay inside the chosen window
        if not regs: raise SystemExit(f"no speech in {ln['id']}_{k}")
        regs[0][0] = max(regs[0][0], a - 0.03); regs[-1][1] = min(regs[-1][1], b + 0.03)
        regs = [r for r in regs if r[1] - r[0] > 0.04]
        s0, e0 = regs[0][0] - 0.04, regs[-1][1] + 0.08
        vs = np.concatenate([v[int((r[0] - a + PAD) * sr):int((r[1] - a + PAD) * sr)] for r in regs])
        gains.append(-20.0 - 20 * np.log10(np.sqrt((vs ** 2).mean()) + 1e-9))
        cur = [s0, None]
        for x, y in zip(regs, regs[1:]):
            if y[0] - x[1] > MAXGAP:
                cur[1] = x[1] + KEEP / 2; keep.append((cur[0], cur[1], k)); cur = [y[0] - KEEP / 2, None]
        cur[1] = e0; keep.append((cur[0], cur[1], k))
    H = ln.get("hold", 0.0)
    if H:  # keep the picture running after the line; the voice stem is faded out there
        s_, e_, k_ = keep[-1]; keep[-1] = (s_, e_ + H, k_); vend = (len(keep) - 1, e_ - s_)
    # build remixed audio per piece then cut
    fc, n = "", len(keep)
    T0 = max(0.0, keep[0][0] - 1.0)
    ins = ["-ss", f"{T0:.3f}", "-i", SRC]
    for k in range(len(ln["pieces"])):
        d = f"{SEP}/{ln['id']}_{k}"; ins += ["-i", d + "/vocals.wav", "-i", d + "/no_vocals.wav"]
    vfade = lambda i: (f",afade=t=out:st={vend[1]:.3f}:d=0.06" if H and i == vend[0] else "")
    for i, (s, e, k) in enumerate(keep):
        a = ln["pieces"][k][0]; ls, le = s - a + PAD, e - a + PAD
        vi, gi = 1 + 2 * k, 2 + 2 * k
        fc += (f"[0:v]trim={s - T0:.3f}:{e - T0:.3f},setpts=PTS-STARTPTS,fps=60,split[c{i}][g{i}];"
               f"[{vi}:a]atrim={ls:.3f}:{le:.3f},asetpts=PTS-STARTPTS{vfade(i)}[va{i}];"
               f"[{gi}:a]atrim={ls:.3f}:{le:.3f},asetpts=PTS-STARTPTS,volume={GAME_GAIN}[ga{i}];"
               f"[va{i}][ga{i}]amix=inputs=2:normalize=0,afade=t=in:d=0.01,afade=t=out:st={max(0, e - s - 0.015):.3f}:d=0.015[a{i}];")
    fx = 60 + ln["focus"] * (964 - 418)
    fc += "".join(f"[c{i}][g{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=2:a=1[cv][gv][aa];"
    fc += (f"[cv]setpts=PTS/{SPEED},{CAM}[cam];"
           f"[gv]setpts=PTS/{SPEED},crop=418:503:{fx:.0f}:415,scale=1080:1300:flags=lanczos,unsharp=5:5:0.5[game];"
           f"[aa]atempo={SPEED},volume={float(np.mean(gains)):.2f}dB,alimiter=limit=0.89:level=false[aud]")
    enc = ["-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", "-r", "60"]
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *ins, "-filter_complex", fc,
                    "-map", "[cam]", *enc, "-an", f"{OUT}/{ln['id']}_cam.mp4",
                    "-map", "[game]", "-map", "[aud]", *enc, "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", f"{OUT}/{ln['id']}_game.mp4"], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                f"{OUT}/{ln['id']}_game.mp4"], capture_output=True, text=True).stdout)
    def remap(t):
        acc = 0.0
        for s, e, _ in keep:
            if t < s: return acc / SPEED
            if t <= e: return (acc + t - s) / SPEED
            acc += e - s
        return acc / SPEED
    lw = [[round(remap(w[0]), 3), round(remap(w[1]), 3), w[2]] for w in words
          if any(s - 0.15 <= w[0] <= e for s, e, _ in keep)]
    cuts, acc = [], 0.0
    for s, e, _ in keep[:-1]:
        acc += e - s; cuts.append(round(acc / SPEED, 3))
    lines.append({"id": ln["id"], "sec": ln["sec"], "dur": round(dur, 3), "words": lw, "cuts": cuts,
                  "src": [round(keep[0][0], 2), round(keep[-1][1], 2)]})
    print(f"{ln['id']:3s} {sum(b - a for a, b in ln['pieces']):5.2f} -> {dur:5.2f}  " + " ".join(w[2] for w in lw), flush=True)
json.dump(lines, open(os.path.join(ROOT, "build", "lines.json"), "w"), ensure_ascii=False, indent=0)
print("TOTAL speech", round(sum(l["dur"] for l in lines), 2))
