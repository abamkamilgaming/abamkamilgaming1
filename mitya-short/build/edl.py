"""Edit decision list for the Mitya pull short. Source times in seconds of
'Pulling Mitya and Signature Weapon.mp4'. speed>1 = faster (talking pieces 1.1x)."""
# (id, src_in, src_out, speed, section)
PIECES = [
    # HOOK: signature weapon gold -> scream -> falls off chair
    ("h1", 770.55, 772.25, 1.0, "hook"),
    ("h2", 773.55, 778.40, 1.0, "hook"),
    # INTRO (Delfino Plaza)
    ("i1", 10.00, 14.62, 1.1, "intro"),   # mengadap Her Majesty Tsaritsa, Yang di-Pertuan Agung
    ("i2", 26.40, 28.05, 1.1, "intro"),   # Plus Mitya memang best okay
    ("i3", 31.65, 35.40, 1.1, "intro"),   # Please double gold early, signature early
    ("i4", 50.00, 55.95, 1.1, "intro"),   # Kalau live ni dapat 20 view aku tekan terus. Serius aku tak bergurau
    ("i5", 169.55, 171.75, 1.1, "intro"), # dah lah susah nak buat keputusan
    ("i6", 172.80, 175.72, 1.1, "intro"), # Kau ingat senang ke nak pull Mitya ni?
    ("i7", 176.40, 177.55, 1.0, "intro"), # Ya Allah
    ("i8", 296.70, 301.60, 1.1, "intro"), # Janganlah ya Allah... jangan bagi hard pity
    ("i9", 410.90, 414.55, 1.1, "intro"), # Aku tak terkejut pun kalau menang
    # MITYA PULL
    ("m1", 431.40, 436.25, 1.0, "mitya"), # wish -> gold star
    ("m2", 437.00, 505.00, 34.0, "mitya"),# fast forward through 4-stars
    ("m3", 507.80, 510.70, 1.0, "mitya"), # silhouette
    ("m4", 510.70, 513.45, 1.0, "mitya"), # MITYA! facepalm
    ("m5", 514.80, 519.85, 1.0, "mitya"), # waving, laughing
    # WEAPON BANNER
    ("w1", 657.75, 659.30, 1.1, "weapon"),# nak signature kalau boleh
    ("w2", 696.55, 698.35, 1.0, "weapon"),# Nooooo
    ("w3", 700.55, 701.35, 1.0, "weapon"),# ya Allah
    ("w4", 732.85, 733.95, 1.0, "weapon"),# Wasted
    ("w5", 765.45, 769.00, 1.0, "weapon"),# 46... 46
    ("w6", 769.00, 772.25, 1.0, "weapon"),# gold star
    ("w7", 773.45, 775.30, 1.0, "weapon"),# scream
    ("w8", 775.30, 778.85, 1.0, "weapon"),# Starsealed Edict + falls
    ("w9", 783.30, 787.05, 1.0, "weapon"),# N-I-C-E-E let's go
    ("w10", 788.60, 791.65, 1.0, "weapon"),# wow, yay, tahniah
    ("w11", 809.55, 810.95, 1.0, "weapon"),# this is my night
    ("w12", 813.45, 814.45, 1.0, "weapon"),# is it?
    # ENDING
    ("e1", 574.35, 576.65, 1.0, "end"),   # Habis primo aku. Habis!
    ("e2", 855.25, 860.40, 1.0, "end"),   # No Tsaritsa! Sorry!
]
FREEZE_AT = 775.30   # hook freeze frame
