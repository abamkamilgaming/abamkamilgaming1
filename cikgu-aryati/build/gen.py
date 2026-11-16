"""Generate index.html for the Cikgu Aryati short (1080x1920, 60 fps).
Style copied from "Contoh content": top = comic word typed letter by letter (white, black 3D edge,
yellow glow); bottom = torn notebook strip with rainbow letters + the reference ding.
Here: top = the word people usually use (wrong, red X), bottom = Cikgu's correct word (green tick).
Run: python3 build/gen.py  (after build/aroll.py)"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDL = json.load(open(os.path.join(ROOT, "build", "edl.json")))
L = EDL["lines"]
DUR = EDL["dur"]

PAIRS = [  # (wrong as asked, correct from Tatabahasa list, sticker)
    ("VIRAL", "Tular", None),
    ("SELFIE", "Swafoto", None),
    ("HASHTAG", "Tanda pagar", None),
    ("EMOJI", "Emoji", "SAMA JE!"),
    ("NETIZEN", "Warganet", None),
    ("KUEY TEOW", "Kuetiau", None),
    ("MEE HOON", "Bihun @ Mihun", "DUA-DUA BETUL!"),
    ("MEE GORENG", "Mi goreng", None),
]
RAINBOW = ["#ec1c24", "#f7931e", "#1ea0e6", "#3bb54a", "#ec4899", "#8e44ad"]
GRADE = {"preset": "skin-soft", "intensity": 0.62,
         "adjust": {"exposure": 0.08, "contrast": 0.08, "highlights": -0.24, "shadows": 0.14,
                    "whites": -0.06, "blacks": 0.02, "temperature": 0.05, "tint": 0.01,
                    "vibrance": 0.06, "saturation": 0.03},
         "details": {"vignette": 0.05}}

E = lambda s: html.escape(s, quote=True)
r3 = lambda x: round(x, 3)

# ---------- timing ----------
pairs = []
for i, (wrong, right, sticker) in enumerate(PAIRS):
    q, a = L[2 + 2 * i], L[3 + 2 * i]
    nxt = L[4 + 2 * i]["s"]
    pairs.append(dict(i=i, wrong=wrong, right=right, sticker=sticker, qs=max(q["s"] - 0.03, 2.0),
                      a_s=a["s"], end=nxt - 0.02))
END_S = L[18]["s"]           # "Dapat sesuatu?"
HOOK_END = pairs[0]["qs"]

def top_size(t):  return min(150, int(800 / (0.62 * len(t))))
def bot_size(t):  return min(185, int(740 / (0.56 * len(t))))

def letters(t, cls, colors=None):
    out, k = [], 0
    for ch in t:
        if ch == " ":
            out.append('<span class="sp"> </span>'); continue
        style = f' style="color:{colors[k % len(colors)]}"' if colors else ""
        out.append(f'<span class="{cls}"{style}>{E(ch)}</span>'); k += 1
    return "".join(out)

X_SVG = ('<svg viewBox="0 0 100 100"><path d="M22 22 L78 78 M78 22 L22 78" stroke="#fff" '
         'stroke-width="17" stroke-linecap="round"/></svg>')
V_SVG = ('<svg viewBox="0 0 100 100"><path d="M22 53 L42 72 L79 30" fill="none" stroke="#fff" '
         'stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/></svg>')

groups, js, sfx = [], [], []
def add_sfx(name, t, vol, dur):
    sfx.append((name, r3(max(0, t)), vol, dur))

# ---------- hook ----------
js.append(f"""
  // HOOK — on screen from frame 0 (thumbnail), settles, then flies out
  tl.fromTo("#hook-a", {{scale: 1.06, rotation: -4}}, {{scale: 1, rotation: -3, duration: 0.28, ease: "back.out(2.2)"}}, 0);
  tl.fromTo("#hook-b", {{scale: 1.1, y: 18}}, {{scale: 1, y: 0, duration: 0.32, ease: "back.out(2.4)"}}, 0.04);
  tl.fromTo("#hook-tag", {{y: -30, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.25, ease: "power3.out"}}, 0.35);
  tl.to("#hook-b", {{scale: 1.06, duration: 0.09, yoyo: true, repeat: 3, ease: "sine.inOut"}}, 0.95);
  tl.fromTo("#hook-x", {{scale: 2.6, opacity: 0, rotation: -25}}, {{scale: 1, opacity: 1, rotation: -12, duration: 0.22, ease: "back.out(2)"}}, 0.62);
  tl.to("#hook", {{y: -260, opacity: 0, duration: 0.22, ease: "power3.in"}}, {r3(HOOK_END - 0.24)});
  tl.fromTo("#nametag", {{x: -420, opacity: 0}}, {{x: 0, opacity: 1, duration: 0.3, ease: "power3.out"}}, 0.55);
  tl.to("#nametag", {{x: -420, opacity: 0, duration: 0.2, ease: "power2.in"}}, {r3(HOOK_END - 0.2)});
