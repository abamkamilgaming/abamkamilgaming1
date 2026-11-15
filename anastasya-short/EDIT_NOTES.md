# Anastasya (Cryo Archon) — Short (preview draft)

**Format:** 1080×1920 (9:16), 60 fps, **49.8 s** (bawah 1 minit)
**Status:** PREVIEW sahaja — belum render akhir.
**Render (bila dah approve):** `npm run render` → 1080×1920, 60 fps, 11 Mbps.
**Gaya:** muka penuh ↔ B-roll penuh (macam Minslief), caption pop 1–2 perkataan, salji jatuh, tema ais + merah jambu (cinta).

## Skrip (BM santai) — rakam ikut ID ni
| ID | Ayat |
|---|---|
| h1 | Tsaritsa ni jahat? Salah! Kuasa sebenar dia, cinta! |
| i1 | Ni Anastasya. Cryo Archon, bos besar Fatui. |
| r1 | Dalam Archon Quest tujuh perpuluhan dua, dia sendiri kumpulkan semua Archon untuk selamatkan Teyvat. |
| r2 | Kali terakhir the Seven berkumpul? Lima ratus tahun lepas, masa Cataclysm. |
| l1 | Authority dia, cinta. Kuasa untuk hapuskan sumpahan. |
| s1 | Rakyat dia kena wabak sumpahan. Dia janji, bila salji turun, semua sembuh. Dan memang jadi! |
| t1 | Lepas tu Celestia uji dia. Subjek ujian? Cinta. |
| t2 | Dia sound balik Celestia, korang yang cemarkan makna cinta. Meremang weh! |
| p1 | Bayangkan bila Anastasya jadi playable nanti. Archon tema cinta, confirm gempak! |
| p2 | Aku dah mula simpan primo. |
| e1 | Korang pull tak? Follow for more! |

Dua petikan suara asal game diselit (bukan suara kau):
- selepas `r2`: Pierro — *"Love. That is Her Majesty's power."* (4:57:52)
- selepas `t1`: Anastasya — *"Clearly, even you do not know what love is, Phanes."* (4:59:39 dalam babak ujian, 5:02:58)

## Keypoint Hoyoverse → di mana dalam video
- Peranan & babak penting: bos Fatui, kumpulkan 7 Archon (1:14:35), sembuhkan wabak sumpahan dengan salji (4:58–5:00), ujian "Love" Celestia (5:01–5:03)
- Hype playable: bahagian `p1`/`p2` + CTA
- Tema Cinta: hook, kad "AUTHORITY: CINTA", petikan Pierro, "SUBJEK: CINTA", "ARCHON TEMA CINTA"

## Yang masih PLACEHOLDER
1. **Suara** — TTS (ms-MY) untuk timing sahaja.
2. **Muka** — potongan bisu dari talking head Mitya (ada tag merah "STAND-IN").
3. Bila talking head sebenar masuk: potong ke `assets/th/<id>.mp4` + `build/th_words.json` (macam projek mitya-short), `gen.py` tukar mod sendiri.

## Sumber
- Footage: "Version 7.2 Archon Quest … ACT 5 & 6 (Full Playthrough).mp4" (timestamp dalam `build/cut_clips.py`)
- Muzik: "Background song" (volume 0.30, suara ~-15 LUFS vs muzik ~-26 LUFS)

## Rebuild
```
python3 build/tts.py && python3 build/tighten_vo.py
python3 build/cut_clips.py <playthrough.mp4> "<Background song>" [standin.mp4]
python3 build/gen.py
npx hyperframes preview --background
```
