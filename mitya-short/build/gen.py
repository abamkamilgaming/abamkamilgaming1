"""Mitya pull short (1080x1920 TikTok). Generates index.html from the EDL.
Layout (Doro44 / TheJonathon style): face cam on top (0-780), game below (780-1920),
big pop captions on the seam so they never cover the face.
Run: python3 build/gen.py   (from the project root)"""
import html, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from edl import PIECES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = 1.85          # hook freeze-frame + rewind
END_HOLD = 0.0

# ---------------------------------------------------------------- timeline
SRC = {p[0]: p for p in PIECES}
T = {}            # piece id -> (start, dur)
t = 0.0
for pid, a, b, sp, sec in PIECES:
    d = round((b - a) / sp, 3)
    T[pid] = (round(t, 3), d)
    t += d
    if pid == "h2":
        T["freeze"] = (round(t, 3), FREEZE)
        t += FREEZE
TOTAL = round(t + END_HOLD, 3)
E = lambda pid: round(T[pid][0] + T[pid][1], 3)

def at(pid, src_t):
    """timeline time of a source timestamp inside piece pid"""
    _, a, b, sp, _ = SRC[pid]
    return round(T[pid][0] + (src_t - a) / sp, 3)

def f(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")

# ---------------------------------------------------------------- captions
# (piece, src_start, text)  — *word* = gold, ~word~ = red. Ends at next caption / piece end.
CAP = [
    ("h2", 773.70, "AAAAAAA!!!"),
    ("h2", 776.90, "*JATUH KERUSI*"),
    ("i1", 10.00, "Sekarang aku tengah mengadap"),
    ("i1", 12.00, "Her Majesty *TSARITSA*"),
    ("i1", 13.36, "Yang di-Pertuan *Agung*"),
    ("i2", 26.40, "Plus, *MITYA* memang best!"),
    ("i3", 31.65, "Please..."),
    ("i3", 32.60, "double gold *EARLY*"),
    ("i3", 33.80, "signature *EARLY*"),
    ("i3", 34.85, "*PLEASE!*"),
    ("i4", 50.00, "Kalau live ni dapat"),
    ("i4", 52.45, "*20 VIEW*"),
    ("i4", 53.60, "aku tekan *TERUS!*"),
    ("i4", 54.90, "Serius tak bergurau"),
    ("i5", 169.55, "Dah lah susah"),
    ("i5", 170.95, "nak buat *KEPUTUSAN*"),
    ("i6", 172.80, "Kau ingat *SENANG* ke"),
    ("i6", 174.00, "nak pull *MITYA* ni?!"),
    ("i7", 176.40, "~YA ALLAH~"),
    ("i8", 296.70, "Janganlah ya Allah"),
    ("i8", 297.75, "janganlah bagi"),
    ("i8", 298.90, "~HARD PITY~"),
    ("i8", 299.40, "aku nak *signature* lagi"),
    ("i9", 410.90, "Aku tak *TERKEJUT* pun"),
    ("i9", 412.70, "kalau menang"),
    ("i9", 413.40, "sebab ni *HARD PITY*"),
    ("m1", 432.60, "*EMAS?!*"),
    ("m3", 508.60, "JAP JAP JAP..."),
    ("m4", 510.75, "*MITYAAAA!!!*"),
    ("m5", 514.80, "*DAPAT PUN!!*"),
    ("m5", 517.60, "*HAPPY GILA*"),
    ("w1", 657.75, "Nak *SIGNATURE* kalau boleh"),
    ("w2", 696.60, "~NOOOOO!!~"),
    ("w3", 700.55, "Ya Allah..."),
    ("w4", 732.85, "~WASTED~"),
    ("w5", 765.45, "Eh betul eh?"),
    ("w5", 766.80, "Pity *46...*"),
    ("w6", 769.90, "*EMAS LAGI?!*"),
    ("w7", 773.60, "AAAAAAA!!!"),
    ("w8", 775.40, "*SIGNATURE DAPAT!!*"),
    ("w8", 777.00, "*JATUH KERUSI*"),
    ("w9", 783.30, "*N-I-C-E-E!!*"),
    ("w9", 785.55, "LET'S *GOOO!*"),
    ("w10", 788.65, "*WOW*"),
    ("w10", 789.45, "*YAYYY!*"),
    ("w10", 790.80, "Tahniah, bam!"),
    ("w11", 809.55, "This is *MY NIGHT*"),
    ("w12", 813.45, "...is it?"),
    ("e1", 574.40, "Habis primo aku..."),
    ("e1", 575.90, "~HABIS!!~"),
    ("e2", 855.40, "No... *TSARITSA!*"),
    ("e2", 857.90, "~SORRY TUANKU!!~"),
]
caps = []
for i, (pid, st, txt) in enumerate(CAP):
    s = at(pid, st)
    if i + 1 < len(CAP) and CAP[i + 1][0] == pid:
        e = at(pid, CAP[i + 1][1])
    else:
        e = E(pid)
        if i + 1 < len(CAP):
            e = min(e + 0.05, at(CAP[i + 1][0], CAP[i + 1][1]))
    caps.append((s, round(e - s, 3), txt))

def mark(txt):
    out = []
    for w in txt.split(" "):
        cls = "w"
        if w.startswith("*") or w.endswith("*"):
            cls += " g"
        if w.startswith("~") or w.endswith("~"):
            cls += " r"
        out.append(f'<span class="{cls}">{html.escape(w.strip("*~").upper())}</span>')
    return " ".join(out)

# ---------------------------------------------------------------- stickers / popups
# (id, start, dur, html, css class)
def stk(sid, s, e, inner, cls):
    return (sid, round(s, 3), round(e - s, 3), inner, cls)
STK = [
    stk("hook-top", 0.0, E("h1") + 0.6, '<span class="k1">BILA KAU ALL-IN</span><span class="k2">PRIMOGEM</span><span class="k3">UNTUK MITYA...</span>', "hook"),
    stk("fz-q", T["freeze"][0] + 0.05, E("freeze"), '<span class="k1">TAPI JAP...</span><span class="k2">MACAM MANA</span><span class="k3">BOLEH JADI GINI?</span>', "hook"),
    stk("fz-rw", E("freeze") - 0.6, E("freeze"), '<span class="rw">&#9194; REWIND</span>', "rewind"),
    stk("tsa", at("i1", 12.0), E("i1"), '<img src="assets/img/tsaritsa.jpg" alt="Tsaritsa"><span class="lbl">HER MAJESTY</span>', "pop pop-r"),
    stk("mit", T["i2"][0] + 0.05, E("i2"), '<img src="assets/img/mitya.jpg" alt="Mitya"><span class="lbl">MITYA</span>', "pop pop-l wide"),
    stk("v20", at("i4", 52.45), E("i4"), '<span class="t1">SYARAT PULL</span><span class="t2">20 VIEW</span>', "badge"),
    stk("p47", T["i8"][0], E("i8"), '<span class="t1">PITY</span><span class="t2">50</span>', "badge red"),
    stk("flw", E("i9") - 1.25, E("i9"), '<span class="t1">FAMOUS</span><span class="t2">LAST WORDS</span>', "badge red tilt"),
    stk("ff", T["m2"][0], E("m2"), '<span class="ff">SKIP 4-STAR &#9193;&#9193;</span>', "ffbar"),
    stk("sec2", T["w1"][0], E("w1") + 0.3, '<span class="t1">ROUND 2</span><span class="t2">SIGNATURE WEAPON</span>', "badge violet"),
    stk("p46", T["w5"][0] + 0.9, E("w5"), '<span class="t1">PITY</span><span class="t2">46</span>', "badge"),
    stk("sorry", T["e2"][0] + 0.35, TOTAL, '<img src="assets/img/tsaritsa.jpg" alt="Tsaritsa"><span class="lbl">MAAF TUANKU...<br>PRIMO HABIS KAT MITYA</span>', "pop pop-c"),
]


# ---------------------------------------------------------------- viewer chat bubbles
# Re-typed from the stream's own chat overlay (covers it). (piece_a, src_a, piece_b, src_b, name, text|None)
# Voice-aligned: Kaze "NICEEE!!!" lands as AbamKamil spells N-I-C-E-E; Mer "This is your night bam" as he answers.
CHAT = [
    ("h1", 770.55, "h2", 778.40, "Amzarishere", "swipe je kad"),
    ("i1", 10.00, "i3", 35.40, "Kaze Shohkan", "hope you get double gold + early \U0001F60C"),
    ("i4", 50.00, "i4", 55.95, "Kaze Shohkan", "\U0001F602\U0001F923"),
    ("i5", 169.55, "i7", 177.55, "OCAK ★Farahin", "Pasti Mitya dgn Vesna merebut Odette"),
    ("i8", 296.70, "i8", 297.95, "⛓\U0001F5A4\U0001F356", "dh 20"),
    ("i8", 298.70, "i8", 301.60, "bukan eiz", "letsgo"),
    ("i9", 410.90, "i9", 414.55, "⛓\U0001F5A4\U0001F356", "75"),
    ("m1", 431.40, "m1", 436.25, "⛓\U0001F5A4\U0001F356", "Nk Mr door"),
    ("m3", 507.80, "m5", 519.85, "OCAK ★Farahin", None),
    ("w1", 657.75, "w1", 659.30, "fanfaley1", "shared the live stream!"),
    ("w2", 696.55, "w3", 701.35, "Mer", "Boleh cuba dapat r5 kalau dapat"),
    ("w4", 732.85, "w4", 733.95, "Qilah Nak Illuga", "ALA LAMBAT"),
    ("w5", 765.45, "w8", 778.85, "Amzarishere", "swipe je kad"),
    ("w9", 783.35, "w9", 785.75, "Kaze Shohkan", "NICEEE!!!"),
    ("w9", 785.95, "w9", 787.05, "Dyluna", "gelo"),
    ("w10", 789.30, "w10", 790.75, "Butterscotch", "jj"),
    ("w10", 791.45, "w10", 791.65, "Mer", "Yeyy"),
    ("w11", 809.55, "w12", 814.45, "Mer", "This is your night bam"),
    ("e1", 574.35, "e1", 575.00, "⛓\U0001F5A4\U0001F356", "weapon LAK"),
    ("e1", 575.00, "e1", 576.65, "⛓\U0001F5A4\U0001F356", "\U0001F970"),
    ("e2", 855.60, "e2", 860.40, "Butterscotch", "misi tercapai"),
]
chats = []
for pa, sa, pb, sb, name, text in CHAT:
    s0 = at(pa, sa) if sa > SRC[pa][1] + 0.01 else T[pa][0]
    s1 = at(pb, sb) if sb < SRC[pb][2] - 0.01 else E(pb)
    if pa == "h1":
        s1 = E("freeze")          # the freeze frame carries the same burned-in bubble
    chats.append((round(s0, 3), round(s1 - s0, 3), name, text))

# ---------------------------------------------------------------- audio
MUSIC = [  # (id, file, start, dur, volume, media_start, fade_in, fade_out)
    ("mu-delfino", "delfino", 0.0, E("i9") + 0.25, 0.22, 0, 0.0, 0.5),
    ("mu-p5a", "p5_intro", T["m1"][0], E("m3") - T["m1"][0], 0.55, 0, 0.0, 0.15),
    ("mu-p5b", "p5_climax", T["m4"][0], E("m5") - T["m4"][0] + 0.2, 0.6, 0, 0.0, 0.6),
    ("mu-chick", "chicken", T["w1"][0], E("w4") - T["w1"][0], 0.3, 0, 0.1, 0.2),
    ("mu-tense", "tension", T["w5"][0], T["w5"][1], 0.35, 0, 0.1, 0.1),
    ("mu-p5c", "p5_intro", T["w6"][0], E("w7") - T["w6"][0], 0.55, 0, 0.0, 0.1),
    ("mu-p5d", "p5_climax", T["w8"][0], E("e1") - T["w8"][0], 0.6, 0, 0.0, 0.6),
]
SFX = [  # (file, start, dur, volume, media_start)
    ("impact-bass-1.mp3", 0.0, 1.6, 0.5, 0),
    ("whoosh.mp3", T["h2"][0] - 0.08, 0.5, 0.4, 0),
    ("vine-boom-meme-cccpxzg.m4a", at("h2", 776.95), 1.25, 0.7, 0),
    ("glitch-1.mp3", T["freeze"][0], 0.6, 0.35, 0),
    ("rewind.m4a", E("freeze") - 0.5, 0.44, 0.6, 0),
    ("whoosh-short.mp3", T["i1"][0] - 0.05, 0.5, 0.35, 0),
    ("sparkle.mp3", at("i1", 12.0), 1.5, 0.35, 0),
    ("illuminati-confirmed-the-x-f.m4a", at("i1", 13.36), 1.45, 0.35, 1.0),
    ("cute-wow-sfx.m4a", T["i2"][0] + 0.05, 1.5, 0.5, 4.55),
    ("pop.mp3", at("i3", 34.85), 0.6, 0.45, 0),
    ("pop.mp3", at("i4", 52.45), 0.6, 0.45, 0),
    ("awkward-moment.m4a", E("i4") - 0.25, 1.1, 0.6, 0),
    ("vine-boom-meme-cccpxzg.m4a", T["i7"][0], 1.0, 0.55, 0),
    ("pop.mp3", at("i8", 298.9), 0.6, 0.45, 0),
    ("illuminati-confirmed-the-x-f.m4a", E("i9") - 1.25, 1.35, 0.45, 0.0),
    ("sparkle.mp3", at("m1", 432.6), 1.5, 0.4, 0),
    ("glitch-1.mp3", T["m2"][0], T["m2"][1], 0.4, 0),
    ("whoosh.mp3", T["m2"][0] + 0.6, 0.5, 0.35, 0),
    ("waitwaitwait-what-da-helllll.m4a", T["m3"][0] + 0.1, T["m3"][1] - 0.1, 0.55, 0),
    ("impact-bass-1.mp3", T["m4"][0], 1.6, 0.6, 0),
    ("kids-saying-yay-sound-effect.m4a", T["m5"][0] + 0.2, 2.6, 0.35, 0),
    ("whoosh.mp3", T["w1"][0] - 0.05, 0.5, 0.4, 0),
    ("fahhh-sound-effect.m4a", E("w2") - 0.15, 1.2, 0.5, 0),
    ("roblox-death-sound-oof-sound.m4a", T["w4"][0] + 0.25, 0.4, 0.7, 0.69),
    ("sparkle.mp3", at("w6", 769.9), 1.5, 0.4, 0),
    ("impact-bass-1.mp3", T["w8"][0], 1.6, 0.6, 0),
    ("what-the-hell-oh-my-god-no-w.m4a", T["w8"][0] + 0.2, 2.6, 0.4, 0),
    ("vine-boom-meme-cccpxzg.m4a", at("w8", 777.0), 1.25, 0.6, 0),
    ("kids-saying-yay-sound-effect.m4a", at("w10", 789.45), 1.8, 0.3, 0),
    ("awkward-moment.m4a", T["w12"][0] + 0.3, 0.7, 0.55, 0),
    ("emotional-damage-meme.m4a", at("e1", 575.9) + 0.2, 1.6, 0.55, 0),
    ("sad-sound-effect.m4a", T["e2"][0] + 0.3, TOTAL - T["e2"][0] - 0.3, 0.6, 0.77),
]

# ---------------------------------------------------------------- grades (media-treatment payloads)
G_FACE = {"preset": "deep-contrast", "intensity": 0.35,
          "adjust": {"exposure": -0.05, "contrast": 0.18, "highlights": -0.55, "whites": -0.22, "shadows": 0.08,
                     "blacks": -0.06, "temperature": 0.07, "tint": 0.02, "vibrance": 0.16, "saturation": 0.02},
          "details": {"vignette": 0.28}}
G_GAME = {"preset": "deep-contrast", "intensity": 0.45,
          "adjust": {"exposure": 0.02, "contrast": 0.1, "highlights": -0.14, "shadows": 0.12, "vibrance": 0.22,
                     "temperature": 0.02},
          "details": {"vignette": 0.18}, "effects": {"bloom": 0.2}}
def attr(g):
    return html.escape(json.dumps(g, separators=(",", ":")), quote=True)

# ---------------------------------------------------------------- HTML
P = []
for k, (pid, a, b, sp, sec) in enumerate(PIECES):
    s, d = T[pid]
    aud = 'data-has-audio="true" data-volume="1"' if sp < 3 else "muted"
    P.append(f'      <div class="gw" style="z-index:{10 + k}"><div class="gz" id="gw-{pid}">'
             f'<video id="g-{pid}" class="clip game" src="assets/clips/{pid}_g.mp4" data-start="{f(s)}" data-duration="{f(d)}" '
             f'data-track-index="2" muted playsinline data-color-grading="{attr(G_GAME)}"></video></div></div>')
    P.append(f'      <div class="fw" style="z-index:{60 + k}"><div class="fz" id="fw-{pid}">'
             f'<video id="f-{pid}" class="clip face" src="assets/clips/{pid}_f.mp4" data-start="{f(s)}" data-duration="{f(d)}" '
             f'data-track-index="1" {aud} playsinline data-color-grading="{attr(G_FACE)}"></video></div></div>')
s, d = T["freeze"]
P.append(f'      <div class="gw" style="z-index:40"><div class="gz" id="gw-fz"><img id="fz-g" class="clip game" src="assets/img/freeze_g.jpg" alt="" '
         f'data-start="{f(s)}" data-duration="{f(d)}" data-track-index="2"></div></div>')
P.append(f'      <div class="fw" style="z-index:95"><div class="fz" id="fw-fz"><img id="fz-f" class="clip face" src="assets/img/freeze_f.jpg" alt="" '
         f'data-start="{f(s)}" data-duration="{f(d)}" data-track-index="1"></div></div>')
P.append(f'      <div id="fz-dim" class="clip" data-start="{f(s)}" data-duration="{f(d)}" data-track-index="3"><div class="dim-in"></div></div>')
MEDIA = "\n".join(P); P.clear()

for sid, s, d, inner, cls in STK:
    P.append(f'      <div id="st-{sid}" class="clip stk {cls}" data-start="{f(s)}" data-duration="{f(d)}" data-track-index="5">'
             f'<div class="stk-in">{inner}</div></div>')
STICK = "\n".join(P); P.clear()

for i, (cs, cd, name, text) in enumerate(chats):
    first = name.strip()[0]
    ini = html.escape(first.upper()) if first.isalpha() else "&#128172;"
    n = len(text) if text else 0
    fs = 62 if n <= 12 else 52 if n <= 22 else 46 if n <= 30 else 42
    body = f'<div class="ch-msg" style="font-size:{fs}px">{html.escape(text)}</div>' if text else ''
    P.append(f'      <div id="chat-{i}" class="clip chat" data-start="{f(cs)}" data-duration="{f(cd)}" data-track-index="6">'
             f'<div class="ch-in{"" if text else " solo"}"><div class="ch-av">{ini}</div><div class="ch-txt"><div class="ch-name">{html.escape(name)}</div>{body}</div></div></div>')
CHATS = "\n".join(P); P.clear()


for i, (s, d, txt) in enumerate(caps):
    P.append(f'        <div id="cap-{i}" class="clip cap" data-start="{f(s)}" data-duration="{f(d)}"><div class="cap-in">{mark(txt)}</div></div>')
CAPS = "\n".join(P); P.clear()

for mid, fn, s, d, vol, ms, fi, fo in MUSIC:
    P.append(f'      <audio id="{mid}" class="clip" src="assets/music/{fn}.m4a" data-start="{f(s)}" data-duration="{f(d)}" '
             f'data-volume="{vol}" data-media-start="{f(ms)}" data-fade-in="{fi}" data-fade-out="{fo}" data-track-index="10"></audio>')
for i, (fn, s, d, vol, ms) in enumerate(SFX):
    s = max(0.0, s); d = min(d, TOTAL - s)
    P.append(f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{fn}" data-start="{f(s)}" data-duration="{f(d)}" '
             f'data-volume="{vol}" data-media-start="{f(ms)}" data-track-index="11"></audio>')
AUDIO = "\n".join(P); P.clear()

TL = {"total": TOTAL, "T": T, "flash": [T["m4"][0], T["w8"][0]],
      "shake": [[T["h2"][0], 1.4], [T["w7"][0], T["w7"][1]], [T["m4"][0], 0.5], [T["w8"][0], 0.5]],
      "push": ["h2", "m4", "m5", "w7", "w8", "w9", "e2", "i7", "w2"],
      "gamezoom": ["m4", "m5", "w8"], "freeze": T["freeze"]}

page = open(os.path.join(ROOT, "build", "template.html")).read()
for k, v in {"{{TOTAL}}": f(TOTAL), "{{MEDIA}}": MEDIA, "{{STICKERS}}": STICK, "{{CHATS}}": CHATS, "{{CAPTIONS}}": CAPS,
             "{{AUDIO}}": AUDIO, "{{TL}}": json.dumps(TL)}.items():
    page = page.replace(k, v)
open(os.path.join(ROOT, "index.html"), "w").write(page)
print("TOTAL", TOTAL)
for pid, (s, d) in T.items():
    print(f"  {s:6.2f} +{d:5.2f}  {pid}")
