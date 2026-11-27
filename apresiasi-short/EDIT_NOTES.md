# Majlis Apresiasi Kecemerlangan Murid 2026 — TikTok Short

**Format:** 1080×1920 (9:16), 30 fps, **35.6 s** (had 40 s)
**Status:** PREVIEW sahaja — belum render final.
**Gaya:** ikut "Video rujukan / TVPSS Five One" — caption serif italic di tengah bawah, grade lembut hangat (film memory), push-in perlahan, kad polaroid di hujung.

## Lagu (Lewati Berdua) — diedit ke 35.5 s
- Lagu 0:00–0:20.3 → crossfade 0.5 s (atas beat, 80.75 BPM) → lagu 0:40.6–tamat. Ending asli lagu kekal (hit akhir ≈ 33.2 s), fade out 34.6 s.
- Setiap potongan shot jatuh atas grid beat (2 beat = 1.49 s).

## Timeline
| Masa | Shot | Sumber (masa dalam fail asal) | Teks |
|---|---|---|---|
| 0.00 | HOOK | CS 11:57 — pose "sayap" (slow-mo 0.8×) | "Setahun berusaha…" |
| 1.49 | HOOK | tarian.mov 2:56 | "…hari ini, mereka diraikan." |
| 2.97 | HOOK | CS 6:02 | |
| 4.46 | TITLE | Perarakan masuk 0:00.5 | MAJLIS APRESIASI / Kecemerlangan Murid / 2026 / SK BUNUT PAYONG · 25.11.2026 |
| 7.43 | | Perarakan masuk 0:09.5 | "Melangkah penuh bangga" |
| 8.92 | | Tokoh Murid Lelaki 0:02.5 | "Setiap usaha, ada harganya" |
| 11.89 | | tarian.mov 1:00.5 | "Bakat yang bersinar" |
| 13.37 | Ucapan PKP | Ucapan PKP 0:00.3 (zoom ke podium) | “…salam dan ingatan daripada Guru Besar.” |
| 16.34 | Ucapan PPD | Ucapan Tuan PPD 0:05.6 | DIRASMIKAN OLEH / Dr. Mohd Nazri bin Hassan / Pegawai Pendidikan Daerah Kota Bharu |
| 20.07 | Gimik | Gimik pelancaran 0:37 | "Saat yang dinanti…" |
| 22.30 | Gimik (slow-mo 0.5×) | Gimik pelancaran 0:39.9 | kotak diangkat 23.29 s → flash + sparkle + "Dirasmikan." |
| 24.52 | **Choral Speaking — finale** | CS 11:44.6 (slow-mo 0.6×, pan kiri→kanan) | CHORAL SPEAKING / "Suara yang bersatu" |
| 27.49 | | CS 11:54.8 (slow-mo 0.6×, pan kanan→kiri) | "Satu hati, satu irama" |
| 29.72 | | CS 11:59.6 — klimaks sayap (slow-mo 0.6×) | "Terus bersinar, selamanya" |
| 32.69 | END | polaroid (CS 6:16), masuk tepat atas hit akhir lagu | "Tahun 2026" · "Tahniah, kalian kebanggaan kami." |

Choral Speaking: guna bahagian paling best = finale formasi "sayap" (11:44–12:04), crop potret 9:16 dengan pan perlahan + slow-mo supaya ikut mood balada di hujung lagu ("Membasuh perih di hatimu" → ending).

Ucapan PKP & PPD: suara asal **dimute**, lagu terus jalan (ikut mood lagu); petikan ucapan jadi caption gaya rujukan.

## Transkrip (Whisper large-v3, BM)
- Ucapan PKP: "Terlebih dahulu saya ingin menyampaikan salam dan ingatan daripada Guru Besar…"
- Ucapan Tuan PPD: "Yang Berbahagia Cikgu Suzila binti … / Yang Berbahagia Cikgu …" (salam pembuka, banyak jeda — sebab tu tak guna suara)
- Lagu: "Namun percayalah, kita akan lewati berdua / Di kala hujan turun deras / Lebatnya badai mungkin terasa / Tenangkan dirimu, aku bersamamu …"
- CS APRESIASI 2026 (12.5 min) = persembahan Choral Speaking; audio dewan bergema, transkrip tak boleh dipakai — guna untuk visual sahaja.
- JSON penuh: `build/transcripts/`.

## Rawatan
- Grade (HyperFrames media-treatment): `vintage-wash` 0.5 + exposure −0.06…−0.22 per shot, highlights −0.7, whites −0.35, contrast +0.16, blacks −0.1, warm +0.05, vignette 0.14, grain 0.1. Footage asal over-exposed — highlight ditarik turun.
- SFX: impact lembut di hook, whoosh di peralihan seksyen, riser → impact + sparkle masa kotak gimik diangkat, chime masa polaroid.

## Rebuild
```
python3 build/cut_clips.py "<Raw Footage dir>" assets/clips   # potong + reframe 9:16 dari 4K asal
python3 build/gen.py                                           # jana index.html
npx hyperframes preview                                        # preview
npx hyperframes render -q looks -o out.mp4                     # render final (lepas approve)
```
