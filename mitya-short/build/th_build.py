"""Potong talking head -> satu clip ketat per ayat (assets/th/<id>.mp4, 1080x960, 60 fps) + build/th_words.json
- pilih take terbaik (LINES), buang retake / filler (DROP)
- pause > MAXGAP dipotong ke KEEP, laju SPEED, suara dibersihkan + ~-14 LUFS
- word timing: whisper atas clip akhir
Usage: python3 build/th_build.py <Talking Head.mp4>"""
import json, os, re, subprocess, sys, wave
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1]
OUT = os.path.join(ROOT, "assets", "th"); os.makedirs(OUT, exist_ok=True)
MAXGAP, KEEP, SPEED = 0.18, 0.09, 1.15
CROP = "crop=2160:1920:0:100"      # muka: separuh atas frame portrait 4K
LINES = [  # id, mula, tamat (saat dalam rakaman mentah)
    ("h1", 0.70, 4.28), ("s1", 8.66, 15.60), ("m1", 16.37, 18.72), ("m2", 19.64, 22.71), ("m3", 23.11, 26.10),
    ("m4", 26.60, 31.63), ("m5", 32.35, 40.50), ("m6", 41.06, 44.66), ("b1", 58.36, 65.90), ("b2", 76.74, 82.20),
    ("b3", 84.54, 92.60), ("t1", 93.66, 98.66), ("z1", 98.90, 103.03), ("e1", 106.45, 109.06),
]
DROP = [(27.32, 28.80)]            # "Tak risau" (filler)
# dibuang terus: 4.3-8.1 (intro ke-2), 44.7-58.3 (talent + retake stat), 66-76.7 (retake crit), 82.2-84.2, 103-106.4 (retake)
TEXT = {  # apa yang sebenarnya disebut (betulkan slip whisper), ikut turutan perkataan
    "h1": "Jangan pull Mitya selagi korang tak tengok video ni",
    "s1": "Mitya 5 star Electro baru Tengok rupa dia idle dia pun dah nampak mahal",
    "m1": "Mechanic dia senang je Dia ada 2 mode",
    "m2": "Tap skill dia jadi sub off-field DPS",
    "m3": "Hold skill dia jadi main DPS on-field",
    "m4": "Salah tekan? Tekan skill sekali lagi terus dia tukar mode",
    "m5": "Buat reaction Stellar Conduct untuk kumpul stack Bila stack dia dah penuh meteor jatuh Damage dia besar gila",
    "m6": "Burst dia pula terus bagi 3 stack",
    "b1": "Stat Crit 70 200 EM 500 ER 140",
    "b2": "Artifact korang boleh pakai Deep Shadow 4 pieces ataupun Gilded Dreams",
    "b3": "Weapon signature dia paling padu Takde? Kagura's Verity ataupun Widsith pun jalan",
    "t1": "Team gandingkan dengan unit Cryo dan Sucrose",
    "z1": "Dan aku rasa Mitya ni ngam gila satu team dengan Tsaritsa nanti",
    "e1": "Simpan primo korang Follow for more",
}
sil = subprocess.run(["ffmpeg", "-nostdin", "-i", SRC, "-vn", "-af", "highpass=f=100,silencedetect=noise=-30dB:d=0.18",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
SIL = list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", sil)],
               [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", sil)]))
AF = ("highpass=f=85,afftdn=nr=10:nf=-50,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
      "equalizer=f=3500:t=q:w=1:g=2.5,loudnorm=I=-14:TP=-1.5:LRA=7")
meta = {}
for lid, a, b in LINES:
    rm = [(s + KEEP / 2, e - KEEP / 2) for s, e in SIL if s > a + 0.03 and e < b - 0.03 and e - s > MAXGAP]
    rm += [(max(a, s), min(b, e)) for s, e in DROP if s < b and e > a]
    rm.sort(); merged = []
    for r in rm:
        if merged and r[0] <= merged[-1][1]: merged[-1] = (merged[-1][0], max(merged[-1][1], r[1]))
        else: merged.append(r)
    keep, cur = [], a
    for s, e in merged:
        if s > cur: keep.append((cur, s))
        cur = max(cur, e)
    keep.append((cur, b))
    cuts, acc = [], 0.0
    for s, e in keep[:-1]:
        acc += e - s; cuts.append(round(acc / SPEED, 3))
    fc = ""
    for i, (s, e) in enumerate(keep):
        fc += (f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS[v{i}];"
               f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,"
               f"afade=t=out:st={max(0, e - s - 0.015):.3f}:d=0.015[a{i}];")
    n = len(keep)
    fc += "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v0][a0];"
    fc += (f"[v0]{CROP},scale=1080:960:flags=lanczos,unsharp=5:5:0.5,setpts=PTS/{SPEED},fps=60,format=yuv420p[v];"
           f"[a0]atempo={SPEED},{AF}[a]")
    dst = os.path.join(OUT, lid + ".mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{a - 1:.3f}", "-i", SRC, "-filter_complex",
                    fc.replace("trim=", "trim=").replace("\0", ""), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16",
                    "-preset", "fast", "-g", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", dst]
                   if False else
                   ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-g", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", dst], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
                               capture_output=True, text=True).stdout)
    meta[lid] = {"dur": round(dur, 3), "cuts": cuts, "raw": [a, b]}
    print(lid, f"{b - a:.2f} -> {dur:.2f}  ({len(keep) - 1} potongan)", flush=True)

# ---- word timings on the final clips ----
from faster_whisper import WhisperModel
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=4)
for lid in meta:
    wav = os.path.join(OUT, lid + ".wav")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", os.path.join(OUT, lid + ".mp4"), "-vn", "-ac", "1",
                    "-ar", "16000", wav], check=True)
    w = wave.open(wav); au = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    os.remove(wav)
    segs, _ = m.transcribe(au, language="ms", word_timestamps=True, initial_prompt=TEXT[lid] + ".", condition_on_previous_text=False)
    W = [[x.word.strip(), round(x.start, 3), round(x.end, 3)] for g in segs for x in g.words]
    want = TEXT[lid].split()
    if len(W) == len(want):
        W = [[t, s, e] for t, (_, s, e) in zip(want, W)]
    else:   # kiraan tak sama: agih masa secara linear ikut panjang perkataan
        print("  !! word count", lid, len(W), len(want), [x[0] for x in W])
        t0, t1 = (W[0][1], W[-1][2]) if W else (0.0, meta[lid]["dur"])
        tot = sum(len(x) + 1 for x in want); acc = 0; NW = []
        for x in want:
            s = t0 + (t1 - t0) * acc / tot; acc += len(x) + 1; NW.append([x, round(s, 3), round(t0 + (t1 - t0) * acc / tot, 3)])
        W = NW
    meta[lid]["words"] = W
json.dump(meta, open(os.path.join(ROOT, "build", "th_words.json"), "w"), ensure_ascii=False, indent=0)
print("total", round(sum(v["dur"] for v in meta.values()), 2))
