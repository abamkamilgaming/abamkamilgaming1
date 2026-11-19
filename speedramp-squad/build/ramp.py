"""Speed-ramp renderer.

Reads build/plan.json + build/beats.json, time-remaps each proxy clip so every hit
lands in slow-mo on a song beat and the gaps whip through the camera move, then bakes:
  - shutter motion blur (frames averaged across the exposure window when fast)
  - optical-flow frame interpolation (smooth slow-mo when slower than 1x)
  - radial zoom blur that grows with speed (the speed-ramp "whip" look)
  - colour grade + lighting (exposure match, filmic contrast, teal/gold split tone,
    rich reds, bloom, vignette, fine grain)
Writes assets/video/base.mp4 (1080x1920, 60 fps, silent) and build/timeline.json.

usage: python3 build/ramp.py <proxy_dir> [--draft]
"""
import json, sys, subprocess, math
from pathlib import Path
import numpy as np, cv2

ROOT = Path(__file__).resolve().parent.parent
PROXY = Path(sys.argv[1])
DRAFT = "--draft" in sys.argv
plan = json.load(open(ROOT / "build/plan.json"))
beats = json.load(open(ROOT / "build/beats.json"))
FPS = plan["fps"]; W, H = 1080, 1920
period = beats["period"]; B = list(beats["beats"])
while len(B) < 45: B.append(round(B[-1] + period, 3))


def tval(x):
    if isinstance(x, (int, float)): return float(x)
    if x.endswith("-"): return B[int(x[1:-1])] - plan["lead"]
    return B[int(x[1:])]


# ---------- time remap -------------------------------------------------------
# A key is [time, src] or [time, src, {"slow": x, "hold": h}]: the hit at that key plays at
# `slow` x real time and stays there for the first `hold` fraction of the gap to the next hit
# (deep slow-mo on the musical "breaths"), then whips into the next hit.
def seg_profile(kind, hold=0.25, n=400):
    u = (np.arange(n) + 0.5) / n
    if kind == "mid":      # hold, then accelerate late and slam into the next hit
        x = np.clip((u - hold) / (0.92 - hold), 0, 1); p = x ** 2.5 * (1 - x)   # whip done ~8% before the hit
    elif kind == "entry":  # cut lands mid-whip, decelerate into the hit
        p = np.clip(1 - u / 0.7, 0, 1) ** 2
    elif kind == "exit":   # leave the hit (after its hold), accelerate into the cut
        x = np.clip((u - max(0.2, hold * 0.5)) / (1 - max(0.2, hold * 0.5)), 0, 1); p = x ** 2
    else:
        p = np.zeros(n)
    return u, p / (p.mean() if p.mean() > 0 else 1)


def key_opt(k):
    return k[2] if len(k) > 2 else {}


def build_map(shot):
    raw = shot["keys"]
    keys = [(tval(k[0]), float(k[1])) for k in raw]
    vs = shot.get("slow", plan["slow"])
    t0, t1 = keys[0][0], keys[-1][0]
    ts = np.arange(math.ceil(t0 * FPS - 1e-6), math.ceil(t1 * FPS - 1e-6)) / FPS
    is_cut = lambda k: isinstance(k[0], str) and k[0].endswith("-")
    slow_at = [key_opt(k).get("slow", vs) for k in raw]
    T, Sx = [keys[0][0]], [keys[0][1]]
    for i in range(len(keys) - 1):
        (ta, sa), (tb, sb) = keys[i], keys[i + 1]
        dur, D = tb - ta, sb - sa
        avg = D / dur
        kind = "mid"
        if i == 0 and is_cut(raw[0]): kind = "entry"
        if i == len(keys) - 2 and is_cut(raw[-1]): kind = "exit"
        if i == len(keys) - 2 and not isinstance(raw[-1][0], str): kind = "lin"
        hold = key_opt(raw[i]).get("hold", 0.25)
        u, p = seg_profile(kind, hold)
        if kind == "lin":
            v = np.full_like(u, avg)
        else:
            va = slow_at[i] if kind != "entry" else 0.0     # entry: fast at the cut
            vb = slow_at[i + 1] if kind != "exit" else 0.0  # exit: fast at the cut
            va, vb = min(va, 0.85 * avg), min(vb, 0.85 * avg)
            base = va + (vb - va) * (u * u * (3 - 2 * u))   # speeds meet the neighbours' slow-mo
            v = base + (avg - base.mean()) * p              # mean(v) == avg
        cum = np.concatenate([[0], np.cumsum(v)]) / len(v) * dur
        T += list(ta + np.linspace(0, dur, len(cum))[1:]); Sx += list(sa + cum[1:])
    T, Sx = np.array(T), np.array(Sx)
    return ts, (lambda t: np.interp(t, T, Sx)), vs


