#!/usr/bin/env python3
"""Generate index.html for the Majlis Apresiasi 2026 TikTok short (1080x1920, 30fps).
Every cut sits on the song's beat grid (80.75 BPM -> 0.743 s/beat, 2 beats per short shot)."""
import json, html, os
B = 60 / 80.75
def bt(n): return round(n * B, 3)

# id, start(beats), length(beats), per-shot exposure trim
SHOTS = [
 ("h1", 0, 2, -0.10), ("h2", 2, 2, -0.06), ("h3", 4, 2, -0.10),
 ("t1", 6, 4, -0.22), ("p3", 10, 2, -0.16), ("tk", 12, 4, -0.12), ("tr", 16, 2, -0.06),
 ("pk", 18, 4, -0.10), ("pd", 22, 5, -0.10),
 ("g1", 27, 3, -0.08), ("g2", 30, 3, -0.08),
 ("c1", 33, 4, -0.12), ("c2", 37, 2, -0.12), ("c3", 39, 3, -0.12),
]
END0 = bt(42)          # 31.21 end card: four polaroids drop on the beat
HIT = 33.19            # song's final hit -> group photo lands
TOTAL = 35.6
REVEAL = bt(30) + 1.0  # box lifts ~0.5 s of source into the 0.5x slow-mo shot

def grade(exp):
    g = {"preset": "vintage-wash", "intensity": 0.5,
         "adjust": {"exposure": exp, "contrast": 0.16, "highlights": -0.7, "whites": -0.35,
                    "shadows": 0.05, "blacks": -0.1, "temperature": 0.05, "tint": 0.01,
                    "vibrance": 0.08, "saturation": -0.06},
         "details": {"vignette": 0.14, "grain": 0.1, "grainSize": 0.2, "grainRoughness": 0.6}}
    return html.escape(json.dumps(g, separators=(",", ":")), quote=True)

# captions: id, start, end, html, class
CAPS = [
 ("cap-hook1", 0.0,  bt(3) - 0.05, 'Setahun berusaha…', "big"),
 ("cap-hook2", bt(3), bt(6) - 0.12, '…hari ini, mereka <em>diraikan.</em>', "big"),
 ("cap-p3",  bt(10) + 0.08, bt(12) - 0.08, 'Melangkah penuh bangga', ""),
 ("cap-tk",  bt(12) + 0.1, bt(16) - 0.08, 'Setiap usaha, ada harganya', ""),
 ("cap-tr",  bt(16) + 0.08, bt(18) - 0.08, 'Bakat yang bersinar', ""),
 ("cap-g1",  bt(27) + 0.1, bt(30) - 0.08, 'Saat yang dinanti…', ""),
 ("cap-c1",  bt(33) + 0.15, bt(37) - 0.08, '<span class="kick">CHORAL SPEAKING</span><br/>Suara yang bersatu', ""),
 ("cap-c2",  bt(37) + 0.1, bt(39) - 0.08, 'Satu hati, satu irama', ""),
 ("cap-c3",  bt(39) + 0.1, bt(42) - 0.1, 'Terus bersinar, selamanya', ""),
]

SFX = [  # id, file, start, dur, vol
 ("sfx-hook", "impact-bass-1.mp3", 0.0, 2.1, 0.22),
 ("sfx-w1", "whoosh-short.mp3", bt(6) - 0.2, 0.57, 0.22),
 ("sfx-pop1", "pop.mp3", bt(6) + 0.55, 0.72, 0.14),
 ("sfx-w2", "whoosh-short.mp3", bt(18) - 0.2, 0.57, 0.16),
 ("sfx-w3", "whoosh-short.mp3", bt(27) - 0.2, 0.57, 0.2),
 ("sfx-riser", "riser3.wav", REVEAL - 3.1, 3.1, 0.22),
 ("sfx-hit", "impact-bass-1.mp3", REVEAL, 2.1, 0.42),
 ("sfx-spark", "sparkle.mp3", REVEAL + 0.05, 1.8, 0.32),
 ("sfx-w4", "whoosh-short.mp3", END0 - 0.2, 0.57, 0.22),
 ("sfx-drop1", "pop.mp3", END0 + 0.05, 0.72, 0.12),
 ("sfx-drop2", "pop.mp3", round(bt(43), 3) + 0.05, 0.72, 0.12),
 ("sfx-drop3", "pop.mp3", round(bt(44), 3) - 0.25, 0.72, 0.12),
 ("sfx-chime", "chime.mp3", HIT, 2.4, 0.24),
]

