import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon, FancyArrowPatch
import numpy as np, sys
sys.path.insert(0,'/home/claude/scripts')
O='/home/claude/final/pkg/images/'
L,W,ZS,ZT=110.6,71.2,11.6,25.5
XP0=22.5; XP1=XP0+85.9; YP0=7.9; YP1=58.1
ink='#222'; blue='#1f5fa8'; red='#c0392b'; grey='#9a9a94'
def dim(ax,p0,p1,text,off=0,vert=False,fs=10,col=blue):
    p0=np.array(p0,float);p1=np.array(p1,float)
    if vert: p0[0]+=off;p1[0]+=off
    else: p0[1]+=off;p1[1]+=off
    ax.annotate('',xy=p0,xytext=p1,arrowprops=dict(arrowstyle='<->',color=col,lw=1.1,shrinkA=0,shrinkB=0))
    m=(p0+p1)/2
    ax.text(m[0]+(1.2 if vert else 0),m[1]+(0 if vert else 1.2),text,color=col,fontsize=fs,ha='left' if vert else 'center',va='center' if vert else 'bottom',rotation=90 if vert else 0,bbox=dict(fc='white',ec='none',pad=0.5))
def setup(ax,xl,yl,title):
    ax.set_xlim(*xl);ax.set_ylim(*yl);ax.set_aspect('equal');ax.axis('off');ax.set_title(title,fontsize=13,loc='left',color=ink,fontweight='bold')
# ---------- 1. enclosure dimensions (front + back views + end)
fig,axs=plt.subplots(2,1,figsize=(13,15))
ax=axs[0]; setup(ax,(-14,L+22),(-14,W+14),'Enclosure, front view (screen toward you, USB-C end on the RIGHT). All sizes in mm')
ax.add_patch(FancyBboxPatch((4,4),L-8,W-8,boxstyle='round,pad=4,rounding_size=4',fc='#e9ecf2',ec=ink,lw=2))
ax.add_patch(FancyBboxPatch((33.8+1,10.7+1),59-2,44.9-2,boxstyle='round,pad=1,rounding_size=1',fc='#222',ec=ink,lw=1.5))
ax.text((33.8+92.8)/2,6.2,'CYDaddy (engraved)',ha='center',fontsize=9,color=grey)
for cx,cy in ((4.4,4.4),(L-4.4,4.4),(4.4,61.6),(L-4.4,61.6)):
    ax.add_patch(Circle((cx,cy),1.8,fc='white',ec=red,lw=1.5)); ax.plot([cx-3,cx+3],[cy,cy],color=red,lw=0.6);ax.plot([cx,cx],[cy-3,cy+3],color=red,lw=0.6)
ax.plot([0,76.5],[67.6,67.6],ls='--',color='#c9631c',lw=2); ax.text(38,69.0,'stylus tunnel 4.4 mm, centre 3.6 mm below the top edge',ha='center',fontsize=9,color='#c9631c')
ax.add_patch(Rectangle((92-5.6,W-2),11.2,2,fc='#c0392b'))
ax.text(92,W+3,'switch + finger notch',ha='center',fontsize=9,color=red)
ax.add_patch(Rectangle((L-1,24.35),2,14,fc='#f4c542',ec=ink)); ax.text(L-5.2,31.3,'USB-C opening 14 x 7.2',fontsize=8.5,va='center',ha='center',rotation=90)
dim(ax,(0,-5),(L,-5),'110.6',0); dim(ax,(-6,0),(-6,W),'71.2',0,vert=True)
dim(ax,(33.8,-9.5),(92.8,-9.5),'window 59.0',0)
dim(ax,(L+8,10.7),(L+8,55.6),'window 44.9',0,vert=True)
dim(ax,(4.4,-1.5),(L-4.4,-1.5),'corner screws 101.8 apart',0,fs=9)
ax.text(2,W/2,'corner screw centres 4.4 mm\nfrom each edge (101.8 x 57.2)',fontsize=8,color=red,rotation=90,va='center')
ax=axs[1]; setup(ax,(-14,L+22),(-14,W+14),'Enclosure, back view (flipped left to right). BOOT/RESET slot, speaker grille, grip grooves')
ax.add_patch(FancyBboxPatch((4,4),L-8,W-8,boxstyle='round,pad=4,rounding_size=4',fc='#dfe6f1',ec=ink,lw=2))
# in back view x is mirrored: draw using X'=L-x
mx=lambda x:L-x
for cx,cy in ((4.4,4.4),(L-4.4,4.4),(4.4,61.6),(L-4.4,61.6)):
    ax.add_patch(Circle((cx,cy),1.8,fc='white',ec=red,lw=1.5));ax.add_patch(Circle((cx,cy),3.0,fc='none',ec=red,lw=0.8,ls=':'))
