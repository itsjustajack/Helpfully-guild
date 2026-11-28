"""Isometric city block, 2:1 pixel iso (tile 32x16), dusk. Art grid 384x336, then an HD-2D look pass (bloom, tilt-shift, vignette)."""
import math, random
from PIL import Image, ImageFilter, ImageChops
W,H=384,336; OX,OY=192,128; N=12
def hx(s): s=s.lstrip('#'); return tuple(int(s[i:i+2],16) for i in (0,2,4))
def lerp(a,b,t): return tuple(max(0,min(255,int(a[i]+(b[i]-a[i])*t))) for i in range(3))
def hsh(*a): return (hash(a)&0xffff)/65535.0
SKY=[hx(c) for c in ("#3b3170","#5a3f86","#8a4a90","#c05a86","#e8776e","#ffa06a","#ffc383")]
im=Image.new("RGB",(W,H)); px=im.load()
for y in range(H):
    for x in range(W): px[x,y]=SKY[min(6,int(y/H*7*1.0))]
def put(x,y,c):
    if 0<=x<W and 0<=y<H: px[x,y]=c
def scr(gx,gy,gz=0): return int(round(OX+(gx-gy)*16)), int(round(OY+(gx+gy)*8-gz))
def inv(sx,sy): a=(sx-OX)/16; b=(sy-OY)/8; return (a+b)/2,(b-a)/2
BUILD=[(0,4,0,4,112,"brick"),(8,12,0,4,96,"orange")]      # bx0,bx1,by0,by1,height,colour
def inshadow(gx,gy):
    for bx0,bx1,by0,by1,h,_ in BUILD:
        d=h/40.0
        if bx0<=gx<bx1 and by1<=gy<by1+d*(1-0.0): return True
    return False
ROAD=lambda g:5<=g<7
ASPH=hx("#3b3354"); ASPH2=hx("#453b5e"); SIDE=hx("#8a7eb0"); SIDE2=hx("#7a6ea0"); JOINT=hx("#5c5280"); CURB=hx("#b4a8d8")
# ---- ground by inverse mapping
for y in range(H):
    for x in range(W):
        gx,gy=inv(x+.5,y+.5)
        if not(0<=gx<N and 0<=gy<N): continue
        rx,ry=ROAD(gx),ROAD(gy)
        if rx or ry:
            c=ASPH if int(gx*3+gy*3)%5 else ASPH2
            if rx and ry: pass
            elif ry:   # road runs along x (gy in 5..7)
                if abs(gy-6)<.05 and not(3.9<gx<5.05 or 6.95<gx<8.1): c=hx("#f2c14e")
                elif (3.9<gx<4.9 or 7.1<gx<8.1) and int((gy-5)*4.5)%2==0: c=hx("#e2dce8")
            else:      # road runs along y
                if abs(gx-6)<.05 and not(3.9<gy<5.05 or 6.95<gy<8.1): c=hx("#f2c14e")
                elif (3.9<gy<4.9 or 7.1<gy<8.1) and int((gx-5)*4.5)%2==0: c=hx("#e2dce8")
        else:
            c=SIDE if (int(gx)+int(gy))%2 else SIDE2
            for e in (5,7):
                if abs(gx-e)<.09 or abs(gy-e)<.09: c=CURB
            if abs(gx-int(gx))<.04 or abs(gy-int(gy))<.04: c=JOINT
        if inshadow(gx,gy): c=lerp(c,hx("#1d1a3a"),.42)
        px[x,y]=c
# ---- slab sides (diorama thickness)
TH=14
for i in range(N*16):
    for side in (0,1):
        if side==0: xc=OX-(N-0)*0; sx=scr(N,N)[0]-1-i; ytop=scr(N,N)[1]-i//2   # left face (gy=N)
        else: sx=scr(N,N)[0]+i; ytop=scr(N,N)[1]-i//2
        for t in range(TH):
            c=hx("#3a2a50") if side==0 else hx("#4e3a66")
            if t%5==4: c=lerp(c,(0,0,0),.25)
            put(sx,ytop+t,c)
