"""Anastasya (Cryo Archon) short — 1080x1920, 60 fps, < 60 s. Gaya: muka penuh <-> B-roll penuh, caption pop.
MODE "tts": VO sementara (assets/voice) + stand-in muka bisu.  MODE "th": talking head sebenar (assets/th/<line>.mp4).
Run dari root projek:  python3 build/gen.py  -> index.html"""
import html, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODE = "th" if os.path.exists(os.path.join(ROOT, "build", "th_words.json")) else "tts"
VO = json.load(open(os.path.join(ROOT, "build", "th_words.json" if MODE == "th" else "vo_words_tight.json")))
SHOTS = {s[0]: s for s in json.load(open(os.path.join(ROOT, "assets", "clips", "shots.json")))}
GAP, START, END_HOLD, BGM_VOL = 0.05, 0.08, 1.0, 0.3
DLG = {"I1", "R1", "R1b", "R2", "Q1", "Q2", "T1", "T2"}       # shot dialog: ada subtitle game -> shade tinggi
SLAM = {"A", "Q2", "S2", "P2", "Q3"}

def K(line, key, n=0):
    return [i for i, w in enumerate(VO[line]["words"]) if w[0].lower().strip("?,.!").startswith(key.lower())][n]
# ("vo", line, [(shot, from, to)])  from/to: indeks perkataan atau "end" · ("sync", shot) = petikan suara game
SEQ = [
    ("vo", "h1", [("A", K("h1", "salah"), "end")]),
    ("vo", "i1", [("I1", K("i1", "anastasya"), "end")]),
    ("vo", "r1", [("R1b", 0, K("r1", "dia")), ("R1", K("r1", "dia"), "end")]),
    ("sync", "Q1"),
    ("vo", "l1", [("L1", K("l1", "kuasa"), "end")]),
    ("vo", "s1", [("S1", 0, K("s1", "dia", 1)), ("S2", K("s1", "dia", 1), K("s1", "dan")), ("S3", K("s1", "dan"), "end")]),
    ("vo", "s2", [("S4", 0, "end")]),
    ("sync", "Q3"),
    ("vo", "t1", [("T1", 0, "end")]),
    ("sync", "Q2"),
    ("vo", "t2", []),
    ("vo", "p1", [("P1", 0, K("p1", "archon")), ("P2", K("p1", "archon"), "end")]),
    ("vo", "p2", []),
    ("vo", "e1", [("E", 0, K("e1", "follow"))]),
]
t = START; ev = []
for e in SEQ:
    d = VO[e[1]]["dur"] if e[0] == "vo" else SHOTS[e[1]][2]
    ev.append({"kind": e[0], "id": e[1], "start": round(t, 3), "dur": d, "ovl": e[2] if e[0] == "vo" else []}); t += d + GAP
TOTAL = round(t - GAP + END_HOLD, 2)
assert TOTAL < 60, TOTAL
EV = {e["id"]: e for e in ev}
def wt(line, idx):
    e = EV[line]
    return round(e["start"] + (e["dur"] if idx == "end" else VO[line]["words"][idx][1]), 3)
def T_(line, key, n=0): return wt(line, key if isinstance(key, int) else K(line, key, n))
def nxt(i): return ev[i + 1]["start"] if i + 1 < len(ev) else TOTAL
def NX(line): return nxt([e["id"] for e in ev].index(line))
L = lambda x: EV[x]["start"]

shots = []
for i, e in enumerate(ev):
    if e["kind"] == "sync":
        shots.append({"sid": e["id"], "start": e["start"], "end": round(nxt(i), 3), "sync": True}); continue
    for sid, a, b in e["ovl"]:
        s0 = 0.0 if (i == 0 and a == 0) else (e["start"] if a == 0 else wt(e["id"], a))
        s1 = nxt(i) if b == "end" else wt(e["id"], b)
        if s1 - s0 > SHOTS[sid][2] + 0.02: print("SHOT TOO SHORT", sid, round(s1 - s0, 2), SHOTS[sid][2])
        shots.append({"sid": sid, "start": round(s0, 3), "end": round(s1, 3)})
for i, o in enumerate(shots): o["idx"] = i; o["slam"] = o["sid"] in SLAM