sx,sy=17.05,26.95
import itertools
pitch=3.4
for j in range(-4,5):
    for i in range(-4,5):
        px=sx+i*pitch+(pitch/2 if j%2 else 0); py=sy+j*pitch*0.866
        if np.hypot(px-sx,py-sy)<=10.2: ax.add_patch(Circle((mx(px),py),0.9,fc='#333',ec='none'))
ax.add_patch(Rectangle((mx(XP0+16.5),51.7),9,1.2,fc='#222')); ax.text(mx(XP0+12),56,'BOOT slot',fontsize=9,ha='center')
ax.text(mx(XP0+7.5)-1.5,53.8,'R',fontsize=11,fontweight='bold');ax.text(mx(XP0+16.5)+0.5,53.8,'B',fontsize=11,fontweight='bold')
for side in (0,1):
    for k in range(6):
        xc=9.5+2.4*k; xc=L-xc if side else xc
        segs=[(9,63)]
        dx=abs(xc-sx)
        if side==0 and dx<12.5:
            h=np.sqrt(12.5**2-dx**2); segs=[(9,sy-h),(sy+h,63)]
        for a,b in segs:
            if b-a>1: ax.add_patch(Rectangle((mx(xc)-0.6,a),1.2,b-a,fc='#9aa7bd',ec='none'))
ax.text(mx(60),12,'grip grooves at both ends,\nspeaker grille = hexagon of 3.4 mm pitch holes',fontsize=9,ha='center',color=grey)
dim(ax,(mx(sx)-10.2,sy-12.5),(mx(sx)+10.2,sy-12.5),'grille about 20 dia',0,fs=9)
ax.text(mx(60),7,'speaker centre 17.05 from the lanyard end, 26.95 from the bottom edge',fontsize=8.5,ha='center',color=grey)
fig.savefig(O+'20_drawing_enclosure_front_back.png',dpi=130,bbox_inches='tight',facecolor='white'); plt.close(fig)
# ---------- 2. side views (depth)
fig,axs=plt.subplots(2,1,figsize=(13,8))
ax=axs[0]; setup(ax,(-10,L+14),(-10,ZT+12),'Top edge view: how deep the two shells are (mm). Front shell at the bottom')
ax.add_patch(Rectangle((0,0),L,ZS,fc='#c9d0dd',ec=ink,lw=2)); ax.add_patch(Rectangle((0,ZS),L,ZT-ZS,fc='#aebbd3',ec=ink,lw=2))
ax.text(L/2,ZS/2,'FRONT shell (top) 11.6 deep',ha='center',va='center',fontsize=11); ax.text(L/2,ZS+(ZT-ZS)/2,'BACK shell (bottom) 13.9 deep',ha='center',va='center',fontsize=11)
ax.axhline(ZS,color=red,lw=1,ls='--'); ax.text(L-2,ZS+0.8,'split plane',color=red,fontsize=9,ha='right')
ax.add_patch(Rectangle((-3.5,ZS-1.9),3.5,3.8,fc='#c9631c',ec=ink)); ax.text(-4,ZS+4,'knob sticks out 3.5',fontsize=8,ha='right')
dim(ax,(L+8,0),(L+8,ZT),'25.5',0,vert=True)
dim(ax,(0,-5),(L,-5),'110.6',0)
ax.add_patch(Rectangle((92-5.25,ZT-23.5+0),0.01,0.01))
ax=axs[1]; setup(ax,(-6,W+12),(-10,ZT+12),'USB end view (mm)')
ax.add_patch(Rectangle((0,0),W,ZS,fc='#c9d0dd',ec=ink,lw=2)); ax.add_patch(Rectangle((0,ZS),W,ZT-ZS,fc='#aebbd3',ec=ink,lw=2))
ax.add_patch(Rectangle((24.35,5.4),14,7.2,fc='#f4c542',ec=ink)); ax.text(31.3,9,'USB-C',ha='center',va='center',fontsize=9)
dim(ax,(24.35,3),(38.35,3),'14',0,fs=9); dim(ax,(0,-5),(W,-5),'71.2',0)
ax.text(W/2,ZS+7,'USB-C opening is in the front shell: the CYD\'s own port',ha='center',fontsize=9,color=ink)
fig.savefig(O+'21_drawing_enclosure_depth.png',dpi=130,bbox_inches='tight',facecolor='white'); plt.close(fig)
# ---------- 3. CYD board
fig,ax=plt.subplots(figsize=(13,8.5)); setup(ax,(-12,112),(-14,66),'CYD board ESP32-2432S028 (measured with calipers). Screen side up, USB-C end on the RIGHT. Origin = bottom-left, mm')
ax.add_patch(Rectangle((0,0),85.9,50.2,fc='#2f7d4f',ec=ink,lw=2))
ax.add_patch(Rectangle((9,0.1),69,49.9,fc='#1d1d1d',ec='#555',lw=1)); ax.text(43.5,25,'display glass 69 x 50\n(sits 4 mm above the PCB)',ha='center',va='center',color='white',fontsize=10)
ax.add_patch(Rectangle((11.5,3),58.6,44.5,fc='#3a5a8a',ec='#aac',lw=1)); ax.text(40.8,12,'lit picture area 58.6 x 44.5',ha='center',color='white',fontsize=9)
for x,y in ((3.7,4.1),(82.2,4.1),(3.7,46.1),(82.2,46.1)):
    ax.add_patch(Circle((x,y),1.75,fc='white',ec=ink,lw=1.2))
