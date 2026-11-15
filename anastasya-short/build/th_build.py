"""Potong talking head -> satu clip ketat per ayat (assets/th/<id>.mp4, 1080x1920, 60 fps) + build/th_words.json
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
LINES = [  # id, mula, tamat (saat dalam rakaman mentah)
    ("h1", 0.66, 6.92), ("i1", 7.38, 11.10), ("r1", 12.38, 18.42), ("l1", 26.65, 33.76), ("s1", 34.15, 42.73),
    ("s2", 43.37, 47.58), ("t1", 48.48, 53.26), ("t2", 54.47, 62.68), ("p1", 63.50, 72.34), ("p2", 73.27, 74.89),
    ("e1", 75.34, 78.70),
]
# filler / ulangan dibuang: "Jadi,", "ni guys,", "uff, masa ni memang", "bayangkan" (kali kedua)
DROP = [(28.95, 30.75), (44.86, 45.60), (60.34, 61.83), (67.25, 68.19)]
# dibuang terus untuk masa: 18.4-26.6 ("Kali terakhir the Seven berkumpul? 500 tahun lepas...")
TEXT = {
    "h1": "Tsaritsa jahat? Salah! Kuasa sebenar dia? Cinta!",
    "i1": "Ini Anastasya Cryo Archon bos besar Fatui",
    "r1": "Dalam Archon Quest 7.2 dia sendiri kumpulkan semua Archon untuk selamatkan Teyvat",
    "l1": "Authority dia cinta kuasa untuk hapuskan sumpahan",
    "s1": "Rakyat dia ni kena wabak sumpahan Dia janji bila salji turun semua akan sembuh Dan memang jadi",
    "s2": "Tapi ada satu sumpahan cinta pun tak boleh nak ubat",
    "t1": "Lepas tu Celestia uji dia Subjek ujian? Cinta",
    "t2": "Dia ni sound balik Celestia punya gangster ni korang yang cemarkan nama cinta meremang weh",
    "p1": "Bayangkan bila Anastasya jadi playable nanti Archon tema cinta confirm gempak weh",
    "p2": "Aku dah mula simpan primo",
    "e1": "Korang pull ke tak? Follow for more",
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
        fc += (f"[s{i}]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS[v{i}];"
               f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,"
               f"afade=t=out:st={max(0, e - s - 0.015):.3f}:d=0.015[a{i}];")
    n = len(keep)
    # kecilkan 4K -> 1080x1920 SEBELUM dipotong (jimat memori), kemudian split ke setiap segmen
    fc = (f"[0:v]scale=1080:1920:flags=lanczos[vs];[vs]split={n}" + "".join(f"[s{i}]" for i in range(n)) + ";") + fc
    fc += "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v0][a0];"
    fc += (f"[v0]unsharp=5:5:0.4,setpts=PTS/{SPEED},fps=60,format=yuv420p[v];"
           f"[a0]atempo={SPEED},{AF}[a]")
    dst = os.path.join(OUT, lid + ".mp4")
    if os.path.exists(dst) and os.path.getsize(dst) > 100000 and "--force" not in sys.argv:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
                                   capture_output=True, text=True).stdout)
        meta[lid] = {"dur": round(dur, 3), "cuts": cuts, "raw": [a, b]}; print(lid, "ada, langkau", flush=True); continue
    off = max(0.0, a - 2.0)
    fcs = fc
    for (ks, ke) in keep:
        fcs = fcs.replace(f"trim={ks:.3f}:{ke:.3f}", f"trim={ks - off:.3f}:{ke - off:.3f}")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{off:.3f}", "-i", SRC, "-filter_complex", fcs,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-g", "30", "-c:a", "aac",
                    "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", dst], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
                               capture_output=True, text=True).stdout)
    meta[lid] = {"dur": round(dur, 3), "cuts": cuts, "raw": [a, b]}
    print(lid, f"{b - a:.2f} -> {dur:.2f}  ({len(keep) - 1} potongan)", flush=True)

if "--keep-words" in sys.argv and os.path.exists(os.path.join(ROOT, "build", "th_words.json")):
    old = json.load(open(os.path.join(ROOT, "build", "th_words.json")))
    for k in meta: meta[k]["words"] = old[k]["words"]
    json.dump(meta, open(os.path.join(ROOT, "build", "th_words.json"), "w"), ensure_ascii=False, indent=0)
    print("total", round(sum(v["dur"] for v in meta.values()), 2), "(word timing lama dikekalkan)"); sys.exit(0)
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
