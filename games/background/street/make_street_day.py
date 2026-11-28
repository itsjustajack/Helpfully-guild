"""Dusk street v2: 256x256 art grid, one-point perspective, city backdrop at the end, textured walls, leafy trees. Reduced to 48 colours, shown 4x."""
import random
from PIL import Image
W=H=256; VX,VY=128,178; F=135.0; CAMH=1.5; ZEND=46.0
random.seed(11)
def hx(s): s=s.lstrip('#'); return tuple(int(s[i:i+2],16) for i in (0,2,4))
def lerp(a,b,t): return tuple(max(0,min(255,int(a[i]+(b[i]-a[i])*t))) for i in range(3))
def hsh(*a): return (hash(a)&0xffff)/65535.0
SKY=[hx(c) for c in ("#1678c0","#1a8fd0","#20a8dc","#30c0e6","#60d6ee","#9ae6f0","#c8f2f4")]
HORIZON=hx("#a8e4ee")
im=Image.new("RGB",(W,H)); px=im.load()
BAY=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
for y in range(H):
    t=min(1,y/VY); pos=t*(len(SKY)-1); i=min(int(pos),len(SKY)-2); fr=pos-i
    for x in range(W):
        px[x,y]=SKY[i+(1 if fr>=.5 else 0)] if y<=VY else HORIZON
def put(x,y,c):
    if 0<=x<W and 0<=y<H: px[x,y]=c
def disc(cx,cy,r,col):
    for y in range(int(cy-r),int(cy+r)+1):
        for x in range(int(cx-r),int(cx+r)+1):
            if (x-cx)**2+(y-cy)**2<=r*r: put(x,y,col)
CL=[hx("#a8c8e8"),hx("#e8f4ff"),hx("#ffffff")]
for cx,cy,n in ((55,38,10),(200,26,9),(120,78,6),(236,86,5)):
    bl=[(cx+random.randint(-36,36),cy+random.randint(-7,7),random.randint(9,15)) for _ in range(n)]
    for k,(dx,dy,sh) in enumerate(((0,0,0),(-2,-3,2),(-4,-6,5))):
        for bx,by,r in bl: disc(bx+dx,by+dy,max(3,r-sh),CL[k])
