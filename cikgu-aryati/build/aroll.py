"""Tighten the Cikgu Aryati take: cut every awkward pause, reframe to 1080x1920 @60fps.
Usage: python3 build/aroll.py <Cikgu Aryati.mp4>
Writes assets/video/aroll.mp4 and build/edl.json (utterances remapped onto the tight clip)."""
import json, os, subprocess, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1]

# (speaker, caption text, whisper start, whisper end)  Q = penanya, A = Cikgu Aryati
U = [
    ("Q", "Cikgu, cikgu!", 0.00, 1.40),
    ("A", "Ya, saya.", 1.44, 1.98),
    ("Q", "Viral?", 2.44, 3.04), ("A", "Tular.", 3.06, 3.50),
    ("Q", "Selfie?", 3.80, 4.40), ("A", "Swafoto.", 4.78, 5.38),
    ("Q", "Hashtag?", 5.68, 6.28), ("A", "Tanda pagar.", 6.36, 7.00),
    ("Q", "Emoji?", 7.40, 7.78), ("A", "Emoji.", 8.32, 8.92),
    ("Q", "Netizen?", 9.18, 9.78), ("A", "Warganet.", 10.02, 10.62),
    ("Q", "Kuey teow?", 10.74, 11.34), ("A", "Kuetiau.", 11.52, 12.30),
    ("Q", "Mee hoon?", 12.44, 13.04), ("A", "Bihun atau Mihun.", 13.14, 15.02),
    ("Q", "Mee goreng?", 15.10, 15.78), ("A", "Mi goreng.", 15.90, 16.70),
    ("A", "Dapat sesuatu?", 16.94, 18.02),
]
TAIL = 1.35          # keep a beat after the last line (thumbs-up)
GAP_QA, GAP_AQ = 0.07, 0.12   # pause left between question->answer, answer->next question
THR = -19.0          # dB (room tone sits around -26, speech above -16)

pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True).stdout
a = np.frombuffer(pcm, np.int16).astype(float) / 32768
H = 160  # 10 ms
db = 20 * np.log10(np.array([np.sqrt(np.mean(a[i:i + H] ** 2) + 1e-12) for i in range(0, len(a) - H, H)]))
dbat = lambda t: db[min(len(db) - 1, max(0, int(round(t * 100))))]
# Cikgu's voice is ~5 dB quieter than the asker's (further from the phone mic): her lines get a lower
# threshold and a 50 ms look-ahead, so soft endings ("sa-YA") are not taken for silence.
THR_SPK = {"Q": THR, "A": -21.0}
MIN_END = {1: 2.32}   # "Ya, saya." — the second syllable of "saya" runs to 2.30 s

seg = []
for k, (spk, txt, s, e) in enumerate(U):
    thr = THR_SPK[spk]
    loud = lambda t: any(dbat(t + d * 0.01) > thr for d in range(3 if spk == "A" else 1))
    lo = U[k - 1][3] + 0.02 if k else 0.0            # never reach into the previous line
    hi = U[k + 1][2] - 0.04 if k + 1 < len(U) else e + 0.4
    t = s + 0.1
    while t > max(lo, s - 0.25) and loud(t - 0.03): t -= 0.01   # walk back to the onset
    s2 = max(0.0, t - 0.03)
    t = e - 0.1
    while t < min(hi, e + 0.25) and loud(t + 0.01): t += 0.01    # walk forward to the release
    e2 = max(t + (0.09 if spk == "A" else 0.06), MIN_END.get(k, 0), e + (0.06 if spk == "A" else 0.0))
    seg.append([spk, txt, round(s2, 3), round(e2, 3)])
seg[0][2] = 0.0
seg[-1][3] = round(seg[-1][3] + TAIL, 3)

# keep ranges: cut each gap down to GAP_*
keep = [[seg[0][2], seg[0][3]]]
for i in range(1, len(seg)):
    prev_e, s = seg[i - 1][3], seg[i][2]
    want = GAP_QA if seg[i - 1][0] == "Q" and seg[i][0] == "A" else GAP_AQ
    if s - prev_e <= want + 0.03:
        keep[-1][1] = seg[i][3]                 # natural gap is fine, no cut
    else:
        keep[-1][1] = round(prev_e + want / 2, 3)
        keep.append([round(s - want / 2, 3), seg[i][3]])

def remap(t):
    acc = 0.0
    for s, e in keep:
        if t <= e: return round(acc + max(0.0, t - s), 3)
        acc += e - s
    return round(acc, 3)

cuts, acc = [], 0.0
for s, e in keep[:-1]:
    acc += e - s; cuts.append(round(acc, 3))

fc = ""
for i, (s, e) in enumerate(keep):
    fc += (f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS[v{i}];"
           f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,"
           f"afade=t=out:st={max(0, e - s - 0.012):.3f}:d=0.012[a{i}];")
n = len(keep)
fc += "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac];"
fc += "[vc]fps=60,format=yuv420p[v];"
# clean classroom fan hiss, tame lows, even out the two voices, about -14 LUFS
fc += ("[ac]highpass=f=90,afftdn=nf=-30:nr=12,equalizer=f=3500:t=q:w=1.2:g=2,"
       "acompressor=threshold=0.12:ratio=3:attack=8:release=120:makeup=2,"
       "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]")
dst = os.path.join(ROOT, "assets", "video", "aroll.mp4")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc,
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "13",
                "-g", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", dst],
               check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
                           capture_output=True, text=True).stdout)
edl = {"dur": round(dur, 3), "cuts": cuts, "keep": keep,
       "lines": [{"spk": spk, "text": t, "s": remap(s), "e": remap(e), "raw": [s, e]} for spk, t, s, e in seg]}
json.dump(edl, open(os.path.join(ROOT, "build", "edl.json"), "w"), ensure_ascii=False, indent=1)
print(f"raw 19.56s -> {dur:.2f}s, {len(cuts)} cuts")
for l in edl["lines"]: print(f'{l["spk"]} {l["s"]:6.2f}-{l["e"]:6.2f}  {l["text"]}')