# ---- sprites
def building(bx0,bx1,by0,by1,Hh,kind):
    lit,shd={"brick":(hx("#c83a3a"),hx("#8e2a46")),"orange":(hx("#f08a2a"),hx("#c06030")),"blue":(hx("#4a6ad0"),hx("#2f4496"))}[kind]
    xc,yc=scr(bx1,by1)
    for face in (0,1):
        L=((bx1-bx0) if face==0 else (by1-by0))*16
        base=shd if face==0 else lit
        for i in range(L):
            sx=xc-1-i if face==0 else xc+i
            yb=yc-i//2
            for v in range(Hh):
                y=yb-v-1; c=base
                u=i if face==0 else i
                fl=v//20; fv=v%20
                if v<18:                                         # ground floor shop
                    c=lerp(base,(10,5,30),.5)
                    if 3<v<13 and 3<u%32<29: c=lerp(hx("#5a5aa0"),hx("#ffd36b"),.6) if (u//32+face)%2==0 else hx("#2a2858")
                    elif 13<=v<16: c=hx("#d8434f") if (u//4)%2==0 else hx("#f0d8c8")
                    elif v>=16: c=hx("#7a2f4c") if face==0 else hx("#2f5a4a")
                elif fv>=17 and v<Hh-4: c=lerp(base,(255,225,190),.3)       # floor ledge
                elif v>=Hh-4: c=lerp(base,(255,225,190),.4) if v>=Hh-2 else lerp(base,(0,0,0),.3)  # cornice
                elif 4<fv<14 and 3<u%12<9:
                    inner=5<fv<13 and 4<u%12<8
                    lit_w=hsh(u//12,fl,face,bx0)<.4
                    c=(hx("#ffd36b") if lit_w else hx("#2a2858")) if inner else lerp(base,(255,225,190),.45)
                    if inner and not lit_w and fv>9: c=lerp(c,hx("#5a5aa0"),.4)
                else:
                    row=v//3; off=2 if row%2 else 0
                    j=hsh(row,(u+off)//5,face)
                    c=lerp(base,(0,0,0),.08+.1*j)
                    if v%3==0 or (u+off)%5==0: c=lerp(base,(0,0,0),.3)
                if i<2: c=lerp(c,(255,225,170),.25) if face==1 else c   # edge light
                put(sx,y,c)
    # roof
    pts=[scr(bx0,by0,Hh),scr(bx1,by0,Hh),scr(bx1,by1,Hh),scr(bx0,by1,Hh)]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    for y in range(int(min(ys)),int(max(ys))+1):
        for x in range(int(min(xs)),int(max(xs))+1):
            gx,gy=inv(x+.5,y+.5+ (Hh))   # invert at roof height
            if bx0<=gx<bx1 and by0<=gy<by1:
                c=hx("#6a5a80"); 
                if gx<bx0+.25 or gy<by0+.25 or gx>bx1-.25 or gy>by1-.25: c=hx("#8a7aa0")
                if hsh(int(gx*3),int(gy*3))<.08: c=hx("#4a3f62")
                put(x,y,c)
G=[tuple(hx(c)) for c in ("#12461f","#1f7a2e","#2fa832","#58cc3c","#92e84e","#d0f470")]
def tree(gx,gy,seed):
    rnd=random.Random(seed); sx,sy=scr(gx,gy)
    for y in range(sy-26,sy+1):
        for x in range(sx-2,sx+2): put(x,y,hx("#6a4a50") if x<sx else hx("#3e2640"))
    cx,cy=sx,sy-40
    lumps=[(cx+rnd.uniform(-1,1)*18*math.sqrt(rnd.random()),cy+rnd.uniform(-1,1)*14,rnd.uniform(4.5,7.5)) for _ in range(34)]
    lumps.sort(key=lambda l:l[1]+l[0]*.5)
    for li,(lx,ly,r) in enumerate(lumps):
        for y in range(int(ly-r)-1,int(ly+r)+2):
            for x in range(int(lx-r)-1,int(lx+r)+2):
                dx,dy=x-lx,y-ly
                if dx*dx+dy*dy*1.1>(r*(1+.15*math.sin(math.atan2(dy,dx)*4+li)))**2: continue
                t=(-dx*.6-dy*.8)/r*.9-((ly-cy)/14)*.55
                k=0 if t<-.55 else 1 if t<-.1 else 2 if t<.35 else 3 if t<.75 else 4
                put(x,y,G[k])
    for _ in range(26): put(int(cx+rnd.uniform(-17,12)),int(cy+rnd.uniform(-14,4)),G[5])
def lamp(gx,gy):
    sx,sy=scr(gx,gy)
    for y in range(sy-44,sy+1): put(sx,y,hx("#2a2a48"))
    for dx in range(-2,3):
        for dy in range(-2,3):
            if abs(dx)+abs(dy)<=3: put(sx+dx,sy-47+dy,hx("#ffe0a8"))
objs=[("b",BUILD[0],4),("b",BUILD[1],12)]
for gx,gy in ((4.5,2.2),(7.5,2.2),(4.5,9.3),(7.5,9.3),(1.4,4.5),(9.8,4.6)): objs.append(("t",(gx,gy),gx+gy))
for gx,gy in ((4.5,4.5),(7.5,4.5),(4.5,7.5),(7.5,7.5)): objs.append(("l",(gx,gy),gx+gy+.1))
objs.sort(key=lambda o:o[2])
for k,(kind,a,_) in enumerate(objs):
    if kind=="b": building(*a)
    elif kind=="t": tree(a[0],a[1],k)
    else: lamp(*a)
art=im; art.save("iso_block_art.png")
S=3; big=art.resize((W*S,H*S),Image.NEAREST); big.save("iso_block_x3.png")
# ---- HD-2D look pass: bloom on bright, tilt-shift blur, vignette, warm grade
try:
    import numpy as np
    a=np.asarray(big).astype("float32")/255
    lum=a.max(axis=2); bright=np.where((lum>0.86)[...,None],a,0)
    bl=Image.fromarray((bright*255).astype("uint8")).filter(ImageFilter.GaussianBlur(14))
    a=np.clip(a+np.asarray(bl).astype("float32")/255*1.1,0,1)
    blur=np.asarray(Image.fromarray((a*255).astype("uint8")).filter(ImageFilter.GaussianBlur(5))).astype("float32")/255
    yy=np.linspace(0,1,a.shape[0])[:,None,None]; m=np.clip(np.maximum((0.22-yy)/0.22,(yy-0.78)/0.22),0,1)
    a=a*(1-m)+blur*m
    xx=np.linspace(-1,1,a.shape[1])[None,:,None]; yv=np.linspace(-1,1,a.shape[0])[:,None,None]
    vig=1-0.35*np.clip(xx**2+yv**2-0.25,0,1); a=a*vig
    a=a*np.array([1.04,1.0,0.96])
    Image.fromarray((np.clip(a,0,1)*255).astype("uint8")).save("iso_block_hd2d.png")
    print("hd2d ok")
except Exception as e: print("hd2d skipped",e)
