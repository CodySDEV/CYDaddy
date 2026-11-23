import rlib, math, numpy as np
O='/home/claude/final/pkg/images'
def save(img,name): img.save(f'{O}/{name}.png',optimize=True); print(name)
S=rlib.scene
W,H=1800,1000
dz={'top':0,'cyd':0,'small':26,'backc':52,'bottom':96,'sty_x':-30}
tg=(50,38,-(25.5+96)/2)
img,p=rlib.render(S(dz=dz),-1.28,0.28,W,H,dist=470,target=tg,zoom=1.9)
P=lambda x,y,z:p((x,y,z))
rlib.label(img,(40,60),'Stylus + knob (slides out along the top edge)',P(-25,69,11.6))
rlib.label(img,(1180,880),'1  Front shell with the CYD screwed in',P(40,5,3))
rlib.label(img,(640,880),'2  Straps + charger tabs',P(70,28,13.7+26))
rlib.label(img,(1000,60),'3  Battery, boost, charger, speaker, switch',P(60,26,18+52))
rlib.label(img,(40,880),'4  Back shell (4 corner screws)',P(104,6,25.5+96))
save(img,'09_exploded_side')
img,p=rlib.render(S(dz=dz),-0.75,0.6,W,H,dist=460,target=tg,zoom=1.7)
save(img,'10_exploded_angled')
items=S(include=('bottom','comps_back','top'))
img,p=rlib.render(items,0.45,1.05,W,H,dist=95,target=(85,66,-16))
save(img,'16_switch_closeup_outside')