# ---- grades ---------------------------------------------------------------------------------
TAME = {"S4": -0.34, "Q3": -0.3, "A": -0.4, "L1": -0.42, "S1": -0.3, "S2": -0.36, "S3": -0.3, "P1": -0.32, "P2": -0.2, "Q1": -0.2, "I1": -0.12}
LIFT = {"T1": 0.14, "R1": 0.08, "R2": 0.08, "E": 0.1, "T2": 0.04}
def g_game(sid):
    adj = {"exposure": round(0.02 + LIFT.get(sid, 0) - (0.07 if sid in TAME else 0), 3), "contrast": 0.14,
           "highlights": TAME.get(sid, -0.14), "whites": -0.1 if sid in TAME else 0.0, "shadows": 0.1 + (0.08 if sid in LIFT else 0),
           "blacks": -0.06, "vibrance": 0.26, "saturation": 0.04, "temperature": -0.05, "tint": 0.02}
    return {"preset": "deep-contrast", "intensity": 0.5, "adjust": adj, "details": {"vignette": 0.28}, "effects": {"bloom": 0.22}}
# talking head (rakaman kali ni dah terang & seimbang): kontras ringan, tarik highlight dinding, warm sikit, vignette
G_FACE = {"preset": "deep-contrast", "intensity": 0.3,
          "adjust": {"exposure": 0.03, "contrast": 0.12, "highlights": -0.32, "whites": -0.06, "shadows": 0.08, "blacks": -0.08,
                     "temperature": 0.03, "tint": 0.02, "vibrance": 0.2, "saturation": 0.03}, "details": {"vignette": 0.28}}
def attr(g): return html.escape(json.dumps(g, separators=(",", ":")), quote=True)
def f(x): return f"{x:.3f}".rstrip("0").rstrip(".")
E = html.escape
P = []
# ---- faces / VO --------------------------------------------------------------------------------
vo_html = ""
if MODE == "tts":
    P.append(f'        <video id="face" class="clip face" src="assets/th/standin.mp4" data-start="0" data-duration="{f(TOTAL)}" '
             f'data-track-index="1" muted playsinline data-color-grading="{attr(G_FACE)}"></video>')
    face_html = "\n".join(P); P.clear()
    for e in ev:
        if e["kind"] == "vo":
            P.append(f'      <audio id="vo-{e["id"]}" class="clip" src="assets/voice/{e["id"]}.wav" data-start="{f(e["start"])}" '
                     f'data-duration="{f(e["dur"])}" data-volume="1" data-track-index="10"></audio>')
    vo_html = "\n".join(P); P.clear()
else:
    vos = [(i, e) for i, e in enumerate(ev) if e["kind"] == "vo"]
    for k, (i, e) in enumerate(vos):
        end = vos[k + 1][1]["start"] if k + 1 < len(vos) else TOTAL
        P.append(f'        <video id="face-{e["id"]}" class="clip face" src="assets/th/{e["id"]}.mp4" data-start="{f(e["start"])}" '
                 f'data-duration="{f(end - e["start"])}" data-track-index="1" data-has-audio="true" data-volume="1" playsinline '
                 f'style="z-index:{k + 1}" data-color-grading="{attr(G_FACE)}"></video>')
    face_html = "\n".join(P); P.clear()
shade = []
for o in shots:
    aud = 'data-has-audio="true" data-volume="1.25"' if o.get("sync") else "muted"
    d = o["end"] - o["start"]
    P.append(f'      <div class="shotwrap{" dlg" if o["sid"] in DLG else ""}" id="w-{o["idx"]}" style="z-index:{20 + o["idx"]}"><video id="v-{o["idx"]}-{o["sid"]}" class="clip shot" '
             f'src="assets/clips/{o["sid"]}.mp4" data-start="{f(o["start"])}" data-duration="{f(d)}" data-track-index="2" {aud} playsinline '
             f'data-color-grading="{attr(g_game(o["sid"]))}"></video></div>')
    if o["sid"] in DLG:
        shade.append(f'      <div id="sh-{o["idx"]}" class="clip shade-dlg" data-start="{f(o["start"])}" data-duration="{f(d)}" data-track-index="3"></div>')
shot_html = "\n".join(P); P.clear(); shade_html = "\n".join(shade)

# ---- snow ----------------------------------------------------------------------------------------
SNOW = [(60, 8, 7.2, 0.0, 40), (190, 12, 9.0, 3.1, -30), (310, 6, 6.4, 1.2, 25), (430, 10, 8.3, 5.4, -45), (560, 7, 7.7, 2.6, 30),
        (680, 13, 9.6, 6.8, -20), (800, 8, 6.9, 0.9, 35), (930, 11, 8.8, 4.4, -35), (1010, 6, 7.4, 3.7, 20), (120, 9, 10.2, 7.9, 30),
        (500, 5, 6.1, 4.9, -25), (880, 7, 9.9, 8.6, 40)]
