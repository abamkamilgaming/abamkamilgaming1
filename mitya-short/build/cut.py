"""Cut "Test Run Mitya" into tight segments and reframe the stream layout for TikTok.

Source layout (1080x1920): facecam y 0-679, gameplay y 680-1263, static banner below (dropped).
Output per segment:
  assets/face/<id>.mp4  1080x760  (face crop, with the speech audio)
  assets/game/<id>.mp4  1080x1160 (gameplay crop, muted)
Pauses inside each piece are cut: any gap > MAXGAP between words (whisper words, starts
refined by audio energy) is shortened to KEEP. Everything plays at SPEED (pitch kept).
Writes build/segs.json (durations + remapped word timings for captions).

Usage: python3 build/cut.py "<Test Run Mitya.mp4>" [seg_id,...]
"""
import json, os, subprocess, sys, wave
from concurrent.futures import ThreadPoolExecutor
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1]
ONLY = sys.argv[2].split(",") if len(sys.argv) > 2 else None
MAXGAP, KEEP, LEAD, TAIL = 0.22, 0.10, 0.06, 0.12
SPEED = 1.07
FACE_CROP = "delogo=x=232:y=440:w=294:h=96,crop=720:560:230:0"   # head + chin; "live yang penting" overlay removed
GAME_CROP = "crop=583:583:{x}:680"        # square window of the 1080x583 gameplay strip

# id, face/audio pieces [(in,out)], game source: None = same times (synced) | float = continuous from t
# game_x = left edge of the gameplay crop window, rate = extra speed (fast-forward)
SEGS = [
    # HOOK
    ("h1", [(20.98, 22.56)], 403.2, 248, 1.0),          # "Hoyo nerf Mitya 7.3?"  (viewer chat bubble on screen)
    ("h2", [(955.42, 957.36)], 917.3, 248, 1.0),        # "Oh my god!"            (burst explosion)
    ("h3", [(38.30, 42.56)], None, 248, 1.0),           # "I will be the one who decides he is worthy or not"
    # TEST RUN
    ("s2", [(46.18, 48.88), (51.62, 52.88), (54.92, 58.56)], 140.0, 248, 1.0),  # nerf vs bug slip
    ("i0", [(85.10, 87.04, "raw")], None, 248, 1.0),    # "Not bad, not bad, idle dia"
    ("i1", [(100.90, 108.40, "raw")], None, 248, 1.5),  # IDLE #1: purple cube (face smiling / laughing)
    ("i2", [(112.40, 119.40, "raw")], None, 248, 1.8),  # IDLE #2: Scarf waves (face hand on chin)
    ("i3", [(119.60, 123.16)], None, 248, 1.0),         # reads chat: "Sis suka Mitya selalu gaduh dengan Scarf dia"
    ("sk", [(375.26, 376.72), (378.00, 381.40), (386.05, 388.80)], None, 248, 1.0),  # laughing: "Eh dia main. Dia main awesome eh, dengan Scarf dia... nice nice nice"
    ("ca", [(416.90, 422.50)], None, 248, 1.0),         # "Oh dude, yang tu charge attack! Eh, asal aku tak tekan charge attack pun masalahnya?"
    ("s4", [(427.36, 432.98)], None, 248, 1.0),         # "Dia macam Lisa... version Lisa tapi boy"
    ("s5a", [(567.36, 569.22)], None, 0, 1.0),          # "25 second? Serius lah?"  (skill screen)
    ("s5b", [(613.92, 619.62)], None, 248, 1.0),        # "Aku set timer phone aku. 3, 2, 1"
    ("ff", [(619.70, 645.70)], None, 248, 20.0),        # fast-forward through the 25 s (muted, sfx instead)
    ("s5c", [(646.26, 647.08), (651.50, 653.96), (658.40, 660.60)], None, 248, 1.0),  # "Betul lah. 25 freaking second. Mitya tak main DPS pun dia berguna"
    ("s7", [(871.40, 873.62), (874.44, 876.10), (879.30, 885.80, "raw")], None, 248, 1.0),  # "Sedap tak pula Mitya ni? Sedap lah pula" + burst grin + shocked face
    # FEEDBACK
    ("e1", [(953.06, 955.50), (958.86, 960.32)], 925.6, 248, 1.0),  # "Memang elok sangat lah... Mitya Mitya Mitya"
    ("e2", [(981.66, 984.42), (990.46, 994.88)], 931.6, 248, 1.0),  # "Satisfying feeling when you charge attack... zap zap zap gitu"
    ("e3", [(970.58, 972.86), (975.28, 976.95), (977.75, 979.95, "raw")], 940.0, 248, 1.0),  # "20k like aku terpaksa pull. Memang sedap guys... Gosh, sedap je" (hands on head)
]

