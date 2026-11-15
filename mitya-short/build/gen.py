"""Mitya guide short (1080x1920, 60 fps, < 60 s): muka atas / gameplay bawah, gaya AbamKamil.
Narration = talking head sebenar (assets/th/<line>.mp4, dari build/th_build.py).
Run dari root projek:  python3 build/gen.py  -> index.html"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO = json.load(open(os.path.join(ROOT, "build", "th_words.json")))
SHOTS = {s[0]: s for s in json.load(open(os.path.join(ROOT, "assets", "clips", "shots.json")))}
GAP, START, END_HOLD = 0.05, 0.08, 1.1

def K(line, key, n=0):
    """index perkataan ke-n dalam line yang bermula dengan key"""
    hits = [i for i, w in enumerate(VO[line]["words"]) if w[0].lower().strip("?,.!").startswith(key.lower())]
    return hits[n]

# line -> [(shot, from word, to word)]   ("end" = sampai line seterusnya)
SEQ = [
    ("h1", [("TA", 0, "end")]),
    ("s1", [("S1", 0, K("s1", "tengok")), ("S2", K("s1", "tengok"), "end")]),
    ("m1", [("M1", 0, "end")]), ("m2", [("M2", 0, "end")]), ("m3", [("M3", 0, "end")]), ("m4", [("M4", 0, "end")]),
    ("m5", [("M5", 0, K("m5", "bila")), ("M5b", K("m5", "bila"), K("m5", "damage")), ("M5c", K("m5", "damage"), "end")]),
    ("m6", [("M6", 0, "end")]),
    ("b1", [("B1", 0, "end")]), ("b2", [("B2", 0, "end")]), ("b3", [("B3", 0, "end")]),
    ("t1", [("T1", 0, "end")]), ("z1", [("Z", 0, "end")]), ("e1", [("E", 0, "end")]),
]
SLAM = {"TA", "M5b", "M6", "Z"}

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
LIFT = {"M1": 0.1, "M6": 0.06, "B1": 0.04}
TAME = {"M4": -0.34, "S1": -0.12, "Z": -0.2, "M5": -0.2, "M5c": -0.24, "T1": -0.2, "E": -0.1}
def g_game(sid):
    adj = {"exposure": round(0.02 + LIFT.get(sid, 0) - (0.05 if sid in TAME else 0), 3), "contrast": 0.14,
           "highlights": TAME.get(sid, -0.14), "shadows": 0.1 + (0.08 if sid in LIFT else 0), "blacks": -0.06,
           "vibrance": 0.24, "saturation": 0.04, "temperature": -0.02, "tint": 0.03}
    return {"preset": "deep-contrast", "intensity": 0.5, "adjust": adj, "details": {"vignette": 0.24}, "effects": {"bloom": 0.18}}
# talking head: rakaman flat + cast hijau-kuning dari dinding + dinding terlalu terang
#  -> tambah kontras & hitam, tarik highlight dinding, magenta sikit lawan hijau, warm sikit untuk kulit, vignette
G_FACE = {"preset": "deep-contrast", "intensity": 0.35,
          "adjust": {"exposure": 0.14, "contrast": 0.16, "highlights": -0.45, "whites": -0.1, "shadows": 0.18, "blacks": -0.12,
                     "temperature": 0.08, "tint": 0.06, "vibrance": 0.3, "saturation": 0.06}, "details": {"vignette": 0.3}}
def attr(g): return html.escape(json.dumps(g, separators=(",", ":")), quote=True)
def f(x): return f"{x:.3f}".rstrip("0").rstrip(".")
def E(s): return html.escape(s)

P = []
for i, l in enumerate(lines):
    end = TOTAL if i == len(lines) - 1 else lines[i + 1]["start"]
    P.append(f'        <video id="face-{l["id"]}" class="clip face" src="assets/th/{l["id"]}.mp4" data-start="{f(l["start"])}" '
             f'data-duration="{f(end - l["start"])}" data-track-index="1" data-has-audio="true" data-volume="1" playsinline '
             f'style="z-index:{i + 1}" data-color-grading="{attr(G_FACE)}"></video>')
face_html = "\n".join(P); P.clear()
P = []
for o in shots:
    P.append(f'        <div class="shotwrap" id="w-{o["idx"]}" style="z-index:{20 + o["idx"]}">'
             f'<video id="v-{o["idx"]}-{o["sid"]}" class="clip shot" src="assets/clips/{o["sid"]}.mp4" data-start="{f(o["start"])}" '
             f'data-duration="{f(o["end"] - o["start"])}" data-track-index="2" muted playsinline '
             f'data-color-grading="{attr(g_game(o["sid"]))}"></video></div>')
shot_html = "\n".join(P); P.clear()

vo_html = ""

# ---- sections ------------------------------------------------------------------------------
SECTIONS = [("s1", "01", "SHOWCASE"), ("m1", "02", "CARA MAIN"), ("b1", "03", "BUILD"), ("t1", "04", "TEAM COMP"),
            ("z1", "05", "TEAM MASA DEPAN")]
for i, (line, num, label) in enumerate(SECTIONS):
    s = EV[line]["start"] - 0.03
    e = (EV[SECTIONS[i + 1][0]]["start"] - 0.03) if i + 1 < len(SECTIONS) else EV["e1"]["start"] - 0.03
    P.append(f'      <div id="sec-{num}" class="clip sec" data-start="{f(s)}" data-duration="{f(e - s)}" data-track-index="5">'
             f'<div class="sec-in"><span class="sec-num">#{num}</span><span class="sec-label">{label}</span></div></div>')
sec_html = "\n".join(P); P.clear()

# ---- cards (motion graphics dalam panel game) --------------------------------------------------
def at(line, key, n=0, off=-0.05):
    idx = key if isinstance(key, int) else K(line, key, n)
    return f(max(EV[line]["start"], wt(line, idx) + off))
def T_(line, key, n=0): return wt(line, K(line, key, n))
CARDS = []   # (id, start, end, inner html, dim?)
def card(cid, s, e, inner, dim=True): CARDS.append((cid, round(s, 3), round(e, 3), inner, dim))
L = lambda x: EV[x]["start"]
card("hook", 0.0, nxt("h1"),
     f'<span class="chip" data-at="0">GUIDE &lt; 60 SAAT</span>'
     f'<div class="big white" style="font-size:96px" data-at="0">JANGAN PULL</div>'
     f'<div class="big gold" style="font-size:210px" data-at="0" data-fx="slam">MITYA</div>'
     f'<div class="sub" data-at="0">SEBELUM TENGOK NI!</div>', False)
card("name", L("s1"), T_("s1", "tengok"),
     f'<div class="big white" style="font-size:170px" data-at="{at("s1", 0)}" data-fx="slam">MITYA</div>'
     f'<div class="sub gold" data-at="{at("s1", "5")}">★★★★★</div>'
     f'<span class="chip v" data-at="{at("s1", "electro")}">ELECTRO · CATALYST</span>', False)
card("idle", T_("s1", "tengok"), nxt("s1"),
     f'<div style="height:330px"></div><span class="chip" data-at="{at("s1", "rupa")}">RUPA + IDLE ANIMATION</span>'
     f'<div class="sub" data-at="{at("s1", "mahal")}">NAMPAK MAHAL ✦</div>', False)
card("twomode", T_("m1", "ada") - 0.05, nxt("m1"),
     f'<div class="big gold" style="font-size:230px" data-at="{at("m1", "2")}" data-fx="slam">2 MODE</div>', False)
card("modes", L("m2"), nxt("m3"),
     f'<div class="bar" data-at="{at("m2", "tap")}" data-fx="left"><div class="b-n v">TAP</div><div class="b-t">SUB DPS<small>OFF-FIELD · ikon kiub</small></div></div>'
     f'<div class="bar hot" data-at="{at("m3", "hold")}" data-fx="right"><div class="b-n">HOLD</div><div class="b-t">MAIN DPS<small>ON-FIELD · ikon ∞ infinity</small></div></div>')
card("swap", L("m4"), nxt("m4"),
     f'<div class="sub red" data-at="{at("m4", "salah")}">SALAH TEKAN?</div>'
     f'<div class="big cyan" style="font-size:118px" data-at="{at("m4", "tekan", 1)}" data-fx="slam">TEKAN SKILL<br/>LAGI ⇄</div>'
     f'<span class="chip" data-at="{at("m4", "terus")}">TERUS TUKAR MODE</span>', False)
card("stack", L("m5"), T_("m5", "meteor") - 0.05,
     f'<span class="chip v" data-at="{at("m5", "stellar")}">STELLAR-CONDUCT = +STACK</span>'
     f'<div class="pips"><div class="pip"><i data-at="{at("m5", "untuk")}" data-fx="fill"></i></div><div class="pip"><i data-at="{at("m5", "kumpul")}" data-fx="fill"></i></div>'
     f'<div class="pip"><i data-at="{at("m5", "stack")}" data-fx="fill"></i></div><div class="pip"><i data-at="{at("m5", "penuh")}" data-fx="fill"></i></div></div>'
     f'<div class="sub" data-at="{at("m5", "bila")}">STACK PENUH…</div>', False)
card("meteor", T_("m5", "meteor") - 0.05, nxt("m5"),
     f'<div class="big gold" style="font-size:190px" data-at="{at("m5", "meteor")}" data-fx="slam">METEOR!</div>'
     f'<div class="big red" style="font-size:130px" data-at="{at("m5", "gila")}" data-fx="slam">GILA!</div>', False)
card("burst", L("m6"), nxt("m6"),
     f'<span class="chip v" data-at="{at("m6", "burst")}">ELEMENTAL BURST</span>'
     f'<div class="big cyan" style="font-size:200px" data-at="{at("m6", "3")}" data-fx="slam">+3 STACK</div>', False)
card("stats", L("b1"), nxt("b1"),
     f'<span class="chip" data-at="{at("b1", 0)}">TARGET STAT</span>'
     f'<div class="row"><div class="tile hot" data-at="{at("b1", "crit")}"><div class="t-k">CRIT</div><div class="t-v">70<small> / </small>200</div><div class="t-s">Rate / DMG</div></div></div>'
     f'<div class="row"><div class="tile" data-at="{at("b1", "em")}"><div class="t-k">EM</div><div class="t-v">500<small>+</small></div><div class="t-s">Elemental Mastery</div></div>'
     f'<div class="tile" data-at="{at("b1", "er")}"><div class="t-k">ER</div><div class="t-v">140<small>%</small></div><div class="t-s">Energy Recharge</div></div></div>')
card("arti", L("b2"), nxt("b2"),
     f'<span class="chip" data-at="{at("b2", 0)}">ARTIFACT</span>'
     f'<div class="bar hot" data-at="{at("b2", "deep")}" data-fx="left"><div class="b-ic"><img src="assets/img/deep-shadow.png" alt=""/></div><div class="b-t">DISENCHANTMENT IN DEEP SHADOW<small>4 PIECE · pilihan utama</small></div></div>'
     f'<div class="bar" data-at="{at("b2", "ataupun")}" data-fx="right"><div class="b-ic"><img src="assets/img/gilded-dreams.png" alt=""/></div><div class="b-t">GILDED DREAMS<small>ATAU · fokus EM</small></div></div>'
     f'<div class="sub" style="font-size:40px" data-at="{at("b2", "ataupun", 0, 0.25)}">SANDS EM · GOBLET EM · CIRCLET CRIT</div>')
card("weapon", L("b3"), nxt("b3"),
     f'<span class="chip" data-at="{at("b3", 0)}">WEAPON</span>'
     f'<div class="bar hot" data-at="{at("b3", "signature")}" data-fx="left"><div class="b-ic"><img src="assets/img/starsealed.png" alt=""/></div><div class="b-t">STARSEALED EDICT<small>SIGNATURE · paling padu</small></div></div>'
     f'<div class="bar" data-at="{at("b3", "kagura")}" data-fx="right"><div class="b-ic"><img src="assets/img/kagura.png" alt=""/></div><div class="b-t">KAGURA\'S VERITY<small>5★ alternatif</small></div></div>'
     f'<div class="bar" data-at="{at("b3", "widsith")}" data-fx="right"><div class="b-ic"><img src="assets/img/widsith.png" alt=""/></div><div class="b-t">THE WIDSITH<small>F2P · 4★</small></div></div>')
def av(n): return f'<img class="s-av" src="assets/img/{n}.png" alt=""/>'
card("team", L("t1"), nxt("t1"),
     f'<span class="chip" data-at="{at("t1", 0)}">TEAM STELLAR-CONDUCT</span><div class="row team">'
     f'<div class="slot" data-at="{at("t1", 0)}">{av("mitya")}<div class="s-n">MITYA</div><div class="s-r">Electro · DPS</div></div>'
     f'<div class="slot two" data-at="{at("t1", "unit")}"><div class="duo">{av("odette")}<span class="or">/</span>{av("qiqi")}</div>'
     f'<div class="s-n">ODETTE <small>atau</small> QIQI</div><div class="s-r">Cryo · Qiqi = F2P</div></div>'
     f'<div class="slot" data-at="{at("t1", "sucrose")}">{av("sucrose")}<div class="s-n">SUCROSE</div><div class="s-r">Anemo · EM buff</div></div></div>'
     f'<div class="sub" style="font-size:42px" data-at="{at("t1", "cryo")}">ELECTRO + CRYO = STELLAR-CONDUCT</div>')
card("tsar", L("z1"), nxt("z1"),
     f'<span class="chip v" data-at="{at("z1", 0)}">TEKAAN AKU · VERSION AKAN DATANG</span><div style="height:150px"></div>'
     f'<div class="big white" style="font-size:112px" data-at="{at("z1", "mitya")}" data-fx="slam">MITYA <span class="gold">×</span></div>'
     f'<div class="big cyan" style="font-size:150px" data-at="{at("z1", "tsaritsa")}" data-fx="slam">TSARITSA?</div>', False)
card("end", L("e1"), TOTAL,
     f'<div class="big gold" style="font-size:120px" data-at="{at("e1", "simpan")}" data-fx="slam">SIMPAN PRIMO!</div>'
     f'<div id="follow-btn" data-at="{at("e1", "follow")}" data-pulse="1">FOLLOW FOR MORE</div>')
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
        "sucrose", "tsaritsa", "primo", "follow", "star", "idle", "stat", "besar"}
caps = []
for l in lines:
    if l["id"] == "h1": continue                      # hook text bawa line ni
    W = [list(w) for w in VO[l["id"]]["words"]]
    if l["id"] == "b1": W[-1][0] = "140%"
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
    spans = "".join(f'<span class="w{" g" if w.lower().strip("%?") in GOLD or w[0].isdigit() else ""}">{E(w)}</span>' for w in c["words"])
    P.append(f'        <div id="cap-{i}" class="clip cap" data-start="{f(c["start"])}" data-duration="{f(c["end"] - c["start"])}">'
             f'<div class="cap-in">{spans}</div></div>')
cap_html = "\n".join(P); P.clear()

# ---- SFX -------------------------------------------------------------------------------------------
SFX_DUR = {"impact-bass-1": 2.12, "impact-bass-2": 2.59, "whoosh": 0.57, "whoosh-short": 0.57, "pop": 0.72, "glitch-1": 2.64,
           "ping": 1.32, "riser": 10.03, "sparkle": 1.8, "chime": 2.5, "notification": 2.46}
SFX = [("impact-bass-1", 0.0, 0.5), ("impact-bass-2", T_("h1", "mitya") - 0.3, 0.4),
       ("whoosh", L("s1") - 0.1, 0.35), ("sparkle", T_("s1", "5"), 0.3), ("whoosh-short", T_("s1", "tengok") - 0.1, 0.3),
       ("chime", T_("s1", "mahal"), 0.22),
       ("whoosh", L("m1") - 0.1, 0.35), ("impact-bass-2", T_("m1", "2") - 0.3, 0.4),
       ("pop", T_("m2", "tap"), 0.4), ("whoosh-short", L("m3") - 0.1, 0.28), ("pop", T_("m3", "hold"), 0.4),
       ("glitch-1", L("m4"), 0.24), ("whoosh", T_("m4", "tekan", 1) - 0.1, 0.32), ("ping", T_("m4", "terus"), 0.28),
       ("whoosh-short", L("m5") - 0.08, 0.28), ("pop", T_("m5", "untuk"), 0.32), ("pop", T_("m5", "kumpul"), 0.35),
       ("pop", T_("m5", "stack"), 0.38), ("pop", T_("m5", "penuh"), 0.42), ("riser", T_("m5", "meteor") - 10.03, 0.24),
       ("impact-bass-1", T_("m5", "meteor") - 0.05, 0.55), ("pop", T_("m5", "gila"), 0.45),
       ("whoosh", L("m6") - 0.1, 0.32), ("impact-bass-2", T_("m6", "3") - 0.3, 0.4), ("sparkle", T_("m6", "3"), 0.3),
       ("whoosh", L("b1") - 0.1, 0.36), ("ping", T_("b1", "crit"), 0.28), ("pop", T_("b1", "em"), 0.38), ("pop", T_("b1", "er"), 0.38),
       ("whoosh-short", L("b2") - 0.08, 0.28), ("pop", T_("b2", "deep"), 0.38), ("pop", T_("b2", "ataupun"), 0.38),
       ("whoosh-short", L("b3") - 0.08, 0.28), ("sparkle", T_("b3", "signature"), 0.26), ("pop", T_("b3", "kagura"), 0.38),
       ("pop", T_("b3", "widsith"), 0.38),
       ("whoosh", L("t1") - 0.1, 0.32), ("pop", T_("t1", "unit"), 0.38), ("pop", T_("t1", "sucrose"), 0.38),
       ("whoosh", L("z1") - 0.1, 0.36), ("chime", L("z1"), 0.26), ("impact-bass-1", T_("z1", "tsaritsa") - 0.05, 0.5),
       ("whoosh-short", L("e1") - 0.08, 0.28), ("pop", T_("e1", "simpan"), 0.4), ("notification", T_("e1", "follow"), 0.32)]
for i, (name, s, vol) in enumerate(SFX):
    s = max(0.0, s)
    P.append(f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.mp3" data-start="{f(s)}" '
             f'data-duration="{f(min(SFX_DUR[name], TOTAL - s))}" data-volume="{vol}" data-track-index="12"></audio>')
sfx_html = "\n".join(P); P.clear()

T = {"total": TOTAL, "lines": [{"id": l["id"], "start": l["start"], "cuts": VO[l["id"]]["cuts"]} for l in lines], "shots": shots,
     "punch": [T_("m5", "gila"), T_("z1", "tsaritsa")],
     "flash": [[T_("m5", "meteor"), 0.85], [T_("z1", "tsaritsa"), 0.5], [T_("h1", "mitya"), 0.45]]}
page = open(os.path.join(ROOT, "build", "template.html")).read()
for k, v in {"{{TOTAL}}": f(TOTAL), "{{FACE}}": face_html, "{{SHOTS}}": shot_html, "{{DIMS}}": dim_html, "{{STANDIN}}": "",
             "{{SECTIONS}}": sec_html, "{{CARDS}}": card_html, "{{CAPTIONS}}": cap_html, "{{VO}}": vo_html, "{{SFX}}": sfx_html,
             "{{TIMELINE_JSON}}": json.dumps(T)}.items():
    page = page.replace(k, v)
open(os.path.join(ROOT, "index.html"), "w").write(page)
print("total", TOTAL, "shots", len(shots), "captions", len(caps), "cards", len(CARDS))
for l in lines: print(f'  {l["start"]:6.2f} {l["id"]:3s} {l["dur"]:.2f}  ' + " ".join(w[0] for w in VO[l["id"]]["words"]))
