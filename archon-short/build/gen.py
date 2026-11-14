"""Generates index.html for the Archon Quest 7.2 short (1080x1920, < 60 s).
Timing is derived from the tightened VO durations so there is no dead air.
Run:  python3 build/gen.py   (from the project root)"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO = json.load(open(os.path.join(ROOT, "build", "vo_words_tight.json")))
SHOTS = {s[0]: s for s in json.load(open(os.path.join(ROOT, "assets", "clips", "shots.json")))}
CODE = "QYJW50368SU7"
GAP = 0.10

# --- edit decision list ------------------------------------------------------
# ("vo", line_id, [shots]) — narration over B-roll
# ("sync", shot)           — game voice line played from the clip itself
SEQ = [
    ("vo", "h1", ["A", "B"]), ("vo", "h2", ["C"]),
    ("vo", "d1", ["D1", "D2"]), ("sync", "E"),
    ("vo", "s1", ["F1", "F2"]),
    ("vo", "r1", ["G"]), ("sync", "H"), ("vo", "r2", ["I"]),
    ("vo", "z1", ["J"]), ("vo", "z2", ["K"]), ("sync", "L1"), ("sync", "L2"),
    ("vo", "c1", ["M"]), ("sync", "N"),
    ("vo", "n1", ["O"]), ("sync", "P"),
    ("vo", "e1", ["Q"]), ("vo", "e2", []),
]
END_HOLD = 1.9

t = 0.15
events = []
for ev in SEQ:
    if ev[0] == "vo":
        d = VO[ev[1]]["dur"]
    else:
        d = SHOTS[ev[1]][2]
    events.append({"kind": ev[0], "id": ev[1], "shots": ev[2] if ev[0] == "vo" else [ev[1]], "start": t, "dur": d})
    t += d + GAP
TOTAL = round(t - GAP + END_HOLD, 2)

# shot placement: each event's shots tile [event.start, next.start)
placed = []
for i, ev in enumerate(events):
    s0 = 0.0 if i == 0 else ev["start"]
    s1 = events[i + 1]["start"] if i + 1 < len(events) else TOTAL
    if not ev["shots"]:
        # extend previous shot
        placed[-1]["end"] = s1
        continue
    if i + 1 < len(events) and not events[i + 1]["shots"]:
        s1 = TOTAL
    avail = [SHOTS[s][2] for s in ev["shots"]]
    span = s1 - s0
    tot = sum(avail)
    cur = s0
    for sid, a in zip(ev["shots"], avail):
        d = span * a / tot
        placed.append({"id": sid, "start": cur, "end": cur + d})
        cur += d
for p in placed:
    p["start"] = round(p["start"], 3); p["end"] = round(p["end"], 3)
    assert p["end"] - p["start"] <= SHOTS[p["id"]][2] + 0.25, (p, SHOTS[p["id"]][2])

def ev(id_):
    return next(e for e in events if e["id"] == id_)

def word_t(line, idx):
    e = ev(line); w = VO[line]["words"][idx]
    return round(e["start"] + w[1], 3)

# --- captions ----------------------------------------------------------------
GOLD = {"archon", "teyvat", "celestia", "kewujudan", "seven", "cataclysm", "raiden", "ei", "eternity",
        "celestial", "nail", "gila", "zhongli", "mora", "kontrak", "terakhir", "noy", "meremang", "bergabung",
        "tenaga", "primogems", "redeem", "code", "free", "habis", "bahaya", "besar", "tujuh", "hapuskan",
        "experience", "adventurer's", "claim", "follow", "sejarah", "first"}

def clean(w):
    return w.strip(",.!?").lower()

cap_groups = []
for e in events:
    if e["kind"] != "vo" or e["id"] in ("e1", "e2"):
        continue
    W = VO[e["id"]]["words"]
    groups, cur = [], []
    for j, w in enumerate(W):
        cur.append(w)
        txt = " ".join(x[0] for x in cur)
        nxt = W[j + 1] if j + 1 < len(W) else None
        brk = (len(cur) >= 2 or len(txt) >= 11 or w[0][-1] in ",.!?" or nxt is None
               or (nxt and nxt[1] - w[2] > 0.15))
        if nxt and len(cur) == 1 and len(w[0]) <= 3 and w[0][-1] not in ",.!?":
            brk = False
        if brk:
            groups.append(cur); cur = []
    for g in groups:
        cap_groups.append({"words": [x[0] for x in g], "start": e["start"] + g[0][1], "end": e["start"] + g[-1][2]})
for a, b in zip(cap_groups, cap_groups[1:]):
    a["end"] = min(max(a["end"], a["start"] + 0.25), b["start"])
cap_groups[-1]["end"] += 0.3

# --- quote captions for game lines (English + BM) ------------------------------
QUOTES = {
    "E": ("“True annihilation shall descend.”", "Kemusnahan total akan tiba."),
    "H": ("“…to answer for eternity.”", "Demi keabadian."),
    "L1": ("“Betray it…”", "Khianatinya…"),
    "L2": ("“…and you taint my blood.”", "…dan kau cemari darahku."),
    "N": ("“Celestia welcomes you.”", "Celestia mengalu-alukan kedatangan kau."),
    "P": ("“We have to face it… together.”", "Kita hadap… sama-sama."),
}
SPEAKER = {"E": "THE EVER-SPEAKING ONE", "H": "RAIDEN EI", "L1": "ZHONGLI", "L2": "ZHONGLI",
           "N": "CELESTIA", "P": "MAVUIKA"}
SYNC_VOL = {"E": 1.5, "H": 1.6, "L1": 1.6, "L2": 1.6, "N": 1.6, "P": 1.5}

# --- sections (keypoint chapter tags) -----------------------------------------
SECTIONS = [
    ("d1", "z", "01", "BAHAYA KEWUJUDAN TEYVAT"),
    ("s1", "z", "02", "7 ARCHON BERKUMPUL"),
    ("r1", "z", "03", "RAIDEN EI × CELESTIAL NAIL"),
    ("z1", "z", "04", "KONTRAK TERAKHIR ZHONGLI"),
    ("c1", "z", "05", "CELESTIA & NOY"),
    ("n1", "z", "06", "SEMUA BERGABUNG TENAGA"),
]
sec_list = []
for i, (line, _, num, label) in enumerate(SECTIONS):
    s = ev(line)["start"] - 0.05
    e = (ev(SECTIONS[i + 1][0])["start"] - 0.05) if i + 1 < len(SECTIONS) else ev("e1")["start"] - 0.05
    sec_list.append((num, label, round(s, 3), round(e, 3)))

# --- stickers (big motion-graphic words) ----------------------------------------
STICKERS = [
    # id, start, dur, html, style-class
    ("st-500", word_t("s1", 6) - 0.05, ev("s1")["start"] + VO["s1"]["dur"] - word_t("s1", 6) + 0.1,
     '<span class="big gold">500</span><span class="sub">TAHUN LEPAS</span>', "stk"),
    ("st-42", ev("E")["start"] + 0.1, ev("E")["dur"] - 0.15,
     '<span class="sub">TINGGAL</span><span class="big red">42 HARI</span>', "stk top"),
    ("st-gila", word_t("r2", 7) - 0.05, 0.9, '<span class="big white glow">GILA!</span>', "stk"),
    ("st-kontrak", word_t("z2", 6) - 0.05, ev("z2")["start"] + VO["z2"]["dur"] - word_t("z2", 6) + 0.15,
     '<span class="sub">KONTRAK</span><span class="big gold">TERAKHIR</span>', "stk top"),
    ("st-noy", word_t("c1", 4) - 0.05, ev("c1")["start"] + VO["c1"]["dur"] - word_t("c1", 4) + 0.1,
     '<span class="big gold">NOY</span><span class="sub">MASUK CERITA</span>', "stk top"),
    ("st-reunion", word_t("n1", 6) - 0.05, ev("n1")["start"] + VO["n1"]["dur"] - word_t("n1", 6) + 0.1,
     '<span class="sub">SEMUA</span><span class="big gold">BERGABUNG!</span>', "stk top"),
]

# --- SFX ---------------------------------------------------------------------
strike_t = ev("r2")["start"] + 0.0
SFX = [
    ("impact-bass-1", 0.0, 0.55), ("whoosh-short", placed[1]["start"] - 0.1, 0.4),
    ("whoosh", ev("h2")["start"] - 0.12, 0.45), ("pop", ev("h2")["start"] + 0.25, 0.5),
    ("pop", word_t("h2", 5) - 0.05, 0.45),
    ("glitch-1", ev("d1")["start"] - 0.05, 0.35), ("impact-bass-2", ev("E")["start"] - 0.35, 0.6),
    ("whoosh", ev("s1")["start"] - 0.12, 0.4), ("ping", word_t("s1", 6) - 0.05, 0.35),
    ("riser", strike_t - 10.03, 0.32), ("impact-bass-1", strike_t, 0.6),
    ("pop", word_t("r2", 7) - 0.05, 0.5),
    ("whoosh-short", ev("z1")["start"] - 0.1, 0.4), ("sparkle", word_t("z2", 5) - 0.1, 0.4),
    ("impact-bass-2", word_t("z2", 6) - 0.4, 0.45),
    ("whoosh", ev("c1")["start"] - 0.12, 0.4), ("chime", ev("N")["start"], 0.35),
    ("whoosh-short", ev("n1")["start"] - 0.1, 0.4), ("sparkle", word_t("n1", 6) - 0.05, 0.4),
    ("impact-bass-1", ev("e1")["start"] - 0.05, 0.55), ("ping", word_t("e1", 3) - 0.05, 0.4),
    ("pop", word_t("e1", 6) - 0.05, 0.45), ("pop", word_t("e1", 9) - 0.05, 0.45),
    ("notification", ev("e2")["start"] + 0.9, 0.4),
]
SFX_DUR = {"impact-bass-1": 2.12, "impact-bass-2": 2.59, "whoosh": 0.57, "whoosh-short": 0.57, "pop": 0.72,
           "glitch-1": 2.64, "ping": 1.32, "riser": 10.03, "sparkle": 1.8, "chime": 2.5, "notification": 2.46}

# --- assemble HTML -------------------------------------------------------------
def f(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")

# --- colour grade + lighting per shot (HyperFrames media treatment payload) ----
LIFT = {"B": 0.22, "D2": 0.18, "F1": 0.12, "G": 0.15, "I": 0.05, "K": 0.08, "L1": 0.05, "L2": 0.12, "Q": 0.1, "O": 0.1}
TAME = {"E": -0.28, "M": -0.28, "N": -0.32, "C": -0.12, "D1": -0.15, "A": -0.12}
def grade(sid):
    adj = {"exposure": round(0.04 + LIFT.get(sid, 0) - (0.06 if sid in TAME else 0), 3), "contrast": 0.1,
           "highlights": TAME.get(sid, -0.16), "shadows": 0.14 + (0.08 if sid in LIFT else 0),
           "vibrance": 0.22, "temperature": 0.03}
    g = {"preset": "deep-contrast", "intensity": 0.55, "adjust": adj,
         "details": {"vignette": 0.24}, "effects": {"bloom": 0.22}}
    return html.escape(json.dumps(g, separators=(",", ":")), quote=True)

out = []
A = out.append
z = 10
for i, p in enumerate(placed):
    sid = p["id"]; d = p["end"] - p["start"]
    sync = sid in SYNC_VOL or sid == "I"
    audio = f'data-has-audio="true" data-volume="{SYNC_VOL.get(sid, 0.7)}"' if sync else "muted"
    A(f'      <div class="shotwrap" id="w-{sid}" style="z-index:{z+i}">\n'
      f'        <video id="v-{sid}" class="clip shot" src="assets/clips/{sid}.mp4" data-start="{f(p["start"])}" '
      f'data-duration="{f(d)}" data-track-index="1" {audio} playsinline data-color-grading="{grade(sid)}"></video>\n      </div>')
video_html = "\n".join(out); out.clear()

for i, (num, label, s, e) in enumerate(sec_list):
    A(f'      <div id="sec-{num}" class="clip sec" data-start="{f(s)}" data-duration="{f(e-s)}" data-track-index="5">'
      f'<div class="sec-in"><span class="sec-num">#{num}</span><span class="sec-label">{label}</span></div></div>')
sec_html = "\n".join(out); out.clear()

for sid, (en, bm) in QUOTES.items():
    e = ev(sid)
    A(f'      <div id="q-{sid}" class="clip quote" data-start="{f(e["start"])}" data-duration="{f(e["dur"])}" data-track-index="6">'
      f'<div class="q-in"><div class="q-who">{SPEAKER[sid]}</div><div class="q-en">{html.escape(en)}</div>'
      f'<div class="q-bm">{html.escape(bm)}</div></div></div>')
quote_html = "\n".join(out); out.clear()

for i, g in enumerate(cap_groups):
    spans = " ".join(f'<span class="w{" g" if clean(w) in GOLD else ""}">{html.escape(w.strip(",.").upper())}</span>' for w in g["words"])
    A(f'        <div id="cap-{i}" class="clip cap" data-start="{f(g["start"])}" data-duration="{f(g["end"]-g["start"])}">'
      f'<div class="cap-in">{spans}</div></div>')
cap_html = "\n".join(out); out.clear()

import re as _re
def _fit(m):
    word = _re.sub("<[^>]+>", "", m.group(2))
    size = min(190, int(860 / (max(1, len(word)) * 0.76)))
    return f'<span class="big{m.group(1)}" style="font-size:{size}px">{m.group(2)}</span>'
STICKERS = [(a, b, c, _re.sub(r'<span class="big([^"]*)">([^<]+)</span>', _fit, d), e) for a, b, c, d, e in STICKERS]
for sid, s, d, inner, cls in STICKERS:
    A(f'      <div id="{sid}" class="clip {cls}" data-start="{f(s)}" data-duration="{f(d)}" data-track-index="7">'
      f'<div class="stk-in">{inner}</div></div>')
stk_html = "\n".join(out); out.clear()

for i, (name, s, vol) in enumerate(SFX):
    s = max(0.0, s)
    A(f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.mp3" data-start="{f(s)}" '
      f'data-duration="{f(min(SFX_DUR[name], TOTAL - s))}" data-volume="{vol}" data-track-index="12"></audio>')
sfx_html = "\n".join(out); out.clear()

for e in events:
    if e["kind"] == "vo":
        A(f'      <audio id="vo-{e["id"]}" class="clip" src="assets/voice/{e["id"]}.wav" data-start="{f(e["start"])}" '
          f'data-duration="{f(e["dur"])}" data-volume="1" data-track-index="10"></audio>')
vo_html = "\n".join(out); out.clear()

code_spans = "".join(f'<span class="ch" id="ch-{i}">{c}</span>' for i, c in enumerate(CODE))
e1 = ev("e1"); e2 = ev("e2")
end_start = round(e1["start"] - 0.05, 3)
t_code = word_t("e1", 3) - 0.05
t_primo = word_t("e1", 6) - 0.05
t_exp = word_t("e1", 9) - 0.05
t_follow = e2["start"] + 0.75

timeline = {
    "total": TOTAL, "placed": placed, "events": events, "caps": cap_groups,
    "end_start": end_start, "t_code": t_code, "t_primo": t_primo, "t_exp": t_exp, "t_follow": t_follow,
    "strike": strike_t, "hook_end": ev("h2")["start"], "gift": [ev("h2")["start"], ev("d1")["start"]],
}

page = open(os.path.join(ROOT, "build", "template.html")).read()
for k, v in {
    "{{TOTAL}}": f(TOTAL), "{{VIDEOS}}": video_html, "{{SECTIONS}}": sec_html, "{{QUOTES}}": quote_html,
    "{{CAPTIONS}}": cap_html, "{{STICKERS}}": stk_html, "{{SFX}}": sfx_html, "{{VO}}": vo_html,
    "{{CODE_SPANS}}": code_spans, "{{CODE}}": CODE, "{{END_START}}": f(end_start),
    "{{END_DUR}}": f(TOTAL - end_start), "{{HOOK_DUR}}": f(ev("h2")["start"] - 0.02),
    "{{GIFT_START}}": f(ev("h2")["start"]), "{{GIFT_DUR}}": f(ev("d1")["start"] - ev("h2")["start"] - 0.02),
    "{{TIMELINE_JSON}}": json.dumps(timeline), "{{FLASH_T}}": f(strike_t),
}.items():
    page = page.replace(k, v)
open(os.path.join(ROOT, "index.html"), "w").write(page)
print("total", TOTAL, "shots", len(placed), "captions", len(cap_groups))
for e in events:
    print(f'  {e["start"]:6.2f}  {e["kind"]:4s} {e["id"]:3s} {e["dur"]:.2f}')