FIX = {"idea": "idle", "Ideal": "Idle", "Tuk": "Teruk", "Minja": "Mitya", "siang": "sia", "Betullah": "Betul lah", "Media": "Mitya",
       "media": "Mitya", "up": "apa", "boy.": "boy!", "lah?": "lah?!", "Who": "who", "He": "he"}

# ---- audio energy (10 ms) used to tighten word starts that swallowed silence ----
wav = os.path.join(ROOT, "build", ".main16k.wav")
if not os.path.exists(wav):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", SRC, "-ac", "1", "-ar", "16000", wav], check=True)
w = wave.open(wav)
A = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
H = 160
n = len(A) // H
DB = 20 * np.log10(np.sqrt((A[: n * H].reshape(n, H) ** 2).mean(1)) + 1e-6)

WORDS = [x for s in json.load(open(os.path.join(ROOT, "build", "transcript_l3.json"))) for x in s["w"]]


def merge_tokens(ws):
    out = []
    for x in ws:
        if out and x[2].startswith("."):            # "7" ".3." -> "7.3"
            out[-1] = [out[-1][0], x[1], out[-1][2] + x[2].rstrip(".") + "?"]
        else:
            out.append(list(x[:3]))
    return out


def refine_start(s, e):
    """first 10 ms frame above (segment floor + 9 dB) inside the word"""
    a, b = int(s * 100), int(e * 100)
    if b - a < 4:
        return s
    seg = DB[max(0, a - 50): b + 50]
    thr = max(np.percentile(seg, 20) + 9, -45)
    for i in range(a, b):
        if DB[i] > thr:
            return max(s, i / 100 - 0.03)
    return s


def plan(pieces):
    """-> kept source ranges (silences > MAXGAP shortened to KEEP) and the words in them"""
    keep, words = [], []
    for p in pieces:
        a, b = p[0], p[1]
        if len(p) > 2:                                   # ("raw") keep untouched
            keep.append([a, b]); words += merge_tokens([list(x) for x in WORDS if a - 0.05 <= x[0] < b - 0.02]); continue
        ws = merge_tokens([list(x) for x in WORDS if a - 0.05 <= x[0] < b - 0.02])
        i0, i1 = int(a * 100), int(b * 100)
        seg = DB[i0:i1]
        thr = min(max(np.percentile(DB[max(0, i0 - 300):i1 + 300], 25) + 7, -46), -30)
        quiet = seg < thr
        cur = a
        j = 0
        while j < len(quiet):
            if quiet[j]:
                k = j
                while k < len(quiet) and quiet[k]:
                    k += 1
                s0, s1 = a + j / 100, a + k / 100
                if s1 - s0 > MAXGAP:
                    if j == 0:
                        cur = max(a, s1 - LEAD)
                    elif k >= len(quiet):
                        keep.append([cur, min(b, s0 + TAIL)]); cur = None
                    else:
                        keep.append([cur, s0 + KEEP / 2]); cur = s1 - KEEP / 2
                j = k
            else:
                j += 1
        if cur is not None:
            keep.append([cur, b])
        words += ws
    return keep, words


def remap(keep, words, rate):
    out, t = [], 0.0
    offs = []
    for a, b in keep:
        offs.append((a, b, t)); t += b - a
    for s, e, txt in words:
        for a, b, o in offs:
            if a - 0.06 <= s <= b:
                ss = (max(s, a) - a + o) / rate
                ee = (min(e, b) - a + o) / rate
                out.append([round(ss, 3), round(max(ee, ss + 0.08), 3), FIX.get(txt, txt)])
                break
    return out, t / rate


