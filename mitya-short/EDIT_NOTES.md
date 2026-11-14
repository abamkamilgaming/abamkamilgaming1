# Mitya Guide — Short (preview v2, talking head sebenar)

**Format:** 1080×1920 (9:16), 60 fps, **56.5 s** (bawah 1 minit)
**Status:** PREVIEW sahaja — belum render.
**Render (bila dah approve):** `npm run render` → 1080×1920, 60 fps, video bitrate 11 Mbps.
**Layout:** muka atas / gameplay bawah, caption pop di garisan tengah.

## Sumber
- Muka + suara: `Talking Head.mp4` (4K, 110 s) → 14 clip ketat dalam `assets/th/`
- Gameplay: `1115.mp4` (footage rasmi Special Program 7.2) + shot cinematic dari `Mitya Theme Music.mp4`
- Muzik: audio `Mitya Theme Music.mp4` (bed bawah suara)
- Tsaritsa: clip dari projek `archon-short`

## Timeline (ayat sebenar yang kau sebut)
| Masa | Bahagian | Ayat | Grafik |
|---|---|---|---|
| 0.08 | HOOK | Jangan pull Mitya selagi korang tak tengok video ni | "JANGAN PULL MITYA" |
| 3.33 | #01 Showcase | Mitya, 5 star Electro baru. Tengok rupa dia, idle dia pun dah nampak mahal | Nama + ★★★★★, RUPA + IDLE |
| 8.78 | #02 Cara main | Mechanic dia senang je. Dia ada 2 mode | "2 MODE" |
| 10.70 | #02 | Tap skill, dia jadi sub off-field DPS | Kad TAP |
| 13.36 | #02 | Hold skill, dia jadi main DPS on-field | Kad HOLD |
| 15.87 | #02 | Salah tekan? Tekan skill sekali lagi, terus dia tukar mode | "TEKAN SKILL LAGI ⇄" |
| 19.02 | #02 | Buat reaction Stellar Conduct untuk kumpul stack. Bila stack dia dah penuh, meteor jatuh. Damage dia besar gila | Meter stack → "METEOR!" → "GILA!" |
| 25.97 | #02 | Burst dia pula, terus bagi 3 stack | "+3 STACK" |
| 28.83 | #03 Build | Stat. Crit 70, 200. EM 500. ER 140 | Tile stat |
| 34.78 | #03 | Artifact, korang boleh pakai Deep Shadow 4 pieces, ataupun Gilded Dreams | Kad artifact |
| 39.53 | #03 | Weapon, signature dia paling padu. Takde? Kagura's Verity ataupun Widsith pun jalan | Kad weapon |
| 45.58 | #04 Team | Team, gandingkan dengan unit Cryo dan Sucrose | Slot team |
| 49.73 | #05 Masa depan | Dan aku rasa Mitya ni ngam gila satu team dengan Tsaritsa nanti | "MITYA × TSARITSA?" |
| 53.48 | END | Simpan primo korang. Follow for more | Butang FOLLOW |

## Yang dipotong dari rakaman 110 s (supaya muat < 60 s)
- Semua pause > 0.18 s (19 potongan) + laju 1.15×
- Retake / ulangan: "Stats, crit 70, 20…" (take pertama), "Alright… so korang kena fokuskan crit rate…", "haa… Tsaritsa nanti" (ulang)
- Filler: "guys", "Tak risau", "yang fokuskan dekat EM"
- Dibuang untuk masa: "Cara main dan build Mitya under 60 second" (3.8 s) dan talent priority (6.9 s)

## Colour grade
- Muka: rakaman asal flat + cast hijau-kuning + dinding terlalu terang → kontras & hitam ditambah, highlight dinding ditarik,
  tint magenta lawan hijau, warm untuk kulit, vibrance, vignette, sharpen ringan.
- Gameplay: deep-contrast + vibrance + bloom + vignette; shot salji terlalu terang diturunkan.

## Rebuild
```
python3 build/th_build.py "<Talking Head.mp4>"                               # ~20 minit (decode 4K)
python3 build/cut_clips.py "<Mitya Theme Music.mp4>" <1115.mp4> <tsaritsa_clip.mp4>
python3 build/gen.py
npx hyperframes preview --background
```
