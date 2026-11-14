import subprocess, json, sys, os
from concurrent.futures import ThreadPoolExecutor
SRC=sys.argv[1]; OUT=sys.argv[2]
# id, src_start, out_dur, rate, cx(px in 1920), mode, keep_audio
SHOTS=[
 ("A",5556.0,2.5,1.0,960,"wide",0),("B",18806.0,2.4,1.0,960,"wide",0),("C",2993.0,3.2,1.0,960,"wide",0),
 ("D1",1295.0,2.1,1.0,960,"full",0),("D2",19032.5,2.3,1.0,1000,"full",0),("E",19132.9,3.5,1.0,960,"full",1),
 ("F1",4466.0,2.3,1.0,960,"wide",0),("F2",4475.5,2.4,1.0,960,"full",0),("G",8893.4,2.6,1.0,960,"full",0),
 ("H",8903.7,1.45,1.0,1000,"full",1),("I",8918.0,4.0,2.0,960,"full",1),("J",18560.6,1.2,1.0,1350,"full",0),
 ("K",5508.0,3.5,1.6,760,"full",0),("L1",5493.3,1.35,1.0,960,"full",1),("L2",5495.7,1.55,1.0,1150,"full",1),
 ("M",18690.0,2.9,1.0,960,"full",0),("N",19138.8,2.15,1.0,960,"full",1),("O",2984.0,3.0,1.6,960,"wide",0),
 ("P",19371.45,1.5,1.0,1000,"full",1),("Q",19338.0,10.5,1.0,960,"wide",0),
]
def job(s):
    sid,ss,dur,rate,cx,mode,aud=s
    srcdur=(dur+0.25)*rate+0.1
    x=max(0,min(1920-608,int(cx-304)))
    if mode=="full":
        vf=f"setpts=PTS/{rate},crop=608:1080:{x}:0,scale=1080:1920:flags=lanczos,fps=30"
        fc=f"[0:v]{vf}[v]"
    else:
        fc=(f"[0:v]setpts=PTS/{rate},fps=30,split[a][b];"
            f"[a]crop=608:1080:{x}:0,scale=540:960,boxblur=20:2,scale=1080:1920,eq=brightness=-0.12:saturation=1.1[bg];"
            f"[b]crop=1100:860:410:0,scale=1080:-2:flags=lanczos[fg];[bg][fg]overlay=0:(H-h)/2-60[v]")
    cmd=["ffmpeg","-nostdin","-v","error","-y","-ss",str(ss),"-t",str(srcdur),"-i",SRC,"-filter_complex",fc,"-map","[v]"]
    if aud:
        cmd+=["-map","0:a","-af",f"atempo={rate}" if rate!=1 else "anull","-c:a","aac","-b:a","192k","-ar","48000"]
    else: cmd+=["-an"]
    cmd+=["-t",str(dur+0.25),"-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",f"{OUT}/{sid}.mp4"]
    r=subprocess.run(cmd,capture_output=True,text=True); return sid, r.returncode, r.stderr[-300:]
ONLY=sys.argv[3].split(',') if len(sys.argv)>3 else None
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(job,[x for x in SHOTS if not ONLY or x[0] in ONLY]): print(*r)
json.dump(SHOTS,open(f"{OUT}/shots.json","w"))