def job(seg):
    sid, pieces, gsrc, gx, rate = seg
    if sid == "ff":
        keep, words = [list(pieces[0])], []
    else:
        keep, words = plan(pieces)
    sp = SPEED * rate if sid != "ff" else rate
    ws, dur = remap(keep, words, sp)
    t0 = keep[0][0] - 0.5
    span = keep[-1][1] - t0 + 0.5
    fc = []
    vparts, aparts = [], []
    for i, (a, b) in enumerate(keep):
        fc.append(f"[0:v]trim=start={a - t0:.3f}:end={b - t0:.3f},setpts=PTS-STARTPTS[v{i}]")
        fade = min(0.012, (b - a) / 4)
        fc.append(f"[0:a]atrim=start={a - t0:.3f}:end={b - t0:.3f},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d={fade:.3f},afade=t=out:st={b - a - fade:.3f}:d={fade:.3f}[a{i}]")
        vparts.append(f"[v{i}]"); aparts.append(f"[a{i}]")
    k = len(keep)
    fc.append(f"{''.join(v + a for v, a in zip(vparts, aparts))}concat=n={k}:v=1:a=1[vc][ac]")
    fc.append(f"[vc]setpts=PTS/{sp},fps=60,split[vf][vg]")
    fc.append(f"[vf]{FACE_CROP},scale=1080:840:flags=lanczos,unsharp=5:5:0.5[face]")
    tempo = sp
    atf = []
    while tempo > 2.0:
        atf.append("atempo=2.0"); tempo /= 2.0
    atf.append(f"atempo={tempo:.4f}")
    fc.append(f"[ac]{','.join(atf)},highpass=f=70,acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=2,"
              f"loudnorm=I=-15:TP=-1.5:LRA=8,aresample=48000[aout]")
    inputs = ["-ss", f"{t0:.3f}", "-t", f"{span:.3f}", "-i", SRC]
    if gsrc is None:
        fc.append(f"[vg]{GAME_CROP.format(x=gx)},scale=1080:1080:flags=lanczos,unsharp=5:5:0.7[game]")
    else:
        inputs += ["-ss", f"{gsrc:.3f}", "-t", f"{dur + 0.5:.3f}", "-i", SRC]
        fc.append("[vg]nullsink")
        fc.append(f"[1:v]fps=60,trim=duration={dur:.3f},setpts=PTS-STARTPTS,{GAME_CROP.format(x=gx)},"
                  f"scale=1080:1080:flags=lanczos,unsharp=5:5:0.7[game]")
    enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    face_out = os.path.join(ROOT, "assets", "face", f"{sid}.mp4")
    game_out = os.path.join(ROOT, "assets", "game", f"{sid}.mp4")
    amap = ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"] if sid != "ff" else ["-an"]
    if sid == "ff":
        fc = [x for x in fc if "[aout]" not in x] + ["[ac]anullsink"]
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
           "-map", "[face]", *amap, *enc, "-t", f"{dur:.3f}", face_out,
           "-map", "[game]", "-an", *enc, "-t", f"{dur:.3f}", game_out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return sid, r.returncode, r.stderr[-600:], {"dur": round(dur, 3), "keep": keep, "words": ws,
                                                 "cuts": [round(sum(b - a for a, b in keep[:i]) / sp, 3) for i in range(1, len(keep))]}


segs_path = os.path.join(ROOT, "build", "segs.json")
OUT = json.load(open(segs_path)) if os.path.exists(segs_path) else {}
todo = [s for s in SEGS if not ONLY or s[0] in ONLY]
with ThreadPoolExecutor(3) as ex:
    for sid, rc, err, info in ex.map(job, todo):
        print(sid, "OK" if rc == 0 else "FAIL", info["dur"], "pieces", len(info["keep"]), err if rc else "")
        if rc == 0:
            OUT[sid] = info
OUT = {s[0]: OUT[s[0]] for s in SEGS if s[0] in OUT}
json.dump(OUT, open(segs_path, "w"), indent=1, ensure_ascii=False)
print("total", round(sum(v["dur"] for v in OUT.values()), 2))
