"""Isometric city block, 2:1 pixel iso (tile 32x16), dusk. Art grid 384x336, then an HD-2D look pass (bloom, tilt-shift, vignette)."""
import math, random
from PIL import Image, ImageFilter, ImageChops
W,H=384,336; OX,OY=192,128; N=12
def hx(s): s=s.lstrip('#'); return tuple(int(s[i:i+2],16) for i in (0,2,4))
def lerp(a,b,t): return tuple(max(0,min(255,int(a[i]+(b[i]-a[i])*t))) for i in range(3))
def hsh(*a): return (hash(a)&0xffff)/65535.0
SKY=[hx(c) for c in ("#3b3170","#5a3f86","#8a4a90","#c05a86","#e8776e","#ffa06a","#ffc383")]
im=Image.new("RGB",(W,H)); px=im.load()
STEPS=18
def skycol(k):
    pos=k/(STEPS-1)*(len(SKY)-1); i=min(int(pos),len(SKY)-2); return lerp(SKY[i],SKY[i+1],pos-i)
for y in range(H):
    k=min(STEPS-1,int(y/ (H*0.78) *STEPS))
    for x in range(W): px[x,y]=skycol(k)
rs=random.Random(5)
def blob(cx,cy,r,col):
    for yy in range(int(cy-r),int(cy+r)+1):
        for xx in range(int(cx-r),int(cx+r)+1):
            if (xx-cx)**2+(yy-cy)**2<=r*r and 0<=xx<W and 0<=yy<H: px[xx,yy]=col
rs2=random.Random(21)
for _ in range(46):                                   # stars: distinct pixel clusters in the upper sky
    x,y=rs2.randint(0,W-1),rs2.randint(0,95); c=hx("#ffe9c8") if rs2.random()<.4 else hx("#c9b8f0")
    px[x,y]=c
    if rs2.random()<.18:
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            if 0<=x+dx<W and 0<=y+dy<H: px[x+dx,y+dy]=lerp(c,SKY[1],.5)
CLS=[hx("#7a4590"),hx("#d9708e"),hx("#ffc7a0")]
for cx,cy,n in ((70,70,7),(300,58,8),(210,28,6)):      # clouds: flat 3-tone clumps
    bl=[(cx+rs2.randint(-26,26),cy+rs2.randint(-5,5),rs2.randint(7,12)) for _ in range(n)]
    for k,(dx,dy,sh) in enumerate(((0,0,0),(-2,-3,2),(-4,-6,4))):
        for bx,by,r in bl: blob(bx+dx,by+dy,max(3,r-sh),CLS[k])
