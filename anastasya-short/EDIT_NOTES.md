# Anastasya (Cryo Archon) — Short (preview v2, talking head sebenar)

**Format:** 1080×1920 (9:16), 60 fps, **58.1 s** (bawah 1 minit)
**Status:** PREVIEW sahaja — belum render akhir.
**Render (bila dah approve):** `npm run render` → 1080×1920, 60 fps, 11 Mbps.
**Gaya:** muka penuh ↔ B-roll penuh (macam Minslief), caption pop, salji jatuh, tema ais + merah jambu (cinta).

## Ayat (ikut apa yang kau sebut)
| ID | Ayat | Durasi |
|---|---|---|
| h1 | Tsaritsa jahat? Salah! Kuasa sebenar dia? Cinta! | 3.9s |
| i1 | Ini Anastasya Cryo Archon bos besar Fatui | 2.8s |
| r1 | Dalam Archon Quest 7.2 dia sendiri kumpulkan semua Archon untuk selamatkan Teyvat | 5.1s |
| l1 | Authority dia cinta kuasa untuk hapuskan sumpahan | 4.2s |
| s1 | Rakyat dia ni kena wabak sumpahan Dia janji bila salji turun semua akan sembuh Dan memang jadi | 6.9s |
| s2 | Tapi ada satu sumpahan cinta pun tak boleh nak ubat | 3.1s |
| t1 | Lepas tu Celestia uji dia Subjek ujian? Cinta | 3.2s |
| t2 | Dia ni sound balik Celestia punya gangster ni korang yang cemarkan nama cinta meremang weh | 5.7s |
| p1 | Bayangkan bila Anastasya jadi playable nanti Archon tema cinta confirm gempak weh | 6.1s |
| p2 | Aku dah mula simpan primo | 1.4s |
| e1 | Korang pull ke tak? Follow for more | 1.9s |

Tiga petikan suara asal game:
- selepas `r1`: Pierro — *"Love. That is Her Majesty's power."*
- selepas `s2`: Anastasya — *"Love cannot cure you of this curse."*
- selepas `t1`: Anastasya — *"Clearly, even you do not know what love is, Phanes."*

## Yang dipotong dari rakaman 80 s
- Pause > 0.18 s + laju 1.15×
- Filler: "Jadi,", "ni guys,", "uff, masa ni memang", "bayangkan" (kali kedua)
- Dibuang untuk masa: "Kali terakhir bila the Seven berkumpul? 500 tahun yang lepas, masa Cataclysm di Khaenri'ah" (7.4 s)

## Keypoint Hoyoverse → di mana
- Peranan & babak penting: bos Fatui, kumpulkan 7 Archon, sembuhkan wabak sumpahan dengan salji, satu sumpahan yang cinta tak boleh ubat, ujian "Love" Celestia
- Hype playable: `p1`, `p2`, `e1`
- Tema Cinta: hook, "AUTHORITY: CINTA", tiga petikan, "SUBJEK: CINTA", "ARCHON TEMA CINTA"

## Sumber
- Muka + suara: "Talking Head" (4K60, 80 s) → `assets/th/`
- Footage: playthrough Archon Quest 7.2 (timestamp dalam `build/cut_clips.py`); "Tsaritsa cutscene" = cinematic yang sama
- Muzik: "Background song", volume 0.30

## Rebuild
```
python3 build/th_build.py "<Talking Head>"          # tambah --keep-words untuk kekalkan timing perkataan
python3 build/cut_clips.py <playthrough.mp4> "<Background song>"
python3 build/gen.py
```
