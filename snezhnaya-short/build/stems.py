"""Extract each script piece (+0.5s pad) as wav and split voice/game with demucs.
Usage: python3 build/stems.py <source.mp4>  -> /home/user/work/stems/<id>_<k>/{vocals,no_vocals}.wav"""
import json, os, subprocess, sys
SRC = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = "/home/user/work/stems"; os.makedirs(W + "/raw", exist_ok=True)
PAD = 0.5
S = json.load(open(os.path.join(ROOT, "build", "script.json")))["lines"]
files = []; offs = {}
for ln in S:
    for k, (a, b) in enumerate(ln["pieces"]):
        name = f'{ln["id"]}_{k}'; dst = f"{W}/raw/{name}.wav"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{a - PAD:.3f}", "-t", f"{b - a + 2 * PAD:.3f}",
                        "-i", SRC, "-vn", "-ac", "2", "-ar", "44100", dst], check=True)
        offs[name] = round(a - PAD, 3)
        old = json.load(open(W + "/offsets.json")) if os.path.exists(W + "/offsets.json") else {}
        if old.get(name) == offs[name] and os.path.exists(f"{W}/sep/htdemucs/{name}/vocals.wav"): continue
        files.append(dst)
if files: subprocess.run([sys.executable, "-m", "demucs", "--two-stems=vocals", "-n", "htdemucs", "-o", W + "/sep", *files], check=True)
json.dump(offs, open(W + "/offsets.json", "w"), indent=0)
print("separated", len(files))
