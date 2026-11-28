"""Isometric city, true 2:1 (tile 64x32). STEP 2: ground + roads + one intersection, curbs with three-face shading (light upper-left).
Camera is close: canvas 1280x720 art px, world runs off-screen (no slab, no table edge)."""
import random, math, sys
from PIL import Image
TW,TH=64,32; W,H=1280,720; WORLD=40; CX=CY=20          # intersection centre tile corner
OX=W//2-(CX-CY)*(TW//2); OY=H//2-(CX+CY)*(TH//2)+40
def hx(s): s=s.lstrip('#'); return tuple(int(s[i:i+2],16) for i in (0,2,4))
def lerp(a,b,t): return tuple(max(0,min(255,int(a[i]+(b[i]-a[i])*t))) for i in range(3))
def hsh(*a): return (hash(a)&0xffff)/65535.0
def scr(gx,gy,gz=0): return int(round(OX+(gx-gy)*TW/2)), int(round(OY+(gx+gy)*TH/2-gz))
def inv(sx,sy,gz=0):
    a=(sx-OX)/(TW/2); b=(sy+gz-OY)/(TH/2); return (a+b)/2,(b-a)/2
# ---- palette (hue-shifted: shadows cool/purple, highlights warm)
SW_TOP=hx("#b8aed8"); SW_JOINT=hx("#9a90c0"); SW_ALT=hx("#aea4d0")
FACE_L=hx("#8478a8"); FACE_R=hx("#5a4e84"); EDGE_HI=hx("#e6dcf0")
ASP=[hx("#4a4468"),hx("#443e62"),hx("#524c70")]; GUTTER=hx("#3a3458")
YEL=hx("#f0c050"); WHT=hx("#e8e0f0"); MAN=[hx("#2e2848"),hx("#3e3860")]
LOT=hx("#7a7098"); LOT2=hx("#776d95")
SKY=[hx("#3b3170"),hx("#8a4a90"),hx("#e8776e"),hx("#ffc383")]
CURB_H=10
A0,A1=CY-2,CY+2      # corridor A (along gx): gy in [18,22)
B0,B1=CX-2,CX+2      # corridor B (along gy): gx in [18,22)
SIDE=2
def kind(i,j):       # i=gx tile, j=gy tile
    inA=A0<=j<A1; inB=B0<=i<B1
    if inA or inB: return "road"
    nearA=A0-SIDE<=j<A1+SIDE; nearB=B0-SIDE<=i<B1+SIDE
    if nearA or nearB: return "side"
    return "lot"
def height(i,j):
    if not(0<=i<WORLD and 0<=j<WORLD): return 0
    return 0 if kind(i,j)=="road" else CURB_H
img=Image.new("RGB",(W,H)); px=img.load()
for y in range(H):
    t=y/H; k=min(2,int(t*3)); 
    for x in range(W): px[x,y]=lerp(SKY[k],SKY[k+1],(t*3)%1)
def put(x,y,c):
    if 0<=x<W and 0<=y<H: px[x,y]=c
