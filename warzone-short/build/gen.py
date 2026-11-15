"""Warzone short, Doro44-style (1080x1920, < 60 s).
Face cam top panel (0-900), gameplay bottom panel (900-1920), big pop captions on the seam,
meme stickers + meme SFX on the funny beats, premium grade on both panels.
Run: python3 build/gen.py  (after build/cut.py) -> index.html"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEG = json.load(open(os.path.join(ROOT, "build", "segs.json")))
ORDER = ["hook", "helo", "genshin", "act1", "alone", "res", "baz", "uzi", "best", "act",
         "gift", "gift2", "minyak", "chat", "end"]
END_HOLD = 1.6

start, t = {}, 0.0
for sid in ORDER:
    start[sid] = round(t, 3); t += SEG[sid]["dur"]
TOTAL = round(t + END_HOLD, 2)


def at(sid, i):
    """absolute time of caption group i of a segment ("end" = segment end)"""
    if i == "end":
        return round(start[sid] + SEG[sid]["dur"], 3)
    return round(start[sid] + SEG[sid]["caps"][i][1], 3)


def f(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


# --- grades (HyperFrames media-treatment payloads) ---------------------------------
G_FACE = {"preset": "deep-contrast", "intensity": 0.4,
          "adjust": {"exposure": 0.03, "contrast": 0.16, "highlights": -0.45, "whites": -0.15, "shadows": 0.16,
                     "blacks": -0.06, "temperature": 0.05, "tint": 0.01, "vibrance": 0.16, "saturation": 0.02},
          "details": {"vignette": 0.28}}
LIFT = {"baz": 0.22, "uzi": 0.22, "act1": 0.0, "alone": 0.06, "res": 0.08}      # dark warehouse shots
def g_game(sid):
    lift = LIFT.get(sid, 0.0)
    return {"preset": "deep-contrast", "intensity": 0.55,
            "adjust": {"exposure": round(0.02 + lift, 3), "contrast": 0.14, "highlights": -0.28,
                       "shadows": round(0.12 + lift * 0.6, 3), "vibrance": 0.26, "temperature": 0.03},
            "details": {"vignette": 0.22}, "effects": {"bloom": 0.14}}
def attr(g):
    return html.escape(json.dumps(g, separators=(",", ":")), quote=True)


# --- panels --------------------------------------------------------------------------
P = []
for i, sid in enumerate(ORDER):
    s = start[sid]
    d = SEG[sid]["dur"] + (END_HOLD if sid == "end" else 0)
    P.append(f'      <div class="fw" id="fw-{sid}" style="z-index:{10 + i}">'
             f'<video id="face-{sid}" class="clip face" src="assets/seg/{sid}_face.mp4" data-start="{f(s)}" '
             f'data-duration="{f(d)}" data-track-index="1" data-has-audio="true" data-volume="1" playsinline '
             f'data-color-grading="{attr(G_FACE)}"></video></div>')
    P.append(f'      <div class="gw" id="gw-{sid}" style="z-index:{10 + i}">'
             f'<video id="game-{sid}" class="clip game" src="assets/seg/{sid}_game.mp4" data-start="{f(s)}" '
             f'data-duration="{f(d)}" data-track-index="2" muted playsinline '
             f'data-color-grading="{attr(g_game(sid))}"></video></div>')
panels = "\n".join(P)

# --- captions (seam, 1-3 words, keywords yellow) ------------------------------------------
HOT = {"gi", "genshin", "bazooka", "uzi", "farahin", "insyaallah", "resources", "sorang", "best", "full", "tank",
       "belum", "lampu", "hijau", "warzone"}
caps = []
for sid in ORDER:
    for j, (txt, ts) in enumerate(SEG[sid]["caps"]):
        s = start[sid] + ts
        nxt = SEG[sid]["caps"][j + 1][1] + start[sid] if j + 1 < len(SEG[sid]["caps"]) else at(sid, "end") + 0.05
        if sid == "hook" and j < 2:
            continue                                     # hook title carries the first beats
        caps.append((txt, round(s, 3), round(nxt, 3)))
C = []
for i, (txt, s, e) in enumerate(caps):
    words = "".join(f'<span class="w{" y" if w.strip(",.!?").lower() in HOT else ""}">'
                    f'{html.escape(w.upper())}</span>' for w in txt.split())
    fs = max(78, min(124, int(960 / (len(txt) * 0.72))))      # Archivo Black caps ~0.72em per glyph
    C.append(f'        <div id="cap-{i}" class="clip cap" data-start="{f(s)}" data-duration="{f(e - s)}" '
             f'data-track-index="3"><div class="cap-in" style="font-size:{fs}px">{words}</div></div>')
cap_html = "\n".join(C)

# --- stickers: (id, start, end, emoji, text, sub, colour class, position) ------------------
STK = [
    ("s-alone", at("alone", 2) - 0.05, at("alone", "end"), "🦗", "FOREVER ALONE", "", "white", "g-top"),
    ("s-baz", at("baz", 1) - 0.04, at("baz", "end"), "🚀", "BAZOOKA?!", "", "yellow", "g-mid"),
    ("s-uzi", at("uzi", 1) - 0.04, at("uzi", "end"), "🤨", "UZI??", "", "yellow", "g-mid"),
    ("s-best", at("best", 0), at("best", "end"), "👎", "0/10", "TAK BEST", "red", "g-mid"),
    ("s-mrk", start["gift"] + 0.1, at("gift2", 1), "🕴️", "MR.K", "ABAM KAMIL SEBAGAI", "yellow", "g-low"),
    ("s-tank", at("minyak", 0) + 0.3, at("minyak", "end"), "⛽", "FULL TANK", "", "yellow", "g-mid"),
    ("s-dmg", at("chat", 0) + 0.15, at("chat", "end"), "💀", "EMOTIONAL DAMAGE", "", "red", "g-low"),
]
S = []
for sid, s, e, emo, txt, sub, cls, pos in STK:
    size = min(170, int(820 / (len(txt) * 0.74)))
    S.append(f'      <div id="{sid}" class="clip stk {pos}" data-start="{f(s)}" data-duration="{f(e - s)}" data-track-index="4">'
             f'<div class="stk-in">{f"<span class=sub>{sub}</span>" if sub else ""}<span class="emo">{emo}</span>'
             f'<span class="big {cls}" style="font-size:{size}px">{txt}</span></div></div>')
stk_html = "\n".join(S)

# --- sfx (file, time, volume, duration cap) ------------------------------------------------
SFX_LEN = {"vine-boom-meme": 1.31, "faaah": 1.96, "awkward-moment": 1.49, "violin-screech-meme": 4.0,
           "laughing-dog-meme": 9.87, "run-vine-sound-effect": 8.28, "french-meme-song": 14.6,
           "emotional-damage-meme": 3.37, "get-out-meme": 1.03, "outro-song": 18.7}
SFX = [
    ("vine-boom-meme", at("hook", 2) - 0.02, 0.55, None),
    ("vine-boom-meme", at("genshin", 0) + 0.35, 0.4, None),
    ("awkward-moment", at("alone", 2), 0.6, None),
    ("violin-screech-meme", at("baz", 1) - 0.05, 0.32, 1.6),
    ("faaah", at("uzi", 1) + 0.05, 0.5, None),
    ("laughing-dog-meme", at("best", 1) + 0.25, 0.35, 2.2),
    ("run-vine-sound-effect", start["act"], 0.45, SEG["act"]["dur"]),
    ("french-meme-song", start["gift"], 0.22, SEG["gift"]["dur"] + SEG["gift2"]["dur"]),
    ("vine-boom-meme", at("minyak", 1) - 0.02, 0.45, None),
    ("emotional-damage-meme", at("chat", 0) + 0.45, 0.55, None),
    ("outro-song", start["end"], 0.3, SEG["end"]["dur"] + END_HOLD),
]
A = []
for i, (name, s, vol, cap) in enumerate(SFX):
    d = min(SFX_LEN[name], cap or 99, TOTAL - s)
    fade = ' data-fade-out="0.3"' if cap else ""
    A.append(f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.mp3" data-start="{f(s)}" '
             f'data-duration="{f(d)}" data-volume="{vol}"{fade} data-track-index="9"></audio>')
sfx_html = "\n".join(A)

T = {"total": TOTAL, "order": ORDER, "start": start, "dur": {k: SEG[k]["dur"] for k in ORDER},
     "cuts": {k: SEG[k]["cuts"] for k in ORDER},
     "hook_end": at("hook", 2) + 0.05, "boom": at("hook", 2),
     "punch": [at("genshin", 0) + 0.35, at("baz", 1), at("uzi", 1), at("minyak", 1), at("chat", 0)],
     "shake": [at("baz", 1), start["act"] + 0.3, start["act1"] + 0.2],
     "chat": [start["chat"], at("chat", "end")], "end": start["end"] + 0.5, "follow": at("end", 2)}

tpl = open(os.path.join(ROOT, "build", "template.html")).read()
for k, v in {"{{TOTAL}}": f(TOTAL), "{{PANELS}}": panels, "{{CAPTIONS}}": cap_html, "{{STICKERS}}": stk_html,
             "{{SFX}}": sfx_html, "{{HOOK_DUR}}": f(T["hook_end"]),
             "{{CHAT_START}}": f(T["chat"][0]), "{{CHAT_DUR}}": f(T["chat"][1] - T["chat"][0]),
             "{{END_START}}": f(T["end"]), "{{END_DUR}}": f(TOTAL - T["end"]), "{{T}}": json.dumps(T)}.items():
    tpl = tpl.replace(k, v)
open(os.path.join(ROOT, "index.html"), "w").write(tpl)
print("TOTAL", TOTAL)
for sid in ORDER:
    print(f"  {start[sid]:6.2f}  {sid:8s} {SEG[sid]['dur']:.2f}")
