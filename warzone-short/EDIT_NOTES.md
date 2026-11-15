# Warzone Short — gaya Doro44

**Format:** 1080×1920, 30 fps, **33.9 s** (bawah 1 minit) · **Status:** PREVIEW je, belum render.

## Struktur (face cam atas 0–900px, gameplay bawah 900–1920px, caption besar kat tengah)
| Masa | Segmen | Line (BM santai) | Motion / SFX |
|---|---|---|---|
| 0.00 | HOOK | "Game apa? GI ke? **Bukan GI ni!**" | Tajuk "BILA GENSHIN PLAYER MAIN WARZONE 💀", flash + vine boom |
| 2.35 | helo | "Helo, Farahin!" | |
| 3.90 | genshin | "Eh, bukan Genshin! Jap, aku Genshin..." | punch-zoom + vine boom |
| 6.37 | act1 | (scope, tembak) | shake |
| 9.17 | alone | "Aku rasa aku sorang je kat sini ni..." | 🦗 FOREVER ALONE + awkward-moment |
| 10.83 | res | "Aku nak ambil resources, eh." | |
| 12.39 | baz | "Uish, BAZOOKA!" | 🚀 sticker, violin screech, shake |
| 13.70 | uzi | "Ke apa ni? Uzi, Uzi." | 🤨 UZI?? + faaah |
| 15.31 | best | "Tak best eh, weapon ni." | 👎 0/10 + laughing dog |
| 16.86 | act | (firefight) | run vine + shake |
| 19.96 | gift/gift2 | "Terima kasih! Terima kasih Farahin! Semoga lampu hijau sentiasa!" | 🕴️ "ABAM KAMIL SEBAGAI MR.K", lagu french meme |
| 24.13 | minyak | "Minyak full tank! InsyaAllah." | ⛽ FULL TANK + vine boom |
| 27.63 | chat | (chat: "Abam dah buat Archon Quest ke belum?") "Belum lagi." | bubble chat, 💀 EMOTIONAL DAMAGE |
| 30.36 | end | "Ni, lepas ni aku main Genshin!" | "TEAM GENSHIN ATAU TEAM WARZONE?" + FOLLOW 🔔, outro song |

## Apa yang dibuat
- Transcribe kedua-dua video (Whisper large-v3, semak semula setiap segmen lepas potong).
- Buang awkward pause (jeda > 0.16 s dipotong ke 0.07 s) + line berulang ("Helo, helo", "Bukan Genshin" ×3, "Terima kasih, sudah punch card" ×2, "saja try je ni" ×2). Line yang bisik/tak jelas ("Weapon apa sia?") dibuang. Talking dipercepat 1.1×.
- Overlay stream (gambar Genshin bawah, teks "live yang penting") di-crop keluar.
- Grade: deep-contrast + vibrance + vignette; face — highlight dinaikkan sikit ke bawah, shadow diangkat, warm; gameplay gelap (warehouse) diterangkan.
- Audio setiap segmen loudnorm −15 LUFS supaya sekata.

## Rebuild
```
python3 build/cut.py "<Warzone 1.mp4>" "<Warzone 2.mp4>"   # potong, crop, buang pause → assets/seg
python3 build/gen.py                                       # jana index.html
npx hyperframes preview --background                       # preview
npx hyperframes render -o out.mp4                          # (lepas approve)
```
