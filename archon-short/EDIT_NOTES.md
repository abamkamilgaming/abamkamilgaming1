# Archon Quest 7.2 — Short

**FINAL:** 1080×1920, **60 fps**, **57.6 s**, H.264 CRF 16, 66 MB, −12.5 LUFS
**Versi final = talking head AbamKamil** (`build/gen2.py` → `index.html`). Jadual di bawah ialah versi TTS awal, simpan sebagai rujukan.

Rebuild versi final:
```
python3 build/th_build.py <AbamKamil Gaming Talking Head.mp4> build/th_tx.json   # potong pause/filler, 1.15x, loudness
python3 build/cut_clips.py <playthrough.mp4> assets/clips                          # B-roll 9:16 @60fps
python3 build/gen2.py                                                              # jana index.html
npx hyperframes render -q looks --fps 60 -o out.mp4
```

---

**Format:** 1080×1920 (9:16), 30 fps, **56.29 s** (bawah 1 minit)
**Status:** PREVIEW sahaja — belum render.

## Skrip VO (BM santai) + timeline

| Masa | Babak | VO / audio | Footage (timestamp dalam video 5j24m) |
|---|---|---|---|
| 0.00 | HOOK | "Weh! First kali dalam sejarah Genshin, kesemua tujuh Archon berkumpul!" | 1:32:36 (plaza Snezhnaya), 5:13:26 (7 Archon di Divine Throne) |
| 4.75 | Umpan code | "Stay sampai habis, aku ada redeem code free untuk korang!" | 0:49:53 (montaj kawan-kawan) |
| 7.94 | #01 Bahaya | "Teyvat sekarang dalam bahaya besar. Celestia nak hapuskan Teyvat dari kewujudan!" | 0:21:35 (Nail of Retribution), 5:17:12 |
| 11.79 | #01 (game VO) | *"True annihilation shall descend."* + sticker "TINGGAL 42 HARI" | 5:18:52 |
| 15.39 | #02 7 Archon | "Kali terakhir Seven berkumpul? Masa Cataclysm, lima ratus tahun lepas!" | 1:14:26 (meja bulat), 1:14:35 (Tsaritsa) |
| 20.05 | #03 Raiden | "Raiden Ei pula, datang demi eternity," | 2:28:13 |
| 22.60 | #03 (game VO) | *"…to answer for eternity."* | 2:28:23 |
| 24.15 | #03 | "dan hancurkan Celestial Nail, satu tebasan je. Gila!" | 2:28:38 (tebasan, 2× laju) |
| 27.52 | #04 Zhongli | "Tapi Zhongli tak ada." | 5:09:20 (Ningguang: "If Rex Lapis were still with us") |
| 28.65 | #04 | "Dia masuk dalam Nail guna Mora. Kontrak terakhir dia." | 1:31:48 (Zhongli dalam Nail) |
| 31.92 | #04 (game VO) | *Zhongli: "Betray it… and you taint my blood."* (pause dibuang) | 1:31:33 |
| 35.02 | #05 Celestia & Noy | "Dan bila sampai Celestia," | 5:11:30 (Divine Throne) |
| 36.37 | #05 (game VO) | *"Celestia welcomes you."* | 5:18:58 |
| 38.62 | #05 | "Lepas tu, muncul pula watak baru. Noy!" | 4:53:17 (Noy close-up) |
| 41.12 | #05 (game VO) | *Noy: "Tysyatsky Noy."* | suara 4:51:56, visual 4:52:23 |
| 42.62 | #06 Nostalgia | "Part paling meremang untuk player lama, semua bergabung tenaga!" | 0:49:44 (montaj) |
| 45.46 | #06 (game VO) | *Mavuika: "We have to face it… together."* | 5:22:51 |
| 47.06 | END | "Janji aku, ni redeem code dia! Enam puluh Primogems, lima Adventurer's Experience." | Kad code **QYJW50368SU7** |
| 52.53 | END | "Cepat claim! Follow for more." | Butang FOLLOW |

## Apa yang dah dibuat
- Transcribe penuh video 5j24m (Whisper) → cari timestamp setiap keypoint Hoyoverse.
- Awkward pause dibuang: setiap jeda > 0.3 s dalam VO dipotong ke 0.2 s; jeda dalam dialog Zhongli dipotong; tiada dead air antara line (gap 0.1 s).
- Hook kuat frame-0 ("7 ARCHON BERKUMPUL!") + umpan redeem code + progress bar dengan ikon Primogem sampai hujung.
- Caption pop 1–2 perkataan gaya AbamKamil (keyword warna emas), tag keypoint #01–#06, sticker (500 TAHUN, 42 HARI, GILA!, KONTRAK TERAKHIR, NOY, BERGABUNG!).
- SFX: impact, whoosh, riser ke tebasan Raiden, sparkle, pop, chime; music bed = OST cinematic Raiden (dari playthrough), duck bawah VO.
- Colour grade (HyperFrames media-treatment): deep-contrast + vibrance + bloom + vignette; lighting per shot (shot gelap dinaikkan, shot throne yang terlalu terang diturunkan).

## Perlu tindakan kau
1. **VO sekarang suara TTS sementara** (ms-MY Osman) — untuk timing je. Rakam suara kau ikut skrip atas, letak fail dalam `assets/voice/<id>.wav` (h1, h2, d1, s1, r1, r2, z1, z2, c1a, c1b, n1, e1, e2), lepas tu run `python3 build/tighten_vo.py` dan `python3 build/gen.py` (perlu re-align word timing — aku boleh buat).
2. ~~Sahkan "Noy"~~ — dah betulkan: Noy = Tysyatsky Noy (fae lord Snezhnaya, rambut merah, armour perak). Diperkenalkan 3:25:36, masuk istana Tsaritsa 4:51:47.
3. Approve preview → baru render.

## Rebuild
```
python3 build/cut_clips.py <path/to/main.mp4> assets/clips   # potong & reframe 9:16
python3 build/tighten_vo.py                                   # buang pause VO
python3 build/gen.py                                          # jana index.html
npx hyperframes preview                                       # preview
```