# ---------- frame access ------------------------------------------------------
def load_frames(clip, s0, s1):
    i0 = max(0, int(s0 * FPS) - 2); i1 = int(s1 * FPS) + 3
    cap = cv2.VideoCapture(str(PROXY / f"{clip}.mp4"))
    cap.set(cv2.CAP_PROP_POS_FRAMES, i0)
    fr = []
    for _ in range(i0, i1):
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    return i0, fr


DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
GX, GY = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))


class Src:
    def __init__(self, clip, s0, s1):
        self.i0, self.fr = load_frames(clip, s0, s1)
        self.flow = {}

    def get(self, i):
        return self.fr[int(np.clip(i - self.i0, 0, len(self.fr) - 1))]

    def flows(self, i):
        if i not in self.flow:
            a = cv2.cvtColor(cv2.resize(self.get(i), (540, 960)), cv2.COLOR_BGR2GRAY)
            b = cv2.cvtColor(cv2.resize(self.get(i + 1), (540, 960)), cv2.COLOR_BGR2GRAY)
            f01 = cv2.resize(DIS.calc(a, b, None), (W, H)) * 2
            f10 = cv2.resize(DIS.calc(b, a, None), (W, H)) * 2
            self.flow = {k: v for k, v in self.flow.items() if k >= i - 2}
            self.flow[i] = (f01, f10)
        return self.flow[i]

    def interp(self, pos):
        i = int(math.floor(pos)); a = np.float32(pos - i)
        if a < 0.04 or DRAFT: return self.get(i if a < 0.5 else i + 1).astype(np.float32)
        if a > 0.96: return self.get(i + 1).astype(np.float32)
        f01, f10 = self.flows(i)
        w0 = cv2.remap(self.get(i), GX - a * f01[..., 0], GY - a * f01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        w1 = cv2.remap(self.get(i + 1), GX - (1 - a) * f10[..., 0], GY - (1 - a) * f10[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return (1 - a) * w0.astype(np.float32) + a * w1.astype(np.float32)

    def expose(self, p0, p1):
        span = p1 - p0
        if span < 1.2: return self.interp((p0 + p1) / 2)
        n = int(min(24, math.ceil(span * 1.5)))
        acc = np.zeros((H, W, 3), np.float32)
        for k in range(n):
            q = p0 + span * (k + 0.5) / n; i = int(q); a = q - i
            acc += (1 - a) * self.get(i) + a * self.get(i + 1)
        return acc / n


# ---------- look ---------------------------------------------------------------
def zoom_blur(img, s, cx=540, cy=900):
    if s <= 0.01: return img
    K = 7; acc = img.copy()
    for k in range(1, K):
        sc = 1 + 0.075 * s * k / K
        M = np.float32([[sc, 0, cx * (1 - sc)], [0, sc, cy * (1 - sc)]])
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    acc /= K
    r = np.sqrt(((GX - cx) / 540) ** 2 + ((GY - cy) / 960) ** 2)
    m = np.clip(r * 1.3 - 0.15, 0, 1)[..., None] * min(1, s * 1.4)
    return img * (1 - m) + acc * m


VIG = None


def grade(bgr, gain):
    global VIG
    x = np.clip(bgr / 255.0 * gain, 0, None)
    lum = x @ np.float32([0.114, 0.587, 0.299])
    # lighting: lift shadows a touch, roll off highlights (soft shoulder), filmic S contrast
    x = x / (1 + 0.22 * x)  * 1.22
    x = np.clip(x, 0, 1)
    s = x * x * (3 - 2 * x)
    x = x * 0.45 + s * 0.55
    x = 0.025 + x * 0.965                       # matte blacks
    lum = (x @ np.float32([0.114, 0.587, 0.299]))[..., None]
    # split tone: teal shadows, golden highlights (BGR)
    sh = np.clip(1 - lum * 2.2, 0, 1); hi = np.clip(lum * 1.6 - 0.55, 0, 1)
    x = x + sh * np.float32([0.035, 0.012, -0.03]) + hi * np.float32([-0.06, 0.012, 0.05])
    # warm overall + richer saturation, protect skin (orange) from over-sat
    x = x * np.float32([0.95, 1.0, 1.04])
    lum = (x @ np.float32([0.114, 0.587, 0.299]))[..., None]
    chroma = (x.max(2, keepdims=True) - x.min(2, keepdims=True))
    sat = 1.0 + 0.28 * (1 - np.clip(chroma / 0.55, 0, 1))   # vibrance: boost muted colours, spare saturated reds
    x = lum + (x - lum) * sat
    x = np.clip(x, 0, 1)
    # bloom
    hl = np.clip(x - 0.68, 0, None)
    bl = cv2.GaussianBlur(hl, (0, 0), 28)
    x = 1 - (1 - x) * (1 - bl * 0.9 * np.float32([0.75, 0.92, 1.0]))
    # local clarity
    soft = cv2.GaussianBlur(x, (0, 0), 3)
    x = x + (x - soft) * 0.35
    # vignette
    if VIG is None:
        r = np.sqrt(((GX - 540) / 620) ** 2 + ((GY - 900) / 1100) ** 2)
        VIG = (1 - 0.42 * np.clip(r - 0.45, 0, 1) ** 1.6)[..., None].astype(np.float32)
    x = x * VIG
    return np.clip(x * 255, 0, 255)


def grain(n):
    rng = np.random.default_rng(1000 + n)  # deterministic per frame
    g = rng.standard_normal((H // 2, W // 2), dtype=np.float32)
    return cv2.resize(g, (W, H))[..., None] * 3.0


# ---------- render -------------------------------------------------------------
def main():
    out = ROOT / ("assets/video/base_draft.mp4" if DRAFT else "assets/video/base.mp4")
    total = int(round(plan["duration"] * FPS))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium" if not DRAFT else "veryfast",
                            "-crf", "14" if not DRAFT else "22", "-pix_fmt", "yuv420p", "-g", "30", "-movflags", "+faststart", str(out)],
                           stdin=subprocess.PIPE)
    tl = {"beats": B, "shots": [], "fast": []}
    n = 0
    for shot in plan["shots"]:
        ts, F, vs = build_map(shot)
        if len(ts) == 0: continue
        srcs = F(np.concatenate([[ts[0] - 0.02], ts, [ts[-1] + 0.02]]))
        src = Src(shot["clip"], srcs.min(), srcs.max())
        # exposure match: aim mid-grey of the shot at 0.40
        sample = [src.get(int(F(t) * FPS)) for t in ts[:: max(1, len(ts) // 6)]]
        m = np.mean([cv2.cvtColor(cv2.resize(f, (108, 192)), cv2.COLOR_BGR2GRAY).mean() / 255 for f in sample])
        gain = float(np.clip(0.40 / m, 0.8, 1.35))
        tl["shots"].append({"id": shot["id"], "clip": shot["clip"], "start": round(float(ts[0]), 3), "end": round(float(ts[-1] + 1 / FPS), 3), "gain": round(gain, 3)})
        print(shot["id"], shot["clip"], f"{ts[0]:.3f}-{ts[-1]:.3f}", "src", f"{srcs.min():.2f}-{srcs.max():.2f}", "gain", round(gain, 2), flush=True)
        h = 1 / 200
        for t in ts:
            if n >= total: break
            p0, p1 = F(t - h) * FPS, F(t + h) * FPS
            speed = (F(t + 0.004) - F(t - 0.004)) / 0.008
            img = src.expose(p0, p1)
            zs = float(np.clip((speed - 2.2) / 5.5, 0, 1))
            if zs > 0.02: tl["fast"].append([round(float(t), 3), round(zs, 2)])
            img = zoom_blur(img, zs)
            img = grade(img, gain) + grain(n)
            enc.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
            n += 1
    while n < total:  # pad (should not happen)
        enc.stdin.write(np.zeros((H, W, 3), np.uint8).tobytes()); n += 1
    enc.stdin.close(); enc.wait()
    json.dump(tl, open(ROOT / "build/timeline.json", "w"), indent=1)
    print("frames", n, "->", out)


if __name__ == "__main__":
    main()
