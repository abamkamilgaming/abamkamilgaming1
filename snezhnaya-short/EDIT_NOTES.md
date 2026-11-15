# SNEZHNAYA — Funny Moments Short

**FINAL:** 1080×1920, **60 fps**, **64.8 s**, HEVC (H.265) 2-pass 11 Mbps, AAC 256k, −15.9 LUFS
Fail: `out/snezhnaya_final_1080p60_hevc.mp4` (tak di-commit — 90 MB)

Perubahan selepas draf: "bodoh" dibeep (caption B*D*H); part kerusi jadi ragebait (grade merah, riser, zoom ke
kerusi + "SIAPA LETAK NI?!", gegaran, flash, suara bass-boost, 💢 TERSANGKUT!!); end card "ABAMKAMIL GAMING".
**Gaya:** Doro44 / Thejonathon — webcam atas, gameplay bawah, caption besar 1–3 perkataan di garis tengah, popup live chat, sticker emoji, freeze B&W, SFX meme.

## Timeline

| Masa | Babak | Abam cakap (dari stream) | Overlay / SFX |
|---|---|---|---|
| 0.00 | HOOK | "Eh, jadah apa kau ni TikTok?" | Tajuk **STREAMER VS TIKTOK** + chip "⚠ AMARAN TIKTOK", impact + glitch |
| 1.98 | HOOK | "Reproduce kotak kepala Acik engkau!" | "KENA WARNING 2 KALI 💀", vine boom, punch zoom |
| 4.72 | HOOK | "Bodoh lah TikTok ni. Sorry lah TikTok, aku kena maki lah. Kau memang bongok." | Chat **taufik**: "kenapa kata x original, tiktok ni 😩", 🤬 + faaah |
| 9.08 | Barai | "Aku mengantuk sangat ni, tapi aku paksakan juga malam ni live." | 😴 MODE: BARAI |
| 12.22 | Barai | "Semalam tidur 2 jam je." | 💤 2 JAM |
| 14.23 | Event | "Susah gila nak aim." | Chat **hanis**: "event sng ni" → 💀 SENANG?? + awkward |
| 16.25 | Event | "Kenapa kena isi peluru manual? Patutnya auto reload lah." | 🔫 AUTO RELOAD PLS |
| 21.63 | Event | "Pakai phone senang je." | Chat **Batman Arkham**: "pakai phone senang je" |
| 23.25 | Event | "Siapa letak kerusi sini? Aku tersangkut tadi." | 🪑 TERSANGKUT, violin screech, shake |
| 26.43 | Event | "Sebab dia bangang. Itu je. The only explainable reason." | 🧠 100 IQ + vine boom |
| 30.75 | Makanan | "Yo, sakitnya! Nooo!" | 😭, shake |
| 33.60 | Makanan | "Habis lah makanan aku." | 🍗 HABIS! |
| 35.27 | Makanan | "Nampak tak? Effect tak cukup tidur." | 😵‍💫 KURANG TIDUR |
| 38.03 | Makanan | "Wasted. Just like that." | **Freeze B&W + WASTED**, emotional damage |
| 40.77 | Makanan | "Ingat guys, pengajaran. Cook your food every single week." | 👨‍🍳 PENGAJARAN, lagu French meme |
| 45.28 | Review | "Apa kata aku review kejap…" (baca chat) | Chat **Batman Arkham** ×2 |
| 47.58 | Review | "My brain juice is gone already. The one talking to you right now is not AbamKamil Gaming." | Meter 🧠 BRAIN JUICE → 0%, vine boom, laughing dog |
| 54.78 | Outro | "Sentiasa lampu hijau, takde traffic jam, takde congestion, takde traffic light." | 🚦, outro song |
| 59.10 | Outro | "Pergi kerja semua lampu hijau je, aku doakan korang." | 🤲 AMIN + yay |
| 61.58 | Outro | "Bye bye!" | 👋 → end card FOLLOW ABAMKAMIL |

Masa sumber (dalam video stream 1j07m) untuk setiap baris: `build/script.json`.

## Apa yang dibuat
- Transcribe penuh stream 67 minit (Whisper medium, word timestamps) → cari moment lucu & interaksi chat.
- Mesej chat dalam popup ialah mesej sebenar dari panel Live Chat stream (taufik, hanis, Batman Arkham).
- Awkward pause dibuang guna track suara yang diasingkan (demucs): jeda > 0.2 s dipotong ke 0.09 s, hujung/kepala dipotong rapat; ucapan dilajukan 1.06×.
- Ayat berulang dibuang (cth. "Siapa letak kerusi sini, kenapa? Kenapa letak kerusi sini?" → sekali sahaja; "Nampak tak? Nampak?" → sekali; "Pakai phone senang je. Pakai phone senang." → sekali).
- Bunyi game direndahkan (−10 dB) bawah suara; suara dinormalkan.
- Colour grade (HyperFrames media-treatment): webcam = skin-soft + exposure/shadow lift + warm + contrast + vignette; gameplay = deep-contrast + vibrance + bloom + vignette; freeze = mono-clean.
- Lagu latar: muzik dari video Thejonathon (vokal dibuang dengan demucs), tukar ke french-meme-song untuk segmen masak, outro-song di hujung.
- SFX dari folder "Sound Effects" + whoosh/pop/impact.

## Rebuild
```
python3 build/stems.py "<SNEZHNAYA!.mp4>"   # extract + asingkan suara (demucs)
python3 build/cut.py "<SNEZHNAYA!.mp4>"     # potong jeda, crop cam + gameplay, 60fps
python3 build/gen.py                        # jana index.html
npx hyperframes preview                     # preview
npx hyperframes render -f 60 -q delivery -o master60.mp4
/home/user/scripts/final_hevc.sh            # atau: ffmpeg libx265 -b:v 11M 2-pass, -tag:v hvc1
```