# ---- city backdrop at end of street (3 fog layers)
YG=int(VY+CAMH*F/ZEND)
def layer(col,n,hmin,hmax,wmin,wmax,win,fogt):
    x=-10
    while x<W+10:
        w=random.randint(wmin,wmax); h=random.randint(hmin,hmax); c=lerp(col,HORIZON,fogt)
        top=YG-h
        for y in range(top,YG+1):
            for xx in range(x,x+w):
                c2=c
                if xx<x+2: c2=lerp(c,(255,215,170),.25)      # sunlit edge
                elif xx>=x+w-2: c2=lerp(c,(30,20,70),.25)
                if win and (xx-x)%4 in (1,2) and (y%5) in (1,2) and y<YG-3 and 2<xx-x<w-3:
                    c2=lerp(c,hx("#b8d0f8"),.7) if hsh(xx//4,y//5,x)<.33 else lerp(c,(20,15,60),.25)
                put(xx,y,c2)
        if random.random()<.5: # stepped top / antenna
            for y in range(top-6,top): put(x+w//2,y,lerp(c,(0,0,0),.2))
            for y in range(top-3,top):
                for xx in range(x+3,x+w-3): put(xx,y,c)
        x+=w+random.randint(-3,2)
layer(hx("#7a88c0"),0,40,100,12,24,False,.55)
layer(hx("#5a68b0"),0,28,76,10,22,True,.38)
layer(hx("#4a50a0"),0,16,52,9,18,True,.2)
# ---- facades
def blocks():
    z=0.4; out=[]; prev=None
    while z<ZEND+8:
        L=random.uniform(6,11); k=random.choice([c for c in ("brick","orange","blue","red","cream","orange","blue") if c!=prev]); prev=k
        H=random.uniform(34,44) if z<9 else random.uniform(13,27)
        out.append((z,z+L,H,k)); z+=L
        g=random.uniform(1.3,2.2); out.append((z,z+g,30,"alley")); z+=g
    return out
BL={-1:blocks(),1:blocks()}
BASE={"cream":(hx("#d8d8e8"),hx("#9a9ab8")),"brick":(hx("#b03030"),hx("#6a1830")),"orange":(hx("#f08a2a"),hx("#c06030")),"blue":(hx("#4a3fa0"),hx("#2f2878")),"red":(hx("#c82828"),hx("#7a1a30"))}
NAVY=hx("#1a2060"); GLASS=hx("#4a6ad0"); LIT=hx("#8ab8f4"); CREAM=(235,235,250)
def fog(c,z): return lerp(c,HORIZON,min(1,(z/ZEND))**1.1*0.25)
for x in range(W):
    dx=x-VX
    if dx==0: dx=0.01
    side=-1 if dx<0 else 1
    zw=F*5.2/abs(dx)
    if zw<ZEND:
        blk=next((b for b in BL[side] if b[0]<=zw<b[1]),BL[side][-1]); bi=BL[side].index(blk)
        if blk[3]=="alley":
            z2=F*10.0/abs(dx); yt=int(VY+(CAMH-blk[2])*F/z2); yb=int(VY+CAMH*F/z2)
            for y in range(max(0,yt),min(H,yb+1)):
                hh=CAMH-(y-VY)*z2/F
                c=lerp(hx("#1a1a50"),hx("#4a4a90"),min(1,max(0,(hh-4)/20)))
                if hsh(x//2,y//3)<.05: c=hx("#8ab8f4")
                px[x,y]=fog(c,zw)
            wb=yb; continue_ground=True
            ytop=yt; ybot=yb
        else:
            ytop=int(VY+(CAMH-blk[2])*F/zw); ybot=int(VY+CAMH*F/zw)
        if blk[3]=='alley': lit,shd=BASE['brick']
        else: lit,shd=BASE[blk[3]]
        base=lit if side==1 else lerp(shd,lit,.35)
        ytop2=max(0,ytop)
        for y in (range(ytop2,min(H,ybot+1)) if blk[3]!='alley' else []):
            z=zw; h=CAMH-(y-VY)*z/F; fl=int(h//3.4); fh=h%3.4; wz=z%2.7; wi=int(z/2.7)
            c=base
            if fl==0:
                ac=[(hx("#d8434f"),hx("#f0d8c8")),(hx("#3fa7a3"),hx("#e0f0e8")),(hx("#e0a03f"),hx("#f8e8c0"))][(bi+int(z/9))%3]
                sg=[hx("#7a2f4c"),hx("#1f3f6a"),hx("#2f5a4a")][(bi+int(z/9))%3]
                c=lerp(base,(10,5,30),.5); sx=z%4.2
                if 2.5<=fh<3.1:
                    c=sg
                    if 0.5<sx<3.7 and int(fh*9)%3!=0 and (int(z*5)+int(fh*9))%2==0 and int(z*5)%3!=0: c=hx("#f5e6c8")
                elif 2.05<=fh<2.5:
                    c=ac[0] if int(z*0.9)%2==0 else ac[1]
                    if fh<2.15: c=lerp(c,(10,5,30),.45)
                elif 0.15<fh<2.05 and 0.35<sx<3.85:
                    if 2.7<sx<3.6 and fh<1.95: c=lerp(hx("#2a2040"),LIT,.35)
                    elif abs(sx-2.65)<.05 or abs(sx-.35)<.05 or fh<.3: c=lerp(base,CREAM,.3)
                    else: c=lerp(GLASS,LIT,.55) if (bi+int(z/4.2))%2==0 else lerp(NAVY,GLASS,.35)
                else:
                    c=lerp(c,base,.2*hsh(int(z*3),int(h*4)))
            else:
                inwin=0.6<fh<2.7 and 0.4<wz<2.1
                if fh>3.05:                                   # cornice band with shadow below
                    c=lerp(base,CREAM,.3) if fh<3.25 else lerp(base,(255,200,150),.15)
                elif fh>2.95: c=lerp(base,(0,0,0),.35)
                elif inwin:
                    inner=0.78<fh<2.55 and 0.55<wz<1.95
                    lit_w=((bi*7+fl*13+wi*5)%10)<3
                    arch=fh>2.3 and (abs(wz-1.25)>0.55-(fh-2.3)*0.9)
                    if not inner or arch: c=lerp(base,CREAM,.45)
                    elif abs(wz-1.25)<.05 or abs(fh-1.65)<.06: c=lerp(base,CREAM,.3)
                    elif lit_w: c=LIT if fh<1.65 else lerp(LIT,(255,245,200),.5)
                    else:
                        c=NAVY if fh<1.65 else lerp(NAVY,GLASS,.35)
                        if (wz*2.2+fh)%1.3<.18: c=lerp(c,GLASS,.55)
                elif 0.5<fh<=0.6 and 0.3<wz<2.2: c=lerp(base,CREAM,.5)
                elif 0.6<fh<0.78 and 0.3<wz<2.2 and (fl+bi)%3==0: c=hx("#1d1a3a")   # fire-escape rail
                else:
                    row=int(h*3.2); off=.5 if row%2 else 0
                    j=hsh(row,int(z*1.1+off),bi)
                    c=lerp(base,(0,0,0),.1+.12*j) if j<.75 else lerp(base,(255,200,160),.14)
                    if (h*3.2)%1<.14 or ((z*1.1+off)%1)<.1: c=lerp(base,(0,0,0),.34)
                    if wz<.18 or wz>2.55: c=lerp(c,CREAM,.14)        # pilaster
            if y in (ytop,ytop+1): c=lerp(base,(255,225,170),.4)
            px[x,y]=fog(c,z)
        wb=ybot
    else: wb=None
    # ground (z<ZEND only)
    y0=max((wb+1) if wb is not None else 0,YG)
    for y in range(y0,H):
        if y<=VY: continue
        z=CAMH*F/(y-VY)
        if z>=ZEND: continue
        X=(x-VX)*z/F; ax=abs(X)
        if ax<3.0:
            c=hx("#3a3a52") if int(z*.8+X*.5)%7 else hx("#42425c")
            if ax<.08 or .17<ax<.25: c=hx("#f2c14e")
            elif 1.4<ax<1.5 and (z%4)<2: c=hx("#d8d0e0")
            if 3.4<z<5.0 and int((X+3)/.55)%2==0: c=hx("#e2dce8")
            if X<-.4 or ((X*1.1-z*.33)%4.0)<1.5: c=lerp(c,hx("#14143c"),.45)
            if abs(ax-3.0)<.1: c=hx("#d0d8f0")
        else:
            c=hx("#b4bce0") if (int(z/1.5)+int(ax*1.2))%2 else hx("#a4acd4")
            if abs(z%1.5)<.07: c=hx("#8a92c0")
            if X<0: c=lerp(c,hx("#2a2a70"),.3)
        px[x,y]=fog(c,z)
# ---- trees
G=[hx("#1f5a3a"),hx("#2f8a3a"),hx("#4fb83a"),hx("#8ee04a"),hx("#d0f470")]
def tree(side,z):
    s=F/z; X=side*3.75; sx=VX+X*s; gy=VY+CAMH*s; cy=VY+(CAMH-3.9)*s; rx=1.5*s; ry=1.35*s
    for y in range(int(cy+ry*.2),int(gy)):
        for x in range(int(sx-s*.1),int(sx+s*.1)+1): put(x,y,fog(hx("#4a2f44") if x>sx else hx("#352038"),z))
    rnd=random.Random(int(z*100)+side)
    for y in range(int(cy-ry),int(cy+ry)+1):                       # dark mass
        for x in range(int(sx-rx),int(sx+rx)+1):
            if ((x-sx)/rx)**2+((y-cy)/ry)**2<=.92: put(x,y,fog(G[1],z))
    pts=[]
    for _ in range(int(60+14*s/6)):
        a=rnd.uniform(0,6.283); d=rnd.random()**.6; pts.append((sx+d*rx*.9*__import__('math').cos(a),cy+d*ry*.88*__import__('math').sin(a)))
    for ox,oy in pts:
        t=(-(ox-sx)/rx*.55-(oy-cy)/ry*.85)             # light from top-left
        k=max(0,min(4,int((t+.95)*2.1))); r=max(1.2,s*rnd.uniform(.13,.2))
        disc(ox,oy,r,fog(G[max(1,k-1)],z))
        disc(ox-r*.25,oy-r*.35,r*.62,fog(G[k],z))
        if k>=3 and rnd.random()<.6: put(int(ox-r*.5),int(oy-r*.6),fog(G[4],z))
def lamp(side,z):
    s=F/z; sx=VX+side*3.15*s; gy=VY+CAMH*s; top=VY+(CAMH-5)*s
    for y in range(int(top),int(gy)): put(int(sx),y,hx("#2a2a48"))
    disc(sx,top,max(1,s*.12),hx("#ffe0a8"))
for z in (42,32,24,17,12,8.5,5.8,3.8):
    for side in (-1,1):
        if (int(z)+side)%2==0 or z>20: tree(side,z)
        if z in (32,17,8.5,5.8): lamp(-side,z*1.05)
def car(X,z,c):
    s=F/z; x0=int(VX+(X-.9)*s); x1=int(VX+(X+.9)*s); yb=int(VY+CAMH*s); y0=int(yb-1.4*s)
    for y in range(y0,yb):
        for x in range(x0,x1): put(x,y,fog(c if y>y0+.45*s else hx("#2a2858"),z))
car(1.5,30,hx("#d8434f")); car(-1.6,38,hx("#e8e0d0"))
PAL=["#1d1a3a","#1a1a50","#3b3170","#5a3f86","#8a4a90","#c05a86","#e8776e","#ffa06a","#ffc383","#f2a58e","#e58a98",
"#8a6aa0","#6a5a9a","#4a3f82","#f08a2a","#b05a30","#d83030","#8e2040","#4a6ad0","#2f4496","#e0d0b0","#a09080",
"#ffd36b","#2a2858","#5a5aa0","#1f5a3a","#2f8a3a","#4fb83a","#8ee04a","#d0f470","#3a3a52","#b4bce0","#f2c14e","#e2dce8","#4a2f44","#3fa7a3"]
pim=Image.new("P",(1,1)); flat=[]
for c in PAL: flat+=list(hx(c))
pim.putpalette(flat+[0]*(768-len(flat)))
out=im.quantize(64,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert("RGB")
rich=im.quantize(128,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert("RGB"); rich.save("street_day_rich_unused.png")
out.save("street_day_art_256.png"); out.resize((1024,1024),Image.NEAREST).save("street_day_x4.png")
print("colours:",len(out.getcolors(100000)))
ref=Image.open("../../style-guide/references/ref_city_street.webp").convert("RGB").resize((512,512))
cmp=Image.new("RGB",(1024,512)); cmp.paste(ref,(0,0)); cmp.paste(out.resize((512,512),Image.NEAREST),(512,0)); cmp.save("compare_day.png")