snow_html = "\n".join(f'      <div class="snow" style="left:{x}px;width:{s}px;height:{s}px;opacity:{0.5 + (s % 5) / 12:.2f}" '
                      f'data-d="{d}" data-o="{o}" data-sway="{sw}"></div>' for x, s, d, o, sw in SNOW)

# ---- cards -------------------------------------------------------------------------------------------
def at(line, key, n=0, off=-0.05): return f(max(EV[line]["start"], T_(line, key, n) + off))
CARDS = []
def card(cid, s, e, inner, cls=""): CARDS.append((cid, round(s, 3), round(e, 3), inner, cls))
H = '<span class="heart">♥</span>'
card("hook", 0.0, NX("h1"),
     f'<div class="big white" style="font-size:112px" data-at="0">TSARITSA JAHAT?</div>'
     f'<div class="big red" style="font-size:150px" data-at="{at("h1", "salah")}" data-fx="slam">SALAH!</div>'
     f'<div class="big rose love" style="font-size:118px" data-at="{at("h1", "cinta")}" data-fx="beat">KUASA DIA:<br/>CINTA {H}</div>', "low")
card("name", T_("i1", "anastasya") - 0.05, NX("i1"),
     f'<div class="big white" style="font-size:132px" data-at="{at("i1", "anastasya")}" data-fx="slam">ANASTASYA</div>'
     f'<span class="chip" data-at="{at("i1", "cryo")}">❄ CRYO ARCHON · TSARITSA</span>'
     f'<div class="sub ice" data-at="{at("i1", "bos")}">BOS BESAR FATUI</div>')
card("seven", L("r1"), NX("r1"),
     f'<span class="chip g" data-at="{at("r1", 0)}">ARCHON QUEST 7.2</span>'
     f'<div class="big ice" style="font-size:150px" data-at="{at("r1", "kumpulkan")}" data-fx="slam">7 ARCHON</div>'
     f'<div class="sub" data-at="{at("r1", "selamatkan")}">SELAMATKAN TEYVAT</div>')
card("love", L("l1"), NX("l1"),
     f'<span class="chip" data-at="{at("l1", 0)}">AUTHORITY</span>'
     f'<div class="big rose love" style="font-size:230px" data-at="{at("l1", "cinta")}" data-fx="beat">CINTA {H}</div>'
     f'<div class="sub" data-at="{at("l1", "hapuskan")}">HAPUSKAN SUMPAHAN</div>')
card("plague", L("s1"), T_("s1", "dia", 1) - 0.05,
     f'<div class="big red" style="font-size:112px" data-at="{at("s1", "wabak")}" data-fx="slam">WABAK<br/>SUMPAHAN</div>')
card("snow", T_("s1", "dia", 1) - 0.05, NX("s1"),
     f'<span class="chip" data-at="{at("s1", "bila")}">❄ BILA SALJI TURUN…</span>'
     f'<div class="big ice" style="font-size:132px" data-at="{at("s1", "semua")}" data-fx="slam">SEMUA SEMBUH!</div>')
card("nocure", L("s2"), NX("s2"),
     f'<div class="sub" data-at="{at("s2", "satu")}">TAPI ADA SATU…</div>'
     f'<div class="big red" style="font-size:104px" data-at="{at("s2", "cinta")}" data-fx="slam">CINTA PUN<br/>TAK BOLEH UBAT</div>')
card("trial", L("t1"), NX("t1"),
     f'<span class="chip g" data-at="{at("t1", "celestia")}">UJIAN CELESTIA</span>'
     f'<div class="sub" data-at="{at("t1", "subjek")}">SUBJEK:</div>'
     f'<div class="big rose love" style="font-size:210px" data-at="{at("t1", "cinta")}" data-fx="beat">CINTA {H}</div>')
card("clap", L("t2"), NX("t2"),
     f'<div class="sub" style="font-size:58px" data-at="{at("t2", "korang")}">“KORANG YANG CEMARKAN CINTA”</div>'
     f'<div class="big ice" style="font-size:132px" data-at="{at("t2", "meremang")}" data-fx="slam">MEREMANG!</div>')
card("play", L("p1"), NX("p1"),
     f'<div class="big gold" style="font-size:150px" data-at="{at("p1", "playable")}" data-fx="slam">PLAYABLE?!</div>'
     f'<span class="chip l" data-at="{at("p1", "tema")}">ARCHON TEMA CINTA ♥</span>'
     f'<div class="sub ice" data-at="{at("p1", "confirm")}">CONFIRM GEMPAK</div>')
