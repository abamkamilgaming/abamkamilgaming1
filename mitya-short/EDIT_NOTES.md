# Mitya Pull Short — PREVIEW (belum render)

**Format:** 1080×1920 (TikTok portrait), **88.0 s**, layout Doro44/TheJonathon: muka atas (0–860 px), game bawah, caption besar di sempadan (tak tutup muka).
Sumber: `Pulling Mitya and Signature Weapon.mp4` (14:21). Storyboard: `preview-frames/storyboard.jpg`.

| Masa | Babak | Footage (sumber) | Muzik / SFX |
|---|---|---|---|
| 0:00 | **HOOK** — bintang emas + jerit + jatuh kerusi. Teks "BILA KAU ALL-IN PRIMOGEM UNTUK MITYA..." | 12:50–12:58 | Delfino Plaza mula, impact, vine boom |
| 0:06 | Freeze muka terkejut → "TAPI JAP... MACAM MANA BOLEH JADI GINI?" → ⏪ REWIND | 12:55 | glitch, rewind |
| 0:08 | Mengadap Her Majesty Tsaritsa "Yang di-Pertuan Agung" (pop gambar Tsaritsa) | 0:10 | Delfino Plaza, sparkle, X-Files |
| 0:12 | "Plus Mitya memang best!" (pop gambar Mitya) | 0:26 | cute wow |
| 0:13 | "Please double gold early, signature early" | 0:31 | |
| 0:17 | "Kalau live ni dapat 20 view aku tekan terus" (badge SYARAT PULL 20 VIEW) | 0:50 | awkward moment |
| 0:22 | "Dah lah susah nak buat keputusan... kau ingat senang ke nak pull Mitya? Ya Allah" | 2:49 | vine boom |
| 0:28 | "Janganlah bagi hard pity" (badge PITY 50) | 4:56 | |
| 0:32 | "Aku tak terkejut pun kalau menang" → badge FAMOUS LAST WORDS | 6:50 | X-Files |
| 0:36 | Pull Mitya: bintang emas | 7:11 | **Last Surprise 0:00–0:10** |
| 0:41 | Fast-forward 4-star (VFX FF green screen, 34×) | 7:17–8:25 | glitch |
| 0:43 | "JAP JAP JAP..." silhouette | 8:27 | WAIT WAIT WHAT DA HELL |
| 0:46 | **MITYA!!** facepalm → lambai tangan happy | 8:30–8:40 | **Last Surprise 0:46 "You'll never see it coming"**, yay |
| 0:54 | ROUND 2: SIGNATURE WEAPON — "Nak signature kalau boleh" | 10:57 | Silly Chicken |
| 0:56 | "NOOOOO!!" / "Ya Allah" / "WASTED" | 11:36, 12:12 | FAHHH, Roblox oof |
| 0:59 | "Eh betul eh? Pity 46..." | 12:45 | Yu-Gi-Oh 1000 LP |
| 1:03 | Bintang emas lagi → AAAAA!!! | 12:49 | **Last Surprise 0:00** |
| 1:07 | **SIGNATURE DAPAT** (Starsealed Edict) → jatuh kerusi → N-I-C-E-E, Let's go, Tahniah | 12:55–13:11 | **Last Surprise 0:46→**, OMG no way, vine boom, yay |
| 1:19 | "This is my night... is it?" (chat: This is your night bam) | 13:29 | awkward |
| 1:21 | "Habis primo aku... HABIS!!" | 9:34 | emotional damage |
| 1:23 | **"No... Tsaritsa! SORRY TUANKU!!"** + kad "MAAF TUANKU... PRIMO HABIS KAT MITYA" | 14:15 | SAD sound effect |

Grade: media-treatment `deep-contrast` — face cam (highlight turun, contrast + warmth, vignette), game (vibrance + bloom).
Audio: suara stream +8 dB + compressor/limiter; muzik duck ~0.22–0.6.

## Rebuild
```
python3 build/cut.py "<Pulling Mitya and Signature Weapon.mp4>"   # potong klip muka/game 60fps
python3 build/gen.py                                              # jana index.html
npx hyperframes preview                                           # preview
npx hyperframes render -q looks --fps 60 -o out.mp4               # render (bila dah approve)
```
