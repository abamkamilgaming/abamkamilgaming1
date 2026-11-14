"""Potong B-roll Mitya dari "1115.mp4" (gameplay rasmi) + "Mitya Theme Music.mp4" (1920x1080, 60 fps) -> assets/clips/<id>.mp4 (1080x960, 60 fps, bisu)
+ music bed assets/audio/bed.wav. Jalur y 150-755 sahaja dipakai (elak watermark atas & waveform bawah).
Usage: python3 build/cut_clips.py <Mitya Theme Music.mp4> <1115.mp4> <tsaritsa_clip.mp4>"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T, G, Z = sys.argv[1:4]
def band(x=620): return f"crop=655:582:{x}:176"
G_ = "crop=956:850:482:212"            # 1115.mp4: buang label atas-kiri & disclaimer bawah
SHOTS = [  # id, src, start, dur, crop, slow
    ("TA", G, 26.9, 3.5, G_, 1.0), ("S1", T, 8.95, 2.0, band(1010), 1.5), ("S2", T, 17.8, 1.15, band(), 3.1),
    ("M1", G, 36.0, 2.1, G_, 1.0), ("M2", G, 50.2, 2.85, G_, 1.0), ("M3", G, 40.0, 2.7, G_, 1.0),
    ("M4", G, 15.0, 3.4, G_, 1.0), ("M5", G, 54.0, 2.4, G_, 1.0), ("M5b", G, 77.5, 3.15, G_, 1.0),
    ("M5c", G, 63.5, 2.55, G_, 1.0), ("M6", G, 99.3, 3.1, G_, 1.0), ("B1", G, 67.0, 7.0, G_, 1.0),
    ("B2", G, 82.0, 4.8, G_, 1.0), ("B3", G, 87.0, 7.5, G_, 1.0), ("T1", G, 56.5, 4.6, G_, 1.0),
    ("Z", Z, 0.0, 2.4, "crop=1080:960:0:250", 1.7), ("E", T, 26.0, 3.6, band(), 1.0),
]
out = []
for sid, src, s, d, crop, slow in SHOTS:
    p = os.path.join(ROOT, "assets", "clips", sid + ".mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(s), "-t", str(d), "-i", src, "-an",
                    "-vf", f"{crop},setpts={slow}*PTS,fps=60,scale=1080:960:flags=lanczos,unsharp=5:5:0.6,format=yuv420p",
                    "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-g", "30", "-movflags", "+faststart", p], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                               capture_output=True, text=True).stdout)
    out.append([sid, s, round(dur, 3)])
json.dump(out, open(os.path.join(ROOT, "assets", "clips", "shots.json"), "w"))
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", "0.8", "-t", "62", "-i", T, "-vn", "-af",
                "loudnorm=I=-16:TP=-1.5", "-ar", "48000", "-ac", "2", os.path.join(ROOT, "assets", "audio", "bed.wav")], check=True)
print(out)
