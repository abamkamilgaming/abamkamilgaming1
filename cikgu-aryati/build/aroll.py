"""Tighten the Cikgu Aryati take: cut every awkward pause, reframe to 1080x1920 @60fps.
Usage: python3 build/aroll.py <Cikgu Aryati.mp4>
Writes assets/video/aroll.mp4 and build/edl.json (utterances remapped onto the tight clip)."""
import json, os, subprocess, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1]

# (speaker, caption text, speech start, speech end) in the raw take, in seconds.
# Measured from the audio itself (bursts above -17 dB, soft onsets like "Ya", the "s" of Swafoto and the
# "T" of Tanda read from the waveform), NOT from whisper: whisper's word times drift 0.2-0.6 s here.
U = [
    ("Q", "Cikgu, cikgu!", 0.00, 1.51),
    ("A", "Ya, saya.", 1.50, 2.30),
    ("Q", "Viral?", 2.62, 3.09), ("A", "Tular.", 3.38, 3.86),
    ("Q", "Selfie?", 4.00, 4.49), ("A", "Swafoto.", 5.02, 5.58),
    ("Q", "Hashtag?", 5.80, 6.27), ("A", "Tanda pagar.", 6.43, 7.36),
    ("Q", "Emoji?", 7.51, 8.03), ("A", "Emoji.", 8.47, 9.00),
    ("Q", "Netizen?", 9.33, 9.94), ("A", "Warganet.", 10.15, 10.68),
    ("Q", "Kuey teow?", 10.97, 11.45), ("A", "Kuetiau.", 11.89, 12.41),
    ("Q", "Mee hoon?", 12.68, 13.08), ("A", "Bihun atau Mihun.", 13.60, 15.06),
    ("Q", "Mee goreng?", 15.27, 15.85), ("A", "Mi goreng.", 16.17, 16.61),
    ("A", "Dapat sesuatu?", 17.34, 18.15),
]
END_AT = 19.0        # keep her thumbs-up after the last line
LEAD, TAIL_PAD = 0.10, 0.08   # kept before each line's onset / after its release (never cut into a word)
SILENCE = -17.5      # a removed stretch must stay below this everywhere (room tone is about -26 dB)

pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True).stdout
a = np.frombuffer(pcm, np.int16).astype(float) / 32768
H = 160  # 10 ms
db = 20 * np.log10(np.array([np.sqrt(np.mean(a[i:i + H] ** 2) + 1e-12) for i in range(0, len(a) - H, H)]))

seg = [[spk, txt, s, e] for spk, txt, s, e in U]
keep = [[0.0, None]]
for i in range(1, len(seg)):
    cut_a = round(seg[i - 1][3] + TAIL_PAD, 3)
    cut_b = round(seg[i][2] - LEAD, 3)
    quiet = cut_b - cut_a > 0.04 and db[int(cut_a * 100):int(cut_b * 100)].max() < SILENCE
    if quiet:
        keep[-1][1] = cut_a
        keep.append([cut_b, None])
    elif cut_b - cut_a > 0.04:
        print(f"  not cut (sound in gap) {cut_a:.2f}-{cut_b:.2f} max {db[int(cut_a*100):int(cut_b*100)].max():.1f} dB")
keep[-1][1] = END_AT
for s, e in zip([k[1] for k in keep[:-1]], [k[0] for k in keep[1:]]):
    print(f"  cut {s:.2f}-{e:.2f} ({e - s:.2f}s) max {db[int(s*100):int(e*100)].max():.1f} dB")

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
# light fan-hiss reduction only (a strong afftdn chewed up her soft "Swafoto"); clean classroom fan hiss, tame lows, even out the two voices, about -14 LUFS
fc += ("[ac]highpass=f=80,afftdn=nf=-40:nr=5:tn=1,equalizer=f=3500:t=q:w=1.2:g=2,"
       "acompressor=threshold=0.15:ratio=2:attack=15:release=200:makeup=1.5,"
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
