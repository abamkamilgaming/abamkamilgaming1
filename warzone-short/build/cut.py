"""Cut the Warzone stream recordings into tight Doro-style segments.

For every segment in SEGS:
  - silences longer than MAXGAP (silencedetect, voice band) are cut down to KEEP
  - talking segments are sped up (SPEED); action segments play at 1.0x
  - face cam is cropped from the stream layout to 1080x900 (top panel)
  - gameplay strip is cropped to 1080x1020 (bottom panel); the stream's static
    bottom overlay is dropped
  - loudness: two-pass loudnorm to -15 LUFS per segment so every cut sits level
  - caption groups (source times) are remapped onto the tightened clip

Usage: python3 build/cut.py <Warzone 1.mp4> <Warzone 2.mp4>
Writes assets/seg/<id>_face.mp4 (with audio), assets/seg/<id>_game.mp4 (muted)
and build/segs.json
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = {"W1": sys.argv[1], "W2": sys.argv[2]}
OUT = os.path.join(ROOT, "assets", "seg"); os.makedirs(OUT, exist_ok=True)
MAXGAP, KEEP = 0.16, 0.07
FACE_CROP = "620:517:280:15"     # face cam window in the 1080x1920 stream layout
GAME_CROP = "604:570:238:688"    # gameplay strip, centre-cropped to the panel aspect

# id, source, in, out, speed, caption groups [(text, source time)]
SEGS = [
    ("hook", "W1", 54.45, 57.30, 1.1, [("Game apa?", 54.58), ("GI ke?", 55.68), ("Bukan GI ni!", 56.48)]),
    ("helo", "W2", 7.05, 8.75, 1.1, [("Helo, Farahin!", 7.14)]),
    ("genshin", "W2", 11.55, 14.25, 1.1, [("Eh, bukan Genshin!", 11.62), ("Jap,", 12.74), ("aku Genshin...", 13.42)]),
    ("act1", "W1", 11.60, 14.40, 1.0, []),
    ("alone", "W1", 22.95, 25.00, 1.1, [("Aku rasa", 23.02), ("aku sorang je", 23.68), ("kat sini ni...", 24.40)]),
    ("res", "W1", 26.30, 28.00, 1.1, [("Aku nak ambil", 26.40), ("resources, eh.", 27.24)]),
    ("baz", "W1", 48.30, 49.85, 1.1, [("Uish,", 48.40), ("BAZOOKA!", 48.84)]),
    ("uzi", "W1", 49.95, 51.90, 1.1, [("Ke apa ni?", 50.02), ("Uzi, Uzi.", 51.10)]),
    ("best", "W2", 40.45, 42.30, 1.1, [("Tak best eh,", 40.54), ("weapon ni.", 41.70)]),
    ("act", "W2", 42.60, 45.70, 1.0, []),
    ("gift", "W2", 20.00, 21.50, 1.1, [("Terima kasih!", 20.08)]),
    ("gift2", "W2", 23.50, 26.55, 1.1, [("Terima kasih Farahin!", 23.56), ("Semoga lampu hijau", 24.32), ("sentiasa!", 25.70)]),
    ("minyak", "W2", 28.90, 32.70, 1.1, [("Minyak full tank!", 29.00), ("InsyaAllah.", 31.18)]),
    ("chat", "W2", 54.20, 57.30, 1.1, [("Belum lagi.", 56.50)]),
    ("end", "W1", 57.20, 59.98, 1.1, [("Ni,", 57.24), ("lepas ni aku", 57.60), ("main Genshin!", 59.00)]),
]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def silences(src, a, b):
    # threshold sits 14 dB under the segment's own voice-band peak, so quiet lines survive
    band = "highpass=f=120,lowpass=f=4000"
    v = run(["ffmpeg", "-nostdin", "-ss", f"{a}", "-t", f"{b - a}", "-i", src, "-af", band + ",volumedetect",
             "-f", "null", "-"]).stderr
    peak = float(re.search(r"max_volume: (-?[0-9.]+)", v).group(1))
    thr = min(-34.0, peak - 14.0)
    r = run(["ffmpeg", "-nostdin", "-ss", f"{a}", "-t", f"{b - a}", "-i", src, "-af",
             f"{band},silencedetect=noise={thr:.1f}dB:d=0.14", "-f", "null", "-"]).stderr
    st = [float(x) + a for x in re.findall(r"silence_start: (-?[0-9.]+)", r)]
    en = [float(x) + a for x in re.findall(r"silence_end: (-?[0-9.]+)", r)]
    if len(en) < len(st): en.append(b)
    return list(zip(st, en))


out = {}
for sid, src_id, a, b, speed, caps in SEGS:
    src = SRC[src_id]
    keep = [(a, b)]
    if not sid.startswith("act"):
        rm = [(max(a, s) + KEEP / 2, min(b, e) - KEEP / 2) for s, e in silences(src, a, b)
              if min(b, e) - max(a, s) > MAXGAP]
        # leading / trailing silence goes entirely
        rm = [((a if s - KEEP / 2 <= a + 0.01 else s), (b if e + KEEP / 2 >= b - 0.01 else e)) for s, e in rm]
        keep, cur = [], a
        for s, e in sorted(rm):
            if s > cur + 0.02: keep.append((cur, s))
            cur = max(cur, e)
        if b > cur + 0.02: keep.append((cur, b))

    def remap(t):
        acc = 0.0
        for s, e in keep:
            if t <= e: return round((acc + max(0.0, t - s)) / speed, 3)
            acc += e - s
        return round(acc / speed, 3)

    cuts, acc = [], 0.0
    for s, e in keep[:-1]:
        acc += e - s; cuts.append(round(acc / speed, 3))

    # measure loudness of the kept audio, then normalise linearly
    fa = "".join(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[a{i}];" for i, (s, e) in enumerate(keep))
    fa += "".join(f"[a{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1[ac]"
    meas = run(["ffmpeg", "-nostdin", "-i", src, "-filter_complex", fa + ";[ac]loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json",
                "-f", "null", "-"]).stderr
    m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    ln = (f"loudnorm=I=-15:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")

    fc = ""
    for i, (s, e) in enumerate(keep):
        fc += (f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS[v{i}];"
               f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,"
               f"afade=t=out:st={max(0, e - s - 0.012):.3f}:d=0.012[a{i}];")
    n = len(keep)
    fc += "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac];"
    fc += f"[vc]setpts=PTS/{speed},fps=30,split[vf][vg];"
    fc += f"[vf]crop={FACE_CROP},scale=1080:900:flags=lanczos,unsharp=5:5:0.7[face];"
    fc += f"[vg]crop={GAME_CROP},scale=1080:1020:flags=lanczos,unsharp=5:5:0.5[game];"
    fc += f"[ac]atempo={speed},{ln},aresample=48000[aout]"
    enc = ["-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", "-g", "15"]
    face = os.path.join(OUT, f"{sid}_face.mp4"); game = os.path.join(OUT, f"{sid}_game.mp4")
    r = run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-filter_complex", fc,
             "-map", "[face]", "-map", "[aout]", *enc, "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", face,
             "-map", "[game]", *enc, "-an", "-movflags", "+faststart", game])
    if r.returncode: sys.exit(r.stderr)
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", face]).stdout)
    C = [[t, remap(ts)] for t, ts in caps]
    out[sid] = {"dur": round(dur, 3), "caps": C, "cuts": cuts, "src": [src_id, a, b]}
    print(f"{sid:8s} {b - a:5.2f} -> {dur:5.2f}  cuts={len(cuts)}  " + " | ".join(f"{t}@{s}" for t, s in C))
json.dump(out, open(os.path.join(ROOT, "build", "segs.json"), "w"), ensure_ascii=False, indent=1)
print("total", round(sum(v["dur"] for v in out.values()), 2))
