# Beat grid for the song: fit a constant tempo to librosa beats, then snap each beat to the local onset peak.
import librosa, numpy as np, json, sys
y, sr = librosa.load(sys.argv[1], sr=22050)
_, bt = librosa.beat.beat_track(y=y, sr=sr, units='time')
bt = bt[bt < 14.0]
k = np.round((bt - bt[0]) / np.median(np.diff(bt)))
p = np.polyfit(k, bt, 1)
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=128); t = librosa.times_like(env, sr=sr, hop_length=128)
out = []
for i in range(int(k.max()) + 1):
    g = p[1] + p[0] * i; m = (t > g - 0.03) & (t < g + 0.03)
    out.append(round(float(t[m][env[m].argmax()]), 3) if m.any() else round(g, 3))
print("period", p[0], "bpm", 60 / p[0]); print(out)
json.dump({"period": p[0], "beats": out}, open(sys.argv[2], "w"))
