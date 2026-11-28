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
for bx,by,bw,bh,k in BUILD:
    darken((bx)*T+4,(by+bh)*T,(bx+bw)*T+10,(by+bh)*T+20,.38)
    darken((bx+bw)*T,by*T+10,(bx+bw)*T+10,(by+bh)*T,.3)
# ---------------- draw buildings
NAVY=hx("#2a2858"); LIT=hx("#ffd36b"); CREAM=hx("#e8d8c0"); BLK=hx("#1d1a3a")
def building(bx,by,bw,bh,kind):
    name,lit,shd=kind; x0,y0,w=bx*T,by*T,bw*T; rf=32; fh=bh*T-rf
    # roof
    R(x0,y0,x0+w,y0+rf,hx("#4a4058"))
    for y in range(y0,y0+rf):
        for x in range(x0,x0+w):
            if hsh(x,y)<.12: P(x,y,hx("#5a5068"))
    R(x0,y0,x0+w,y0+2,hx("#7a6a8a")); R(x0,y0,x0+2,y0+rf,hx("#6a5a7a")); R(x0+w-2,y0,x0+w,y0+rf,hx("#3a3048")); R(x0,y0+rf-3,x0+w,y0+rf,hx("#2a2238"))
    for k in range(rnd.randint(1,3)):                      # rooftop clutter
        t=rnd.random(); cx=x0+6+int(rnd.random()*(w-26)); cy=y0+6+rnd.randint(0,10)
        if t<.4: R(cx,cy,cx+10,cy+8,hx("#8a8aa0")); R(cx+2,cy+2,cx+8,cy+6,hx("#5a5a78")); R(cx,cy+8,cx+10,cy+10,hx("#3a3048"))
        elif t<.7: R(cx,cy,cx+12,cy+8,hx("#7ab0d8")); R(cx,cy,cx+12,cy+1,hx("#c8e4f4")); R(cx,cy+8,cx+12,cy+10,hx("#3a3048"))
        else: R(cx,cy,cx+6,cy+10,hx("#6a4a50")); R(cx+1,cy,cx+5,cy+2,hx("#2a2238"))
    # facade
    fy=y0+rf
    R(x0,fy,x0+w,fy+fh,lit)
    for y in range(fy,fy+fh):
        for x in range(x0,x0+w):
            row=(y-fy)//3; off=3 if row%2 else 0; j=hsh(row,(x-x0+off)//6,bx)
            c=lerp(lit,(0,0,0),.06+.1*j) if j<.75 else lerp(lit,(255,200,160),.12)
            if (y-fy)%3==0 or (x-x0+off)%6==0: c=lerp(lit,(0,0,0),.26)
            P(x,y,c)
    R(x0,fy,x0+w,fy+2,CREAM); R(x0,fy+2,x0+w,fy+4,shd)            # cornice
    R(x0,fy,x0+3,fy+fh,lerp(lit,(255,225,190),.25))               # left edge light
    R(x0+w-3,fy,x0+w,fy+fh,shd)                                    # right edge shade
    cols=max(1,(w-8)//16)
    sx0=x0+(w-cols*16)//2+4
    lit_chance=.4
    for fl,wy in enumerate((fy+8,fy+28)):
        for k in range(cols):
            wx=sx0+k*16
            R(wx-1,wy-1,wx+9,wy+17,CREAM)                          # frame
            on=hsh(bx,by,k,fl)<lit_chance
            R(wx,wy,wx+8,wy+16,LIT if on else NAVY)
            if on: R(wx,wy,wx+8,wy+4,hx("#ffe9a0")); R(wx+3,wy,wx+5,wy+16,hx("#c8963a"))
            else: R(wx+1,wy+9,wx+7,wy+15,hx("#3a3a78"))
            R(wx+3,wy,wx+4,wy+16,CREAM) if not on else None
            R(wx-2,wy+17,wx+10,wy+19,CREAM); R(wx-2,wy+19,wx+10,wy+20,shd)   # sill
    # ground floor: shop or door
    gy=fy+48
    if rnd.random()<.5:                                            # shop
        ac=rnd.choice(((hx("#d8434f"),hx("#f0d8c8")),(hx("#3fa7a3"),hx("#e0f0e8")),(hx("#e0a03f"),hx("#f8e8c0"))))
        for x in range(x0+4,x0+w-4):
            R(x,gy-2,x+1,gy+5,ac[0] if ((x-x0)//4)%2==0 else ac[1])
        R(x0+4,gy+5,x0+w-4,gy+7,hx("#14102a"))
        R(x0+6,gy+7,x0+w-6,gy+fh-48,hx("#3a2a58")) if fh>48 else None
        yy=gy+7
        R(x0+6,yy,x0+w-6,fy+fh-1,lerp(hx("#5a5aa0"),LIT,.5) if rnd.random()<.6 else hx("#2a2858"))
    else:                                                          # door + stoop
        dx=x0+w//2-5
        R(dx-2,gy+1,dx+12,fy+fh,CREAM); R(dx,gy+3,dx+10,fy+fh,hx("#4a2a30")); R(dx+1,gy+4,dx+9,gy+8,LIT); R(dx+8,gy+10,dx+9,gy+11,hx("#e8c868"))
        R(dx-4,fy+fh-3,dx+14,fy+fh,hx("#a8a0c0")); R(dx-6,fy+fh-1,dx+16,fy+fh,hx("#7a7298"))
    # fire escape
    if name in("brick","brown","dbrick","orange") and rnd.random()<.55 and cols>=2:
        ex=sx0-4; ex2=sx0+cols*16-4
        for py in (fy+26,fy+46):
            R(ex,py,ex2+2,py+2,BLK)
            for xx in range(ex,ex2+2,3): R(xx,py-5,xx+1,py,BLK)
            R(ex,py-5,ex2+2,py-4,BLK)
        d.line([(ex2-2,fy+28),(ex+6,fy+46)],fill=BLK,width=1); d.line([(ex2,fy+28),(ex+8,fy+46)],fill=BLK,width=1)
        R(ex2-2,fy+46,ex2+2,fy+fh-6,hx("#2a2440"))
    # water tower
    if hsh(bx,by,77)<.28 and w>=64:
        tx=x0+w//2-6+rnd.randint(-8,8); base=y0+18
        for lx in (tx,tx+11): R(lx,base-4,lx+2,base+2,hx("#2a2238"))
        R(tx-2,base-22,tx+16,base-3,hx("#8a5a3a"))
        for yy in (base-20,base-14,base-8): R(tx-2,yy,tx+16,yy+1,hx("#3a2430"))
        for xx in range(tx-2,tx+16,4): R(xx,base-22,xx+1,base-3,hx("#6a4228"))
        R(tx-2,base-22,tx+3,base-3,hx("#a8704a")); R(tx-3,base-26,tx+17,base-22,hx("#4a2e38")); R(tx+4,base-30,tx+10,base-26,hx("#4a2e38"))
        R(tx+16,base-18,tx+26,base+4,hx("#2a2238")) if False else None
    # outline
    d.rectangle([x0,y0,x0+w-1,fy+fh-1],outline=OUT)
for b in sorted(BUILD,key=lambda b:b[1]): building(*b)
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
img.save("city_topdown_art.png")
img.crop((0,0,640,480)).resize((1280,960),Image.NEAREST).save("city_topdown_crop_x2.png")
print(img.size,len(img.getcolors(10**6)),"colours,",len(BUILD),"buildings")