card("primo", L("p2"), NX("p2"),
     f'<div class="big gold" style="font-size:126px" data-at="{at("p2", "simpan")}" data-fx="slam">SIMPAN PRIMO!</div>')
card("end", L("e1"), TOTAL,
     f'<div class="big white" style="font-size:100px" data-at="{at("e1", 0)}" data-fx="slam">KORANG PULL TAK?</div>'
     f'<div id="follow-btn" data-at="{at("e1", "follow")}" data-pulse="1">FOLLOW FOR MORE</div>', "low")
for cid, s, e, inner, cls in CARDS:
    P.append(f'      <div id="card-{cid}" class="clip card {cls}" data-start="{f(s)}" data-duration="{f(e - s)}" data-track-index="7">'
             f'<div class="card-in">{inner}</div></div>')
card_html = "\n".join(P); P.clear()

QUOTES = {"Q1": ("THE JESTER · PIERRO", "“<b>Love.</b> That is Her Majesty's power.”", "Cinta. Itulah kuasa Baginda."),
          "Q3": ("ANASTASYA", "“<b>Love</b> cannot cure you of this curse.”", "Cinta tak mampu sembuhkan sumpahan kau."),
          "Q2": ("ANASTASYA", "“Clearly, even you do not know what <b>love</b> is, Phanes.”", "Kau sendiri pun tak tahu apa itu cinta, Phanes.")}
for sid, (who, en, bm) in QUOTES.items():
    e = EV[sid]
    P.append(f'      <div id="q-{sid}" class="clip quote" data-start="{f(e["start"])}" data-duration="{f(e["dur"])}" data-track-index="6">'
             f'<div class="q-in"><div class="q-who">{who}</div><div class="q-en">{en}</div><div class="q-bm">{E(bm)}</div></div></div>')
quote_html = "\n".join(P); P.clear()

# ---- captions ---------------------------------------------------------------------------------------------
ICE = {"tsaritsa", "anastasya", "cryo", "archon", "fatui", "teyvat", "seven", "cataclysm", "salji", "sembuh", "celestia", "playable",
       "primo", "follow", "authority", "kuasa", "7.2", "500"}
ROSE = {"cinta", "jahat", "salah", "sumpahan", "wabak", "meremang", "gempak", "ubat"}
NUM = {}     # (teks ganti, bilangan perkataan digabung)
caps = []
for e in ev:
    if e["kind"] != "vo" or e["id"] in ("h1", "e1"): continue
    W = []; skip = 0
    for j, w in enumerate(VO[e["id"]]["words"]):
        if skip: W[-1][2] = w[2]; skip -= 1; continue
        k = (e["id"], w[0].lower())
        if k in NUM: W.append([NUM[k][0], w[1], w[2]]); skip = NUM[k][1] - 1; continue
        W.append(list(w))
    groups, cur = [], []
    for j, w in enumerate(W):
        cur.append(w); n = W[j + 1] if j + 1 < len(W) else None
        txt = " ".join(x[0] for x in cur)
        brk = len(cur) >= 2 or len(txt) >= 10 or n is None or (n[1] - w[2] > 0.1)
        if n and len(cur) == 1 and len(w[0]) <= 3 and (n[1] - w[2] <= 0.1) and len(n[0]) <= 8: brk = False
        if brk: groups.append(cur); cur = []
    for g in groups:
        caps.append({"words": [x[0] for x in g], "start": round(e["start"] + g[0][1], 3), "end": round(e["start"] + g[-1][2], 3),
                     "line_end": e["start"] + e["dur"]})
for a, b in zip(caps, caps[1:]):
    a["end"] = round(min(max(a["end"], a["start"] + 0.3), b["start"], a["line_end"] + 0.08), 3)
caps[-1]["end"] = round(caps[-1]["end"] + 0.3, 3)
def wcls(w):
    k = w.lower().strip("?,.!")
    return " r" if k in ROSE else (" g" if k in ICE else "")
for i, c in enumerate(caps):
    spans = "".join(f'<span class="w{wcls(w)}">{E(w)}</span>' for w in c["words"])
    P.append(f'        <div id="cap-{i}" class="clip cap" data-start="{f(c["start"])}" data-duration="{f(c["end"] - c["start"])}">'
             f'<div class="cap-in">{spans}</div></div>')
cap_html = "\n".join(P); P.clear()

# ---- SFX ------------------------------------------------------------------------------------------------------
SFX_DUR = {"impact-bass-1": 2.12, "impact-bass-2": 2.59, "whoosh": 0.57, "whoosh-short": 0.57, "pop": 0.72, "glitch-1": 2.64,
           "ping": 1.32, "riser": 10.03, "sparkle": 1.8, "chime": 2.5, "notification": 2.46}
