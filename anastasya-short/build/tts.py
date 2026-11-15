"""Placeholder VO (edge-tts, ms-MY Osman) + word timings -> assets/voice/raw/<id>.wav, build/vo_words.json"""
import asyncio, json, os, ssl, subprocess, sys, edge_tts, edge_tts.communicate as _c
PROXY = os.environ.get("HTTPS_PROXY")
if os.path.exists("/root/.ccr/ca-bundle.crt"): _c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "voice", "raw")
async def one(i, text):
    c = edge_tts.Communicate(text, "ms-MY-OsmanNeural", rate="+22%", pitch="+2Hz", boundary="WordBoundary", proxy=PROXY)
    mp3 = os.path.join(RAW, i + ".mp3"); W = []
    with open(mp3, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7; W.append([ch["text"], round(s, 3), round(s + ch["duration"] / 1e7, 3)])
    wav = os.path.join(RAW, i + ".wav")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", mp3, "-ar", "48000", "-ac", "1", wav], check=True)
    os.remove(mp3)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav],
                             capture_output=True, text=True).stdout)
    return i, {"dur": d, "words": W}
async def main():
    out = {}
    for line in open(os.path.join(ROOT, "build", "script.tsv")):
        i, text = line.rstrip("\n").split("\t")
        k, v = await one(i, text); out[k] = v; print(k, round(v["dur"], 2), len(v["words"]))
    json.dump(out, open(os.path.join(ROOT, "build", "vo_words.json"), "w"), ensure_ascii=False, indent=0)
    print("total", round(sum(v["dur"] for v in out.values()), 2))
asyncio.run(main())
