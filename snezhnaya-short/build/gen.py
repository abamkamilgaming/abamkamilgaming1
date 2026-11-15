"""Generate index.html for the Snezhnaya funny-moments short.
Inputs: build/lines.json (from cut.py), build/template.html. Usage: python3 build/gen.py"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINES = json.load(open(os.path.join(ROOT, "build", "lines.json")))
END_DUR = 2.2

# --- timeline: lines back to back ------------------------------------------------------
t = 0.0
L = {}
for ln in LINES:
    ln["start"] = round(t, 3); t += ln["dur"]; L[ln["id"]] = ln
SPEECH_END = round(t, 3)
END_START = SPEECH_END
TOTAL = round(END_START + END_DUR, 3)
def at(lid, rel=0.0): return round(L[lid]["start"] + rel, 3)
def end(lid): return round(L[lid]["start"] + L[lid]["dur"], 3)

# --- captions (BM santai, his own words; *word* = yellow keyword). rel times from clip transcripts
CAPS = {
    "h1": [(0.0, "EH"), (0.36, "*JADAH* APA"), (1.12, "KAU NI *TIKTOK?*")],
    "h2": [(0.0, "*REPRODUCE*"), (0.66, "KOTAK KEPALA"), (1.62, "ACIK *ENGKAU!*")],
    "h3": [(0.0, "*BODOH* LAH"), (0.94, "TIKTOK NI"), (1.74, "SORRY LAH TIKTOK"), (2.52, "AKU KENA *MAKI*"), (3.40, "KAU MEMANG *BONGOK*")],
    "s1": [(0.0, "AKU *MENGANTUK*"), (1.10, "TAPI AKU *PAKSA*"), (2.14, "JUGA *LIVE* MALAM NI")],
    "s2": [(0.0, "SEMALAM TIDUR"), (1.24, "*2 JAM* JE")],
    "e1": [(0.0, "*SUSAH* GILA"), (0.82, "NAK AIM")],
    "e3": [(0.0, "KENAPA KENA"), (0.88, "ISI PELURU *MANUAL?*"), (2.16, "PATUTNYA DIA BUAT"), (3.40, "*AUTO RELOAD* LAH")],
    "e4": [(0.0, "PAKAI *PHONE*"), (0.74, "*SENANG* JE")],
    "e5": [(0.0, "SIAPA LETAK"), (1.00, "*KERUSI* SINI?"), (1.90, "AKU *TERSANGKUT*")],
    "e6": [(0.0, "SEBAB DIA *BANGANG*"), (1.22, "ITU JE"), (1.62, "THE ONLY"), (2.38, "*EXPLAINABLE*"), (3.46, "*REASON*")],
    "f1": [(0.0, "YO *SAKITNYA!*"), (1.84, "*NOOOO!*")],
    "f2": [(0.0, "HABIS LAH"), (0.76, "*MAKANAN* AKU")],
    "f3": [(0.0, "NAMPAK TAK?"), (0.96, "EFFECT TAK CUKUP"), (1.90, "*TIDUR*")],
    "f4": [(0.0, "*WASTED*"), (0.84, "JUST LIKE THAT")],
    "f5": [(0.0, "INGAT GUYS"), (0.76, "*PENGAJARAN*"), (1.48, "COOK YOUR *FOOD*"), (2.75, "*EVERY SINGLE WEEK*")],
    "r1": [(0.0, "APA KATA AKU"), (0.80, "*REVIEW* KEJAP"), (1.64, "BAGUSKAN SARAN SAYA?")],
    "r2": [(0.0, "MY *BRAIN JUICE*"), (1.08, "IS *GONE* ALREADY"), (2.90, "THE ONE TALKING"), (4.18, "TO YOU RIGHT NOW"),
           (4.96, "IS *NOT*"), (5.40, "*ABAMKAMIL GAMING*")],
    "o1": [(0.0, "SENTIASA *LAMPU HIJAU*"), (1.22, "TAKDE TRAFFIC JAM"), (2.36, "TAKDE *CONGESTION*"), (3.48, "TAKDE TRAFFIC LIGHT")],
    "o2": [(0.0, "PERGI KERJA"), (0.82, "SEMUA *LAMPU HIJAU*"), (1.52, "AKU DOAKAN KORANG")],
    "o3": [(0.0, "*BYE BYE!*")],
}
# hold tails (no speech) must not keep a caption on screen
HOLD = {"h2": 0.3, "e1": 0.6, "e6": 0.45, "f4": 0.55, "r2": 0.5}
caps = []
for lid, chunks in CAPS.items():
    for i, (rel, txt) in enumerate(chunks):
        s = at(lid, rel)
        e = at(lid, chunks[i + 1][0]) if i + 1 < len(chunks) else end(lid) - HOLD.get(lid, 0) + 0.15
        caps.append((s, round(e - 0.02, 3), txt))

# --- real chat messages from the stream (read off the live-chat panel) -----------------------
CHATS = [  # id, start, dur, name, colour, msg, position
    ("c-taufik", at("h3", 0.15), 2.9, "taufik", "#3fa7ff", "kenapa kata x original, tiktok ni <span class=\"em\">😩</span>", ""),
    ("c-hanis", end("e1") - 0.62, 1.95, "hanis", "#ff5fa2", "event sng ni", ""),
    ("c-batman1", at("e4", 0.0), 1.7, "Batman Arkham", "#e53935", "pakai phone senang je", ""),
    ("c-batman2", at("r1", 0.0), 2.35, "Batman Arkham", "#e53935", "apa kata abam review kejap", ""),
    ("c-batman3", at("r1", 0.75), 1.75, "Batman Arkham", "#e53935", "sudah terlalu lama menanti", "lower"),
]

# --- stickers: id, start, dur, top(px), emoji, text, text class ---------------------------------
STICKERS = [
    ("st-maki", at("h3", 3.35), 1.05, 1080, "🤬", "", ""),
    ("st-barai", at("s1", 0.1), 2.9, 1180, "😴", "MODE: BARAI", "box"),
    ("st-2jam", at("s2", 1.2), 0.85, 1120, "💤", "2 JAM", "ice"),
    ("st-sng", end("e1") - 0.6, 0.62, 1170, "💀", "SENANG??", "red"),
    ("st-reload", at("e3", 3.38), 1.95, 1150, "🔫", "AUTO RELOAD PLS", "box"),
    ("st-kerusi", at("e5", 1.9), 1.27, 1100, "🪑", "TERSANGKUT", "red"),
    ("st-iq", at("e6", 3.44), 0.86, 1080, "🧠", "100 IQ", "box"),
    ("st-sakit", at("f1", 1.8), 1.05, 1120, "😭", "", ""),
    ("st-makan", at("f2", 0.74), 0.93, 1120, "🍗", "HABIS!", "red"),
    ("st-tidur", at("f3", 1.88), 0.89, 1140, "😵‍💫", "KURANG TIDUR", "box"),
    ("st-chef", at("f5", 0.74), 3.76, 1180, "👨‍🍳", "PENGAJARAN", "box"),
    ("st-hijau", at("o1", 0.0), 4.3, 1150, "🚦", "", ""),
    ("st-doa", at("o2", 1.5), 0.98, 1140, "🤲", "AMIN", "green"),
    ("st-bye", at("o3", 0.0), 1.07, 1140, "👋", "", ""),
]
METER = (at("r2", 0.1), round(at("r2", 2.85) - at("r2", 0.1), 3))
WASTED = (at("f4", 0.84), round(end("f4") - at("f4", 0.84), 3))

# --- punch zooms (webcam) & shakes ---------------------------------------------------------------
PUNCH = [("h1", 0.36, 1.0, True), ("h2", 1.62, 1.12, True), ("h3", 3.40, 1.0, True), ("e1", 1.42, 1.12, False),
         ("e5", 1.90, 1.0, True), ("e6", 3.46, 1.0, True), ("f1", 1.84, 1.0, True), ("f4", 0.0, 1.0, False),
         ("r2", 5.40, 1.12, True), ("o3", 0.0, 1.12, False)]
GSHAKE = [("e1", 0.0), ("e5", 1.90), ("f1", 0.40), ("f1", 1.84)]
FLASH = [(at("s1"), 0.5), (at("e1"), 0.45), (at("f1"), 0.55), (at("r1"), 0.45), (at("o1"), 0.4), (END_START, 0.5)]

# --- sound: SFX from the user's folder + a few utility hits -------------------------------------
SFXDUR = {"vine-boom": 1.306, "emotional-damage": 3.37, "faaah": 1.959, "awkward": 1.489, "violin-screech": 3.997,
          "get-out": 1.032, "laughing-dog": 9.874, "yay": 8.176, "ack": 5.042, "movie": 0.864, "run-vine": 8.28,
          "whoosh": 0.575, "whoosh-short": 0.575, "pop": 0.72, "impact-bass-1": 2.116, "ping": 1.32,
          "notification": 2.456, "glitch-1": 2.638, "riser": 10.03}
SFX = [  # name, time, volume, max duration
    ("impact-bass-1", 0.0, 0.35, 1.2), ("glitch-1", 0.02, 0.22, 0.6),
    ("vine-boom", at("h2", 1.62), 0.5, None),
    ("pop", at("h3", 0.15), 0.6, None),
    ("faaah", at("h3", 3.38), 0.42, None),
    ("whoosh", at("s1") - 0.1, 0.45, None), ("pop", at("s1", 0.1), 0.5, None),
    ("ping", at("s2", 1.22), 0.8, None),
    ("whoosh", at("e1") - 0.1, 0.45, None),
    ("pop", end("e1") - 0.62, 0.6, None), ("awkward", end("e1") - 0.55, 1.3, None),
    ("pop", at("e3", 3.38), 0.5, None),
    ("pop", at("e4"), 0.6, None),
    ("violin-screech", at("e5", 1.88), 0.32, 1.3),
    ("vine-boom", at("e6", 3.44), 0.55, None),
    ("whoosh", at("f1") - 0.1, 0.45, None), ("ack", at("f1", 1.8), 0.4, 1.0),
    ("pop", at("f2", 0.74), 0.5, None),
    ("movie", at("f4", 0.84), 0.5, None), ("emotional-damage", at("f4", 0.9), 0.42, None),
    ("pop", at("r1"), 0.6, None), ("pop", at("r1", 0.75), 0.55, None),
    ("whoosh-short", at("r2", 0.1), 0.45, None),
    ("vine-boom", at("r2", 5.40), 0.45, None), ("laughing-dog", end("r2") - 0.5, 0.35, 1.3),
    ("whoosh", at("o1") - 0.1, 0.45, None),
    ("yay", at("o2", 1.5), 0.35, 2.4),
    ("notification", END_START + 0.35, 0.5, None),
]
# music: bed (Jon's track, voice removed) -> French meme song for the cooking lesson -> outro song
MUSIC = [
    ("bgm-a", "assets/audio/bed_jon.wav", 0.0, at("f5"), 0.0, 0.8, 0.0, 0.2),
    ("bgm-fr", "assets/sfx/french.mp3", at("f5") - 0.05, round(at("r1") - at("f5") + 0.05, 3), 0.0, 0.9, 0.15, 0.25),
    ("bgm-b", "assets/audio/bed_jon.wav", at("r1"), round(at("o1") - at("r1"), 3), 30.0, 0.8, 0.2, 0.3),
    ("bgm-out", "assets/sfx/outro-song.mp3", at("o1") - 0.1, round(TOTAL - at("o1") + 0.1, 3), 0.0, 0.32, 0.2, 0.8),
]

# --- colour grades (HyperFrames media-treatment payloads) --------------------------------------
# webcam: flat, cool, a bit dark -> lift exposure/shadows, warm skin, add contrast + gentle vignette
G_CAM = {"preset": "skin-soft", "intensity": 0.5,
         "adjust": {"exposure": 0.16, "contrast": 0.16, "highlights": -0.3, "shadows": 0.2, "whites": -0.1,
                    "blacks": -0.06, "temperature": 0.07, "tint": 0.02, "vibrance": 0.16},
         "details": {"vignette": 0.28}}
# gameplay: punchy, premium -> deep contrast, vibrance, soft bloom, vignette
G_GAME = {"preset": "deep-contrast", "intensity": 0.5,
          "adjust": {"exposure": 0.05, "contrast": 0.1, "highlights": -0.18, "shadows": 0.16, "vibrance": 0.24,
                     "temperature": 0.02},
          "details": {"vignette": 0.22}, "effects": {"bloom": 0.2}}
G_MONO = {"preset": "mono-clean", "intensity": 1.0, "adjust": {"contrast": 0.25}, "details": {"vignette": 0.35}}
def attr(g): return html.escape(json.dumps(g, separators=(",", ":")), quote=True)
def f(x): return f"{x:.3f}".rstrip("0").rstrip(".")

def caption_html(txt):
    out = []
    for w in txt.split(" "):
        k = w.startswith("*") or w.endswith("*") or w.endswith("*?") or w.endswith("*!")
        out.append(f'<span class="w{" k" if k else ""}">{html.escape(w.replace("*", ""))}</span>')
    return "".join(out)

# --- HTML pieces ---------------------------------------------------------------------------------
cams, games = [], []
for i, ln in enumerate(LINES):
    s, d, lid = ln["start"], ln["dur"], ln["id"]
    cams.append(f'        <div class="cw" id="cw-{lid}" style="z-index:{10 + i}">'
                f'<video id="cam-{lid}" class="clip cam" src="assets/clips/{lid}_cam.mp4" data-start="{f(s)}" '
                f'data-duration="{f(d)}" data-track-index="1" muted playsinline data-color-grading="{attr(G_CAM)}"></video></div>')
    games.append(f'        <div class="gw" id="gw-{lid}" style="z-index:{10 + i}">'
                 f'<video id="game-{lid}" class="clip game" src="assets/clips/{lid}_game.mp4" data-start="{f(s)}" '
                 f'data-duration="{f(d)}" data-track-index="2" data-has-audio="true" data-volume="1" playsinline '
                 f'data-color-grading="{attr(G_GAME)}"></video></div>')
# WASTED: black-and-white freeze over the end of f4 (both zones)
ws, wd = WASTED
games.append(f'        <img id="freeze-game" class="clip still" src="assets/img/f4_freeze.jpg" alt="" style="z-index:60;height:1300px" '
             f'data-start="{f(ws)}" data-duration="{f(wd)}" data-track-index="3" data-color-grading="{attr(G_MONO)}" />')
cams.append(f'        <img id="freeze-cam" class="clip still" src="assets/img/f4_cam_freeze.jpg" alt="" style="z-index:60;height:620px" '
            f'data-start="{f(ws)}" data-duration="{f(wd)}" data-track-index="3" data-color-grading="{attr(G_MONO)}" />')

chat_html = []
for cid, s, d, name, col, msg, pos in CHATS:
    chat_html.append(f'      <div id="{cid}" class="clip chat {pos}" data-start="{f(s)}" data-duration="{f(d)}" data-track-index="5">'
                     f'<div class="chat-in"><div class="av" style="background:{col}">{html.escape(name[0].upper())}</div>'
                     f'<div><div class="who" style="color:{col}">{html.escape(name)}<small>· live chat</small></div>'
                     f'<div class="msg">{msg}</div></div></div></div>')

stk_html = []
for sid, s, d, top, emo, txt, cls in STICKERS:
    inner = (f'<span class="emo">{emo}</span>' if emo else "") + (f'<span class="txt {cls}">{html.escape(txt)}</span>' if txt else "")
    stk_html.append(f'      <div id="{sid}" class="clip stk" style="top:{top}px" data-start="{f(s)}" data-duration="{f(d)}" '
                    f'data-track-index="6"><div class="stk-in">{inner}</div></div>')

cap_html = [f'        <div id="cap-{i}" class="clip cap" data-start="{f(s)}" data-duration="{f(e - s)}">'
            f'<div class="cap-in">{caption_html(txt)}</div></div>' for i, (s, e, txt) in enumerate(caps)]

aud = []
for mid, src, s, d, ms, vol, fi, fo in MUSIC:
    aud.append(f'      <audio id="{mid}" class="clip" src="{src}" data-start="{f(s)}" data-duration="{f(d)}" '
               f'data-media-start="{f(ms)}" data-volume="{vol}" data-fade-in="{fi}" data-fade-out="{fo}" data-track-index="11"></audio>')
for i, (name, s, vol, mx) in enumerate(SFX):
    s = max(0.0, s); d = min(SFXDUR[name], mx or 99, TOTAL - s)
    aud.append(f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.mp3" data-start="{f(s)}" data-duration="{f(d)}" '
               f'data-volume="{vol}"{" data-fade-out=\"0.15\"" if mx else ""} data-track-index="12"></audio>')

punches = [{"id": a, "t": at(a, r), "z": z, "shake": sh} for a, r, z, sh in PUNCH]
T = {"lines": [{"id": l["id"], "start": l["start"], "dur": l["dur"], "cuts": l["cuts"]} for l in LINES],
     "punches": punches, "gshakes": [{"id": a, "t": at(a, r)} for a, r in GSHAKE], "flashes": FLASH,
     "hook_end": end("h2") - 0.3, "meter": [METER[0], METER[0] + METER[1]], "wasted": [ws, ws + wd], "end_start": END_START}

page = open(os.path.join(ROOT, "build", "template.html")).read()
for k, v in {"{{TOTAL}}": f(TOTAL), "{{CAMS}}": "\n".join(cams), "{{GAMES}}": "\n".join(games),
             "{{CHATS}}": "\n".join(chat_html), "{{STICKERS}}": "\n".join(stk_html), "{{CAPTIONS}}": "\n".join(cap_html),
             "{{AUDIO}}": "\n".join(aud), "{{HOOK_DUR}}": f(end("h2") - 0.3),
             "{{METER_START}}": f(METER[0]), "{{METER_DUR}}": f(METER[1]),
             "{{WASTED_START}}": f(ws), "{{WASTED_DUR}}": f(wd),
             "{{END_START}}": f(END_START), "{{END_DUR}}": f(END_DUR), "{{TIMELINE_JSON}}": json.dumps(T)}.items():
    page = page.replace(k, v)
open(os.path.join(ROOT, "index.html"), "w").write(page)
print(f"total {TOTAL}s  lines {len(LINES)}  captions {len(caps)}  chats {len(CHATS)}  stickers {len(STICKERS)}  sfx {len(SFX)}")