# deterministic sparkle burst for the reveal
SPARKS = []
import math
for i in range(22):
    a = (i * 137.508) % 360
    r = 220 + (i * 53) % 260
    SPARKS.append((round(math.cos(math.radians(a)) * r), round(math.sin(math.radians(a)) * r * 1.15), 8 + (i * 5) % 12))

vids = []
for z, (sid, s, n, exp) in enumerate(SHOTS):
    st, du = bt(s), round(bt(s + n) - bt(s), 3)
    vids.append(f'''      <div id="w-{sid}" class="shotwrap"><video id="v-{sid}" class="clip shot" src="assets/clips/{sid}.mp4" data-start="{st}" data-duration="{du}" data-track-index="1" muted playsinline data-color-grading="{grade(exp)}"></video></div>''')

caps = []
for cid, s, e, txt, cls in CAPS:
    caps.append(f'''        <div id="{cid}" class="clip cap {cls}" data-start="{round(s,3)}" data-duration="{round(e-s,3)}"><div class="cap-in">{txt}</div></div>''')

sfx = "\n".join(f'      <audio id="{i}" class="clip" src="assets/sfx/{f}" data-start="{round(s,3)}" data-duration="{d}" data-volume="{v}" data-track-index="12"></audio>' for i, f, s, d, v in SFX)
sparks = "".join(f'<i id="spk-{i}" class="spk" style="width:{s}px;height:{s}px"></i>' for i, (x, y, s) in enumerate(SPARKS))

T = dict(total=TOTAL, shots=[dict(id=s, start=bt(a), end=bt(a + n)) for s, a, n, _ in SHOTS],
         caps=[dict(id=c, start=round(s,3), end=round(e,3)) for c, s, e, _, _ in CAPS],
         sparks=[[x, y] for x, y, _ in SPARKS], drops=[END0 + 0.02, bt(43) + 0.02, bt(44) - 0.28, HIT - 0.06], end0=END0, reveal=round(REVEAL,3), title=[bt(6), bt(10)], pk=[bt(18), bt(22)], pd=[bt(22), bt(27)], cuts=[bt(6), bt(27), END0])

tpl = open(os.path.join(os.path.dirname(__file__), "template.html"), encoding="utf-8").read()
out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{VIDEOS}}", "\n".join(vids))
          .replace("{{CAPS}}", "\n".join(caps)).replace("{{SFX}}", sfx).replace("{{SPARKS}}", sparks)
          .replace("{{T}}", json.dumps(T)).replace("{{END0}}", str(END0)).replace("{{ENDDUR}}", str(round(TOTAL - END0, 3)))
          .replace("{{TITLE0}}", str(bt(6))).replace("{{TITLED}}", str(round(bt(10) - bt(6) - 0.06, 3)))
          .replace("{{PK0}}", str(round(bt(18) + 0.15, 3))).replace("{{PKD}}", str(round(bt(22) - bt(18) - 0.3, 3)))
          .replace("{{PD0}}", str(round(bt(22) + 0.2, 3))).replace("{{PDD}}", str(round(bt(27) - bt(22) - 0.3, 3)))
          .replace("{{REV0}}", str(round(REVEAL - 0.05, 3))).replace("{{REVD}}", str(round(bt(33) - REVEAL - 0.03, 3))))
open(os.path.join(os.path.dirname(__file__), "..", "index.html"), "w", encoding="utf-8").write(out)
print("ok", TOTAL, "end0", END0, "reveal", REVEAL)
