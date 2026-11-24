"""Generate index.html for the ISLAND pronunciation-challenge short.
Reads build/clips.json (from build/cut.py) for clip durations / jump-cut points."""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(ROOT, "build", "clips.json")))
ORDER = ["intro", "s1", "s2", "s3", "s4", "s5", "s6", "ans", "end"]

T, t = {}, 0.0
for cid in ORDER:
    T[cid] = (round(t, 3), round(t + C[cid]["dur"], 3))
    t += C[cid]["dur"]
TOTAL = round(t, 3)
A0, A1 = T["ans"]
E0, E1 = T["end"]
ANS_ISLAND = round(A0 + C["ans"]["segs"][1], 3)          # "Island"
ANS_ISLAND2 = round(A0 + C["ans"]["segs"][2], 3)         # 2nd "Island"
ANS_CAPISH = round(A0 + C["ans"]["segs"][3] + 0.05, 3)   # "Capish?"
END_SEG2 = round(E0 + C["end"]["segs"][1], 3)            # answer half starts (B&W from here)
src2end = lambda s, seg: round(E0 + C["end"]["segs"][seg] + (s - C["end"]["wins"][seg][0]), 3)
W_USTAZAH = src2end(1.00, 0)
W_PULAU = src2end(1.98, 0)
W_BERSAMA = src2end(3.08, 0)
W_BOLEH = src2end(4.25, 1)
W_AWAK = src2end(4.54, 1)
W_ANS_END = src2end(5.36, 1)
ACK_HIT = round(W_ANS_END + 0.04, 3)       # "ack" onset lands right after "...belanja saya?"
ACK_START = round(ACK_HIT - 0.30, 3)       # onset is 0.30 s into ack.wav
FREEZE = round(E0 + C["end"]["speech"], 3)

# what each kid actually said
ATTEMPTS = {"s1": "ISLANDE?", "s2": "SELAN DAY?", "s3": "ISLAN?", "s4": "ISLAM?!", "s5": "EAST LONDON?!",
            "s6": "ISLAM… LAGI?!"}

# ---- grade: warm, contrasty, premium daylight; per-shot exposure fixes (s4 is dark + flat)
EXPO = {"intro": 0.06, "s1": 0.05, "s2": 0.07, "s3": -0.03, "s4": 0.17, "s5": 0.04, "s6": 0.04, "ans": 0.03,
        "end": 0.03}
def grade(cid):
    return {"preset": "warm-daylight", "intensity": 0.5,
            "adjust": {"exposure": EXPO[cid], "contrast": 0.14, "highlights": -0.3, "shadows": 0.12,
                       "whites": -0.05, "blacks": -0.06, "vibrance": 0.3 if cid == "s4" else 0.22,
                       "saturation": 0.05, "temperature": 0.04},
            "details": {"vignette": 0.2}}
G_BW = {"preset": "mono-clean", "intensity": 1,
        "adjust": {"exposure": 0.02, "contrast": 0.32, "highlights": -0.22, "shadows": 0.04},
        "details": {"vignette": 0.5, "grain": 0.22}}
attr = lambda g: html.escape(json.dumps(g, separators=(",", ":")), quote=True)
f = lambda x: f"{x:.3f}".rstrip("0").rstrip(".")

# ---- video layers
V = []
for i, cid in enumerate(ORDER):
    s, e = T[cid]
    if cid == "end":
        V.append(f'      <div class="vw" id="vw-end" style="z-index:{10 + i}">\n'
                 f'        <video id="v-end" class="clip vid" src="assets/clips/end.mp4" data-start="{f(s)}" '
                 f'data-duration="{f(END_SEG2 - s)}" data-track-index="1" data-has-audio="true" data-volume="1" '
                 f'playsinline data-color-grading="{attr(grade(cid))}"></video>\n      </div>')
        V.append(f'      <div class="vw" id="vw-bw" style="z-index:{11 + i}">\n'
                 f'        <video id="v-bw" class="clip vid" src="assets/clips/end.mp4" data-start="{f(END_SEG2)}" '
                 f'data-media-start="{f(END_SEG2 - s)}" data-duration="{f(e - END_SEG2)}" data-track-index="1" '
                 f'data-has-audio="true" data-volume="1" playsinline data-color-grading="{attr(G_BW)}"></video>\n      </div>')
    else:
        V.append(f'      <div class="vw" id="vw-{cid}" style="z-index:{10 + i}">\n'
                 f'        <video id="v-{cid}" class="clip vid" src="assets/clips/{cid}.mp4" data-start="{f(s)}" '
                 f'data-duration="{f(e - s)}" data-track-index="1" data-has-audio="true" data-volume="1" '
                 f'playsinline data-color-grading="{attr(grade(cid))}"></video>\n      </div>')

