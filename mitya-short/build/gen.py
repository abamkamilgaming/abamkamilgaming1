"""Test Run Mitya — TikTok short (1080x1920, 60 fps).
Layout like Doro44 / thejonathon: facecam on top (0-760), gameplay below (760-1920),
2-3 word captions on the seam, chat bubbles, stickers, meme SFX + VFX.
Run from the project root:  python3 build/gen.py  -> index.html"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEG = json.load(open(os.path.join(ROOT, "build", "segs.json")))
ORDER = ["h1", "h2", "h3", "s1", "s2", "sm", "s3", "s4", "s5a", "s5b", "ff", "s5c", "s6", "s7", "e1", "e2", "e3"]
END_HOLD = 2.5

T0 = {}
t = 0.0
for sid in ORDER:
    T0[sid] = round(t, 3)
    t += SEG[sid]["dur"]
END_START = round(t, 3)
TOTAL = round(t + END_HOLD, 3)


def at(sid, x):
    return round(T0[sid] + x, 3)


def f(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- captions (seg-local times)
# "*word" = yellow keyword
CAPS = {
    "h3": [("I WILL BE THE ONE", 0.05, 1.36), ("WHO *DECIDES", 1.36, 2.07), ("HE IS *WORTHY", 2.07, 2.98), ("OR NOT", 2.98, 3.55)],
    "s1": [("AKU DAH DENGAR", 0.05, 0.86), ("TAPI APA?", 0.86, 1.95), ("*TERUK SANGAT KE?", 1.95, 2.62), ("*BUG TU.", 2.62, 2.92)],
    "s2": [("DIA TAK *NERF DAMAGE", 0.05, 1.21), ("TAPI DIA ADA *BUG", 1.21, 1.98), ("THERE'S A DIFFERENCE", 1.98, 2.78),
           ("BETWEEN", 2.78, 3.16), ("*DAMAGE NERF", 3.16, 3.9), ("OR *GAMEPLAY NERF", 3.9, 5.27),
           ("EH SORRY", 5.27, 5.54), ("GAMEPLAY *BUG", 5.54, 6.32)],
    "sm": [("NOT BAD", 0.05, 0.86), ("NOT BAD *IDLE DIA", 0.86, 1.8)],
    "s3": [("AKU BUAT APA NI?", 1.13, 2.0), ("AKU TENGAH *TEST RUN", 2.0, 3.12), ("*MITYA", 3.12, 3.5),
           ("FOR THE *FIRST TIME", 3.5, 4.1), ("IN LIFETIME!", 4.1, 4.62)],
    "s4": [("DIA MACAM *LISA", 0.05, 1.48), ("BETUL, SERIUS NI", 1.48, 2.3), ("DIA VERSION *LISA", 2.3, 3.38), ("TAPI *BOY!", 3.38, 4.24)],
    "s5a": [("*25 SECOND?", 0.02, 1.05), ("SERIUS LAH?!", 1.05, 1.49)],
    "s5b": [("OKAY, AKU SET *TIMER", 0.04, 1.88), ("PHONE AKU", 1.88, 2.7)],
    "s5c": [("BETUL LAH!", 0.02, 0.36), ("*25 FREAKING SECOND!", 0.36, 1.95), ("MITYA TAK MAIN *DPS PUN", 1.95, 2.86), ("DIA *BERGUNA!", 2.86, 3.43)],
    "s6": [("KENAPA AKU PULA", 4.98, 5.6), ("YANG *TINGGI SUARA NI?", 5.6, 7.15)],
    "s7": [("*SEDAP LAH PULA", 0.04, 0.6), ("*MITYA NI", 0.6, 1.31)],
    "e1": [("MEMANG *ELOK", 0.05, 1.58), ("*SANGAT LAH!", 1.58, 2.62), ("MITYA MITYA *MITYA!", 2.62, 3.645)],
    "e2": [("*SATISFYING FEELING", 0.05, 1.22), ("WHEN YOU *CHARGE ATTACK", 1.22, 2.6), ("TAPI MEMANG *DAMAGE DIA", 2.6, 4.5),
           ("GITU.", 5.8, 6.336)],
    "e3": [("*20K LIKE,", 0.02, 0.72), ("AKU TERPAKSA *PULL!", 0.72, 1.7), ("MEMANG *SEDAP GUYS", 1.7, 2.748)],
}
caps = []
for sid, groups in CAPS.items():
    for txt, a, b in groups:
        caps.append((at(sid, a), at(sid, min(b, SEG[sid]["dur"])), txt))
caps.sort()

# ---------------------------------------------------------------- stickers: (id, start, end, html, class)
STK = [
    ("st-salah", at("s2", 5.27), at("s2", 6.32), "SALAH SEBUT 💀", "red tilt-l"),
    ("st-lisa", at("s4", 2.9), at("s4", 4.243), "LISA<br><small>VERSI LELAKI 💜</small>", "violet tilt-r"),
    ("st-25", at("s5a", 0.3), at("s5a", 1.486), "25 SAAT?!", "gold tilt-l"),
    ("st-3", at("s5b", 2.72), at("s5b", 3.2), "3", "num"),
    ("st-2", at("s5b", 3.2), at("s5b", 3.55), "2", "num"),
    ("st-1", at("s5b", 3.55), at("s5b", 4.243), "1", "num"),
    ("st-ok", at("s5c", 0.36), at("s5c", 1.95), "✅ 25 SAAT<br><small>CONFIRMED</small>", "green tilt-r"),
    ("st-berguna", at("s5c", 2.86), at("s5c", 3.43) + 0.1, "BERGUNA!", "gold tilt-l"),
    ("st-tinggi", at("s6", 5.6), at("s6", 7.15), "😂😂😂", "emoji"),
    ("st-sedap", at("s7", 0.3), at("s7", 1.308), "SEDAP 🤤", "gold tilt-r"),
    ("st-z1", at("e2", 4.56), at("e2", 5.8), "ZAP!", "zap z1"),
    ("st-z2", at("e2", 4.88), at("e2", 5.8), "ZAP!", "zap z2"),
    ("st-z3", at("e2", 5.18), at("e2", 5.8), "ZAP!", "zap z3"),
    ("st-z4", at("e2", 5.48), at("e2", 5.95), "ZAP!", "zap z4"),
]

# ---------------------------------------------------------------- SFX (name, time, volume)
SFX = [
    ("vine", 0.0, 0.55), ("whoosh", at("h2", -0.08), 0.5), ("impact-bass-1", at("h2", 0.0), 0.6), ("wth", at("h2", 0.62), 0.0),
    ("whoosh-short", at("h3", -0.06), 0.4), ("pop", at("h3", 2.1), 0.4),
    ("whoosh", at("s1", -0.06), 0.35),
    ("illuminati", at("s2", 1.98), 0.38), ("awkward", at("s2", 5.27), 0.7),
    ("whoosh-short", at("sm", -0.06), 0.35), ("sparkle", at("sm", 1.85), 0.3),
    ("notification", at("s3", 0.0), 0.45), ("pop", at("s3", 2.0), 0.35),
    ("whoosh-short", at("s4", -0.05), 0.35), ("cutewow", at("s4", 3.78), 0.6),
    ("vine", at("s5a", 1.03), 0.6), ("faaah", at("s5a", 1.42), 0.45),
    ("pop", at("s5b", 2.72), 0.5), ("pop", at("s5b", 3.2), 0.5), ("pop", at("s5b", 3.55), 0.55),
    ("glitch-1", at("ff", 0.0), 0.35), ("whoosh", at("ff", 1.15), 0.4),
    ("yay", at("s5c", 0.36), 0.45), ("sparkle", at("s5c", 2.86), 0.4),
    ("whoosh-short", at("s6", -0.05), 0.35), ("laugh", at("s6", 6.9), 0.5),
    ("whoosh", at("s7", -0.08), 0.45), ("sparkle", at("s7", 0.3), 0.35),
    ("impact-bass-2", at("e1", 1.56), 0.55),
    ("whoosh-short", at("e2", -0.05), 0.35), ("pop", at("e2", 4.56), 0.55), ("pop", at("e2", 4.88), 0.55),
    ("pop", at("e2", 5.18), 0.55), ("pop", at("e2", 5.48), 0.6),
    ("ping", at("e3", 0.05), 0.4), ("impact-bass-1", END_START, 0.5), ("notification", END_START + 0.55, 0.4),
]
SFX = [s for s in SFX if s[2] > 0]
SFX_DUR = {"vine": 1.2, "awkward": 1.464, "cutewow": 1.632, "faaah": 1.776, "glitch-1": 2.638, "illuminati": 3.216,
           "impact-bass-1": 2.116, "impact-bass-2": 2.592, "laugh": 1.824, "notification": 2.455, "ping": 1.32, "pop": 0.72,
           "quack": 0.624, "sparkle": 1.802, "vine": 1.2, "whoosh-short": 0.575, "whoosh": 0.575, "wth": 2.232, "yay": 1.824,
           "emodmg": 2.04, "riser": 10.03}

# ---------------------------------------------------------------- grades (HyperFrames media treatments)
G_FACE = {"preset": "skin-soft", "intensity": 0.62,
          "adjust": {"exposure": 0.06, "contrast": 0.08, "highlights": -0.1, "shadows": 0.1, "temperature": 0.05,
                     "tint": -0.03, "vibrance": 0.04, "saturation": 0.02},
          "details": {"vignette": 0.05}}
TAME = {"h2": -0.3, "s5a": -0.22, "h3": -0.18, "s1": -0.18, "s2": -0.18, "e1": -0.2}
def g_game(sid):
    return {"preset": "deep-contrast", "intensity": 0.5,
            "adjust": {"exposure": 0.05 if sid not in TAME else -0.02, "contrast": 0.1, "highlights": TAME.get(sid, -0.12),
                       "shadows": 0.12, "vibrance": 0.2, "temperature": 0.02},
            "details": {"vignette": 0.12}, "effects": {"bloom": 0.18}}
def attr(g):
    return html.escape(json.dumps(g, separators=(",", ":")), quote=True)


# ---------------------------------------------------------------- HTML
P = []
for i, sid in enumerate(ORDER):
    d = SEG[sid]["dur"]
    aud = 'muted' if sid == "ff" else 'data-has-audio="true" data-volume="1"'
    P.append(f'      <div class="facewrap" id="fw-{sid}" style="z-index:{10 + i}">'
             f'<video id="face-{sid}" class="clip face" src="assets/face/{sid}.mp4" data-start="{f(T0[sid])}" data-duration="{f(d)}" '
             f'data-track-index="1" {aud} playsinline data-color-grading="{attr(G_FACE)}"></video></div>')
    P.append(f'      <div class="gamewrap" id="gw-{sid}" style="z-index:{10 + i}">'
             f'<video id="game-{sid}" class="clip game" src="assets/game/{sid}.mp4" data-start="{f(T0[sid])}" data-duration="{f(d)}" '
             f'data-track-index="2" muted playsinline data-color-grading="{attr(g_game(sid))}"></video></div>')
media_html = "\n".join(P); P.clear()

def cap_spans(txt):
    out = []
    for w in txt.split():
        k = w.startswith("*")
        out.append(f'<span class="w{" k" if k else ""}">{html.escape(w.lstrip("*"))}</span>')
    return "".join(out)

for i, (s, e, txt) in enumerate(caps):
    P.append(f'        <div id="cap-{i}" class="clip cap" data-start="{f(s)}" data-duration="{f(e - s)}"><div class="cap-in">{cap_spans(txt)}</div></div>')
cap_html = "\n".join(P); P.clear()

for sid, s, e, inner, cls in STK:
    P.append(f'      <div id="{sid}" class="clip stk {cls.split()[0]}" data-start="{f(s)}" data-duration="{f(e - s)}" data-track-index="6">'
             f'<div class="stk-in {cls}">{inner}</div></div>')
stk_html = "\n".join(P); P.clear()

for i, (name, s, vol) in enumerate(SFX):
    s = max(0.0, s)
    P.append(f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.mp3" data-start="{f(s)}" '
             f'data-duration="{f(min(SFX_DUR[name], TOTAL - s))}" data-volume="{vol}" data-track-index="12"></audio>')
sfx_html = "\n".join(P); P.clear()

TL = {"total": TOTAL, "end": END_START, "order": ORDER, "t0": T0,
      "dur": {k: SEG[k]["dur"] for k in ORDER}, "cuts": {k: SEG[k]["cuts"] for k in ORDER},
      "h2": T0["h2"], "h3": T0["h3"], "omg": at("h2", 0.0), "serius": at("s5a", 1.05), "boy": at("s4", 3.8),
      "salah": at("s2", 5.27), "tinggi": at("s6", 5.6), "elok": at("e1", 1.58), "e1": T0["e1"], "ff": T0["ff"],
      "galaxy": [at("s2", 1.98), at("s2", 4.6)], "chat": [T0["s3"], at("s3", 1.9)],
      "q1": [at("sm", 1.8), at("sm", SEG["sm"]["dur"])], "q2": [T0["s6"], at("s6", 4.95)],
      "zaps": [at("e2", x) for x in (4.56, 4.88, 5.18, 5.48)], "e3": T0["e3"]}

R = {
    "{{TOTAL}}": f(TOTAL), "{{MEDIA}}": media_html, "{{CAPTIONS}}": cap_html, "{{STICKERS}}": stk_html, "{{SFX}}": sfx_html,
    "{{H1_DUR}}": f(T0["h2"]), "{{H2_START}}": f(T0["h2"]), "{{H2_DUR}}": f(SEG["h2"]["dur"]),
    "{{H3_START}}": f(T0["h3"]), "{{H3_DUR}}": f(SEG["h3"]["dur"]),
    "{{HUD_START}}": f(T0["s1"]), "{{HUD_DUR}}": f(END_START - T0["s1"]),
    "{{GAL_START}}": f(TL["galaxy"][0]), "{{GAL_DUR}}": f(TL["galaxy"][1] - TL["galaxy"][0]),
    "{{CHAT_START}}": f(TL["chat"][0]), "{{CHAT_DUR}}": f(TL["chat"][1] - TL["chat"][0]),
    "{{Q1_START}}": f(TL["q1"][0]), "{{Q1_DUR}}": f(TL["q1"][1] - TL["q1"][0]),
    "{{Q2_START}}": f(TL["q2"][0]), "{{Q2_DUR}}": f(TL["q2"][1] - TL["q2"][0]),
    "{{VERDICT_START}}": f(at("e1", 1.58)), "{{VERDICT_DUR}}": f(1.7),
    "{{CTA_START}}": f(T0["e3"]), "{{CTA_DUR}}": f(END_START - T0["e3"]),
    "{{END_START}}": f(END_START), "{{END_DUR}}": f(END_HOLD),
    "{{CARMEN_START}}": f(T0["h3"]), "{{CARMEN_DUR}}": f(T0["e1"] - T0["h3"]),
    "{{WIN_START}}": f(T0["e1"]), "{{WIN_DUR}}": f(TOTAL - T0["e1"]),
    "{{TIMELINE_JSON}}": json.dumps(TL),
}
page = open(os.path.join(ROOT, "build", "template.html")).read()
for k, v in R.items():
    page = page.replace(k, v)
open(os.path.join(ROOT, "index.html"), "w").write(page)
print("total", TOTAL, "end card at", END_START, "captions", len(caps), "sfx", len(SFX))
for sid in ORDER:
    print(f"  {T0[sid]:6.2f}  {sid:4s} {SEG[sid]['dur']:.2f}")
