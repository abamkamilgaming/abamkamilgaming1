#!/usr/bin/env python3
"""Cut + reframe each shot to 1080x1920 @30fps from the 4K originals.
usage: cut_clips.py <Raw Footage dir> <out dir>
shot: id, file, src_start, out_dur, speed, cx, cy, hfrac  (crop centre as fraction of frame, crop height as fraction)"""
import sys, subprocess, json, os
RAW, OUT = sys.argv[1], sys.argv[2]
CS, TA, PR, TK = "CS APRESIASI 2026", "tarian.mov", "Perarakan masuk", "Tokoh Murid Lelaki"
PK, PD, GM = "Ucapan PKP", "Ucapan Tuan PPD, Dr Nazri", "Gimik pelancaran"
SHOTS = [
 ("h1", CS, 717.3, 1.49, 0.8, .46, .40, .78),
 ("h2", TA, 176.0, 1.49, 1.0, .36, .58, .85),
 ("h3", CS, 362.0, 1.49, 0.8, .45, .40, .82),
 ("t1", PR,   0.5, 2.97, 1.0, .36, .50, 1.0),
 ("p3", PR,   9.5, 1.49, 1.0, .27, .50, 1.0),
 ("tk", TK,   2.5, 2.97, 1.0, .40, .55, .85),
 ("tr", TA,  60.5, 1.49, 1.0, .45, .62, .70),
 ("pk", PK,   0.3, 2.97, 1.0, .40, .50, .60),
 ("pd", PD,   5.6, 3.73, 1.0, .36, .50, .60),
 ("g1", GM,  37.0, 2.23, 1.0, .50, .42, .65),
 ("g2", GM,  39.9, 2.23, 0.5, .50, .42, .65),
 # Choral Speaking finale (best part): slow-mo 0.6x, portrait crop panning across the formation
 ("c1", CS, 704.6, 2.97, 0.6, .34, .40, .78, .54),
 ("c2", CS, 714.8, 2.23, 0.6, .58, .40, .78, .42),
 ("c3", CS, 719.6, 2.97, 0.6, .40, .40, .78, .52),
]
only = set(sys.argv[3:])
def dims(f):
    o = json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height:stream_side_data=rotation","-of","json",f]))
    s=o["streams"][0]; w,h=s["width"],s["height"]
    rot=abs(int(float((s.get("side_data_list") or [{}])[0].get("rotation",0) or 0)))
    return (h,w) if rot in (90,270) else (w,h)
os.makedirs(OUT, exist_ok=True)
meta = {}
for sid,f,ss,dur,sp,cx,cy,hf,*rest in SHOTS:
    if only and sid not in only: continue
    src=os.path.join(RAW,f); W,H=dims(src)
    ch=int(H*hf)//2*2; cw=int(ch*9/16)//2*2
    if cw>W: cw=W//2*2; ch=int(cw*16/9)//2*2
    x=min(max(0,int(cx*W-cw/2)),W-cw); y=min(max(0,int(cy*H-ch/2)),H-ch)
    srcdur=dur*sp+0.05
    xe=str(x)
    if rest:
        x2=min(max(0,int(rest[0]*W-cw/2)),W-cw); xe=f"'{x}+({x2-x})*min(t/{dur*sp:.3f}\\,1)'"
    vf=f"crop={cw}:{ch}:{xe}:{y},scale=1080:1920:flags=lanczos,setpts=PTS/{sp},fps=60,format=yuv420p"
    cmd=["ffmpeg","-v","error","-y","-ss",str(ss),"-t",f"{srcdur:.3f}","-i",src,"-vf",vf,"-an","-t",f"{dur:.3f}",
         "-c:v","libx264","-preset","medium","-crf","16","-g","30","-movflags","+faststart",os.path.join(OUT,sid+".mp4")]
    subprocess.run(cmd,check=True); meta[sid]=dict(file=f,src_start=ss,dur=dur,speed=sp,crop=[cw,ch,x,y], pan_to=(rest[0] if rest else None))
    print(sid, meta[sid], flush=True)
json.dump(meta, open(os.path.join(OUT,"shots.json"),"w"), indent=1)
