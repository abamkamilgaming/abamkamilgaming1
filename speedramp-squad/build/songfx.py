"""Slow-mo audio: muffle the song (low-pass) through every deep slow-mo hold, open it back up on the whip.
Also builds the pitched-down "bwoom" slow-mo SFX.

Reads plan.json + beats.json; writes assets/audio/song_fx.wav, assets/sfx/slowmo-down.wav, build/deep.json.
usage: python3 build/songfx.py
"""
import json, subprocess
from pathlib import Path
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt

ROOT = Path(__file__).resolve().parent.parent
plan = json.load(open(ROOT / "build/plan.json"))
B = json.load(open(ROOT / "build/beats.json"))["beats"]
LEAD = plan["lead"]


def tv(x):
    if isinstance(x, (int, float)): return float(x)
    return B[int(x[1:-1])] - LEAD if x.endswith("-") else B[int(x[1:])]


# deep slow-mo windows: hits with slow <= 0.2, held for hold * gap to the next key
deep = []
for s in plan["shots"]:
    for i, k in enumerate(s["keys"][:-1]):
        o = k[2] if len(k) > 2 else {}
        if o.get("slow", 1) <= 0.2:
            t0 = tv(k[0]); gap = tv(s["keys"][i + 1][0]) - t0
            deep.append({"t": round(t0, 3), "hold": round(o.get("hold", 0.25) * gap, 3)})
json.dump(deep, open(ROOT / "build/deep.json", "w"), indent=1)

y, sr = sf.read(ROOT / "assets/audio/song.wav", always_2d=True)
y = y.astype(np.float64)
sos = butter(4, 650, "low", fs=sr, output="sos")
lp = sosfiltfilt(sos, y, axis=0) * 1.25
t = np.arange(len(y)) / sr
mix = np.zeros(len(y))  # 0 = dry, 1 = muffled
drop = B[11]
for d in deep:
    a = d["t"]
    b = drop if d["t"] < drop < d["t"] + 1.0 else a + d["hold"] + 0.06  # pre-drop: stay muffled until the drop
    env = np.clip((t - (a - 0.03)) / 0.06, 0, 1) * np.clip((b - t) / 0.05, 0, 1)
    mix = np.maximum(mix, env * 0.85)
out = y * (1 - mix[:, None]) + lp * mix[:, None]
sf.write(ROOT / "assets/audio/song_fx.wav", np.clip(out, -1, 1), sr, subtype="PCM_16")

# slow-mo SFX: whoosh + bass impact pitched down an octave with a short tail
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "assets/sfx/whoosh.mp3"), "-i", str(ROOT / "assets/sfx/impact-bass-2.mp3"),
                "-filter_complex",
                "[0]aresample=48000,asetrate=24000,aresample=48000,volume=0.9[a];"
                "[1]aresample=48000,asetrate=33600,aresample=48000,volume=0.6[b];"
                "[a][b]amix=inputs=2:normalize=0,aecho=0.8:0.6:90:0.3,afade=t=out:st=0.9:d=0.5,atrim=0:1.4",
                "-ac", "2", str(ROOT / "assets/sfx/slowmo-down.wav")], check=True)
print("deep", deep)