# ---- attempt captions
CAP = []
for cid, txt in ATTEMPTS.items():
    s, e = T[cid]
    CAP.append(f'      <div id="at-{cid}" class="clip att" data-start="{f(s)}" data-duration="{f(e - s)}" data-track-index="4">'
               f'<div class="att-in"><span class="att-q">“{html.escape(txt)}”</span>'
               f'<span class="xmark"><i></i><i></i></span></div></div>')

# ---- SFX  (asai-jingle = lifted from the Sir Asai reference; ack = from the folder)
SFX_DUR = {"asai-jingle.wav": 3.42, "ack.wav": 5.0, "impact-bass-1.mp3": 2.11, "ping.mp3": 1.32, "pop.mp3": 0.72,
           "sparkle.mp3": 1.8, "whoosh.mp3": 0.57, "whoosh-short.mp3": 0.57, "wrong.wav": 0.36}
SFX = [("asai-jingle.wav", 0.0, 0.5), ("whoosh-short.mp3", T["s1"][0] - 0.2, 0.5),
       ("impact-bass-1.mp3", T["s1"][0], 0.4)]
for cid in ATTEMPTS:
    s, e = T[cid]
    SFX.append(("pop.mp3", s + 0.03, 0.32))
    SFX.append(("wrong.wav", max(s + 0.35, e - 0.36), 0.42))
SFX += [("whoosh.mp3", A0 - 0.12, 0.45), ("sparkle.mp3", ANS_ISLAND, 0.45), ("ping.mp3", ANS_ISLAND + 0.05, 0.3), ("pop.mp3", ANS_ISLAND2, 0.35),
        ("pop.mp3", ANS_CAPISH, 0.5), ("whoosh-short.mp3", E0 - 0.15, 0.4),
        ("ack.wav", ACK_START, 0.95), ("impact-bass-1.mp3", ACK_HIT, 0.35)]
A = []
for i, (fn, s, vol) in enumerate(SFX):
    d = min(SFX_DUR[fn], TOTAL - s)
    fade = ' data-fade-out="0.6"' if fn == "ack.wav" else ""
    A.append(f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{fn}" data-start="{f(s)}" data-duration="{f(d)}" '
             f'data-volume="{vol}"{fade} data-track-index="9"></audio>')

K = {"total": TOTAL, "T": T, "ansIsland": ANS_ISLAND, "ansIsland2": ANS_ISLAND2, "ansCapish": ANS_CAPISH, "endSeg2": END_SEG2,
     "wUstazah": W_USTAZAH, "wPulau": W_PULAU, "wBersama": W_BERSAMA, "wBoleh": W_BOLEH, "wAwak": W_AWAK,
     "ansEnd": W_ANS_END, "ack": ACK_HIT, "freeze": FREEZE, "attempts": list(ATTEMPTS)}
D = {"wordIn": T["s1"][0], "wordDur": E0 - T["s1"][0], "ansTagIn": A0, "ansTagDur": ANS_ISLAND - A0,
     "capDur": E0 - ANS_CAPISH, "hookOut": T["intro"][1], "endIn": E0, "namesDur": W_BOLEH - E0,
     "c1Dur": W_BERSAMA - W_USTAZAH, "c2Dur": W_BOLEH - W_BERSAMA, "c3Dur": ACK_HIT + 0.5 - W_BOLEH, "twistIn": ACK_HIT + 0.5,
     "twistDur": TOTAL - ACK_HIT - 0.5, "scoreIn": ACK_HIT + 1.6, "scoreDur": TOTAL - ACK_HIT - 1.6}

tpl = open(os.path.join(ROOT, "build", "template.html")).read()
out = (tpl.replace("%TOTAL%", f(TOTAL)).replace("%VIDEOS%", "\n".join(V)).replace("%ATTEMPTS%", "\n".join(CAP))
       .replace("%AUDIO%", "\n".join(A)).replace("%K%", json.dumps(K)))
for k, v in list(K.items()) + list(D.items()):
    if isinstance(v, float):
        out = out.replace("%" + k + "%", f(v))
open(os.path.join(ROOT, "index.html"), "w").write(out)
print(json.dumps(K, indent=1))
