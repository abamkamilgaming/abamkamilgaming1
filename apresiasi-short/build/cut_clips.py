#!/usr/bin/env python3
"""Cut + reframe each shot to 1080x1920 @30fps from the 4K originals.
usage: cut_clips.py <Raw Footage dir> <out dir>
shot: id, file, src_start, out_dur, speed, cx, cy, hfrac  (crop centre as fraction of frame, crop height as fraction)"""
import sys, subprocess, json, os
RAW, OUT = sys.argv[1], sys.argv[2]
CS, TA, PR, TK = "CS APRESIASI 2026", "tarian.mov", "Perarakan masuk", "Tokoh Murid Lelaki"
PK, PD, GM = "Ucapan PKP", "Ucapan Tuan PPD, Dr Nazri", "Gimik pelancaran"
SHOTS = [
 ("h1", CS, 719.0, 1.49, 0.8, .40, .40, .82),
 ("h2", TA, 176.0, 1.49, 1.0, .36, .58, .85),
 ("h3", CS, 528.0, 1.49, 0.8, .45, .40, .82),
 ("t1", PR,   0.5, 2.97, 1.0, .36, .50, 1.0),
 ("p3", PR,   9.5, 1.49, 1.0, .27, .50, 1.0),
 ("tk", TK,   2.5, 2.97, 1.0, .40, .55, .85),
 ("tr", TA,  60.5, 1.49, 1.0, .45, .62, .70),
 ("pk", PK,   0.3, 2.97, 1.0, .40, .50, .60),
 ("pd", PD,   5.6, 3.73, 1.0, .36, .50, .60),
 ("g1", GM,  37.0, 2.23, 1.0, .50, .42, .65),
 ("g2", GM,  39.9, 2.97, 0.5, .50, .42, .65),
 ("c1", CS, 352.0, 1.49, 0.8, .45, .40, .82),
 ("c2", CS, 484.0, 1.49, 0.8, .42, .40, .82),
 ("c3", CS, 708.0, 1.49, 0.8, .45, .40, .82),
 ("c4", CS, 494.5, 1.49, 0.8, .52, .45, .88),
]
only = set(sys.argv[3:])
def dims(f):
    o = json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height:stream_side_data=rotation","-of","json",f]))
    s=o["streams"][0]; w,h=s["width"],s["height"]
    rot=abs(int(float((s.get("side_data_list") or [{}])[0].get("rotation",0) or 0)))
    return (h,w) if rot in (90,270) else (w,h)
os.makedirs(OUT, exist_ok=True)
meta = {}
for sid,f,ss,dur,sp,cx,cy,hf in SHOTS:
    if only and sid not in only: continue
    src=os.path.join(RAW,f); W,H=dims(src)
    ch=int(H*hf)//2*2; cw=int(ch*9/16)//2*2
    if cw>W: cw=W//2*2; ch=int(cw*16/9)//2*2
    x=min(max(0,int(cx*W-cw/2)),W-cw); y=min(max(0,int(cy*H-ch/2)),H-ch)
    srcdur=dur*sp+0.05
    vf=f"crop={cw}:{ch}:{x}:{y},scale=1080:1920:flags=lanczos,setpts=PTS/{sp},fps=30,format=yuv420p"
    cmd=["ffmpeg","-v","error","-y","-ss",str(ss),"-t",f"{srcdur:.3f}","-i",src,"-vf",vf,"-an","-t",f"{dur:.3f}",
         "-c:v","libx264","-preset","medium","-crf","16","-g","15","-movflags","+faststart",os.path.join(OUT,sid+".mp4")]
    subprocess.run(cmd,check=True); meta[sid]=dict(file=f,src_start=ss,dur=dur,speed=sp,crop=[cw,ch,x,y])
    print(sid, meta[sid], flush=True)
json.dump(meta, open(os.path.join(OUT,"shots.json"),"w"), indent=1)
