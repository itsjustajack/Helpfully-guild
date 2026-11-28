"""Dusk street, one-point perspective, drawn on a 256x256 pixel grid, reduced to <=32 colours, shown 4x."""
import random, math
from PIL import Image
W=H=256; VX,VY=128,140; F=120.0; CAMH=1.5
random.seed(7)
def hx(s): s=s.lstrip('#'); return tuple(int(s[i:i+2],16) for i in (0,2,4))
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
SKY=[hx(c) for c in ("#3b3170","#5a3f86","#8a4a90","#c05a86","#e8776e","#ff9d6a","#ffc383")]
HORIZON=hx("#f2a58e")
im=Image.new("RGB",(W,H)); px=im.load()
BAYER=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
for y in range(H):
    t=min(1,y/VY); pos=t*(len(SKY)-1); i=min(int(pos),len(SKY)-2); fr=pos-i
    for x in range(W):
        k=i+(1 if fr>BAYER[y%4][x%4]/16 else 0)
        px[x,y]=SKY[k] if y<VY+1 else HORIZON
def disc(cx,cy,r,col):
    for y in range(int(cy-r),int(cy+r)+1):
        for x in range(int(cx-r),int(cx+r)+1):
            if 0<=x<W and 0<=y<H and (x-cx)**2+(y-cy)**2<=r*r: px[x,y]=col
# clouds: shadow, mid, lit layers
CL=[hx("#8a5a9a"),hx("#e58a98"),hx("#ffd2a8")]
for cx,cy,n in ((60,40,9),(190,24,8),(120,75,6),(232,70,5)):
    blobs=[(cx+random.randint(-34,34),cy+random.randint(-7,7),random.randint(9,15)) for _ in range(n)]
    for k,(dx,dy,sh) in enumerate(((0,0,0),(-2,-3,2),(-4,-6,5))):
        for bx,by,r in blobs: disc(bx+dx,by+dy,max(3,r-sh),CL[k])
# far towers
for x0,w,h,c in ((92,22,98,"#6a5a9a"),(138,24,84,"#7a62a0"),(114,12,60,"#8a6aa0"),(158,14,52,"#9a72a4"),(122,8,26,"#a87ba6")):
    c=hx(c)
    for y in range(VY-h,VY+1):
        for x in range(x0,x0+w):
            wnd=(x-x0)%4 in (1,2) and (y%5) in (1,2) and y<VY-3
            px[x,y]=lerp(c,hx("#ffd890"),0.55) if wnd and random.random()<0.35 else (lerp(c,(0,0,0),.12) if wnd else c)
# facade blocks
def blocks():
    z=0.4; out=[]
    while z<70:
        L=random.uniform(6,13); out.append((z,z+L,random.uniform(13,30),random.choice(("brick","orange","blue","brick")))); z+=L
    return out