# far skyline: two flat layers with a few lit windows (hard shapes, no dither)
def skyline(base,hmin,hmax,col,win,seed):
    r=random.Random(seed); x=-6
    while x<W:
        w=r.randint(14,30); h=r.randint(hmin,hmax)
        for xx in range(x,min(W,x+w)):
            for yy in range(base-h,base):
                if 0<=xx<W and 0<=yy<H:
                    c=col
                    if xx==x or xx==x+1: c=lerp(col,(255,190,150),.22)
                    if win and (xx-x)%5 in (2,3) and (yy%6) in (2,3) and yy<base-4 and 3<xx-x<w-3 and hsh(xx//5,yy//6,seed)<.3: c=hx("#ffd890")
                    px[xx,yy]=c
        if r.random()<.4:
            for yy in range(base-h-8,base-h):
                if 0<=x+w//2<W and 0<=yy<H: px[x+w//2,yy]=col
        x+=w+r.randint(-4,3)
skyline(232,40,110,hx("#7a4e8e"),False,1)
skyline(246,26,80,hx("#5a3a7e"),True,2)
for yy in range(246,H):
    for xx in range(W): px[xx,yy]=lerp(hx("#5a3a7e"),hx("#2a2048"),(yy-246)/(H-246))
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
def box(bx0,bx1,by0,by1,z0,z1,lit,shd,top,glass=False,head=None):
    xc,yc=scr(bx1,by1)
    for face in (0,1):
        L=int(round(((bx1-bx0) if face==0 else (by1-by0))*16))
        for i in range(L):
            sx=xc-1-i if face==0 else xc+i; yb=yc-z0-i//2
            for v in range(z1-z0):
                c=shd if face==0 else lit
                if glass and 1<v<z1-z0-1 and 2<i<L-3:
                    c=hx("#2a2858") if (i+v)%7 else hx("#5a5aa0")
                if v==z1-z0-1: c=lerp(c,(255,235,200),.2)
                if v<1: c=lerp(c,(0,0,0),.35)
                put(sx,yb-v-1,c)
            if head and ((head=="R" and face==1) or (head=="L" and face==0)) and (i<2 or i>=L-2) and 1<=z1-z0:
                put(sx,yc-z0-i//2-3,hx("#ffe0a8")); put(sx,yc-z0-i//2-4,hx("#ffe0a8"))
            if head and ((head=="L" and face==1) or (head=="R" and face==0)) and (i<2 or i>=L-2):
                put(sx,yc-z0-i//2-3,hx("#e03030"))
    pts=[scr(bx0,by0,z1),scr(bx1,by0,z1),scr(bx1,by1,z1),scr(bx0,by1,z1)]
    for y in range(min(p[1] for p in pts),max(p[1] for p in pts)+1):
        for x in range(min(p[0] for p in pts),max(p[0] for p in pts)+1):
            gx,gy=inv(x+.5,y+.5+z1)
            if bx0<=gx<bx1 and by0<=gy<by1: put(x,y,top)
def car(cx,cy,axis,col,head):
    ln,wd=(0.75,0.3) if axis=="x" else (0.3,0.75)
    lit,shd=col,lerp(col,(20,10,50),.4); top=lerp(col,(255,235,200),.15)
    box(cx-ln,cx+ln,cy-wd,cy+wd,0,6,lit,shd,top,False,head)
    k=0.55
    box(cx-ln*k*0.9,cx+ln*k*0.9,cy-wd*.8,cy+wd*.8,6,11,lerp(col,(255,255,255),.1),lerp(shd,col,.3),lerp(col,(255,235,200),.25),True)
def ped(gx,gy,col,seed):
    sx,sy=scr(gx,gy)
    for dx in range(-3,4):
        for dy in range(-1,2): 
            if abs(dx)+abs(dy)*2<=3: put(sx+dx,sy+dy,hx("#1d1a3a"))
    r=random.Random(seed); skin=[hx("#e8b890"),hx("#c88a60"),hx("#f0c8a0")][seed%3]; hair=[hx("#2a1a20"),hx("#5a3a20"),hx("#c8a040")][seed%3]
    for y in range(sy-4,sy): put(sx-1,y,hx("#2a2858")); put(sx,y,hx("#2a2858"))
    for y in range(sy-10,sy-4):
        for x in range(sx-2,sx+2): put(x,y,col if x<sx else lerp(col,(255,255,255),.2))
    put(sx-2,sy-9,col); put(sx+1,sy-9,col)
    for y in range(sy-13,sy-10):
        for x in range(sx-1,sx+1): put(x,y,skin)
    for x in range(sx-1,sx+1): put(x,sy-14,hair)
    put(sx-2,sy-13,hair)
objs=[("b",BUILD[0],4),("b",BUILD[1],12)]
for gx,gy in ((4.5,2.2),(7.5,2.2),(4.5,9.3),(7.5,9.3),(1.4,4.5),(9.8,4.6)): objs.append(("t",(gx,gy),gx+gy))
for gx,gy in ((4.5,4.5),(7.5,4.5),(4.5,7.5),(7.5,7.5)): objs.append(("l",(gx,gy),gx+gy+.1))
for cx,cy,ax,col,hd in ((2.5,6.5,"x",hx("#d8434f"),"L"),(9.6,5.5,"x",hx("#e8e0d0"),"R"),(5.5,9.6,"y",hx("#3fa7a3"),"L"),(6.5,2.4,"y",hx("#e0a03f"),"R")):
    objs.append(("c",(cx,cy,ax,col,hd),cx+cy))
for i,(gx,gy,col) in enumerate(((2.0,4.55,hx("#d8434f")),(2.5,4.6,hx("#3fa7a3")),(9.2,4.55,hx("#e0a03f")),(9.7,4.6,hx("#d8434f")),(2.6,8.6,hx("#3fa7a3")),(3.1,8.45,hx("#e8e0d0")),(8.5,8.7,hx("#4a6ad0")))):
    objs.append(("p",(gx,gy,col,i),gx+gy))
objs.sort(key=lambda o:o[2])
for k,(kind,a,_) in enumerate(objs):
    if kind=="b": building(*a)
    elif kind=="t": tree(a[0],a[1],k)
    elif kind=="c": car(*a)
    elif kind=="p": ped(*a)
    else: lamp(*a)
art=im; art.save("iso_block_art.png")
S=3; big=art.resize((W*S,H*S),Image.NEAREST); big.save("iso_block_x3.png")
# ---- HD-2D look pass: bloom on bright, tilt-shift blur, vignette, warm grade
try:
    import numpy as np
    a=np.asarray(big).astype("float32")/255
    art_np=np.asarray(art).astype("int16")
    def near(c,t=10): return (abs(art_np-np.array(c)).sum(axis=2)<t)
    lights=near((255,211,107))|near((255,224,168))|near((255,217,140),14)
    lm=np.kron(lights,np.ones((S,S),dtype=bool))
    bright=np.where(lm[...,None],a,0)
    bl=Image.fromarray((bright*255).astype("uint8")).filter(ImageFilter.GaussianBlur(10))
    a=np.clip(a+np.asarray(bl).astype("float32")/255*1.0,0,1)
    blur=np.asarray(Image.fromarray((a*255).astype("uint8")).filter(ImageFilter.GaussianBlur(5))).astype("float32")/255
    yy=np.linspace(0,1,a.shape[0])[:,None,None]; m=np.clip(np.maximum((0.22-yy)/0.22,(yy-0.78)/0.22),0,1)
    a=a*(1-m)+blur*m
    xx=np.linspace(-1,1,a.shape[1])[None,:,None]; yv=np.linspace(-1,1,a.shape[0])[:,None,None]
    vig=1-0.28*np.clip(xx**2+yv**2-0.25,0,1); a=a*vig
    a=a*np.array([1.04,1.0,0.96])
    Image.fromarray((np.clip(a,0,1)*255).astype("uint8")).save("iso_block_hd2d.png")
    print("hd2d ok")
except Exception as e: print("hd2d skipped",e)