ax.add_patch(Rectangle((85.9-1,18.9),2,9.1,fc='#c8c8c8',ec=ink)); ax.text(87.8,33,'USB-C (CYD\'s own,\non the back face)',fontsize=9,va='bottom')
ax.add_patch(Rectangle((39,-3),15,3,fc='#c8c8c8',ec=ink,hatch='//')); ax.text(46.5,-6,'microSD socket (bottom long edge), x 39 to 54',ha='center',fontsize=9)
ax.add_patch(Rectangle((53.5,44.2),7.5,6,fc='#e8e4d0',ec=ink,hatch='..')); ax.text(57.2,53,'SPEAK socket (back)\nx 53.5-61, top edge',ha='center',fontsize=9)
ax.add_patch(Rectangle((8,44.0),8,3,fc='#444',ec=ink)); ax.text(12,54,'BOOT + RST buttons (back)\ncentred x 12, 5.8 from the top edge',ha='center',fontsize=8.5,color='white')
dim(ax,(0,-9.5),(85.9,-9.5),'85.9',0); dim(ax,(-5,0),(-5,50.2),'50.2',0,vert=True)
dim(ax,(3.7,56),(82.2,56),'hole spacing 78.5',0,fs=9); dim(ax,(106,4.1),(106,46.1),'hole spacing 42.0',0,vert=True,fs=9)
ax.text(3.7,-1.8,'3.7',fontsize=8,ha='center',color=blue); ax.text(-1.5,4.1,'4.1',fontsize=8,color=blue,ha='right')
ax.text(0,62,'PCB 1.6 thick; total depth 11.2 mm (glass front to the tallest back part). Mounting holes about 3.5 mm.',fontsize=9)
fig.savefig(O+'22_drawing_cyd_board.png',dpi=130,bbox_inches='tight',facecolor='white'); plt.close(fig)
# ---------- 4. inside layout of the back shell
fig,ax=plt.subplots(figsize=(13,8.6)); setup(ax,(-10,L+18),(-14,W+16),'Back shell, looking into the open side (same orientation as the front view). Positions in mm from the lanyard end (x) and bottom edge (y)')
ax.add_patch(FancyBboxPatch((4,4),L-8,W-8,boxstyle='round,pad=4,rounding_size=4',fc='#e9ecf2',ec=ink,lw=2))
def part(x0,x1,y0,y1,col,name,tc='white'):
    ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc=col,ec=ink,lw=1.5,alpha=0.92)); ax.text((x0+x1)/2,(y0+y1)/2,name,ha='center',va='center',color=tc,fontsize=10,fontweight='bold')
