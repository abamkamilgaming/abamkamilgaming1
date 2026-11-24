"""Cut the raw 4K60 HEVC takes into tight 1080x1920 60fps clips.
- keep only the spoken part of each take (pauses/dead air removed, windows set from
  whisper words + spectrogram), the repeated second "Island" is dropped
- audio: highpass, light denoise, 2-pass loudnorm to -14 LUFS
Usage: python3 build/cut.py "<Raw footage dir>"  -> assets/clips/*.mp4 + build/clips.json
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = sys.argv[1]
OUT = os.path.join(ROOT, "assets", "clips")
os.makedirs(OUT, exist_ok=True)

# id: (source file, [keep windows in source seconds], freeze-hold seconds at end)
CLIPS = {
    "intro": ("Intro hook", [(0.12, 2.48)], 0),
    "s1": ("Scene 1", [(0.30, 1.60)], 0),
    "s2": ("Scene 2", [(0.24, 1.10)], 0),
    "s3": ("Scene 3", [(0.02, 0.76)], 0),
    "s4": ("Scene 4", [(0.58, 1.42)], 0),
    "s5": ("Scene 5", [(1.32, 2.52)], 0),
    "s6": ("Scene 6", [(0.47, 1.66)], 0),
    # "The pronunciation is" | "Island" | (2nd Island cut) | "Capish?"
    "ans": ("The right answer is ...", [(0.45, 2.50), (3.04, 3.86), (5.84, 6.80)], 0),
    # "Ustazah, ingin pergi ke pulau bersama saya?" | "Boleh, awak belanja saya?" + reaction, then freeze
    "end": ("End scene", [(0.86, 3.98), (4.10, 6.86)], 2.6),
}
AF = "highpass=f=90,afftdn=nf=-28:tn=1,acompressor=threshold=-20dB:ratio=3:attack=5:release=80"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def build(cid, src, wins, hold):
    path = os.path.join(RAW, src)
    fc = ""
    for i, (a, b) in enumerate(wins):
        fc += (f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,fps=60,format=yuv420p[v{i}];"
               f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,aresample=48000,"
               f"afade=t=in:d=0.015,afade=t=out:st={b - a - 0.02:.3f}:d=0.02[a{i}];")
    n = len(wins)
    fc += "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac];"
    vtail = f"[vc]tpad=stop_mode=clone:stop_duration={hold}[v];" if hold else "[vc]null[v];"
    atail = f",apad=pad_dur={hold}" if hold else ""
    # pass 1: measure loudness
    m = run(["ffmpeg", "-nostdin", "-i", path, "-filter_complex",
             fc + vtail + f"[ac]{AF},loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json[a]",
             "-map", "[v]", "-map", "[a]", "-f", "null", "-"]).stderr
    js = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    dst = os.path.join(OUT, cid + ".mp4")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", path, "-filter_complex",
         fc + vtail + f"[ac]{AF},{ln},aresample=48000{atail}[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "30",
         "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", dst])
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst]).stdout)
    segs, acc = [], 0.0
    for a, b in wins:
        segs.append(round(acc, 3)); acc += b - a
    return {"dur": round(dur, 3), "speech": round(acc, 3), "segs": segs, "src": src, "wins": wins}


meta = {}
for cid, (src, wins, hold) in CLIPS.items():
    meta[cid] = build(cid, src, wins, hold)
    print(cid, meta[cid]["dur"], meta[cid]["segs"])
json.dump(meta, open(os.path.join(ROOT, "build", "clips.json"), "w"), indent=1)
