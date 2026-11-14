"""Talking-head version of the Archon Quest 7.2 short (1080x1920, 60 fps, < 60 s).
AbamKamil's own takes (assets/th/<line>.mp4) carry the narration; game footage
cuts in full-screen or split-screen (face top / game bottom) on the key words.
Run:  python3 build/gen2.py   (from the project root) -> index.html"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TH = json.load(open(os.path.join(ROOT, "build", "th_words.json")))
SHOTS = {s[0]: s for s in json.load(open(os.path.join(ROOT, "assets", "clips", "shots.json")))}
CODE = "QYJW50368SU7"
GAP = 0.06
END_HOLD = 1.2

# --- edit decision list ------------------------------------------------------
# ("th", line, [(shot, from, to, mode)])  from/to: word index (int) or "end"; mode full|split
# ("sync", shot)                           game voice line played from its clip
SEQ = [
    ("th", "h1", [("A", 0, 5, "full"), ("B", 5, 9, "full")]),
    ("th", "h2", []),
    ("th", "d1", [("D1", 5, 9, "full"), ("E", 9, "end", "full")]),
    ("th", "s1", [("F1", 2, 8, "split"), ("F2", 9, "end", "full")]),
    ("th", "r1", [("G", 0, 3, "full"), ("H", 5, "end", "full")]),
    ("th", "r2", [("I", 0, 5, "full")]),
    ("th", "z1", [("J", 1, "end", "split")]),
    ("th", "z2", [("K", 0, 7, "full"), ("L2", 9, "end", "full")]),
    ("th", "c1a", [("M", 0, "end", "full")]),
    ("sync", "N"),
    ("th", "c1b", [("NY", 0, "end", "full")]),
    ("th", "n1", [("O", 1, 6, "full"), ("C", 6, "end", "full")]),
    ("th", "e1", []),
    ("th", "e2", []),
]

t = 0.15
events = []
for ev in SEQ:
    d = TH[ev[1]]["dur"] if ev[0] == "th" else SHOTS[ev[1]][2]
    events.append({"kind": ev[0], "id": ev[1], "start": round(t, 3), "dur": d,
                   "ovl": ev[2] if ev[0] == "th" else []})
    t += d + GAP
TOTAL = round(t - GAP + END_HOLD, 2)
EV = {e["id"]: e for e in events}

def wt(line, idx):
    """absolute time of word idx in a talking-head line ("end" = line end)"""
    e = EV[line]
    if idx == "end":
        return round(e["start"] + e["dur"], 3)
    return round(e["start"] + TH[line]["words"][idx][1], 3)

# --- face clips (audio) + B-roll overlays --------------------------------------
faces, overlays = [], []
for i, e in enumerate(events):
    if e["kind"] == "th":
        nxt = events[i + 1]["start"] if i + 1 < len(events) else TOTAL
        end = TOTAL if e["id"] == "e2" else nxt
        faces.append({"id": e["id"], "start": e["start"], "end": round(end, 3), "dur": e["dur"]})
        for sid, a, b, mode in e["ovl"]:
            s0 = e["start"] if a == 0 else wt(e["id"], a)
            s1 = (nxt if b == "end" else wt(e["id"], b))
            if a == 0 and i == 0:
                s0 = 0.0
            overlays.append({"sid": sid, "start": round(s0, 3), "end": round(s1, 3), "mode": mode})
    else:
        nxt = events[i + 1]["start"]
        overlays.append({"sid": e["id"], "start": e["start"], "end": round(nxt, 3), "mode": "full", "sync": True})
for o in overlays:
    avail = SHOTS[o["sid"]][2] + 0.25
    if o["end"] - o["start"] > avail + 0.01: print("TOO SHORT", o["sid"], round(o["end"] - o["start"], 2), avail)

# --- end card window -----------------------------------------------------------
END_START = wt("e1", 6) - 0.95          # card lands right after "...redeem code dia."
T_CODE = END_START + 0.25
T_PRIMO = wt("e1", 6) - 0.05
T_EXP = wt("e1", 8) - 0.05
END_END = EV["e2"]["start"]
T_FOLLOW = wt("e2", 2) - 0.05

# --- captions (suppressed under hook text, gift, end card and outro) ----------------
GOLD = {"archon", "teyvat", "celestia", "celestial", "nail", "bahaya", "hancurkan", "wujud", "cataclysm", "500",
        "raiden", "ei", "eternity", "gila", "zhongli", "takde", "kontrak", "terakhir", "noy", "meremang",
        "bergabung", "tenaga", "redeem", "code", "primogems", "genshin", "tujuh", "7", "sejarah", "langsung",
        "libas", "mora", "watak", "baru", "60", "5", "claim", "follow"}
def clean(w):
    return w.strip(",.!?").lower()

def suppressed(t0):
    if t0 < EV["h2"]["start"] + EV["h2"]["dur"] + 0.01 and t0 >= EV["h2"]["start"] - 0.01:
        return True                                   # gift card carries this line
    if END_START - 0.05 <= t0:
        return True                                   # end card + outro
    if t0 < wt("h1", 9) - 0.01:
        return True                                   # hook title carries the opening
    return False

caps = []
for e in events:
    if e["kind"] != "th":
        continue
    W = TH[e["id"]]["words"]
    groups, cur = [], []
    for j, w in enumerate(W):
        cur.append(w)
        nxt = W[j + 1] if j + 1 < len(W) else None
        txt = " ".join(x[0] for x in cur)
        brk = len(cur) >= 2 or len(txt) >= 11 or w[0][-1] in ",.!?" or nxt is None or (nxt[1] - w[2] > 0.15)
        if nxt and len(cur) == 1 and len(w[0]) <= 3 and w[0][-1] not in ",.!?":
            brk = False
        if brk:
            groups.append(cur); cur = []
    for g in groups:
        s = e["start"] + g[0][1]
        if suppressed(s):
            continue
        caps.append({"words": [x[0] for x in g], "start": round(s, 3), "end": round(e["start"] + g[-1][2], 3),
                     "line_end": e["start"] + e["dur"]})
for a, b in zip(caps, caps[1:]):
    a["end"] = round(min(max(a["end"], a["start"] + 0.28), b["start"], a["line_end"] + 0.1), 3)
caps[-1]["end"] = round(min(caps[-1]["end"] + 0.25, END_START), 3)

# --- quotes / sections / stickers ------------------------------------------------
QUOTES = {"N": ("CELESTIA", "“Celestia welcomes you.”", "Celestia mengalu-alukan kedatangan kau.")}
SECTIONS = [("d1", "01", "BAHAYA KEWUJUDAN TEYVAT"), ("s1", "02", "7 ARCHON BERKUMPUL"),
            ("r1", "03", "RAIDEN EI × CELESTIAL NAIL"), ("z1", "04", "KONTRAK TERAKHIR ZHONGLI"),
            ("c1a", "05", "CELESTIA & NOY"), ("n1", "06", "SEMUA BERGABUNG TENAGA")]
secs = []
for i, (line, num, label) in enumerate(SECTIONS):
    s = EV[line]["start"] - 0.03
    e = (EV[SECTIONS[i + 1][0]]["start"] - 0.03) if i + 1 < len(SECTIONS) else END_START
    secs.append((num, label, round(s, 3), round(e, 3)))

def stk(sid, s, e, top, big, cls="gold", pos="top"):
    return (sid, round(s, 3), round(e - s, 3), top, big, cls, pos)
STICKERS = [
    stk("st-42", wt("d1", 9) + 0.05, wt("d1", "end") + GAP, "TINGGAL", "42 HARI", "red"),
    stk("st-500", wt("s1", 12) - 0.05, wt("s1", "end") + GAP, "", "500", "gold", "mid"),
    stk("st-500b", wt("s1", 12) - 0.05, wt("s1", "end") + GAP, "TAHUN LEPAS", "", "gold", "midsub"),
    stk("st-kontrak", wt("z2", 9) - 0.05, wt("z2", "end") + GAP, "KONTRAK", "TERAKHIR"),
    stk("st-noy", wt("c1b", 5) - 0.05, wt("c1b", "end") + GAP, "WATAK BARU!", "NOY", "gold", "top"),
    stk("st-gabung", wt("n1", 6) - 0.05, wt("n1", "end") + GAP, "SEMUA", "BERGABUNG!"),
]

# --- SFX ---------------------------------------------------------------------------
SFX = [
    ("impact-bass-1", 0.0, 0.5), ("whoosh-short", wt("h1", 5) - 0.1, 0.4), ("whoosh", wt("h1", 9) - 0.12, 0.4),
    ("whoosh", EV["h2"]["start"] - 0.1, 0.35), ("pop", EV["h2"]["start"] + 0.3, 0.45), ("pop", wt("h2", 5), 0.45),
    ("glitch-1", wt("d1", 5) - 0.05, 0.32), ("impact-bass-2", wt("d1", 9) - 0.3, 0.5),
    ("whoosh-short", wt("s1", 2) - 0.1, 0.35), ("whoosh", wt("s1", 9) - 0.1, 0.35), ("ping", wt("s1", 12) - 0.05, 0.35),
    ("whoosh-short", EV["r1"]["start"] + 0.2, 0.35), ("riser", EV["r2"]["start"] - 10.03, 0.3),
    ("impact-bass-1", EV["r2"]["start"], 0.6), ("pop", wt("r2", 5) - 0.04, 0.5),
    ("whoosh-short", wt("z1", 1) - 0.1, 0.35), ("sparkle", EV["z2"]["start"] + 0.2, 0.35),
    ("impact-bass-2", wt("z2", 9) - 0.35, 0.45),
    ("whoosh", EV["c1a"]["start"] - 0.1, 0.35), ("chime", EV["N"]["start"], 0.3),
    ("whoosh-short", EV["c1b"]["start"] - 0.08, 0.35), ("impact-bass-2", wt("c1b", 5) - 0.35, 0.5),
    ("whoosh-short", wt("n1", 1) - 0.1, 0.35), ("sparkle", wt("n1", 6) - 0.05, 0.4),
    ("impact-bass-1", END_START - 0.03, 0.5), ("ping", T_CODE, 0.35),
    ("pop", T_PRIMO, 0.45), ("pop", T_EXP, 0.45), ("notification", T_FOLLOW, 0.35),
]
SFX_DUR = {"impact-bass-1": 2.12, "impact-bass-2": 2.59, "whoosh": 0.57, "whoosh-short": 0.57, "pop": 0.72,
           "glitch-1": 2.64, "ping": 1.32, "riser": 10.03, "sparkle": 1.8, "chime": 2.5, "notification": 2.46}

# --- grades (HyperFrames media-treatment payloads) ------------------------------------
LIFT = {"B": 0.22, "F1": 0.12, "G": 0.15, "I": 0.05, "K": 0.08, "L2": 0.12, "Q": 0.1, "O": 0.1, "J": 0.05}
TAME = {"E": -0.28, "M": -0.28, "N": -0.32, "C": -0.12, "D1": -0.15, "A": -0.12}
def g_game(sid):
    adj = {"exposure": round(0.04 + LIFT.get(sid, 0) - (0.06 if sid in TAME else 0), 3), "contrast": 0.1,
           "highlights": TAME.get(sid, -0.16), "shadows": 0.14 + (0.08 if sid in LIFT else 0),
           "vibrance": 0.22, "temperature": 0.03}
    return {"preset": "deep-contrast", "intensity": 0.55, "adjust": adj, "details": {"vignette": 0.24},
            "effects": {"bloom": 0.22}}
# talking head: blown-out wall + flat skin -> pull highlights/whites, add contrast and warmth
G_FACE = {"preset": "deep-contrast", "intensity": 0.35,
          "adjust": {"exposure": -0.14, "contrast": 0.2, "highlights": -0.75, "whites": -0.35, "shadows": 0.06,
                     "blacks": -0.08, "temperature": 0.06, "tint": 0.02, "vibrance": 0.14, "saturation": 0.04},
          "details": {"vignette": 0.32}}
def attr(g):
    return html.escape(json.dumps(g, separators=(",", ":")), quote=True)

def f(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")

# --- HTML pieces ------------------------------------------------------------------------
P = []
z = 10
for fc in faces:
    P.append(f'      <div class="facewrap" id="fw-{fc["id"]}" style="z-index:{z}">\n'
             f'        <video id="face-{fc["id"]}" class="clip face" src="assets/th/{fc["id"]}.mp4" data-start="{f(fc["start"])}" '
             f'data-duration="{f(fc["end"] - fc["start"])}" data-track-index="1" data-has-audio="true" data-volume="1" '
             f'playsinline data-color-grading="{attr(G_FACE)}"></video>\n      </div>')
face_html = "\n".join(P); P.clear()

z = 20
for i, o in enumerate(overlays):
    sid = o["sid"]; d = o["end"] - o["start"]
    aud = 'data-has-audio="true" data-volume="1.6"' if o.get("sync") else "muted"
    cls = "split" if o["mode"] == "split" else "full"
    P.append(f'      <div class="shotwrap {cls}" id="w-{i}" style="z-index:{z + i}">\n'
             f'        <video id="v-{i}-{sid}" class="clip shot" src="assets/clips/{sid}.mp4" data-start="{f(o["start"])}" '
             f'data-duration="{f(d)}" data-track-index="2" {aud} playsinline data-color-grading="{attr(g_game(sid))}"></video>\n'
             f'      </div>')
    o["idx"] = i
ovl_html = "\n".join(P); P.clear()

for num, label, s, e in secs:
    P.append(f'      <div id="sec-{num}" class="clip sec" data-start="{f(s)}" data-duration="{f(e - s)}" data-track-index="5">'
             f'<div class="sec-in"><span class="sec-num">#{num}</span><span class="sec-label">{label}</span></div></div>')
sec_html = "\n".join(P); P.clear()

for sid, (who, en, bm) in QUOTES.items():
    e = EV[sid]
    P.append(f'      <div id="q-{sid}" class="clip quote" data-start="{f(e["start"])}" data-duration="{f(e["dur"])}" data-track-index="6">'
             f'<div class="q-in"><div class="q-who">{who}</div><div class="q-en">{html.escape(en)}</div>'
             f'<div class="q-bm">{html.escape(bm)}</div></div></div>')
quote_html = "\n".join(P); P.clear()

for sid, s, d, top, big, cls, pos in STICKERS:
    inner = ""
    if pos == "midsub":
        inner = f'<span class="sub">{top}</span>'
        pos = "midsub"
    else:
        if top and pos == "top" and big:
            inner = f'<span class="sub">{top}</span>' if sid != "st-noy" else ""
        if big:
            size = min(190, int(860 / (max(1, len(big)) * 0.76)))
            inner += f'<span class="big {cls}" style="font-size:{size}px">{big}</span>'
        if sid == "st-noy":
            inner += f'<span class="sub">{top}</span>'
    P.append(f'      <div id="{sid}" class="clip stk {pos}" data-start="{f(s)}" data-duration="{f(d)}" data-track-index="7">'
             f'<div class="stk-in">{inner}</div></div>')
stk_html = "\n".join(P); P.clear()

for i, c in enumerate(caps):
    spans = "".join(f'<span class="w{" g" if clean(w) in GOLD else ""}">{html.escape(w.strip(",.").upper())}</span>'
                    for w in c["words"])
    P.append(f'        <div id="cap-{i}" class="clip cap" data-start="{f(c["start"])}" data-duration="{f(c["end"] - c["start"])}">'
             f'<div class="cap-in">{spans}</div></div>')
cap_html = "\n".join(P); P.clear()

for i, (name, s, vol) in enumerate(SFX):
    s = max(0.0, s)
    P.append(f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.mp3" data-start="{f(s)}" '
             f'data-duration="{f(min(SFX_DUR[name], TOTAL - s))}" data-volume="{vol}" data-track-index="12"></audio>')
sfx_html = "\n".join(P); P.clear()

code_spans = "".join(f'<span class="ch">{c}</span>' for c in CODE)
punch = {fc["id"]: TH[fc["id"]]["cuts"] for fc in faces}
T = {"total": TOTAL, "faces": faces, "overlays": overlays, "punch": punch, "end_start": END_START,
     "end_end": END_END, "t_code": T_CODE, "t_primo": T_PRIMO, "t_exp": T_EXP, "t_follow": T_FOLLOW,
     "strike": EV["r2"]["start"], "gila": wt("r2", 5), "hook_end": wt("h1", 9),
     "gift": [EV["h2"]["start"], EV["d1"]["start"]], "outro": EV["e2"]["start"]}

page = open(os.path.join(ROOT, "build", "template2.html")).read()
for k, v in {"{{TOTAL}}": f(TOTAL), "{{FACES}}": face_html, "{{OVERLAYS}}": ovl_html, "{{SECTIONS}}": sec_html,
             "{{QUOTES}}": quote_html, "{{STICKERS}}": stk_html, "{{CAPTIONS}}": cap_html, "{{SFX}}": sfx_html,
             "{{CODE_SPANS}}": code_spans, "{{CODE}}": CODE, "{{HOOK_DUR}}": f(wt("h1", 9) - 0.02),
             "{{GIFT_START}}": f(EV["h2"]["start"]), "{{GIFT_DUR}}": f(EV["d1"]["start"] - EV["h2"]["start"] - 0.02),
             "{{END_START}}": f(END_START), "{{END_DUR}}": f(END_END - END_START),
             "{{OUTRO_START}}": f(EV["e2"]["start"]), "{{OUTRO_DUR}}": f(TOTAL - EV["e2"]["start"]),
             "{{TIMELINE_JSON}}": json.dumps(T)}.items():
    page = page.replace(k, v)
open(os.path.join(ROOT, "index.html"), "w").write(page)
print("total", TOTAL, "faces", len(faces), "overlays", len(overlays), "captions", len(caps))
for e in events:
    print(f'  {e["start"]:6.2f} {e["kind"]:4s} {e["id"]:4s} {e["dur"]:.2f}')