part(33.4,98.8,8.5,44.5,'#c9a227','LiPo battery 65 x 36 x 9.7\n(pocket 65.8 x 36.8)','#222')
part(40.5,77.8,46.2,63.5,'#2d6fbf','MT3608 boost\n37.3 x 17.3 x 7.3')
part(2.6,20.6,44.5,56.6,'#8a4fbf','TP4056\n18 x 12.1')
part(3.55,30.55,13.45,40.45,'#555','Speaker 27 x 27 x 10')
part(92-5.25,92+5.25,61.8,66.8,'#c0c0c0','','#222'); ax.add_patch(Rectangle((92-9.8,66.4),19.6,0.4,fc='#888'))
ax.text(92,59.4,'SS12F15 slide switch\n(ears at y 66.6)',ha='center',fontsize=9)
for (px,py),lab in (((45,5.2),'M2.5'),((93.5,49),'M2.5')): ax.add_patch(Circle((px,py),1.05,fc='white',ec=red))
ax.plot([45,93.5],[5.2,49],color='#d4a13a',lw=7,alpha=0.8,solid_capstyle='round'); ax.text(60,13,'battery strap (M2.5 x 8 x2)',fontsize=9,rotation=42,color='#7a5a10')
ax.plot([37.9,80.4],[58.5,58.5],color='#d4a13a',lw=10,alpha=0.8,solid_capstyle='round'); ax.text(59,60.7,'boost strap (M2.5 x 8 x2)',fontsize=9,ha='center',color='#7a5a10')
for (px,py) in ((11.6,59.2),(23.2,50.55)): ax.add_patch(Circle((px,py),3.7,fc='#d4a13a',ec=ink,alpha=0.9))
ax.text(11.6,63,'charger tab\n(M2.5 x 8)',fontsize=8.5,ha='center',color='#7a5a10'); ax.text(27,47,'charger\ntab',fontsize=8.5,color='#7a5a10')
for cx,cy in ((4.4,4.4),(L-4.4,4.4),(4.4,61.6),(L-4.4,61.6)): ax.add_patch(Circle((cx,cy),1.8,fc='white',ec=red,lw=1.5))
ax.text(L/2,-3,'4 corner screws M3 (12 or 16 mm) through the back, into brass inserts in the front shell',ha='center',fontsize=9,color=red)
ax.add_patch(Rectangle((30,51.7),9,1.2,fc='#222')); ax.text(34.5,55,'BOOT/RST slot',fontsize=8,ha='center')
ax.add_patch(Rectangle((XP0+7.0,50.5),11,3.6,fc='none',ec='#222',ls=':'))
ax.add_patch(Rectangle((L-2,24.35),2,14,fc='#f4c542',ec=ink)); ax.text(L+1,31,'USB-C\nopening',fontsize=9,va='center')
dim(ax,(0,-9),(L,-9),'110.6',0); dim(ax,(L+10,0),(L+10,W),'71.2',0,vert=True)
fig.savefig(O+'23_drawing_back_shell_layout.png',dpi=130,bbox_inches='tight',facecolor='white'); plt.close(fig)
# ---------- 5. charger tab old vs new
fig,ax=plt.subplots(figsize=(11,5.2)); setup(ax,(-3,34),(-4,13),'Charger tab: old (snapped at the screw) vs new (stronger). Top view, mm')
def stad(x0,y0,w,l,rr,hole,col,lab):
    # old: rounded rect w x l
    pass
ax.add_patch(FancyBboxPatch((0.0,0),6.0,8.4,boxstyle='round,pad=0,rounding_size=1.5',fc='#e7c9c4',ec=red,lw=2)); ax.add_patch(Circle((3.0,2.8),1.35,fc='white',ec=ink))
ax.text(3,10.2,'OLD  6.0 x 8.4',ha='center',color=red,fontweight='bold'); ax.text(3,-1.8,'ring beside hole 1.65\nbehind hole 1.45',ha='center',fontsize=8.5)
x0=14
ax.add_patch(Circle((x0+3.7,3.7),3.7,fc='#cfe3c6',ec='#2c7a2c',lw=2)); ax.add_patch(Rectangle((x0,3.7),7.4,3.6,fc='#cfe3c6',ec='none'))
ax.add_patch(FancyBboxPatch((x0,5.3),7.4,4.0,boxstyle='round,pad=0,rounding_size=2.0',fc='#cfe3c6',ec='none'))
ax.plot([x0,x0],[3.7,7.3],color='#2c7a2c',lw=2);ax.plot([x0+7.4,x0+7.4],[3.7,7.3],color='#2c7a2c',lw=2)
ax.add_patch(Circle((x0+3.7,3.7),1.35,fc='white',ec=ink))
ax.text(x0+3.7,11.2,'NEW  7.4 x 9.3',ha='center',color='#2c7a2c',fontweight='bold'); ax.text(x0+3.7,-1.8,'ring beside hole 2.35\nround end 3.7 behind the hole',ha='center',fontsize=8.5)
ax.text(27,6,'Overhang past the hole is\nunchanged (5.6 mm), still 1.5 mm\nthick, same M2.5 x 8 screw.\nNot wider than 7.4 because the\ncorner screw post is 0.3 mm\nfrom the top tab.',fontsize=9,va='center')
fig.savefig(O+'24_drawing_charger_tab_old_vs_new.png',dpi=130,bbox_inches='tight',facecolor='white'); plt.close(fig)
print('ok')