def road_color(gx,gy,x,y):
    c=ASP[int(hsh(x//2,y//2)*3)%3] if hsh(x,y)<.9 else lerp(ASP[0],(120,110,160),.18)
    inter=B0<=gx<B1 and A0<=gy<A1
    # gutter strip beside curbs (road side)
    for (lo,hi,axis) in ((A0,A1,"y"),(B0,B1,"x")):
        v=gy if axis=="y" else gx
        if lo<=v<hi and (v-lo<.14 or hi-v<.14): c=lerp(c,GUTTER,.6)
    if not inter:
        if A0<=gy<A1 and not(B0-SIDE<=gx<B1+SIDE):         # corridor A markings
            if abs(gy-CY+.07)<.03 or abs(gy-CY-.07)<.03: c=YEL
            elif (abs(gy-(CY-1))<.025 or abs(gy-(CY+1))<.025) and (gx*2)%1<.55: c=WHT
        if B0<=gx<B1 and not(A0-SIDE<=gy<A1+SIDE):         # corridor B markings
            if abs(gx-CX+.07)<.03 or abs(gx-CX-.07)<.03: c=YEL
            elif (abs(gx-(CX-1))<.025 or abs(gx-(CX+1))<.025) and (gy*2)%1<.55: c=WHT
    # crosswalks (bars parallel to travel, spaced across the road)
    if A0<=gy<A1:
        for g0 in (B0-SIDE+.35,B1+SIDE-1.65):
            if g0<=gx<g0+1.3 and ((gy-A0)*2.2)%1<.55: c=WHT
        for g0 in (B0-SIDE-.35,B1+SIDE+.05):               # stop lines
            if g0<=gx<g0+.14 and abs(gy-CY)>.2: c=WHT
    if B0<=gx<B1:
        for g0 in (A0-SIDE+.35,A1+SIDE-1.65):
            if g0<=gy<g0+1.3 and ((gx-B0)*2.2)%1<.55: c=WHT
        for g0 in (A0-SIDE-.35,A1+SIDE+.05):
            if g0<=gy<g0+.14 and abs(gx-CX)>.2: c=WHT
    for mx,my in ((CX-8.5,CY-.5),(CX+7.5,CY+.6),(CX-.5,CY+9.5)):   # manholes
        d2=(gx-mx)**2+(gy-my)**2
        if d2<.07: c=MAN[(int(gx*8)+int(gy*8))%2]
        elif d2<.09: c=lerp(c,(20,15,40),.5)
    return c
def side_color(gx,gy,x,y,i,j):
    c=SW_TOP if (i+j)%2 else SW_ALT
    if hsh(x//3,y//3)<.06: c=lerp(c,(255,235,200),.12)
    fx,fy=gx-int(gx),gy-int(gy)
    if fx<.035 or fy<.035: c=SW_JOINT
    if hsh(i,j,7)<.07 and abs(fx-fy)<.02: c=SW_JOINT                  # hairline crack
    # warm highlight along curb edge where road is lower
    if kind(i+1,j)=="road" and fx>.94: c=EDGE_HI
    if kind(i,j+1)=="road" and fy>.94: c=EDGE_HI
    return c
def lot_color(gx,gy,x,y,i,j):
    c=LOT if (i+j)%2 else LOT2
    if hsh(x//2,y//2)<.08: c=lerp(c,(30,20,60),.12)
    fx,fy=gx-int(gx),gy-int(gy)
    if fx<.03 or fy<.03: c=lerp(c,(30,20,60),.10)
    return c
def tile_top(i,j,z):
    k=kind(i,j); X0,Y0=scr(i,j,z)
    for y in range(Y0,Y0+TH+1):
        for x in range(X0-TW//2,X0+TW//2+1):
            gx,gy=inv(x+.5,y+.5,z)
            if not(i<=gx<i+1 and j<=gy<j+1): continue
            if k=="road": c=road_color(gx,gy,x,y)
            elif k=="side": c=side_color(gx,gy,x,y,i,j)
            else: c=lot_color(gx,gy,x,y,i,j)
            put(x,y,c)
def face_right(i,j,z):   # gx=i+1 plane: darkest. runs from right vertex down-left to bottom vertex
    px0,py0=scr(i+1,j+1,z)
    for k in range(TW//2):
        x=px0+k; yt=py0-k//2
        for v in range(z):
            c=FACE_R
            if v==0: c=EDGE_HI if hsh(i,j,k//8)>.0 else FACE_R
            elif v<2: c=lerp(FACE_R,SW_TOP,.25)
            elif hsh(x//3,v)<.1: c=lerp(FACE_R,(20,10,50),.25)
            put(x,yt+v,c)
def face_left(i,j,z):    # gy=j+1 plane: mid-tone. runs from left vertex down-right to bottom vertex
    px0,py0=scr(i,j+1,z)
    for k in range(TW//2):
        x=px0+k; yt=py0+k//2
        for v in range(z):
            c=FACE_L
            if v==0: c=EDGE_HI
            elif v<2: c=lerp(FACE_L,SW_TOP,.3)
            elif hsh(x//3,v)<.1: c=lerp(FACE_L,(20,10,50),.2)
            put(x,yt+v,c)
# ---- painter's order over visible tiles
tiles=[(i,j) for i in range(WORLD) for j in range(WORLD)]
tiles.sort(key=lambda t:(t[0]+t[1],t[0]))
for i,j in tiles:
    z=height(i,j)
    X0,Y0=scr(i,j,z)
    if X0+TW//2<0 or X0-TW//2>W or Y0>H or Y0+TH+CURB_H<0: continue
    tile_top(i,j,z)
    if z>0:
        if height(i+1,j)<z: face_right(i,j,z)
        if height(i,j+1)<z: face_left(i,j,z)
img.save("iso_ground_art.png")
# ---- automatic checks
ok=True
# 1) 2:1 diamond: width of a tile top at each row must grow by exactly 2 px per row
rows=[]
X0,Y0=scr(5,5,0)
for r in range(TH):
    xs=[x for x in range(X0-TW,X0+TW) if 5<=inv(x+.5,Y0+r+.5)[0]<6 and 5<=inv(x+.5,Y0+r+.5)[1]<6]
    rows.append(len(xs))
steps=[rows[k+1]-rows[k] for k in range(TH//2-1)]
# 2:1 means each edge moves 2 px across per 1 px down, so the full width grows by 4 per row
print("2:1 check (each edge steps 2 across per 1 down => width +4/row):", "PASS" if all(s==4 for s in steps) else "FAIL",steps[:6])
ok&=all(s==4 for s in steps)
# 2) three-face order: top brightest, left mid, right darkest
lum=lambda c:.3*c[0]+.59*c[1]+.11*c[2]
order=lum(SW_TOP)>lum(FACE_L)>lum(FACE_R)
print("three-face light order top>left>right:", "PASS" if order else "FAIL"); ok&=order
# 3) hue shift: shadow face more blue than the top
hs=FACE_R[2]-FACE_R[0]>SW_TOP[2]-SW_TOP[0]
print("shadow shifted cooler than top:", "PASS" if hs else "FAIL"); ok&=hs
print("size",img.size,"colours",len(img.getcolors(10**6)),"ALL PASS" if ok else "SOME FAILED")
