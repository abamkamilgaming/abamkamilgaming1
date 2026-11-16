# Cikgu Aryati: "Biasakan yang betul, betulkan yang biasa"

**Status:** PREVIEW sahaja, belum render final.
**Format:** 1080×1920 potret, 60 fps, 18.5 s (asal 19.56 s)
**Render final (lepas approve):** 1080p 60 fps HEVC 11 Mbps. Arahan ada di bawah.

## Transkrip & timeline (masa dalam video yang dah dipotong)
| Masa | Siapa | Ucapan | Grafik |
|---|---|---|---|
| 0.00 | Penanya | "Cikgu, cikgu!" | HOOK: "8 PERKATAAN YANG KORANG SELALU SALAH!" + ❌, impact |
| 1.51 | Cikgu | "Ya, saya." | Name tag "Cikgu Aryati, Guru Bahasa Melayu" |
| 2.09 / 2.71 | Q / A | Viral? / Tular. | 1/8 ❌ VIRAL → ✅ Tular |
| 3.45 / 4.17 | Q / A | Selfie? / Swafoto. | 2/8 |
| 4.90 / 5.58 | Q / A | Hashtag? / Tanda pagar. | 3/8 |
| 6.23 / 6.92 | Q / A | Emoji? / Emoji. | 4/8 + sticker "SAMA JE!" |
| 7.53 / 8.37 | Q / A | Netizen? / Warganet. | 5/8 |
| 9.09 / 9.87 | Q / A | Kuey teow? / Kuetiau. | 6/8 |
| 10.79 / 11.49 | Q / A | Mee hoon? / Bihun atau Mihun. | 7/8 + "DUA-DUA BETUL!" |
| 13.45 / 14.25 | Q / A | Mee goreng? / Mi goreng. | 8/8 |
| 15.10 | Cikgu | "Dapat sesuatu?" | Outro: "Biasakan yang betul, betulkan yang biasa!" + FOLLOW |

## Apa yang dah dibuat
- **Pause dibuang:** 7 potongan, setiap jeda dipendekkan ke 0.07 s (soalan→jawapan) / 0.12 s (jawapan→soalan). Jump cut disorok dengan jump-zoom (soalan = wide, jawapan = punch-in 1.16×).
- **Gaya "Contoh content":** atas = perkataan comic putih, outline hitam 3D, glow kuning, ditaip huruf demi huruf; bawah = jalur kertas buku koyak dengan huruf pelangi. Perkataan salah kena coret merah bila jawapan keluar.
- **SFX:** bunyi "ding" **diekstrak dari Contoh content** (dipisahkan dengan Demucs, 7 kejadian di-align dan di-median), main setiap kali jawapan betul keluar. Tambahan: impact + whoosh (hook), whoosh halus setiap soalan, pop untuk sticker, sparkle untuk outro.
- **Audio:** buang dengung kipas (afftdn), EQ kejelasan suara, compressor, loudness −14 LUFS.
- **Color grade / lighting:** HyperFrames media-treatment `skin-soft` 0.62, exposure +0.08, shadows +0.14, highlights −0.24 (tingkap terlalu terang diturunkan), contrast +0.08, warm +0.05, vibrance +0.06, vignette 0.05.

## Bina semula
```
python3 build/aroll.py "<Cikgu Aryati.mp4 diturunkan ke 1080x1920>"   # potong pause, -> assets/video/aroll.mp4 + build/edl.json
python3 build/gen.py                                               # -> index.html
npx hyperframes preview
```
Sumber 4K diturunkan dulu (elak kehabisan RAM):
`ffmpeg -i "Cikgu Aryati.mp4" -vf scale=1080:1920:flags=lanczos -r 60 -c:v libx264 -crf 10 -g 1 -c:a pcm_s16le aryati_1080.mov`

## Render final (selepas approve)
```
npx hyperframes render -q delivery --fps 60 -o renders/master.mp4
ffmpeg -i renders/master.mp4 -c:v libx265 -b:v 11M -maxrate 12M -bufsize 22M -tag:v hvc1 -pix_fmt yuv420p -r 60 -c:a aac -b:a 256k -movflags +faststart renders/CikguAryati_1080p60_HEVC_11M.mp4
```

## Revisi v2
- "Ya, saya": suku kata kedua "saya" terpotong. Suara Cikgu ~5 dB lebih perlahan dari penanya, jadi baris Cikgu kini guna had −21 dB + look-ahead 30 ms, dan "saya" dikunci sampai 2.32 s. Jadual masa di atas ikut v1; masa terkini ada dalam `build/edl.json`.
- Caption diturunkan supaya tak tutup dagu: perkataan atas 930→1035 px, jalur kertas 1100→1200 px, FOLLOW 1372→1462 px.
