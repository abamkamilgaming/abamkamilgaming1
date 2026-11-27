import sys, json, wave, numpy as np
def load(f):
    w=wave.open(f); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768; return a
from faster_whisper import WhisperModel
model_name, out = sys.argv[1], sys.argv[2]
m = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
res = {}
for f in sys.argv[3:]:
    segs, info = m.transcribe(load(f), language="ms", word_timestamps=True, vad_filter=True, beam_size=5)
    L=[]
    for s in segs:
        L.append({"s":round(s.start,2),"e":round(s.end,2),"t":s.text.strip(),"w":[[round(w.start,2),round(w.end,2),w.word] for w in s.words]})
        print(f"{f.split('/')[-1]} [{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
    res[f.split('/')[-1]] = L
json.dump(res, open(out,"w"), ensure_ascii=False, indent=1)
