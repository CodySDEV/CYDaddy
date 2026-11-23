import numpy as np
from make_case import *
T=build_top(brim=False); B=build_bottom(brim=False)
S=lambda b,s=0.06:(b[0]+s,b[1]-s,b[2]+s,b[3]-s,b[4]+s,b[5]-s)
comps={
 'plug body':(XP0+53.5,XP0+61,52.1,58.1,7.6,13.2),
 'CYD glass':(XP0+9,XP0+78,8.0,58.0,2,6),
 'CYD pcb':(XP0,XP1,YP0,YP1,6,7.6),
 'CYD chips':(XP0,XP1-0.01,YP0,YP1,7.6,10.8),
 'speaker body':(SPK[0]-9,SPK[0]+9,SPK[1]-9,SPK[1]+9,13.5,23.2),
 'battery':(33.4,98.8,8.5,44.5,13.8,23.5),
 'charger':(2.6,20.6,44.5,56.6,18.5,22.5),
 'boost':(40.5,77.8,46.2,63.5,15.7,23.2),
 'switch body':(SW_X-5.25,SW_X+5.25,SW_YT-5.0,SW_YT,SW_Z-2.95,SW_Z+2.95),
 'switch ears':(SW_X-9.85,SW_X+9.85,SW_YT-0.4,SW_YT,SW_Z-2.95,SW_Z+2.95),
 'boost strap mid':(45,75,53.5,63.5,BST_STRAP_Z-1.5,BST_STRAP_Z),
 'bat strap mid':(60,75,19,30,12.0,13.7),
 'usb plug':(108.6,118,24.5,38.2,5.5,12.5),
}
for n,b in comps.items():
    bb=S(b); pr=box(*bb)
    ov=T.inside_count(pr)+B.inside_count(pr)
    print(f'{n:12s} overlap nodes: {ov}')
for n,(px,py,dx,dy) in {'tab top':(11.6,59.2,0,-1),'tab end':(23.2,50.55,-1,0)}.items():
    z=CHG_ZPT
    if dx==0: bb=(px-3.7,px+3.7,py-5.6,py+3.7,z-1.5,z)
    else: bb=(px-5.6,px+3.7,py-3.7,py+3.7,z-1.5,z)
    print(n,'overlap',T.inside_count(box(*S(bb)))+B.inside_count(box(*S(bb))))
# stylus
sty=[cylx(YC,ZC,1.98,XD,XD+76.5)]
print('stylus overlap with shells:',sum(T.inside_count(p)+B.inside_count(p) for p in sty))
print('wall above tunnel:',round(W-(YC+2.2),2),'mm; below (to cavity top Y=64):',round(YC-2.2-64,2),'mm')