SFX = [("impact-bass-1", 0.0, 0.45), ("glitch-1", T_("h1", "salah") - 0.05, 0.26), ("whoosh", T_("h1", "salah") - 0.12, 0.35),
       ("sparkle", T_("h1", "cinta"), 0.34),
       ("whoosh-short", T_("i1", "anastasya") - 0.1, 0.3), ("impact-bass-2", T_("i1", "anastasya") - 0.28, 0.36), ("chime", T_("i1", "cryo"), 0.22),
       ("whoosh", L("r1") - 0.1, 0.32), ("whoosh-short", T_("r1", "dia") - 0.1, 0.28), ("impact-bass-2", T_("r1", "kumpulkan") - 0.3, 0.38),
       ("whoosh", L("Q1") - 0.1, 0.3), ("chime", L("Q1") + 0.1, 0.2),
       ("sparkle", T_("l1", "cinta"), 0.34), ("whoosh", T_("l1", "kuasa") - 0.1, 0.3), ("pop", T_("l1", "hapuskan"), 0.36),
       ("glitch-1", L("s1"), 0.22), ("whoosh", T_("s1", "dia", 1) - 0.1, 0.3), ("chime", T_("s1", "salji"), 0.24),
       ("impact-bass-1", T_("s1", "semua") - 0.05, 0.42), ("sparkle", T_("s1", "dan"), 0.3),
       ("glitch-1", L("s2"), 0.2), ("impact-bass-2", T_("s2", "cinta") - 0.3, 0.36), ("chime", L("Q3") + 0.05, 0.2),
       ("whoosh", L("t1") - 0.1, 0.32), ("riser", T_("t1", "cinta") - 10.03, 0.2), ("impact-bass-2", T_("t1", "cinta") - 0.3, 0.4),
       ("impact-bass-1", L("Q2"), 0.45),
       ("whoosh-short", L("t2") - 0.08, 0.28), ("pop", T_("t2", "korang"), 0.34), ("impact-bass-2", T_("t2", "meremang") - 0.3, 0.42),
       ("whoosh", L("p1") - 0.1, 0.32), ("impact-bass-1", T_("p1", "playable") - 0.05, 0.42), ("sparkle", T_("p1", "archon"), 0.32),
       ("pop", T_("p1", "confirm"), 0.36),
       ("pop", T_("p2", "simpan"), 0.4), ("whoosh-short", L("e1") - 0.08, 0.28), ("pop", T_("e1", 0), 0.36),
       ("notification", T_("e1", "follow"), 0.32)]
for i, (name, s, vol) in enumerate(SFX):
    s = max(0.0, s)
    P.append(f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.mp3" data-start="{f(s)}" '
             f'data-duration="{f(min(SFX_DUR[name], TOTAL - s))}" data-volume="{vol}" data-track-index="{12 + i % 6}"></audio>')
sfx_html = "\n".join(P); P.clear()

standin = '      <div id="standin">STAND-IN · GANTI DGN TALKING HEAD KAU</div>' if MODE == "tts" else ""
T = {"total": TOTAL, "lines": [{"id": e["id"], "start": e["start"], "cuts": VO[e["id"]].get("cuts", []) if MODE == "th" else []}
                               for e in ev if e["kind"] == "vo"],
     "shots": shots, "punch": [T_("t2", "meremang"), T_("p2", "simpan")],
     "flash": [[T_("h1", "salah"), 0.5], [T_("s1", "semua"), 0.6], [L("Q2"), 0.5], [T_("p1", "playable"), 0.5]]}
page = open(os.path.join(ROOT, "build", "template.html")).read()
for k, v in {"{{TOTAL}}": f(TOTAL), "{{FACES}}": face_html, "{{SHOTS}}": shot_html, "{{SHADES}}": shade_html, "{{SNOW}}": snow_html,
             "{{STANDIN}}": standin, "{{CARDS}}": card_html, "{{QUOTES}}": quote_html, "{{CAPTIONS}}": cap_html, "{{VO}}": vo_html,
             "{{SFX}}": sfx_html, "{{BGM_VOL}}": str(BGM_VOL), "{{TIMELINE_JSON}}": json.dumps(T)}.items():
    page = page.replace(k, v)
open(os.path.join(ROOT, "index.html"), "w").write(page)
print("mode", MODE, "total", TOTAL, "shots", len(shots), "captions", len(caps), "cards", len(CARDS))
