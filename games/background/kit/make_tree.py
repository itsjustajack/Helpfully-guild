"""Kit piece 1: street tree, 80x100 art px, lumpy leaf clusters, 5-tone green, dark gaps, highlight pixels."""
import random, math
from PIL import Image
def hx(s): s=s.lstrip('#'); return tuple(int(s[i:i+2],16) for i in (0,2,4))+(255,)
G=[hx(c) for c in ("#12461f","#1f7a2e","#2fa832","#58cc3c","#92e84e","#d0f870")]
W,H=80,100
def build(seed=3):
    rnd=random.Random(seed); im=Image.new("RGBA",(W,H),(0,0,0,0)); px=im.load()
    # trunk + inner branches
    for y in range(58,99):
        w=3 if y<80 else 3+(y-80)//7
        for x in range(40-w//2-2,40+w//2+3):
            px[x,y]=hx("#6a4a50") if x<40 else hx("#3e2640")
    lumps=[]
    for _ in range(58):
        a=rnd.uniform(0,6.283); d=math.sqrt(rnd.random())
        lumps.append((40+d*34*math.cos(a),31+d*24*math.sin(a),rnd.uniform(5,9)))
    lumps.sort(key=lambda l:(l[1]*1.0+l[0]*0.5))
    mask=[[None]*W for _ in range(H)]
    for li,(cx,cy,r) in enumerate(lumps):
        for y in range(int(cy-r)-1,int(cy+r)+2):
            for x in range(int(cx-r)-1,int(cx+r)+2):
                if not(0<=x<W and 0<=y<H): continue
                dx,dy=x-cx,y-cy
                # slightly squashed round lump with ragged edge
                rr=r*(1+0.18*math.sin(math.atan2(dy,dx)*4+li))
                if dx*dx+dy*dy*1.1>rr*rr: continue
                t=(-dx*.6-dy*.8)/r*.9-((cy-31)/24)*.55+(0.25 if cy<24 else 0)
                k=0 if t<-.55 else 1 if t<-.1 else 2 if t<.35 else 3 if t<.75 else 4
                # 1px dither at tone borders
                for edge,kk in ((-.55,1),(-.1,2),(.35,3),(.75,4)):
                    pass
                mask[y][x]=(li,k)
    for y in range(H):
        for x in range(W):
            m=mask[y][x]
            if m: px[x,y]=G[m[1]]
    # dark gap line where a later (lit) lump overlaps an earlier one: outline lower-right of each lump
    for y in range(H-1):
        for x in range(W-1):
            m=mask[y][x]
            if m and (mask[y+1][x+1] is None or mask[y+1][x+1][0]!=m[0]) and mask[y+1][x+1] is not None and mask[y+1][x+1][0]<m[0]:
                px[x,y]=G[0]
    # highlight speckles on bright zones
    for y in range(H):
        for x in range(W):
            m=mask[y][x]
            if m and m[1]>=3 and rnd.random()<.07: px[x,y]=G[5]
            elif m and m[1]==2 and rnd.random()<.05: px[x,y]=G[3]
    # hard 1px dark underside of crown
    for x in range(W):
        for y in range(H-2,0,-1):
            if mask[y][x] and not mask[y+1][x] and y>50: px[x,y]=G[0]; break
    return im
t=build(); t.save("tree_ref_style_80x100.png")
ref=Image.open("../../style-guide/references/ref_city_street.webp").convert("RGB").crop((95,455,425,870)).resize((80,100),Image.NEAREST)
S=6; c=Image.new("RGB",(80*S*2+30,100*S),(60,70,110))
c.paste(ref.resize((80*S,100*S),Image.NEAREST),(0,0))
bg=Image.new("RGB",(80,100),(60,70,110)); bg.paste(t,(0,0),t)
c.paste(bg.resize((80*S,100*S),Image.NEAREST),(80*S+30,0)); c.save("tree_compare.png"); print("ok")
