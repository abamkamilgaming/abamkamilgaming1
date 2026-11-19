"""Generate index.html (HyperFrames composition) from plan.json, beats.json and timeline.json.

Layers: baked speed-ramp base video -> beat punch/shake (GSAP on #cam) -> light leaks + flashes
-> intro / counter / outro type -> song + SFX.
usage: python3 build/gen.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
plan = json.load(open(ROOT / "build/plan.json"))
tl = json.load(open(ROOT / "build/timeline.json"))
B = tl["beats"]
DUR = plan["duration"]
LEAD = plan["lead"]


def tv(x):
    if isinstance(x, (int, float)): return float(x)
    return B[int(x[1:-1])] - LEAD if x.endswith("-") else B[int(x[1:])]


hits, cuts = [], []
for i, s in enumerate(plan["shots"]):
    for k, _ in s["keys"]:
        if isinstance(k, str) and not k.endswith("-"): hits.append(round(tv(k), 3))
    if i > 0: cuts.append(round(tv(s["keys"][0][0]), 3))
hits = sorted(set(hits))
DROP, FINAL = B[11], B[39]
extra_punch = [B[28]]  # snare accent the plan does not land a hit on

# ---------- audio ----------
sfx, n, lanes = [], 0, []
def add(src, t, dur, vol, media_start=None):
    global n
    t = max(0, t)
    lane = next((i for i, e in enumerate(lanes) if e <= t), None)  # first Studio lane free at t
    if lane is None: lanes.append(0); lane = len(lanes) - 1
    lanes[lane] = t + dur
    ms = f' data-media-start="{media_start}"' if media_start is not None else ""
    sfx.append(f'      <audio id="sfx-{n}" class="clip" src="assets/sfx/{src}" data-start="{t:.3f}" data-duration="{dur:.3f}"{ms} data-volume="{vol}" data-track-index="{3 + lane}"></audio>')
    n += 1

for j, h in enumerate(hits):
    if h in (DROP, FINAL): continue
    add("whoosh-short.mp3" if j % 2 else "whoosh.mp3", h - 0.30, 0.57, 0.22 if h > DROP else 0.16)
add("riser.mp3", DROP - 2.07, 2.07, 0.32, media_start=7.93)
add("whoosh.mp3", DROP - 0.30, 0.57, 0.3)
add("impact-bass-1.mp3", DROP - 0.015, 2.1, 0.75)
add("whoosh.mp3", FINAL - 0.30, 0.57, 0.25)
add("impact-bass-2.mp3", FINAL - 0.015, 1.3, 0.55)
add("sparkle.mp3", FINAL + 0.25, 1.05, 0.22)
for t in [B[1], B[2], B[3]]:
    add("pop.mp3", t - 0.01, 0.3, 0.14)

# counters: one per kid (shots s1..s7)
counters = []
for i, s in enumerate(plan["shots"][:7]):
    first_hit = next(tv(k) for k, _ in s["keys"] if isinstance(k, str) and not k.endswith("-")) if i else B[0]
    end = tv(s["keys"][-1][0])
    counters.append({"i": i + 1, "start": round(first_hit, 3), "end": round(end, 3)})

T = {"dur": DUR, "hits": hits, "cuts": cuts, "drop": DROP, "final": FINAL, "beats": B,
     "extra": extra_punch, "counters": counters, "introEnd": round(tv("b5-"), 3)}

counter_html = "\n".join(
    f'        <div class="ctr" id="ctr-{c["i"]}"><span class="ctr-n">{c["i"]:02d}</span><span class="ctr-bar"><i></i></span><span class="ctr-t">/ 07</span></div>'
    for c in counters)

html = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {{
        --ground: #050505;
        --ink: #fff8ec;
        --gold: #ffc56b;
        --font-display: "Montserrat", sans-serif;
        --font-label: "Oswald", sans-serif;
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }}
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 46%; }}
      #base {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}

      /* light leaks: warm burns that ride the cuts */
      .leak {{ position: absolute; inset: -200px; pointer-events: none; mix-blend-mode: screen; opacity: 0; z-index: 40; }}
      #leak-a {{ background: radial-gradient(ellipse 520px 900px at 8% 30%, rgba(255,150,40,0.95), rgba(255,90,20,0.45) 45%, rgba(0,0,0,0) 75%); }}
      #leak-b {{ background: radial-gradient(ellipse 600px 760px at 96% 70%, rgba(255,205,120,0.9), rgba(255,120,60,0.4) 45%, rgba(0,0,0,0) 75%); }}
      #flash {{ position: absolute; inset: 0; z-index: 60; background: #fff6e6; opacity: 0; pointer-events: none; }}
      #black {{ position: absolute; inset: 0; z-index: 95; background: #000; opacity: 0; pointer-events: none; }}

      /* type */
      .shadow {{ text-shadow: 0 6px 30px rgba(0,0,0,0.45); }}
      #intro {{ position: absolute; left: 0; right: 0; top: 1290px; z-index: 70; text-align: center; color: var(--ink); }}
      #i-label {{ font: 600 34px/1 var(--font-label); letter-spacing: 14px; color: var(--gold); opacity: 0; }}
      #i-the {{ font: 800 70px/1 var(--font-display); letter-spacing: 18px; margin-top: 26px; opacity: 0; }}
      #i-word {{ font: 900 210px/0.95 var(--font-display); letter-spacing: 6px; margin-top: 4px; white-space: nowrap; }}
      #i-word span {{ display: inline-block; opacity: 0; }}
      #i-rule {{ width: 520px; height: 4px; margin: 26px auto 0; background: var(--gold); transform-origin: 50% 50%; transform: scaleX(0); }}

      .ctr {{ position: absolute; left: 72px; bottom: 210px; z-index: 70; display: flex; align-items: center; gap: 18px; color: var(--ink); opacity: 0; }}
      .ctr-n {{ font: 700 92px/1 var(--font-label); letter-spacing: 2px; }}
      .ctr-bar {{ position: relative; width: 120px; height: 4px; background: rgba(255,248,236,0.3); overflow: hidden; }}
      .ctr-bar i {{ position: absolute; inset: 0; background: var(--gold); transform-origin: 0 50%; transform: scaleX(0); }}
      .ctr-t {{ font: 500 34px/1 var(--font-label); letter-spacing: 6px; opacity: 0.85; }}

      #outro {{ position: absolute; left: 0; right: 0; top: 760px; z-index: 70; text-align: center; color: var(--ink); opacity: 0; }}
      #o-word {{ font: 900 150px/1 var(--font-display); letter-spacing: 8px; white-space: nowrap; }}
      #o-word span {{ display: inline-block; }}
      #o-sub {{ font: 600 36px/1 var(--font-label); letter-spacing: 16px; color: var(--gold); margin-top: 22px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <div id="cam">
        <video id="base" class="clip" src="assets/video/base.mp4" data-start="0" data-duration="{DUR}" data-track-index="1" muted playsinline></video>
      </div>
      <div class="leak" id="leak-a"></div>
      <div class="leak" id="leak-b"></div>
      <div id="flash"></div>

      <div id="intro" class="shadow">
        <div id="i-label">SPEED RAMP · 2026</div>
        <div id="i-the">THE</div>
        <div id="i-word"><span>S</span><span>Q</span><span>U</span><span>A</span><span>D</span></div>
        <div id="i-rule"></div>
      </div>
{counter_html}
      <div id="outro" class="shadow">
        <div id="o-word">{"".join(f"<span>{c}</span>" if c != " " else "<span>&nbsp;</span>" for c in "THE SQUAD")}</div>
        <div id="o-sub">SPEED RAMP · 2026</div>
      </div>
      <div id="black"></div>

      <audio id="song" class="clip" src="assets/audio/song.wav" data-start="0" data-duration="{DUR}" data-volume="1" data-track-index="2"></audio>
{chr(10).join(sfx)}
    </div>
    <script>
      const T = {json.dumps(T)};
      const tl = gsap.timeline({{ paused: true }});
      const cam = "#cam";

      // --- beat punch: every slow-mo hit lands with a small scale kick
      tl.set(cam, {{ scale: 1.0, x: 0, y: 0, rotation: 0 }}, 0);
      T.hits.concat(T.extra).forEach((h) => {{
        if (h === T.drop || h === T.final) return;
        tl.fromTo(cam, {{ scale: 1.055 }}, {{ scale: 1.0, duration: 0.3, ease: "power3.out", immediateRender: false }}, h);
      }});
      // --- the drop: big slam + shake
      tl.fromTo(cam, {{ scale: 1.2 }}, {{ scale: 1.0, duration: 0.45, ease: "power4.out", immediateRender: false }}, T.drop);
      [[-16, 10, -1.2], [14, -8, 1.0], [-10, 6, -0.6], [7, -4, 0.4], [-3, 2, 0], [0, 0, 0]].forEach(([x, y, r], i) =>
        tl.to(cam, {{ x: x, y: y, rotation: r, duration: 0.04, ease: "none" }}, T.drop + i * 0.04));
      // --- final hit
      tl.fromTo(cam, {{ scale: 1.14 }}, {{ scale: 1.0, duration: 0.5, ease: "power3.out", immediateRender: false }}, T.final);
      [[10, -6], [-8, 5], [5, -3], [0, 0]].forEach(([x, y], i) => tl.to(cam, {{ x: x, y: y, duration: 0.04, ease: "none" }}, T.final + i * 0.04));
      // slow creep on the outro
      tl.to(cam, {{ scale: 1.06, duration: T.dur - T.final - 0.5, ease: "none" }}, T.final + 0.5);

      // --- light leaks + flash on every cut (cuts sit mid-whip, 0.12 s before the hit)
      T.cuts.forEach((c, i) => {{
        const el = i % 2 ? "#leak-b" : "#leak-a";
        tl.fromTo(el, {{ opacity: 0, x: i % 2 ? 60 : -60 }}, {{ opacity: 0.75, x: 0, duration: 0.1, ease: "none", immediateRender: false }}, c - 0.06);
        tl.to(el, {{ opacity: 0, x: i % 2 ? -40 : 40, duration: 0.42, ease: "power2.out" }}, c + 0.04);
        tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: 0.22, duration: 0.03, ease: "none", immediateRender: false }}, c - 0.01);
        tl.to("#flash", {{ opacity: 0, duration: 0.18, ease: "power2.out" }}, c + 0.02);
      }});
      [[T.drop, 0.85], [T.final, 0.6]].forEach(([t, a]) => {{
        tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: a, duration: 0.03, ease: "none", immediateRender: false }}, t - 0.03);
        tl.to("#flash", {{ opacity: 0, duration: 0.35, ease: "power2.out" }}, t);
      }});

      // --- intro type, letters land on half-beats
      const b = T.beats, half = (b[2] - b[0]) / 4;
      tl.fromTo("#i-label", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }}, b[0]);
      tl.fromTo("#i-the", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2)" }}, b[0]);
      gsap.utils.toArray("#i-word span").forEach((s, i) =>
        tl.fromTo(s, {{ opacity: 0, scale: 1.8, y: -30 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "back.out(2.6)" }}, b[1] + i * half));
      tl.fromTo("#i-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power3.out" }}, b[3] + half);
      gsap.utils.toArray("#i-word span").forEach((s, i) =>
        tl.to(s, {{ x: (i - 2) * 9, duration: T.introEnd - b[3], ease: "none" }}, b[3] + 0.2));
      tl.to("#intro", {{ opacity: 0, scale: 1.6, duration: 0.14, ease: "power2.in" }}, T.introEnd - 0.1);

      // --- kid counter 01..07, bar fills across the shot
      T.counters.forEach((c) => {{
        const el = "#ctr-" + c.i, d = c.end - c.start;
        const t0 = c.i === 1 ? T.introEnd - 1.3 : c.start;
        tl.fromTo(el, {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.18, ease: "power3.out" }}, t0);
        tl.fromTo(el + " .ctr-bar i", {{ scaleX: 0 }}, {{ scaleX: 1, duration: Math.max(0.2, c.end - t0 - 0.05), ease: "none" }}, t0);
        tl.to(el, {{ opacity: 0, duration: 0.06, ease: "none" }}, c.end - 0.06);
      }});

      // --- outro
      tl.fromTo("#outro", {{ opacity: 0, scale: 1.25 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "power3.out" }}, T.final);
      gsap.utils.toArray("#o-word span").forEach((s, i) =>
        tl.fromTo(s, {{ x: 0 }}, {{ x: (i - 4) * 7, duration: T.dur - T.final, ease: "none" }}, T.final));
      tl.fromTo("#black", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "power1.in" }}, T.dur - 0.6);

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(ROOT / "index.html", "w").write(html)
print("hits", hits); print("cuts", cuts); print("sfx", n)
