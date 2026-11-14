# Mitya Guide — Short (preview draft)

**Format:** 1080×1920 (9:16), 60 fps, **55.4 s** (bawah 1 minit)
**Status:** PREVIEW sahaja — belum render.
**Layout:** muka atas / gameplay bawah (gaya "AbamKamil Gaming content 1"), caption pop di garisan tengah.

## Skrip (BM santai) + timeline

| Masa | Bahagian | Skrip | Grafik / SFX |
|---|---|---|---|
| 0.10 | HOOK | Jangan pull Mitya selagi kau tak tengok video ni! | "JANGAN PULL MITYA", impact + flash |
| 2.40 | HOOK | Cara main dan build Mitya, bawah enam puluh second. | Kad CARA MAIN / BUILD, "< 60 SAAT" |
| 5.28 | #01 Showcase | Mitya, five star Electro baru. Tengok rupa dia, idle dia pun dah nampak mahal. | Nama + ★★★★★, ELECTRO · CATALYST |
| 9.90 | #02 Cara main | Mechanic dia senang je. Dia ada dua mode. | "2 MODE" |
| 12.21 | #02 | Tap skill, dia jadi sub DPS off-field. | Kad TAP |
| 14.84 | #02 | Hold skill, dia jadi main DPS on-field. | Kad HOLD |
| 17.65 | #02 | Tersalah tekan? Tekan skill sekali lagi, terus tukar mode. | "TEKAN SKILL LAGI ⇄", glitch |
| 20.76 | #02 | Buat reaction Stellar Conduct untuk kumpul stack. Stack penuh, meteor jatuh. Damage dia gila! | Meter stack 4 bulatan, riser → "METEOR!" |
| 25.85 | #02 | Burst dia pula, terus bagi tiga stack. | "+3 STACK" |
| 28.48 | #03 Build | Build pula. Talent, naikkan normal attack dulu, lepas tu burst, baru skill. | Talent priority 1-2-3 |
| 33.09 | #03 | Stat, Crit tujuh puluh, dua ratus. EM lima ratus. ER seratus empat puluh. | Tile CRIT 70/200, EM 500+, ER 140% |
| 37.55 | #03 | Artifact, pakai Deep Shadow empat piece, ataupun Gilded Dreams. | Kad artifact + main stat |
| 41.38 | #03 | Weapon, signature dia paling padu. Takde? Kagura's Verity ataupun Widsith pun jalan. | Kad weapon BiS / 5★ / F2P |
| 46.44 | #04 Team | Team, gandingkan dengan unit Cryo dan Sucrose. | 4 slot team |
| 48.99 | #05 Masa depan | Dan aku rasa, Mitya ni ngam gila satu team dengan Tsaritsa nanti. | "MITYA × TSARITSA?" |
| 52.32 | END | Simpan primo korang. Follow for more! | Butang FOLLOW |

## Yang masih PLACEHOLDER (mesti diganti sebelum render/post)
1. **Suara** — TTS (ms-MY Osman) untuk timing sahaja. Rakam ikut `build/script.tsv`.
2. **Muka** — potongan bisu dari "AbamKamil Gaming content 1" (576p, bibir tak sync). Ada tag merah "STAND-IN".
3. **Gameplay Mitya** — dipotong dari video Kettletoro & "Build Mitya in 60 seconds" (rakaman skrin, footage orang lain).
   Ganti dengan rakaman gameplay Mitya sendiri sebelum post.
4. **Music bed** — OST dari projek archon-short.
5. **Fakta untuk disahkan** — nama teammate (video rujukan tunjuk ikon sahaja, "based on leaks"), ER 130% (disebut) vs 140% (tertulis).

## Rebuild
```
python3 build/tts.py            # VO sementara (atau letak rakaman sendiri di assets/voice/raw/<id>.wav)
python3 build/tighten_vo.py     # buang pause
python3 build/cut_clips.py <kettletoro.mp4> <build60.mp4> <abamkamil.mp4> <tsaritsa_clip.mp4>
python3 build/gen.py            # jana index.html
npx hyperframes preview --background
```
