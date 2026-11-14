"""Potong B-roll (PLACEHOLDER dari video rujukan) -> assets/clips/<id>.mp4, 1080x960, 60fps, tanpa audio.
Usage: python3 build/cut_clips.py <kettletoro.mp4> <build60.mp4> <abamkamil.mp4> <tsaritsa_clip.mp4>
Bila ada footage Mitya sendiri: tukar SHOTS (src, start, dur, crop) dan run semula."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K, B, F, Z = sys.argv[1:5]
BAND = "crop=1012:900:34:140"            # jalur atas rakaman skrin: bebas caption & UI Shorts
SHOTS = [  # id, src, start, dur, vf
    ("A",  K, 43.2, 2.5, BAND), ("A2", K, 55.1, 3.0, BAND + ",setpts=1.1*PTS"),
    ("S1", B, 3.95, 1.6, BAND + ",setpts=1.5*PTS"), ("S2", K, 31.0, 2.0, BAND + ",setpts=1.5*PTS"),
    ("M1", K, 34.3, 2.3, BAND), ("M2", K, 46.0, 2.8, BAND), ("M3", K, 40.0, 3.0, BAND),
    ("M4", K, 42.6, 3.3, BAND), ("M5", K, 44.6, 2.6, BAND), ("M5b", K, 48.2, 2.9, BAND),
    ("M6", K, 55.2, 3.0, BAND),
    ("B0", K, 46.6, 4.7, BAND), ("B1", K, 49.4, 4.6, BAND), ("B2", K, 40.2, 4.0, BAND),
    ("B3", K, 44.0, 5.2, BAND), ("T1", K, 40.4, 2.8, BAND),
    ("Z",  Z, 0.0, 2.4, "crop=1080:960:0:250,setpts=1.45*PTS"),
]
out = []
for sid, src, s, d, vf in SHOTS:
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(s), "-t", str(d), "-i", src, "-an",
                    "-vf", vf + ",fps=60,scale=1080:960:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "17",
                    "-preset", "fast", "-g", "30", "-movflags", "+faststart",
                    os.path.join(ROOT, "assets", "clips", sid + ".mp4")], check=True)
    p = os.path.join(ROOT, "assets", "clips", sid + ".mp4")
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
    out.append([sid, s, round(d, 3)])
json.dump(out, open(os.path.join(ROOT, "assets", "clips", "shots.json"), "w"))
# stand-in muka (dari "AbamKamil Gaming content 1", bahagian split 48.0-100.5s) -> ganti dengan talking head sebenar
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", F, "-an",
                "-vf", "select='between(t,48,62.3)+between(t,65.6,100.5)',setpts=N/FRAME_RATE/TB,crop=450:400:63:0,setpts=1.15*PTS,scale=1080:960:flags=lanczos,fps=30,format=yuv420p", "-c:v", "libx264",
                "-crf", "18", "-preset", "fast", "-g", "30", "-movflags", "+faststart",
                os.path.join(ROOT, "assets", "face", "standin.mp4")], check=True)
print("ok", len(out))
