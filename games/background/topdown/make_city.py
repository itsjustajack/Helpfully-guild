"""Top-down (3/4 RPG view) New York style city. 16px tiles, 80x63 tiles = 1280x1008 art px. No cars/people yet."""
import random, math
from PIL import Image, ImageDraw
T=16; COLS,ROWS=80,63; W,H=COLS*T,ROWS*T
rnd=random.Random(4)
def hx(s): s=s.lstrip('#'); return tuple(int(s[i:i+2],16) for i in (0,2,4))
def lerp(a,b,t): return tuple(max(0,min(255,int(a[i]+(b[i]-a[i])*t))) for i in range(3))
def hsh(*a): return (hash(a)&0xffff)/65535.0
img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img); px=img.load()
def R(x0,y0,x1,y1,c): d.rectangle([x0,y0,x1-1,y1-1],fill=c)
def P(x,y,c):
    if 0<=x<W and 0<=y<H: px[x,y]=c
OUT=hx("#1d1a3a")
AVE=[(0,8),(36,44),(72,80)]; STR=[(0,6),(21,27),(42,48)]
BLK_C=[(8,36),(44,72)]; BLK_R=[(6,21),(27,42),(48,63)]
def ave_road(c): return any(a+2<=c<a+6 for a,b in AVE)
def str_road(r): return any(a+1<=r<a+5 for a,b in STR)
def in_street_row(r): return any(a<=r<b for a,b in STR)
def in_ave_col(c): return any(a<=c<b for a,b in AVE)
ASP=[hx("#3b3354"),hx("#413760")]; SW=[hx("#8a7eb0"),hx("#7f74a6")]; JOINT=hx("#625890"); CURB=hx("#b4a8d8"); ALLEY=[hx("#4a4264"),hx("#443c5e")]
# ---------------- ground
for r in range(ROWS):
    for c in range(COLS):
        x0,y0=c*T,r*T
        if ave_road(c) or str_road(r):
            for y in range(y0,y0+T):
                for x in range(x0,x0+T): P(x,y,ASP[int(hsh(x//3,y//3)*10)%2] if hsh(x,y)<.97 else lerp(ASP[0],(255,255,255),.08))
        elif in_ave_col(c) or in_street_row(r):
            col=SW[(c+r)%2]
            R(x0,y0,x0+T,y0+T,col); R(x0,y0,x0+T,y0+1,JOINT); R(x0,y0,x0+1,y0+T,JOINT)
        else:
            R(x0,y0,x0+T,y0+T,ALLEY[(c+r)%2])
# curbs
for r in range(ROWS):
    for c in range(COLS):
        if ave_road(c) or str_road(r): continue
        if not(in_ave_col(c) or in_street_row(r)): continue
        x0,y0=c*T,r*T
        if ave_road(c+1) and not str_road(r): R(x0+T-2,y0,x0+T,y0+T,CURB)
        if ave_road(c-1) and not str_road(r): R(x0,y0,x0+2,y0+T,CURB)
        if str_road(r+1) and not ave_road(c): R(x0,y0+T-2,x0+T,y0+T,CURB)
        if str_road(r-1) and not ave_road(c): R(x0,y0,x0+T,y0+2,CURB)
# lane markings
YEL=hx("#f2c14e"); WHT=hx("#e2dce8")
for a,b in AVE:
    for y in range(H):
        if str_road(y//T): continue
        cx=(a+4)*T
        for x in (cx-4,cx-3,cx+2,cx+3): P(x,y,YEL)
        if (y//10)%2==0:
            for x in ((a+3)*T-1,(a+5)*T): P(x,y,WHT)
for a,b in STR:
    for x in range(W):
        if ave_road(x//T): continue
        cy=(a+3)*T
        for y in (cy-4,cy-3,cy+2,cy+3): P(x,y,YEL)
        if (x//10)%2==0:
            for y in ((a+2)*T-1,(a+4)*T): P(x,y,WHT)
# crosswalks
for a,b in AVE:
    for sa,sb in STR:
        for (cx0) in ((a)*T,(a+6)*T):          # across the street road over avenue sidewalk columns
            for k in range(0,4*T,7): R(cx0,(sa+1)*T+k+1,cx0+2*T,(sa+1)*T+k+4,WHT)
        for (ry0) in (sa*T,(sa+5)*T):          # across the avenue road over street sidewalk rows
            for k in range(0,4*T,7): R((a+2)*T+k+1,ry0,(a+2)*T+k+4,ry0+T,WHT)
# manholes
for _ in range(14):
    x=rnd.randint(2,COLS-3)*T+8; y=rnd.randint(2,ROWS-3)*T+8
    if ave_road(x//T) and str_road(y//T) or (not(ave_road(x//T)) and not(str_road(y//T))): continue
    for dy in range(-4,5):
        for dx in range(-4,5):
            if dx*dx+dy*dy<=16: P(x+dx,y+dy,hx("#2a2440") if (dx+dy)%3 else hx("#4a4264"))
# ---------------- building shadows on the ground (light from top-left)
def darken(x0,y0,x1,y1,k):
    for y in range(max(0,y0),min(H,y1)):
        for x in range(max(0,x0),min(W,x1)): px[x,y]=lerp(px[x,y],hx("#14102a"),k)
KINDS=[("brick",hx("#a8404c"),hx("#7a2f4c")),("brown",hx("#8a5a4a"),hx("#5f3a3a")),("orange",hx("#d0782f"),hx("#a04d3a")),
       ("lime",hx("#c8b8a0"),hx("#8e8090")),("blue",hx("#5a6a9a"),hx("#3a4a78")),("dbrick",hx("#7a3040"),hx("#4a2040"))]
BUILD=[]
def plan_row(c0,c1,top_row):
    x=c0; out=[]
    while x<c1:
        w=rnd.choice((4,5,6,7,8))
        if c1-(x+w)<4: w=c1-x
        out.append((x,top_row,w,6,rnd.choice(KINDS))); x+=w
        if x<c1-4 and rnd.random()<.32: x+=rnd.choice((1,2))        # narrow alley between buildings
    return out
for c0,c1 in BLK_C:
    for r0,r1 in BLK_R:
        BUILD+=plan_row(c0,c1,r0); BUILD+=plan_row(c0,c1,r0+9)
def FL(bx,by):
    north=by in (6,27,48)
    return 2+int(hsh(bx,by,5)*(4 if north else 3))
NEON=[]
for bx,by,bw,bh,k in BUILD:
    n=FL(bx,by); yb=(by+bh)*T
    darken(bx*T+4,yb,(bx+bw)*T+10+n*3,yb+16+n*9,.40)          # taller = longer shadow
    darken((bx+bw)*T,yb-n*20-30,(bx+bw)*T+8+n*2,yb,.30)
    if hsh(bx,by,9)<.42:
        NEON.append((bx*T+bw*T-8,yb+4,rnd.choice((hx("#ff3fa8"),hx("#3fe0ff"),hx("#7aff6a")))))
def glow(cx,cy,col,r=26):
    for rr,k in ((r,.10),(int(r*.7),.12),(int(r*.4),.16)):
        for y in range(max(0,cy-rr),min(H,cy+rr)):
            for x in range(max(0,cx-rr),min(W,cx+rr)):
                if (x-cx)**2+(y-cy)**2<=rr*rr: px[x,y]=lerp(px[x,y],col,k)
for nx,ny,col in NEON: glow(nx,ny+6,col)
# ---------------- draw buildings
NAVY=hx("#2a2858"); LIT=hx("#ffd36b"); CREAM=hx("#e8d8c0"); BLK=hx("#1d1a3a")
def desat(c,t=.38): g=sum(c)//3; return lerp(lerp(c,(g,g,g),t),(0,0,0),.1)
def blend(x,y,col,k):
    if 0<=x<W and 0<=y<H: px[x,y]=lerp(px[x,y],col,k)
def building(bx,by,bw,bh,kind):
    name,lit,shd=kind; lit,shd=desat(lit),desat(shd)
    n=FL(bx,by); x0=bx*T; w=bw*T; yb=(by+bh)*T; fh=20*n+24; rf=28; y0=yb-fh-rf; fy=y0+rf
    r=random.Random(bx*131+by)
    # stepped rooftop tier on some tall buildings
    if n>=3 and r.random()<.35 and w>=64:
        tx0,tx1=x0+12,x0+w-12
        R(tx0,y0-16,tx1,y0+2,lerp(lit,(0,0,0),.25)); R(tx0,y0-16,tx1,y0-14,CREAM)
        for k in range((tx1-tx0)//16):
            R(tx0+5+k*16,y0-11,tx0+11+k*16,y0-4,LIT if r.random()<.3 else NAVY)
        R(tx0,y0-24,tx1,y0-16,hx("#4a4058")); R(tx0,y0-24,tx1,y0-22,hx("#7a6a8a")); d.rectangle([tx0,y0-24,tx1-1,y0-1],outline=OUT)
    # roof
    R(x0,y0,x0+w,y0+rf,hx("#4a4058"))
    for y in range(y0,y0+rf):
        for x in range(x0,x0+w):
            if hsh(x,y)<.12: P(x,y,hx("#5a5068"))
    R(x0,y0,x0+w,y0+2,hx("#7a6a8a")); R(x0,y0,x0+2,y0+rf,hx("#6a5a7a")); R(x0+w-2,y0,x0+w,y0+rf,hx("#3a3048")); R(x0,y0+rf-3,x0+w,y0+rf,hx("#2a2238"))
    for k in range(r.randint(1,3)):
        t=r.random(); cx=x0+6+int(r.random()*(w-26)); cy=y0+5+r.randint(0,9)
        if t<.35: R(cx,cy,cx+10,cy+8,hx("#8a8aa0")); R(cx+2,cy+2,cx+8,cy+6,hx("#5a5a78")); R(cx,cy+8,cx+10,cy+10,hx("#3a3048"))
        elif t<.6: R(cx,cy,cx+12,cy+8,hx("#7ab0d8")); R(cx,cy,cx+12,cy+1,hx("#c8e4f4")); R(cx,cy+8,cx+12,cy+10,hx("#3a3048"))
        elif t<.8: R(cx,cy,cx+14,cy+10,hx("#6a5a7a")); R(cx+5,cy+4,cx+9,cy+10,hx("#2a2238")); R(cx,cy+10,cx+14,cy+12,hx("#2a2238"))   # stair bulkhead
        else: R(cx,cy-6,cx+1,cy+8,hx("#2a2238")); R(cx-3,cy-3,cx+4,cy-2,hx("#2a2238"))                                                 # antenna
    # facade with weathered brick
    R(x0,fy,x0+w,fy+fh,lit)
    for y in range(fy,fy+fh):
        for x in range(x0,x0+w):
            row=(y-fy)//3; off=3 if row%2 else 0; j=hsh(row,(x-x0+off)//6,bx)
            c=lerp(lit,(0,0,0),.06+.12*j) if j<.78 else lerp(lit,(200,170,140),.14)
            if (y-fy)%3==0 or (x-x0+off)%6==0: c=lerp(lit,(0,0,0),.30)
            P(x,y,c)
    R(x0,fy,x0+w,fy+2,desat(CREAM)); R(x0,fy+2,x0+w,fy+4,shd)
    R(x0,fy,x0+3,fy+fh,lerp(lit,(255,225,190),.18)); R(x0+w-3,fy,x0+w,fy+fh,shd)
    cols=max(1,(w-8)//16); sx0=x0+(w-cols*16)//2+4
    for fl in range(n):
        wy=fy+6+20*fl
        for k in range(cols):
            wx=sx0+k*16
            R(wx-1,wy-1,wx+9,wy+15,desat(CREAM))
            on=hsh(bx,by,k,fl)<.38; broken=hsh(bx,by,k,fl,3)<.07
            R(wx,wy,wx+8,wy+14,LIT if on else NAVY)
            if on: R(wx,wy,wx+8,wy+4,hx("#ffe9a0")); R(wx+3,wy,wx+5,wy+14,hx("#c8963a"))
            else:
                R(wx+1,wy+8,wx+7,wy+13,hx("#3a3a78"))
                if broken: R(wx,wy,wx+8,wy+14,hx("#14102a")); R(wx,wy+4,wx+8,wy+10,hx("#6a4a30")); d.line([(wx,wy+4),(wx+8,wy+10)],fill=hx("#3a2418"))   # boarded
            R(wx-2,wy+15,wx+10,wy+17,desat(CREAM)); R(wx-2,wy+17,wx+10,wy+18,shd)
            for _ in range(2):                                     # grime drip under the sill
                dx=wx+r.randint(0,7); L=r.randint(4,14)
                for yy in range(wy+18,wy+18+L): blend(dx,yy,hx("#14102a"),.28)
    # ground floor
    gy=fy+fh-24
    if r.random()<.55:
        ac=r.choice(((hx("#a8404c"),hx("#d8c8b8")),(hx("#3a8a86"),hx("#c8d8d0")),(hx("#b8883a"),hx("#e0d0b0"))))
        for x in range(x0+4,x0+w-4): R(x,gy,x+1,gy+7,ac[0] if ((x-x0)//4)%2==0 else ac[1])
        R(x0+4,gy+7,x0+w-4,gy+9,hx("#14102a"))
        R(x0+6,gy+9,x0+w-6,fy+fh-1,lerp(hx("#5a5aa0"),LIT,.5) if r.random()<.6 else hx("#2a2858"))
        if r.random()<.5: R(x0+8,gy+12,x0+w-8,gy+14,hx("#14102a"))        # shutter bars
    else:
        dx=x0+w//2-5
        R(dx-2,gy+4,dx+12,fy+fh,desat(CREAM)); R(dx,gy+6,dx+10,fy+fh,hx("#4a2a30")); R(dx+1,gy+7,dx+9,gy+11,LIT); R(dx+8,gy+14,dx+9,gy+15,hx("#e8c868"))
        R(dx-4,fy+fh-3,dx+14,fy+fh,hx("#a8a0c0")); R(dx-6,fy+fh-1,dx+16,fy+fh,hx("#7a7298"))
    # neon sign on this building (matches glow list)
    for nx,ny,col in NEON:
        if nx==x0+w-8 and ny==yb+4:
            R(nx-1,gy-2,nx+4,gy+18,hx("#14102a")); R(nx,gy-1,nx+3,gy+17,col); R(nx+1,gy,nx+2,gy+16,lerp(col,(255,255,255),.7))
            R(x0+8,gy+2,x0+8+min(26,w//2),gy+4,col)
    # fire escape on every floor
    if name in("brick","brown","dbrick","orange") and r.random()<.6 and cols>=2:
        ex=sx0-4; ex2=sx0+cols*16-4
        for fl in range(n):
            py=fy+6+20*fl+17
            R(ex,py,ex2+2,py+2,BLK)
            for xx in range(ex,ex2+2,3): R(xx,py-5,xx+1,py,BLK)
            R(ex,py-5,ex2+2,py-4,BLK)
            if fl<n-1: d.line([(ex2-2,py+2),(ex+6,py+20)],fill=BLK,width=1); d.line([(ex2,py+2),(ex+8,py+20)],fill=BLK,width=1)
    # scaffolding with netting
    if r.random()<.2:
        for k in range(0,w,14): R(x0+k+2,fy+fh-22-20*min(2,n-1),x0+k+4,fy+fh,hx("#8a8a9a"))
        for fl in range(min(3,n)):
            sy=fy+fh-24-20*fl; R(x0,sy,x0+w,sy+3,hx("#a08a5a")); R(x0,sy+3,x0+w,sy+4,hx("#4a3a28"))
        for y in range(fy+fh-24-20*(min(3,n)-1),fy+fh):
            for x in range(x0,x0+w):
                if (x+y)%3==0: blend(x,y,hx("#2a4a3a"),.55)
    # water tower
    if hsh(bx,by,77)<.28 and w>=64:
        tx=x0+w//2-6+r.randint(-8,8); base=y0+18
        for lx in (tx,tx+11): R(lx,base-4,lx+2,base+2,hx("#2a2238"))
        R(tx-2,base-22,tx+16,base-3,hx("#8a5a3a"))
        for yy in (base-20,base-14,base-8): R(tx-2,yy,tx+16,yy+1,hx("#3a2430"))
        for xx in range(tx-2,tx+16,4): R(xx,base-22,xx+1,base-3,hx("#6a4228"))
        R(tx-2,base-22,tx+3,base-3,hx("#a8704a")); R(tx-3,base-26,tx+17,base-22,hx("#4a2e38")); R(tx+4,base-30,tx+10,base-26,hx("#4a2e38"))
    # grime: roof/cornice stains, mold near the ground, peeling flecks
    for _ in range(6):
        sx=x0+r.randint(4,w-6); L=r.randint(14,fh//2)
        for yy in range(fy+4,fy+4+L): blend(sx,yy,hx("#14102a"),.16); blend(sx+1,yy,hx("#14102a"),.10)
    for _ in range(6):
        mx=x0+r.randint(3,w-8); my=fy+fh-r.randint(30,60)
        for yy in range(my,my+r.randint(5,11)):
            for xx in range(mx,mx+r.randint(4,10)): 
                if hsh(xx,yy,bx)<.7: blend(xx,yy,hx("#3a5a48"),.5)
    for _ in range(16):
        fx=x0+r.randint(3,w-6); fy2=fy+r.randint(6,fh-8)
        R(fx,fy2,fx+2,fy2+1,lerp(lit,(230,210,180),.45)); R(fx+1,fy2+1,fx+3,fy2+2,lerp(lit,(0,0,0),.3))
    d.rectangle([x0,y0,x0+w-1,fy+fh-1],outline=OUT)
for b in sorted(BUILD,key=lambda b:b[1]+b[3]): building(*b)
# ---------------- props: trees, lamps, hydrants, alley clutter
def tree(cx,cy):
    for dy in range(-3,5):
        for dx in range(-9,10):
            if (dx/9)**2+(dy/4)**2<=1 and 0<=cx+dx<W and 0<=cy+dy+9<H: px[cx+dx,cy+dy+9]=lerp(px[cx+dx,cy+dy+9],(10,10,30),.35)
    R(cx-1,cy+2,cx+1,cy+9,hx("#4a2f44"))
    G=[hx("#1f5a3a"),hx("#2f8a3a"),hx("#4fb83a"),hx("#8ee04a"),hx("#d0f470")]
    lumps=[(cx+rnd.uniform(-1,1)*5,cy+rnd.uniform(-1,1)*4,rnd.uniform(3,5)) for _ in range(9)]
    for li,(lx,ly,r) in enumerate(sorted(lumps,key=lambda l:l[1]+l[0]*.5)):
        for y in range(int(ly-r)-1,int(ly+r)+2):
            for x in range(int(lx-r)-1,int(lx+r)+2):
                dx,dy=x-lx,y-ly
                if dx*dx+dy*dy>r*r: continue
                t=(-dx*.6-dy*.8)/r; k=0 if t<-.5 else 1 if t<0 else 2 if t<.45 else 3
                P(x,y,G[k])
    for _ in range(3): P(int(cx+rnd.uniform(-6,3)),int(cy+rnd.uniform(-6,0)),G[4])
def lamp(cx,cy):
    R(cx,cy,cx+2,cy+10,hx("#2a2a48")); R(cx-2,cy-3,cx+4,cy+1,hx("#ffe0a8")); R(cx-1,cy-2,cx+3,cy,hx("#fff4d0"))
def hydrant(cx,cy):
    R(cx,cy,cx+5,cy+7,hx("#d83030")); R(cx-1,cy+2,cx+6,cy+4,hx("#a02020")); R(cx+1,cy-2,cx+4,cy,hx("#d83030"))
for a,b in STR:                                                  # trees + lamps along street sidewalks
    for c in range(1,COLS-1):
        if ave_road(c) or in_ave_col(c): continue
        if c%8==3:
            tree(c*T+8,a*T+8); tree(c*T+8,(a+5)*T+8)
        if c%16==9: lamp(c*T+3,(a+1)*T-8) if False else lamp(c*T+3,(a)*T+3); lamp(c*T+11,(a+5)*T+3)
        if c%24==13: hydrant(c*T+2,a*T+5)
for a,b in AVE:                                                  # along avenue sidewalks
    for r in range(1,ROWS-1):
        if in_street_row(r) or str_road(r): continue
        if r%8==3 and not in_street_row(r-1) and not in_street_row(r+1):
            tree(a*T+24,r*T+8); tree((a+7)*T+8,r*T+8)
        if r%14==9: lamp(a*T+6,r*T); lamp((a+7)*T+6,r*T)
# alley clutter (E-W alleys through each block + gaps)
for c0,c1 in BLK_C:
    for r0,r1 in BLK_R:
        ay=(r0+6)*T
        for _ in range(7):
            x=rnd.randint(c0*T+10,c1*T-40); y=ay+22+rnd.randint(0,10); t=rnd.random()
            if t<.35:   # dumpster
                R(x,y,x+26,y+14,hx("#2f6a4a")); R(x,y,x+26,y+4,hx("#4f9a6a")); R(x,y+14,x+26,y+16,hx("#14102a")); d.rectangle([x,y,x+25,y+13],outline=OUT)
            elif t<.6:  # trash bags
                for k in range(3): 
                    for dy in range(-3,4):
                        for dx in range(-4,5):
                            if (dx/4)**2+(dy/3)**2<=1: P(x+k*7+dx,y+dy,hx("#1d1a2a") if dx+dy<2 else hx("#3a3a50"))
            elif t<.8:  # crates
                R(x,y,x+10,y+10,hx("#8a5a3a")); R(x,y,x+10,y+1,hx("#c08a5a")); R(x,y+5,x+10,y+6,hx("#4a2e1e")); d.rectangle([x,y,x+9,y+9],outline=OUT)
            else:       # puddle + grate
                for dy in range(-3,4):
                    for dx in range(-8,9):
                        if (dx/8)**2+(dy/3)**2<=1: P(x+dx,y+dy,hx("#3a4a78") if dx+dy<4 else hx("#5a6aa0"))
def steam(cx,cy):
    for dy in range(0,10):
        w=4+dy//3
        R(cx-w//2,cy+dy,cx+w//2+1,cy+dy+1,hx("#e8782a") if (dy//2)%2==0 else hx("#e8e0d0"))
    R(cx-4,cy+9,cx+5,cy+11,hx("#1d1a3a"))
    pr=random.Random(cx)
    for k in range(7):
        px0=cx+pr.randint(-3,3)+k//2; py0=cy-4-k*6; rr=4+k//2
        for yy in range(py0-rr,py0+rr+1):
            for xx in range(px0-rr,px0+rr+1):
                if (xx-px0)**2+(yy-py0)**2<=rr*rr: blend(xx,yy,hx("#d8d4e8") if (xx+yy)%2==0 or k<4 else hx("#a8a4c0"),.55-.04*k)
for a,b in STR:
    for t in (.28,.7):
        steam(int(W*t)//T*T+8,(a+3)*T-4)
for a,b in AVE:
    steam((a+4)*T+8,int(H*.45)//T*T)
# lamp light pools (warm flat rings) added after props
for a,b in STR:
    for c in range(1,COLS-1):
        if ave_road(c) or in_ave_col(c): continue
        if c%16==9: glow(c*T+3,a*T+12,hx("#ffb860"),22); glow(c*T+11,(a+5)*T+12,hx("#ffb860"),22)
# ---- moody grade: darker, cooler, desaturated; lights stay bright
try:
    import numpy as np
    A=np.asarray(img).astype("float32")/255
    bright=(A[...,0]>.86)&(A[...,1]>.62)
    neon=((A[...,0]>.9)&(A[...,2]>.5))|((A[...,2]>.9)&(A[...,1]>.8))
    keep=(bright|neon)[...,None]
    g=A.mean(axis=2,keepdims=True)
    G=(A*0.62+g*0.38)*np.array([0.78,0.76,0.95])
    A=np.where(keep,A,G)
    yy,xx=np.mgrid[0:A.shape[0],0:A.shape[1]]
    v=1-0.28*np.clip(((xx/A.shape[1]-.5)**2+(yy/A.shape[0]-.5)**2)*2.2,0,1)
    A=A*v[...,None]
    img=Image.fromarray((np.clip(A,0,1)*255).astype("uint8"))
except Exception as e: print("grade skipped",e)
img.save("city_topdown_art.png")
img.crop((0,0,640,480)).resize((1280,960),Image.NEAREST).save("city_topdown_crop_x2.png")
print(img.size,len(img.getcolors(10**6)),"colours,",len(BUILD),"buildings")
