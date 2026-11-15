"""Potong B-roll Anastasya dari playthrough Archon Quest 7.2 (1920x1080, 60 fps) -> assets/clips/<id>.mp4 (1080x1920).
Shot "sync" simpan audio asal game (petikan dialog). + music bed + stand-in muka (preview sahaja).
Usage: python3 build/cut_clips.py <playthrough.mp4> <Background song> [talking_head_standin.mp4]"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P, SONG = sys.argv[1:3]
def c(x=656): return f"crop=608:1080:{x}:0"
SHOTS = [  # id, start, dur, crop, slow, keep audio
    ("A", 17964.3, 4.4, c(), 1.0, 0),        # cinematic: pusaran ais -> mata Anastasya
    ("I1", 4476.6, 3.0, c(), 1.0, 0),        # close-up di meja bulat
    ("R1", 4491.4, 4.2, c(), 1.0, 0),        # meja bulat the Seven
    ("R1b", 17862.5, 3.2, c(), 1.0, 0),      # Anastasya + Pierrot + Noy
    ("R2", 4496.5, 4.4, c(), 1.0, 0),        # sekeliling meja
    ("Q1", 17871.85, 4.3, c(), 1.0, 1),       # Pierro: "Love. That is Her Majesty's power."
    ("L1", 17975.6, 3.4, c(), 1.0, 0),       # istana + cahaya
    ("S1", 17986.2, 2.7, c(), 1.0, 0),       # pesakit wabak
    ("S2", 18000.0, 4.2, c(), 1.0, 0),       # kepingan salji gergasi, dia berjalan
    ("S3", 18004.2, 2.6, c(), 1.0, 0),       # ayah & anak sembuh
    ("S4", 18022.8, 3.4, c(), 1.0, 0),       # mangsa bertanduk tertimbus salji
    ("Q3", 18034.9, 3.3, c(), 1.0, 1),       # Anastasya: "Love cannot cure you of this curse."
    ("T1", 18080.6, 3.6, c(520), 1.0, 0),    # peranti ujian Celestia
    ("Q2", 18178.9, 4.5, c(), 1.0, 1),       # Anastasya: "even you do not know what love is, Phanes."
    ("T2", 18170.8, 6.2, c(), 1.0, 0),       # close-up marah
    ("P1", 18029.6, 4.2, c(), 1.0, 0),       # berjalan dalam salji
    ("P2", 18039.3, 4.3, c(), 1.0, 0),       # close-up wajah
    ("E", 18046.5, 5.0, c(), 1.0, 0),        # aurora ais
]
out = []
for sid, s, d, crop, slow, aud in SHOTS:
    p = os.path.join(ROOT, "assets", "clips", sid + ".mp4")
    a = ["-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-15:TP=-1.5"] if aud else ["-an"]
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(s), "-t", str(d), "-i", P,
                    "-vf", f"{crop},setpts={slow}*PTS,fps=60,scale=1080:1920:flags=lanczos,unsharp=5:5:0.5,format=yuv420p",
                    "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-g", "30", "-movflags", "+faststart", *a, p], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                               capture_output=True, text=True).stdout)
    out.append([sid, s, round(dur, 3), aud])
json.dump(out, open(os.path.join(ROOT, "assets", "clips", "shots.json"), "w"))
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", SONG, "-vn", "-af", "silenceremove=start_periods=1:start_threshold=-45dB,loudnorm=I=-16:TP=-1.5:LRA=9",
                "-ar", "48000", "-ac", "2", os.path.join(ROOT, "assets", "audio", "bed.wav")], check=True)
if len(sys.argv) > 3:   # stand-in muka bisu untuk preview
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", "8.6", "-t", "58", "-i", sys.argv[3], "-an",
                    "-vf", "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                    "-g", "30", "-movflags", "+faststart", os.path.join(ROOT, "assets", "th", "standin.mp4")], check=True)
print(out)