BL={-1:blocks(),1:blocks()}
BASE={"brick":(hx("#a8404c"),hx("#7a2f4c")),"orange":(hx("#e0803f"),hx("#b05a46")),"blue":(hx("#6a6aa8"),hx("#46467e"))}
NAVY=hx("#2a2858"); GLASS=hx("#5a5aa0"); LIT=hx("#ffd36b"); SHOP=hx("#3a2a58")
def fog(c,z): return lerp(c,HORIZON,min(1,(z/75.0))**0.9*0.40)
for x in range(W):
    dx=x-VX
    if dx==0: dx=0.01
    side=-1 if dx<0 else 1
    z=F*4.5/abs(dx)
    blk=next((b for b in BL[side] if b[0]<=z<b[1]),BL[side][-1]); bi=BL[side].index(blk)
    ytop=int(VY+(CAMH-blk[2])*F/z); ybot=int(VY+CAMH*F/z)
    lit,shd=BASE[blk[3]]; base=lit if side==1 else shd
    for y in range(max(0,ytop),min(H,ybot+1)):
        h=CAMH-(y-VY)*z/F; fl=int(h//3.2); fh=h%3.2; wz=z%2.6
        c=base
        if fl==0:
            c=lerp(base,SHOP,.55)
            if 0.5<fh<2.3 and 0.4<wz<2.2: c=lerp(GLASS,LIT,.5) if (bi+int(z/2.6))%3==0 else lerp(NAVY,GLASS,.3)
            if 2.3<=fh<2.9: c=hx("#d8434f") if (bi+int(z/5))%2 else hx("#3fa7a3")
        else:
            if fh>2.85: c=lerp(base,(255,225,170),.25)
            elif 0.7<fh<2.5 and 0.5<wz<1.9:
                lit_w=((bi*7+fl*13+int(z/2.6)*5)%10)<3
                c=LIT if lit_w else (GLASS if fh>2.2 else NAVY)
            elif z<14 and int(h*2.5)%2==0: c=lerp(base,(0,0,0),.10)
        if y==max(0,ytop) or y==ytop+1: c=lerp(base,(255,225,170),.35) if side==1 else lerp(base,(255,200,150),.2)
        px[x,y]=fog(c,z)
    # ground
    for y in range(max(ybot+1,VY+1),H):
        z=CAMH*F/(y-VY); X=(x-VX)*z/F; ax=abs(X)
        if ax<3.0:
            c=hx("#3b3354") if int(z*0.8+X*0.5)%7 else hx("#453b5e")
            if ax<0.08 or 0.17<ax<0.25: c=hx("#f2c14e")
            elif 1.4<ax<1.5 and (z%4)<2: c=hx("#d8d0e0")
            if 3.4<z<5.0 and ((int((X+3)/0.55))%2==0): c=hx("#e2dce8")
            if X<-0.4: c=lerp(c,hx("#1d1a3a"),.35)
            if abs(ax-3.0)<0.1: c=hx("#9a8cc0")
        else:
            c=hx("#8a7eb0") if (int(z/1.5)+int(ax*1.2))%2 else hx("#7a6ea0")
            if abs(z%1.5)<0.07: c=hx("#5c5280")
            if X<0: c=lerp(c,hx("#3a2f66"),.4)
        px[x,y]=fog(c,z)
# trees, lamps
G=[hx("#1f4a4e"),hx("#2f7a52"),hx("#4f9a50"),hx("#8cc45c")]
def tree(side,z):
    s=F/z; X=side*3.7; sx=VX+X*s; gy=VY+CAMH*s; cy=VY+(CAMH-3.6)*s; r=1.9*s
    for y in range(int(cy),int(gy)):
        for x in range(int(sx-s*0.09),int(sx+s*0.09)+1):
            if 0<=x<W and 0<=y<H: px[x,y]=fog(hx("#4a2f44"),z)
    rnd=random.Random(int(z*100)+side)
    cl=[(rnd.uniform(-.65,.65)*r,rnd.uniform(-.55,.45)*r,rnd.uniform(.22,.36)*r) for _ in range(26)]
    for k,(dx,dy,sh) in enumerate(((0,0,0),(-.08,-.1,.1),(-.16,-.2,.2),(-.22,-.3,.32))):
        for ox,oy,rr in cl: disc(sx+ox+dx*r,cy+oy+dy*r,max(1.5,rr*(1-sh)),fog(G[k],z))
def lamp(side,z):
    s=F/z; sx=VX+side*3.15*s; gy=VY+CAMH*s; top=VY+(CAMH-5)*s
    for y in range(int(top),int(gy)):
        if 0<=int(sx)<W and 0<=y<H: px[int(sx),y]=hx("#2a2a48")
    disc(sx,top,max(1,s*.12),hx("#ffe0a8"))
for z in (60,44,32,24,17,12,8.5,5.5,3.3):
    for side in (-1,1):
        if (int(z)+side)%2==0 or z>20: tree(side,z)
        if z in (44,24,12,5.5): lamp(-side,z*1.05)
# a car or two
def car(X,z,c):
    s=F/z; x0=int(VX+(X-.9)*s); x1=int(VX+(X+.9)*s); yb=int(VY+CAMH*s); y0=int(yb-1.4*s)
    for y in range(y0,yb):
        for x in range(x0,x1):
            if 0<=x<W and 0<=y<H: px[x,y]=fog(c if y>y0+.45*s else hx("#2a2858"),z)
car(1.5,34,hx("#d8434f")); car(-1.6,46,hx("#e8e0d0"))
out=im.quantize(32,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert("RGB")
out.save("street_dusk_art_256.png"); out.resize((1024,1024),Image.NEAREST).save("street_dusk_x4.png")
print("colours:",len(out.getcolors(100000)))
ref=Image.open("../../style-guide/references/ref_city_street.webp").convert("RGB").resize((512,512))
cmp=Image.new("RGB",(1024,512)); cmp.paste(ref,(0,0)); cmp.paste(out.resize((512,512),Image.NEAREST),(512,0)); cmp.save("compare_street.png")
