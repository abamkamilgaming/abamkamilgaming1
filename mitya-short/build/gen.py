"""Mitya guide short (1080x1920, < 60 s): muka atas / gameplay bawah, gaya AbamKamil.
Narration = assets/voice/<line>.wav (TTS sementara -> ganti dgn suara / talking head sebenar).
Run dari root projek:  python3 build/gen.py  -> index.html"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO = json.load(open(os.path.join(ROOT, "build", "vo_words_tight.json")))
SHOTS = {s[0]: s for s in json.load(open(os.path.join(ROOT, "assets", "clips", "shots.json")))}
PREVIEW = True          # tunjuk tag "STAND-IN" pada muka placeholder
GAP, START, END_HOLD = 0.06, 0.1, 1.0

# line -> [(shot, from word, to word)]   ("end" = sampai line seterusnya)
SEQ = [
    ("h1", [("A", 0, "end")]), ("h2", [("A2", 0, "end")]),
    ("s1", [("S1", 0, 5), ("S2", 5, "end")]),
    ("m1", [("M1", 0, "end")]), ("m2", [("M2", 0, "end")]), ("m3", [("M3", 0, "end")]), ("m4", [("M4", 0, "end")]),
    ("m5", [("M5", 0, 7), ("M5b", 7, "end")]), ("m6", [("M6", 0, "end")]),
    ("b0", [("B0", 0, "end")]), ("b1", [("B1", 0, "end")]), ("b2", [("B2", 0, "end")]), ("b3", [("B3", 0, "end")]),
    ("t1", [("T1", 0, "end")]), ("z1", [("Z", 0, "end")]), ("e1", [("A2", 0, "end")]),
]
SLAM = {"A", "M5b", "M6", "Z"}

t = START; lines = []
for lid, ovl in SEQ:
    lines.append({"id": lid, "start": round(t, 3), "dur": VO[lid]["dur"], "ovl": ovl}); t += VO[lid]["dur"] + GAP
TOTAL = round(t - GAP + END_HOLD, 2)
assert TOTAL < 60, TOTAL
EV = {l["id"]: l for l in lines}
def wt(line, idx):
    e = EV[line]
    return round(e["start"] + (e["dur"] if idx == "end" else VO[line]["words"][idx][1]), 3)
def nxt(line):
    i = [l["id"] for l in lines].index(line)
    return lines[i + 1]["start"] if i + 1 < len(lines) else TOTAL

shots = []
for l in lines:
    for sid, a, b in l["ovl"]:
        s0 = 0.0 if (l is lines[0] and a == 0) else (l["start"] if a == 0 else wt(l["id"], a))
        s1 = nxt(l["id"]) if b == "end" else wt(l["id"], b)
        if s1 - s0 > SHOTS[sid][2] + 0.02: print("SHOT TOO SHORT", sid, round(s1 - s0, 2), SHOTS[sid][2])
        shots.append({"sid": sid, "start": round(s0, 3), "end": round(s1, 3), "idx": len(shots), "slam": sid in SLAM})

# ---- grades (HyperFrames media-treatment) ---------------------------------------------
LIFT = {"M6": 0.2, "S2": 0.05, "B3": 0.12}                 # shot gelap -> naikkan
TAME = {"S1": -0.1, "M4": -0.3, "M1": -0.22, "Z": -0.2, "A": -0.2}   # shot terlalu terang -> turunkan highlight
def g_game(sid):
    adj = {"exposure": round(0.02 + LIFT.get(sid, 0) - (0.05 if sid in TAME else 0), 3), "contrast": 0.14,
           "highlights": TAME.get(sid, -0.14), "shadows": 0.12 + (0.08 if sid in LIFT else 0), "blacks": -0.06,
           "vibrance": 0.24, "saturation": 0.04, "temperature": -0.03, "tint": 0.03}
    return {"preset": "deep-contrast", "intensity": 0.55, "adjust": adj, "details": {"vignette": 0.26}, "effects": {"bloom": 0.2}}
# talking head: dinding terlalu terang + kulit flat -> tarik highlight, tambah kontras & warmth
G_FACE = {"preset": "deep-contrast", "intensity": 0.35,
          "adjust": {"exposure": -0.12, "contrast": 0.2, "highlights": -0.7, "whites": -0.3, "shadows": 0.06, "blacks": -0.08,
                     "temperature": 0.06, "tint": 0.02, "vibrance": 0.14, "saturation": 0.04}, "details": {"vignette": 0.34}}
def attr(g): return html.escape(json.dumps(g, separators=(",", ":")), quote=True)
def f(x): return f"{x:.3f}".rstrip("0").rstrip(".")
def E(s): return html.escape(s)

face_html = (f'        <video id="face" class="clip face" src="assets/face/standin.mp4" data-start="0" data-duration="{f(TOTAL)}" '
             f'data-track-index="1" muted playsinline data-color-grading="{attr(G_FACE)}"></video>')
P = []
for o in shots:
    P.append(f'        <div class="shotwrap" id="w-{o["idx"]}" style="z-index:{20 + o["idx"]}">'
             f'<video id="v-{o["idx"]}-{o["sid"]}" class="clip shot" src="assets/clips/{o["sid"]}.mp4" data-start="{f(o["start"])}" '
             f'data-duration="{f(o["end"] - o["start"])}" data-track-index="2" muted playsinline '
             f'data-color-grading="{attr(g_game(o["sid"]))}"></video></div>')
shot_html = "\n".join(P); P.clear()

for l in lines:
    P.append(f'      <audio id="vo-{l["id"]}" class="clip" src="assets/voice/{l["id"]}.wav" data-start="{f(l["start"])}" '
             f'data-duration="{f(l["dur"])}" data-volume="1" data-track-index="10"></audio>')
vo_html = "\n".join(P); P.clear()

# ---- sections ------------------------------------------------------------------------------
SECTIONS = [("s1", "01", "SHOWCASE"), ("m1", "02", "CARA MAIN"), ("b0", "03", "BUILD"), ("t1", "04", "TEAM COMP"),
            ("z1", "05", "TEAM MASA DEPAN")]
for i, (line, num, label) in enumerate(SECTIONS):
    s = EV[line]["start"] - 0.03
    e = (EV[SECTIONS[i + 1][0]]["start"] - 0.03) if i + 1 < len(SECTIONS) else EV["e1"]["start"] - 0.03
    P.append(f'      <div id="sec-{num}" class="clip sec" data-start="{f(s)}" data-duration="{f(e - s)}" data-track-index="5">'
             f'<div class="sec-in"><span class="sec-num">#{num}</span><span class="sec-label">{label}</span></div></div>')
sec_html = "\n".join(P); P.clear()

# ---- cards (motion graphics dalam panel game) --------------------------------------------------
def at(line, idx, off=-0.05): return f(max(EV[line]["start"], wt(line, idx) + off))
CARDS = []   # (id, start, end, inner html, dim?)
def card(cid, s, e, inner, dim=True): CARDS.append((cid, round(s, 3), round(e, 3), inner, dim))
L = lambda x: EV[x]["start"]
card("hook", 0.0, nxt("h1"),
     f'<span class="chip" data-at="0">GUIDE 60 SAAT</span>'
     f'<div class="big white" style="font-size:96px" data-at="0">JANGAN PULL</div>'
     f'<div class="big gold" style="font-size:210px" data-at="0" data-fx="slam">MITYA</div>'
     f'<div class="sub" data-at="0">SEBELUM TENGOK NI!</div>', False)
card("hook2", L("h2"), nxt("h2"),
     f'<div class="row"><div class="tile hot" data-at="{at("h2", 0)}" data-fx="left"><div class="t-k">01</div><div class="t-v" style="font-size:70px">CARA MAIN</div></div>'
     f'<div class="tile hot" data-at="{at("h2", 3)}" data-fx="right"><div class="t-k">02</div><div class="t-v" style="font-size:70px">BUILD</div></div></div>'
     f'<div class="big cyan" style="font-size:120px" data-at="{at("h2", 5)}" data-fx="slam">&lt; 60 SAAT</div>')
card("name", L("s1"), wt("s1", 5),
     f'<div class="big white" style="font-size:170px" data-at="{at("s1", 0)}" data-fx="slam">MITYA</div>'
     f'<div class="sub gold" data-at="{at("s1", 1)}">★★★★★</div>'
     f'<span class="chip v" data-at="{at("s1", 3)}">ELECTRO · CATALYST</span>', False)
card("idle", wt("s1", 8) - 0.05, nxt("s1"),
     f'<div style="height:330px"></div><span class="chip" data-at="{at("s1", 8)}">RUPA + IDLE ANIMATION</span>'
     f'<div class="sub" data-at="{at("s1", 12)}">NAMPAK MAHAL ✦</div>', False)
card("twomode", wt("m1", 4) - 0.05, nxt("m1"),
     f'<div class="big gold" style="font-size:230px" data-at="{at("m1", 6)}" data-fx="slam">2 MODE</div>', False)
card("modes", L("m2"), nxt("m3"),
     f'<div class="bar" data-at="{at("m2", 0)}" data-fx="left"><div class="b-n v">TAP</div><div class="b-t">SUB DPS<small>OFF-FIELD · ikon kiub</small></div></div>'
     f'<div class="bar hot" data-at="{at("m3", 0)}" data-fx="right"><div class="b-n">HOLD</div><div class="b-t">MAIN DPS<small>ON-FIELD · ikon ∞ infinity</small></div></div>')
card("swap", L("m4"), nxt("m4"),
     f'<div class="sub red" data-at="{at("m4", 0)}">TERSALAH TEKAN?</div>'
     f'<div class="big cyan" style="font-size:118px" data-at="{at("m4", 2)}" data-fx="slam">TEKAN SKILL<br/>LAGI ⇄</div>'
     f'<span class="chip" data-at="{at("m4", 7)}">TERUS TUKAR MODE</span>', False)
card("stack", L("m5"), wt("m5", 9) - 0.05,
     f'<span class="chip v" data-at="{at("m5", 2)}">STELLAR-CONDUCT = +STACK</span>'
     f'<div class="pips"><div class="pip"><i data-at="{at("m5", 4)}" data-fx="fill"></i></div><div class="pip"><i data-at="{at("m5", 5)}" data-fx="fill"></i></div>'
     f'<div class="pip"><i data-at="{at("m5", 6)}" data-fx="fill"></i></div><div class="pip"><i data-at="{at("m5", 8)}" data-fx="fill"></i></div></div>'
     f'<div class="sub" data-at="{at("m5", 7)}">STACK PENUH…</div>', False)
card("meteor", wt("m5", 9) - 0.05, nxt("m5"),
     f'<div class="big gold" style="font-size:190px" data-at="{at("m5", 9)}" data-fx="slam">METEOR!</div>'
     f'<div class="big red" style="font-size:130px" data-at="{at("m5", 13)}" data-fx="slam">GILA!</div>', False)
card("burst", L("m6"), nxt("m6"),
     f'<span class="chip v" data-at="{at("m6", 0)}">ELEMENTAL BURST</span>'
     f'<div class="big cyan" style="font-size:200px" data-at="{at("m6", 5)}" data-fx="slam">+3 STACK</div>', False)
card("talent", L("b0"), nxt("b0"),
     f'<span class="chip" data-at="{at("b0", 2)}">TALENT PRIORITY</span>'
     f'<div class="bar hot" data-at="{at("b0", 4)}" data-fx="left"><div class="b-n">1</div><div class="b-t">NORMAL ATTACK</div></div>'
     f'<div class="bar" data-at="{at("b0", 9)}" data-fx="left"><div class="b-n v">2</div><div class="b-t">ELEMENTAL BURST</div></div>'
     f'<div class="bar" data-at="{at("b0", 11)}" data-fx="left"><div class="b-n v">3</div><div class="b-t">ELEMENTAL SKILL</div></div>')
card("stats", L("b1"), nxt("b1"),
     f'<span class="chip" data-at="{at("b1", 0)}">TARGET STAT</span>'
     f'<div class="row"><div class="tile hot" data-at="{at("b1", 1)}"><div class="t-k">CRIT</div><div class="t-v">70<small> / </small>200</div><div class="t-s">Rate / DMG</div></div></div>'
     f'<div class="row"><div class="tile" data-at="{at("b1", 6)}"><div class="t-k">EM</div><div class="t-v">500<small>+</small></div><div class="t-s">Elemental Mastery</div></div>'
     f'<div class="tile" data-at="{at("b1", 9)}"><div class="t-k">ER</div><div class="t-v">140<small>%</small></div><div class="t-s">Energy Recharge</div></div></div>')
card("arti", L("b2"), nxt("b2"),
     f'<span class="chip" data-at="{at("b2", 0)}">ARTIFACT</span>'
     f'<div class="bar hot" data-at="{at("b2", 2)}" data-fx="left"><div class="b-n">4PC</div><div class="b-t">DISENCHANTMENT IN DEEP SHADOW<small>pilihan utama</small></div></div>'
     f'<div class="bar" data-at="{at("b2", 6)}" data-fx="right"><div class="b-n v">ATAU</div><div class="b-t">GILDED DREAMS<small>2pc + 2pc Wanderer\'s Troupe</small></div></div>'
     f'<div class="sub" style="font-size:40px" data-at="{at("b2", 7)}">SANDS EM · GOBLET EM · CIRCLET CRIT</div>')
card("weapon", L("b3"), nxt("b3"),
     f'<span class="chip" data-at="{at("b3", 0)}">WEAPON</span>'
     f'<div class="bar hot" data-at="{at("b3", 1)}" data-fx="left"><div class="b-n">BiS</div><div class="b-t">SIGNATURE MITYA<small>paling padu</small></div></div>'
     f'<div class="bar" data-at="{at("b3", 6)}" data-fx="right"><div class="b-n v">5★</div><div class="b-t">KAGURA\'S VERITY</div></div>'
     f'<div class="bar" data-at="{at("b3", 9)}" data-fx="right"><div class="b-n v">F2P</div><div class="b-t">THE WIDSITH</div></div>')
def slot(cls, ic, n, r, a): return (f'<div class="slot" data-at="{a}"><div class="s-ic {cls}">{ic}</div><div class="s-n">{n}</div>'
                                    f'<div class="s-r">{r}</div></div>')
card("team", L("t1"), nxt("t1"),
     f'<span class="chip" data-at="{at("t1", 0)}">TEAM STELLAR-CONDUCT</span><div class="row">'
     + slot("el-electro", "⚡", "MITYA", "DPS", at("t1", 0)) + slot("el-cryo", "❄", "CRYO", "trigger", at("t1", 3))
     + slot("el-anemo", "🜁", "SUCROSE", "EM buff", at("t1", 6)) + slot("el-flex", "+", "FLEX", "Cryo / healer", at("t1", 6, 0.2)) + '</div>'
     f'<div class="sub" style="font-size:42px" data-at="{at("t1", 4)}">ELECTRO + CRYO = STELLAR-CONDUCT</div>')
card("tsar", L("z1"), nxt("z1"),
     f'<span class="chip v" data-at="{at("z1", 0)}">TEKAAN AKU · VERSION AKAN DATANG</span><div style="height:150px"></div>'
     f'<div class="big white" style="font-size:112px" data-at="{at("z1", 3)}" data-fx="slam">MITYA <span class="gold">×</span></div>'
     f'<div class="big cyan" style="font-size:150px" data-at="{at("z1", 10)}" data-fx="slam">TSARITSA?</div>', False)
card("end", L("e1"), TOTAL,
     f'<div class="big gold" style="font-size:120px" data-at="{at("e1", 0)}" data-fx="slam">SIMPAN PRIMO!</div>'
     f'<div id="follow-btn" data-at="{at("e1", 3)}" data-pulse="1">FOLLOW FOR MORE</div>')
dims = []
for cid, s, e, inner, dim in CARDS:
    P.append(f'      <div id="card-{cid}" class="clip card" data-start="{f(s)}" data-duration="{f(e - s)}" data-track-index="7">'
             f'<div class="card-in">{inner}</div></div>')
    if dim: dims.append(f'      <div id="dim-{cid}" class="clip dim" data-start="{f(s)}" data-duration="{f(e - s)}" data-track-index="3"></div>')
card_html = "\n".join(P); P.clear(); dim_html = "\n".join(dims)

# ---- captions (1-2 perkataan, pop; keyword emas) ---------------------------------------------------
GOLD = {"mitya", "pull", "build", "electro", "mahal", "mode", "tap", "hold", "sub", "main", "dps", "off-field", "on-field", "tukar",
        "stellar", "conduct", "stack", "meteor", "gila", "burst", "tiga", "talent", "normal", "attack", "skill", "crit", "em", "er",
        "artifact", "deep", "shadow", "gilded", "dreams", "weapon", "signature", "kagura's", "verity", "widsith", "team", "cryo",
        "sucrose", "tsaritsa", "primo", "follow", "five", "star", "dua", "enam", "puluh", "second"}
NUM = {("b1", 2): "70", ("b1", 3): None, ("b1", 4): "200", ("b1", 5): None, ("b1", 7): "500", ("b1", 8): None,
       ("b1", 10): "140%", ("b1", 11): None, ("b1", 12): None, ("h2", 6): "60", ("h2", 7): None,
       ("b2", 4): "4", ("m6", 5): "3", ("m1", 6): "2", ("s1", 1): "5"}
caps = []
for l in lines:
    if l["id"] == "h1": continue                      # hook text bawa line ni
    W = []
    for j, w in enumerate(VO[l["id"]]["words"]):
        if (l["id"], j) in NUM:
            if NUM[(l["id"], j)] is None: W[-1][2] = w[2]; continue
            W.append([NUM[(l["id"], j)], w[1], w[2]]); continue
        W.append(list(w))
    groups, cur = [], []
    for j, w in enumerate(W):
        cur.append(w); n = W[j + 1] if j + 1 < len(W) else None
        txt = " ".join(x[0] for x in cur)
        brk = len(cur) >= 2 or len(txt) >= 10 or n is None or (n[1] - w[2] > 0.1)
        if n and len(cur) == 1 and len(w[0]) <= 3 and (n[1] - w[2] <= 0.1) and len(n[0]) <= 8: brk = False
        if brk: groups.append(cur); cur = []
    for g in groups:
        caps.append({"words": [x[0] for x in g], "start": round(l["start"] + g[0][1], 3), "end": round(l["start"] + g[-1][2], 3),
                     "line_end": l["start"] + l["dur"]})
for a, b in zip(caps, caps[1:]):
    a["end"] = round(min(max(a["end"], a["start"] + 0.3), b["start"], a["line_end"] + 0.08), 3)
caps[-1]["end"] = round(caps[-1]["end"] + 0.3, 3)
for i, c in enumerate(caps):
    spans = "".join(f'<span class="w{" g" if w.lower().strip("%") in GOLD or w[0].isdigit() else ""}">{E(w)}</span>' for w in c["words"])
    P.append(f'        <div id="cap-{i}" class="clip cap" data-start="{f(c["start"])}" data-duration="{f(c["end"] - c["start"])}">'
             f'<div class="cap-in">{spans}</div></div>')
cap_html = "\n".join(P); P.clear()

# ---- SFX -------------------------------------------------------------------------------------------
SFX_DUR = {"impact-bass-1": 2.12, "impact-bass-2": 2.59, "whoosh": 0.57, "whoosh-short": 0.57, "pop": 0.72, "glitch-1": 2.64,
           "ping": 1.32, "riser": 10.03, "sparkle": 1.8, "chime": 2.5, "notification": 2.46}
SFX = [("impact-bass-1", 0.0, 0.5), ("impact-bass-2", wt("h1", 2) - 0.3, 0.45), ("whoosh", L("h2") - 0.1, 0.35),
       ("pop", wt("h2", 0), 0.4), ("pop", wt("h2", 3), 0.4), ("ping", wt("h2", 5), 0.35),
       ("whoosh-short", L("s1") - 0.08, 0.35), ("sparkle", wt("s1", 1), 0.35), ("whoosh-short", wt("s1", 5) - 0.1, 0.3),
       ("chime", wt("s1", 12), 0.25),
       ("whoosh", L("m1") - 0.1, 0.35), ("impact-bass-2", wt("m1", 6) - 0.3, 0.45),
       ("pop", wt("m2", 0), 0.45), ("whoosh-short", L("m3") - 0.1, 0.3), ("pop", wt("m3", 0), 0.45),
       ("glitch-1", L("m4"), 0.28), ("whoosh", wt("m4", 2) - 0.1, 0.35), ("ping", wt("m4", 7), 0.3),
       ("whoosh-short", L("m5") - 0.08, 0.3), ("pop", wt("m5", 4), 0.35), ("pop", wt("m5", 5), 0.38), ("pop", wt("m5", 6), 0.41),
       ("pop", wt("m5", 8), 0.45), ("riser", wt("m5", 9) - 10.03, 0.28), ("impact-bass-1", wt("m5", 9) - 0.05, 0.6),
       ("pop", wt("m5", 13), 0.5),
       ("whoosh", L("m6") - 0.1, 0.35), ("impact-bass-2", wt("m6", 5) - 0.3, 0.45), ("sparkle", wt("m6", 5), 0.35),
       ("whoosh", L("b0") - 0.1, 0.4), ("pop", wt("b0", 4), 0.4), ("pop", wt("b0", 9), 0.4), ("pop", wt("b0", 11), 0.4),
       ("whoosh-short", L("b1") - 0.08, 0.3), ("ping", wt("b1", 1), 0.3), ("pop", wt("b1", 6), 0.4), ("pop", wt("b1", 9), 0.4),
       ("whoosh-short", L("b2") - 0.08, 0.3), ("pop", wt("b2", 2), 0.4), ("pop", wt("b2", 6), 0.4),
       ("whoosh-short", L("b3") - 0.08, 0.3), ("sparkle", wt("b3", 1), 0.3), ("pop", wt("b3", 6), 0.4), ("pop", wt("b3", 9), 0.4),
       ("whoosh", L("t1") - 0.1, 0.35), ("pop", wt("t1", 3), 0.4), ("pop", wt("t1", 6), 0.4),
       ("whoosh", L("z1") - 0.1, 0.4), ("chime", L("z1"), 0.3), ("impact-bass-1", wt("z1", 10) - 0.05, 0.55),
       ("whoosh-short", L("e1") - 0.08, 0.3), ("pop", wt("e1", 0), 0.45), ("notification", wt("e1", 3), 0.35)]
for i, (name, s, vol) in enumerate(SFX):
    s = max(0.0, s)
    P.append(f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.mp3" data-start="{f(s)}" '
             f'data-duration="{f(min(SFX_DUR[name], TOTAL - s))}" data-volume="{vol}" data-track-index="12"></audio>')
sfx_html = "\n".join(P); P.clear()

standin = ('      <div id="standin">STAND-IN · GANTI DGN TALKING HEAD KAU</div>' if PREVIEW else "")
T = {"total": TOTAL, "lines": [{"id": l["id"], "start": l["start"]} for l in lines], "shots": shots,
     "punch": [wt("m5", 13), wt("z1", 10)], "flash": [[wt("m5", 9), 0.85], [wt("z1", 10), 0.5], [wt("h1", 2), 0.5]]}
page = open(os.path.join(ROOT, "build", "template.html")).read()
for k, v in {"{{TOTAL}}": f(TOTAL), "{{FACE}}": face_html, "{{SHOTS}}": shot_html, "{{DIMS}}": dim_html, "{{STANDIN}}": standin,
             "{{SECTIONS}}": sec_html, "{{CARDS}}": card_html, "{{CAPTIONS}}": cap_html, "{{VO}}": vo_html, "{{SFX}}": sfx_html,
             "{{TIMELINE_JSON}}": json.dumps(T)}.items():
    page = page.replace(k, v)
open(os.path.join(ROOT, "index.html"), "w").write(page)
print("total", TOTAL, "shots", len(shots), "captions", len(caps), "cards", len(CARDS))
for l in lines: print(f'  {l["start"]:6.2f} {l["id"]:3s} {l["dur"]:.2f}  ' + " ".join(w[0] for w in VO[l["id"]]["words"]))
