"""Cut every EDL piece into two synced files:
  assets/clips/<id>_f.mp4  face cam 1080x780 (with the stream audio)
  assets/clips/<id>_g.mp4  game 1080x1140: sharp game 1080x585 on top, blurred fill below (muted)
Run: python3 build/cut.py <source.mp4>"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from edl import PIECES, FREEZE_AT
SRC = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "clips")
FPS = 60
# stream overlay text "live yang penting" sits over the chest: delogo before crop
FACE = "delogo=x=141:y=436:w=392:h=104,crop=640:462:230:0,scale=1080:780:flags=lanczos"
GAME = ("crop=1080:585:0:680,split[a][b];[b]scale=1080:-1,crop=1080:555:0:0,boxblur=28:2,eq=brightness=-0.12:saturation=1.2[bl];"
        "[a][bl]vstack")
AUD = "highpass=f=70,volume=8dB,acompressor=threshold=-18dB:ratio=3:attack=5:release=120:makeup=1,alimiter=limit=0.89"
info = {}
ONLY = sys.argv[2].split(",") if len(sys.argv) > 2 else None
if os.path.exists(os.path.join(OUT, "durs.json")):
    info = json.load(open(os.path.join(OUT, "durs.json")))
for pid, a, b, sp, sec in PIECES:
    d = b - a
    if ONLY and pid not in ONLY:
        continue
    vs = f"setpts=(PTS-STARTPTS)/{sp},fps={FPS}"
    at = []
    s = sp
    while s > 2.0:
        at.append("atempo=2.0"); s /= 2.0
    at.append(f"atempo={s:.4f}")
    fo, go = os.path.join(OUT, f"{pid}_f.mp4"), os.path.join(OUT, f"{pid}_g.mp4")
    common = ["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", SRC]
    enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-g", "30", "-movflags", "+faststart"]
    if sp > 3:   # fast-forward: no stream audio
        subprocess.run(common + ["-vf", f"{FACE},{vs}", "-an"] + enc + [fo], check=True)
    else:
        subprocess.run(common + ["-vf", f"{FACE},{vs}", "-af", ",".join([AUD] + at), "-c:a", "aac", "-b:a", "192k", "-ar", "48000"] + enc + [fo], check=True)
    subprocess.run(common + ["-filter_complex", f"[0:v]{GAME},{vs}[v]", "-map", "[v]", "-an"] + enc + [go], check=True)
    info[pid] = round(d / sp, 3)
    print(pid, info[pid], flush=True)
# hook freeze frame
for kind, vf in (("f", FACE), ("g", GAME)):
    o = os.path.join(ROOT, "assets", "img", f"freeze_{kind}.jpg")
    if kind == "f":
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(FREEZE_AT), "-i", SRC, "-frames:v", "1", "-vf", vf, "-q:v", "2", o], check=True)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(FREEZE_AT), "-i", SRC, "-frames:v", "1", "-filter_complex", f"[0:v]{vf}", "-q:v", "2", o], check=True)
json.dump(info, open(os.path.join(OUT, "durs.json"), "w"), indent=1)
