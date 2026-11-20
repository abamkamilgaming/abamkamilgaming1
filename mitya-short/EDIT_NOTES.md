# Test Run Mitya — TikTok short (PREVIEW, belum render)

**Format:** 1080×1920 (9:16), 60 fps, **63.8 s** · gaya Doro44 / thejonathon (facecam atas, gameplay bawah, caption 2–3 perkataan, chat bubble, meme SFX/VFX)
**Status:** PREVIEW sahaja — belum render. Storyboard: `preview-frames/storyboard-1.jpg`, `storyboard-2.jpg`.

## Flow & EDL (masa footage asal → masa dalam video)

| Video | Babak | Audio (apa kau cakap) | Footage asal | Edit / SFX / VFX |
|---|---|---|---|---|
| 0.00 | **HOOK 1** | "Hoyo nerf Mitya 7.3?" | 0:21 (gameplay dari 6:43, chat Zangetsu) | Teks frame-0 "VIEWER CAKAP… MITYA KENA NERF?! 😱" + chat bubble *Zangetsu: 7.3 nt neft katanya 💀*, vine boom |
| 1.48 | **HOOK 2** | "Oh my god!" | 15:55 (gameplay letupan burst 15:17) | Flash putih + bass impact, zoom punch + shake, "TAPI LEPAS AKU TEST… OH MY GOD! 🤯" |
| 2.61 | **HOOK 3** | "I will be the one who decides he is worthy or not" | 0:38 | Kad "WORTH IT KE TAK? 🤔 AKU YANG DECIDE" + avatar Mitya; muzik Carmen mula |
| 6.16 | Bug talk | "Aku dah dengar tapi apa? Teruk sangat ke? Bug tu." | 0:23 | HUD "TEST RUN MITYA · FIRST TIME" masuk |
| 9.07 | Salah sebut | "Dia tak nerf damage tapi dia ada bug… damage nerf or gameplay nerf. Eh sorry, gameplay bug" | 0:46–0:58 | Galaxy Brain PIP + X-Files (Illuminati) masa "explain", awkward SFX + "SALAH SEBUT 💀" |
| 15.39 | Idle + voice line | "Not bad, not bad" + Mitya: "I'd love to tell you some funny stories from work, but Scarf won't let me." | 1:25, 1:29 | Kad quote EN + BM santai |
| 20.76 | Interaksi chat | "Bang buat apa ni?" → "Aku tengah test run Mitya for the first time in lifetime" | 2:11, 2:16 | Chat bubble pop + notification |
| 25.37 | Lisa | "Dia macam Lisa… version Lisa tapi boy!" | 7:07 | Sticker "LISA VERSI LELAKI 💜" + cute wow, punch-in |
| 29.62 | 25 saat | "25 second? Serius lah?!" | 9:27 (skrin skill) | "25 SAAT?!" + vine boom + FAAAH, zoom shake |
| 31.10 | Timer | "Aku set timer phone aku. 3, 2, 1" | 10:13 | Countdown 3-2-1 besar + pop |
| 35.35 | Fast-forward | (26 s dipercepat 20×) | 10:19–10:45 | VFX **FF▶▶** (green screen keyed) + glitch |
| 36.65 | Confirmed | "Betul lah. 25 freaking second. Mitya tak main DPS pun dia berguna" | 10:46–11:00 | "✅ 25 SAAT CONFIRMED" + yay, "BERGUNA!" |
| 40.08 | Teater | Mitya: "Did you see the show at the theater yesterday?…" → "Kenapa aku pula yang tinggi suara ni?" | 12:50, 13:02 | Kad quote EN + BM, 😂😂😂 + laughing dog |
| 47.23 | Sedap | "Sedap lah pula Mitya ni" | 14:34 (cut-in burst 14:40) | "SEDAP 🤤" |
| 48.53 | **FEEDBACK** | "Memang elok sangat lah… Mitya Mitya Mitya" | 15:53, 15:58 (combat 15:25) | Muzik tukar Yu-Gi-Oh Winning Theme, stamp **VERDICT: WORTH IT ✅**, flash |
| 52.18 | Feedback | "Satisfying feeling when you charge attack… damage dia tu dia zap zap zap gitu" | 16:21, 16:30 (combat 15:31) | 4× "ZAP!" pop ikut setiap "zap" |
| 58.52 | Penutup | "20k like aku terpaksa pull. Memang sedap guys" | 16:10 (combat 15:40) | Pill "❤️ 20K LIKE = AKU PULL" |
| 61.26 | End card | — | Art Mitya (JPG) | "WORTH IT ✅ · Tekan ❤️ — 20K LIKE aku pull! · FOLLOW FOR MORE" |

## Apa yang dah dibuat
- Transcribe penuh 16.5 min (Whisper medium) + pass kedua large-v3 untuk segmen pilihan (tangkap campur BM/English dengan betul). Lihat `build/transcript_bm.txt`.
- Awkward pause dibuang: setiap senyap > 0.22 s dipotong ke 0.10 s (berasaskan tenaga audio), semua laju 1.07× (pitch kekal). Ayat berulang dibuang ("I will be the one" ×2, "Bam dah tahu…" ×2, "There's a difference" ×2, "25 second" berulang, "Oh my god" kedua, dll). QA: setiap klip ditranscribe semula untuk pastikan tiada perkataan terpotong.
- Layout dibina semula: banner statik bawah dibuang; facecam (1080×760) atas, gameplay (1080×1160) bawah, garis seam ungu-cyan. Chat lama yang burned-in ditutup dengan gradient (kawasan UI TikTok).
- Color grade (HyperFrames media-treatment): muka = `skin-soft` + exposure +0.06, shadows +0.1, kurang magenta (tint −0.03), lebih panas; gameplay = `deep-contrast` + vibrance 0.2 + bloom + vignette; shot terlalu terang (letupan, skrin skill, menu) highlight diturunkan.
- Teks dalam kawasan selamat TikTok (bawah 1330 px, jauh dari rail kanan).

## Rebuild
```
python3 build/cut.py "<Test Run Mitya.mp4>"    # potong, tighten, reframe, grade audio -> assets/face, assets/game, build/segs.json
# (FF overlay dikomposit atas assets/*/ff.mp4 — arahan ffmpeg dalam sejarah sesi)
python3 build/gen.py                            # jana index.html
npm run dev                                     # preview dalam HyperFrames Studio
npx hyperframes render -q looks --fps 60 -o out.mp4   # HANYA lepas approve
```