""")
add_sfx("impact-bass-1", 0.0, 0.55, 1.6)
add_sfx("pop", 0.22, 0.35, 0.6)
add_sfx("error", 0.6, 0.22, 0.9)
add_sfx("whoosh", 0.5, 0.3, 0.55)
add_sfx("whoosh-short", HOOK_END - 0.26, 0.35, 0.55)

# ---------- word pairs ----------
for p in pairs:
    i, qs, a_s, end = p["i"], p["qs"], p["a_s"], p["end"]
    gid = f"p{i + 1}"
    ts, bs = top_size(p["wrong"]), bot_size(p["right"])
    sticker = (f'<div class="sticker" id="{gid}-st"><span>{E(p["sticker"])}</span></div>' if p["sticker"] else "")
    groups.append(f"""
      <div id="{gid}" class="clip grp" data-start="{r3(qs)}" data-duration="{r3(end - qs)}" data-track-index="3">
        <div class="count" id="{gid}-n">{i + 1}<small>/8</small></div>
        <div class="top" id="{gid}-top">
          <div class="badge bad" id="{gid}-x">{X_SVG}</div>
          <div class="word" style="font-size:{ts}px">{letters(p['wrong'], 'tl')}<i class="strike" id="{gid}-s" data-layout-allow-occlusion></i></div>
        </div>
        <div class="strip" id="{gid}-strip">
          <div class="paper" data-layout-allow-occlusion></div>
          <div class="badge good" id="{gid}-v">{V_SVG}</div>
          <div class="rb" style="font-size:{bs}px">{letters(p['right'], 'bl', RAINBOW)}</div>
          {sticker}
        </div>
        <div class="burst" id="{gid}-b">{''.join(f'<b style="--a:{k * 45}deg"></b>' for k in range(8))}</div>
      </div>""")
    q_len = a_s - qs
    type_d = min(0.28, max(0.14, q_len * 0.45))
    js.append(f"""
  // #{i + 1} {p['wrong']} -> {p['right']}
  tl.fromTo("#{gid}-n", {{scale: 0.4, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.2, ease: "back.out(3)"}}, {r3(qs)});
  tl.fromTo("#{gid}-top .tl", {{opacity: 0, scale: 1.8, y: -20}}, {{opacity: 1, scale: 1, y: 0, duration: 0.12, ease: "back.out(2.5)", stagger: {r3(type_d / max(1, len(p['wrong'].replace(' ', ''))))}}}, {r3(qs + 0.02)});
  tl.fromTo("#{gid}-x", {{scale: 0, rotation: -90}}, {{scale: 1, rotation: 0, duration: 0.22, ease: "back.out(2.6)"}}, {r3(qs + type_d)});
  tl.fromTo("#{gid}-s", {{scaleX: 0}}, {{scaleX: 1, duration: 0.16, ease: "power3.out"}}, {r3(a_s + 0.02)});
  tl.to("#{gid}-top", {{scale: 0.86, y: -26, duration: 0.2, ease: "power2.out"}}, {r3(a_s + 0.02)});
  tl.to("#{gid}-top .tl", {{color: "#d9d9d9", duration: 0.2}}, {r3(a_s + 0.02)});
  tl.fromTo("#{gid}-strip", {{scaleX: 0.2, scaleY: 0.6, opacity: 0, rotation: -6}}, {{scaleX: 1, scaleY: 1, opacity: 1, rotation: -2, duration: 0.24, ease: "back.out(2)"}}, {r3(a_s - 0.02)});
  tl.fromTo("#{gid}-strip .bl", {{y: 50, scale: 0.3, opacity: 0}}, {{y: 0, scale: 1, opacity: 1, duration: 0.2, ease: "back.out(3)", stagger: 0.025}}, {r3(a_s + 0.02)});
  tl.fromTo("#{gid}-v", {{scale: 0, rotation: 90}}, {{scale: 1, rotation: 0, duration: 0.24, ease: "back.out(2.8)"}}, {r3(a_s + 0.12)});
  tl.fromTo("#{gid}-b b", {{scale: 0, opacity: 1}}, {{scale: 1, opacity: 0, duration: 0.5, ease: "power2.out"}}, {r3(a_s + 0.04)});
  tl.to("#{gid}", {{opacity: 0, duration: 0.07, ease: "power1.in"}}, {r3(end - 0.07)});""")
    if p["sticker"]:
        js.append(f"""
  tl.fromTo("#{gid}-st", {{scale: 0, rotation: 30}}, {{scale: 1, rotation: 8, duration: 0.24, ease: "back.out(3)"}}, {r3(a_s + 0.1)});""")
        add_sfx("pop", a_s + 0.08, 0.4, 0.6)
    add_sfx("whoosh-short", qs - 0.04, 0.16, 0.5)
    add_sfx("ding-contoh", a_s - 0.06, 0.62, 0.95)

# ---------- outro ----------
groups.append(f"""
      <div id="outro" class="clip grp" data-start="{r3(END_S - 0.03)}" data-duration="{r3(DUR - END_S + 0.03)}" data-track-index="3">
        <div class="top" id="o-top"><div class="word" style="font-size:104px">{letters('DAPAT SESUATU?', 'tl')}</div></div>
        <div class="strip wide" id="o-strip">
          <div class="paper" data-layout-allow-occlusion></div>
          <div class="rb two" style="font-size:68px">{letters('Biasakan yang betul,', 'bl', RAINBOW)}<br>{letters('betulkan yang biasa!', 'bl', RAINBOW[2:] + RAINBOW[:2])}</div>
        </div>
        <div class="follow" id="o-follow"><span>FOLLOW</span> untuk tips BM lagi</div>
      </div>""")
js.append(f"""
  // OUTRO
  tl.fromTo("#o-top .tl", {{opacity: 0, scale: 1.8, y: -20}}, {{opacity: 1, scale: 1, y: 0, duration: 0.12, ease: "back.out(2.5)", stagger: 0.03}}, {r3(END_S)});
  tl.fromTo("#o-strip", {{scaleX: 0.2, opacity: 0, rotation: -6}}, {{scaleX: 1, opacity: 1, rotation: -2, duration: 0.26, ease: "back.out(2)"}}, {r3(END_S + 0.55)});
  tl.fromTo("#o-strip .bl", {{y: 40, scale: 0.3, opacity: 0}}, {{y: 0, scale: 1, opacity: 1, duration: 0.18, ease: "back.out(3)", stagger: 0.012}}, {r3(END_S + 0.6)});
  tl.fromTo("#o-follow", {{y: 80, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.3, ease: "back.out(2)"}}, {r3(END_S + 1.0)});
  tl.to("#o-follow span", {{scale: 1.1, duration: 0.14, yoyo: true, repeat: 1, ease: "sine.inOut"}}, {r3(END_S + 1.35)});""")
add_sfx("whoosh-short", END_S - 0.05, 0.2, 0.5)
add_sfx("ding-contoh", END_S + 0.5, 0.6, 0.95)
add_sfx("sparkle", END_S + 0.95, 0.3, 0.8)

# ---------- camera: jump-zoom per line (hides the pause cuts), punch on each answer ----------
cam = []
cam.append("  tl.fromTo('#cam', {scale: 1.0}, {scale: 1.07, duration: %s, ease: 'none'}, 0);" % r3(HOOK_END))
for k in range(2, 19):
    l = L[k]
    s = l["s"] if k > 2 else HOOK_END
    e = L[k + 1]["s"] if k < 18 else DUR
    if l["spk"] == "Q":
        z0, z1 = 1.0, 1.035
    else:
        z0, z1 = 1.16, 1.19
    if k == 18:
        z0, z1 = 1.08, 1.0
    cam.append(f"  tl.set('#cam', {{scale: {z0}}}, {r3(s)});")
    cam.append(f"  tl.to('#cam', {{scale: {z1}, duration: {r3(max(0.05, e - s - 0.01))}, ease: 'none'}}, {r3(s + 0.005)});")
js.insert(0, "\n".join(cam))

# ---------- assemble ----------
audio = "\n".join(
    f'      <audio id="sfx-{n}" class="clip" src="assets/sfx/{name}.mp3" data-start="{t}" data-duration="{d}" '
    f'data-volume="{v}" data-track-index="{10 + n}"></audio>'
    for n, (name, t, v, d) in enumerate(sfx))
grade = E(json.dumps(GRADE, separators=(",", ":")))

page = f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Luckiest Guy"; src: url("assets/fonts/LuckiestGuy.woff2") format("woff2"); font-weight: 400; }}
      @font-face {{ font-family: "Fredoka"; src: url("assets/fonts/Fredoka.woff2") format("woff2"); font-weight: 700; }}
      :root {{ --ground: #000; --ink: #fff; --glow: #ffe600; --bad: #e5262b; --good: #22a447; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); font-family: "Luckiest Guy", sans-serif; }}
      #cam {{ position: absolute; inset: 0; transform-origin: 530px 690px; }}
      #aroll {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}

      /* hook */
      #hook {{ position: absolute; left: 0; right: 0; top: 190px; display: flex; flex-direction: column; align-items: center; gap: 6px; text-align: center; z-index: 20; }}
      #hook-tag {{ font-family: "Fredoka"; font-weight: 700; font-size: 44px; color: #111; background: var(--glow); padding: 8px 26px; border-radius: 40px; border: 5px solid #111; box-shadow: 6px 6px 0 #111; }}
      #hook-a {{ font-size: 132px; line-height: 0.95; color: var(--glow); -webkit-text-stroke: 14px #111; paint-order: stroke fill; text-shadow: 0 10px 0 #111, 0 0 40px rgba(255,230,0,.55); }}
      #hook-b {{ font-size: 64px; line-height: 1; color: #fff; -webkit-text-stroke: 12px #111; paint-order: stroke fill; text-shadow: 0 8px 0 #111, 0 0 36px rgba(255,230,0,.6); }}
      #hook-c {{ font-family: "Fredoka"; font-weight: 700; font-size: 54px; color: #fff; background: var(--bad); padding: 6px 24px 10px; border-radius: 14px; border: 5px solid #111; box-shadow: 6px 6px 0 #111; margin-top: 10px; }}
      #hook-x {{ position: absolute; right: 150px; top: -14px; width: 92px; height: 92px; border-radius: 50%; background: var(--bad); border: 7px solid #111; box-shadow: 6px 6px 0 #111; }}
      #hook-x svg {{ width: 100%; height: 100%; }}
      #nametag {{ position: absolute; left: 50px; top: 1180px; z-index: 18; font-family: "Fredoka"; font-weight: 700; color: #111; background: #fff; border: 5px solid #111; border-radius: 18px; padding: 10px 26px 12px; box-shadow: 7px 7px 0 var(--glow), 7px 7px 0 5px #111; }}
      #nametag b {{ display: block; font-size: 52px; line-height: 1.05; }}
      #nametag small {{ font-size: 32px; color: #444; }}

      /* caption groups */
      .grp {{ position: absolute; inset: 0; z-index: 15; }}
      .count {{ position: absolute; left: 80px; top: 250px; width: 132px; height: 132px; border-radius: 50%; background: var(--glow); border: 7px solid #111; box-shadow: 6px 6px 0 #111; color: #111; font-size: 70px; display: flex; align-items: center; justify-content: center; padding-top: 10px; }}
      .count small {{ font-size: 34px; margin-left: 2px; }}
      .top {{ position: absolute; left: 40px; right: 120px; top: 1035px; display: flex; justify-content: center; align-items: center; gap: 22px; transform-origin: 50% 50%; }}
      .word {{ position: relative; color: #fff; line-height: 1; white-space: nowrap; -webkit-text-stroke: 16px #111; paint-order: stroke fill;
               text-shadow: 6px 9px 0 #111, 0 0 26px rgba(255,230,0,.95), 0 0 60px rgba(255,230,0,.7); padding-top: 12px; }}
      .tl, .bl {{ display: inline-block; }}
      .sp {{ display: inline-block; width: .32em; }}
      .strike {{ position: absolute; left: -4%; right: -4%; top: 50%; height: 18px; margin-top: -4px; background: var(--bad); border: 4px solid #111; border-radius: 10px; transform-origin: 0 50%; transform: rotate(-4deg) scaleX(0); }}
      .badge {{ width: 96px; height: 96px; flex: none; border: 6px solid #111; box-shadow: 5px 5px 0 #111; }}
      .badge svg {{ width: 100%; height: 100%; }}
      .bad {{ border-radius: 50%; background: var(--bad); }}
      .good {{ border-radius: 22px; background: var(--good); position: absolute; left: -38px; top: -40px; }}
      .strip {{ position: absolute; left: 70px; right: 110px; top: 1200px; height: 225px; display: flex; align-items: center; justify-content: center; transform-origin: 50% 50%; }}
      .strip.wide {{ height: 250px; top: 1190px; }}
      .paper {{ position: absolute; inset: 0; background-color: #fbfbf7;
                background-image: repeating-linear-gradient(180deg, transparent 0 34px, #b9d3ee 34px 37px);
                clip-path: polygon(0% 6%, 3% 0%, 7% 5%, 12% 1%, 17% 6%, 22% 0%, 28% 5%, 33% 1%, 39% 6%, 45% 0%, 51% 5%, 57% 1%, 62% 6%, 68% 0%, 74% 5%, 80% 1%, 86% 6%, 91% 0%, 96% 5%, 100% 1%,
                                   99% 50%, 100% 97%, 96% 92%, 91% 100%, 86% 94%, 80% 99%, 74% 93%, 68% 100%, 62% 94%, 57% 99%, 51% 93%, 45% 100%, 39% 94%, 33% 99%, 28% 93%, 22% 100%, 17% 94%, 12% 99%, 7% 93%, 3% 100%, 0% 95%, 1% 50%);
                filter: drop-shadow(0 8px 0 rgba(0,0,0,.35)); }}
      .rb {{ position: relative; font-family: "Fredoka"; font-weight: 700; line-height: 1; white-space: nowrap; -webkit-text-stroke: 5px rgba(0,0,0,.55); paint-order: stroke fill; text-shadow: 3px 5px 0 rgba(0,0,0,.25); }}
      .rb.two {{ text-align: center; line-height: 1.12; }}
      .sticker {{ position: absolute; right: 10px; top: -78px; background: var(--glow); border: 6px solid #111; border-radius: 16px; box-shadow: 5px 5px 0 #111; padding: 8px 20px 4px; }}
      .sticker span {{ font-size: 50px; color: #111; }}
      .burst {{ position: absolute; left: 500px; top: 1312px; width: 0; height: 0; }}
      .burst b {{ position: absolute; left: -10px; top: -10px; width: 20px; height: 20px; background: var(--glow); border: 3px solid #111; border-radius: 4px;
                 transform-origin: 10px 10px; transform: rotate(var(--a)) translateY(-300px) rotate(45deg); }}
      .follow {{ position: absolute; left: 40px; right: 120px; top: 1462px; text-align: center; font-family: "Fredoka"; font-weight: 700; font-size: 46px; color: #fff; -webkit-text-stroke: 8px #111; paint-order: stroke fill; }}
      .follow span {{ display: inline-block; background: #fe2c55; color: #fff; -webkit-text-stroke: 0; padding: 4px 22px 8px; border-radius: 14px; border: 5px solid #111; margin-right: 10px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920" data-fps="60">
      <div id="cam">
        <video id="aroll" class="clip" src="assets/video/aroll.mp4" data-start="0" data-duration="{DUR}" data-track-index="1"
               data-has-audio="true" data-volume="1" playsinline data-color-grading="{grade}"></video>
      </div>

      <div id="hook" class="clip" data-start="0" data-duration="{r3(HOOK_END)}" data-track-index="2" data-layout-allow-overflow>
        <div id="hook-tag">CIKGU BM BETULKAN</div>
        <div id="hook-a">8 PERKATAAN</div>
        <div id="hook-b">YANG KORANG SELALU SALAH!</div>
        <div id="hook-x">{X_SVG}</div>
      </div>
      <div id="nametag" class="clip" data-start="0" data-duration="{r3(HOOK_END)}" data-track-index="4"><b>Cikgu Aryati</b><small>Guru Bahasa Melayu</small></div>
{''.join(groups)}
{audio}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      gsap.set("#nametag", {{ x: -420, opacity: 0 }});
{''.join(js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(ROOT, "index.html"), "w").write(page)
print("index.html written; duration", DUR, "sfx", len(sfx))
for p in pairs: print(f'#{p["i"] + 1} {p["qs"]:.2f} ans {p["a_s"]:.2f} end {p["end"]:.2f}  {p["wrong"]} -> {p["right"]}')
