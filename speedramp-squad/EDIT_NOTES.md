# The Squad — Speed Ramp

**Format:** 1080×1920 (9:16), 60 fps, **14.9 s**
**Status:** PREVIEW sahaja — belum render final.

## Transcript

### Audio footage
Whisper (small, auto + paksa BM) atas ketujuh-tujuh klip: **tiada dialog**, cuma bunyi ambient koridor.
Audio footage tak dipakai. Lagu ialah satu-satunya muzik.

### Lagu (`Song`, 19.1 s → potong 0–14.9 s)
- ~174 BPM, satu beat = 0.344 s. Grid beat ada dalam `build/beats.json` (b0 = 0.192 s).
- **0 – 3.9 s:** intro melodi, tiada drum (rentak ramp lebih perlahan).
- **3.965 s (b11): DROP.** Drum masuk; kick setiap 2 beat.
- **13.6 s (b39):** hit terakhir, muzik habis ~14.2 s.
- 15.0 s ke atas ialah jingle outro TikTok. Bahagian ni dibuang, dan lagu fade out dari 14.0 s.

### Footage (7 klip 4K 60 fps, potret). Log pergerakan kamera
| Klip | Fail | Subjek | Pergerakan (saat dalam klip) |
|---|---|---|---|
| c1 | 091122 | Budak lelaki A, koridor | tolak masuk 0–1.3 (close-up), tarik keluar 1.5–3.5, masuk 3.8–5.5, keluar 5.7–7.8 |
| c2 | 091143 | Budak lelaki B | orbit sisi 0.3–1.5, toleh 2.5–4, orbit balik 4.5–5.2 |
| c3 | 091221 | Budak lelaki C, peluk tubuh, low angle | masuk 0–1.6, keluar 1.8–4.0, masuk 4.3–6.1, keluar 6.6–8.5 |
| c4 | 091305 | Budak perempuan D (tudung coklat) | orbit kiri ke kanan 0–2.8, balik 3.3–6.5 |
| c5 | 091314 | Budak perempuan D | masuk 0–1.3, keluar 1.5–3.3, masuk 3.7–5.3, keluar 5.5–7.3 (zoom paling kuat) |
| c6 | 091412 | Budak perempuan E (tudung biru) | masuk 0–1.2, keluar 1.3–3.0, masuk 3.2–4.8, keluar 5.0–6.6 |
| c7 | 091424 | Budak perempuan E | orbit 0.3–1.6, naik/masuk 2.5–4.2, sweep 5.5–6.6 |

### Rujukan (`Speedramp Style`)
Analisis optical flow menunjukkan kitaran ~0.4 s: whip laju dan kabur, kemudian **landing slow-mo tepat atas beat**.
Cut berlaku di tengah whip. Ada zoom blur radial, grade golden-hour (teal/oren), vignette, tiada teks.

## Edit
| Masa | Shot | Klip | Hit slow-mo (beat) |
|---|---|---|---|
| 0.00 | Intro, "THE SQUAD" | c1 | b2, b4 |
| 1.78 | Build + riser | c3 | b5, b7, b9, b10 |
| 3.85 | **DROP**: slam + shake + flash + impact | c5 | b11, b13, b14, b16, b18 |
| 6.60 | | c2 | b19, b21, b22 |
| 7.97 | | c6 | b23, b25, b26 |
| 9.35 | | c4 | b27, b29, b30 (+punch b28) |
| 10.72 | | c7 | b31, b33, b34 |
| 12.10 | | c3 | b35, b37, b38 |
| 13.48 | Outro: hit + "THE SQUAD", fade hitam | c1 | b39 |

- **Speed ramp** (`build/ramp.py`): time-remap setiap frame. Atas beat ~0.35× (slow-mo, frame
  diinterpolasi guna optical flow); antara beat sampai ~13×, dengan shutter motion blur + zoom blur radial
  ikut kelajuan.
- **Grade + lighting** (dibakar dalam `ramp.py`): exposure setiap shot diseragamkan, highlight roll-off,
  kontras filmik, black matte, shadow teal / highlight keemasan, vibrance (merah baju tak terlebih), bloom,
  clarity, vignette, grain halus.
- **Motion design** (`index.html`): punch zoom setiap hit, slam + shake masa drop, light leak oren + flash
  kecil setiap cut, tajuk intro (huruf jatuh ikut separuh beat), kaunter 01–07 dengan bar progress
  setiap budak, tajuk outro + fade hitam.
- **SFX:** whoosh setiap whip, riser ke drop, impact bass masa drop & hit akhir, pop masa huruf intro,
  sparkle masa outro.

## Ubah
- Teks "THE SQUAD" / "SPEED RAMP · 2026" ada dalam `build/gen.py`.
- Hit / sumber klip ada dalam `build/plan.json`.

## Rebuild
```
python3 build/beats.py assets/audio/song.wav build/beats.json
python3 build/ramp.py <folder proxy 1080x1920>          # assets/video/base.mp4 (lambat, ~30 min)
python3 build/gen.py                                    # index.html
npx hyperframes preview                                 # preview
npx hyperframes render --fps 60 -o out.mp4              # render final (selepas approve)
```
Proxy: `ffmpeg -i <klip 4K> -an -vf scale=1080:1920:flags=lanczos -c:v libx264 -crf 12 -g 30 c<N>.mp4`
