import rlib, math, numpy as np, os
from PIL import Image
O='/home/claude/final/pkg/images'
def save(img,name): img.save(f'{O}/{name}.png',optimize=True); print(name)
S=rlib.scene
W,H=1800,1000
# exploded
dz={'top':0,'cyd':0,'small':16,'backc':32,'bottom':58,'sty_x':-26}
items=S(dz=dz)
tg=(55.3,35.6,-(25.5+58)/2+2)
img,p=rlib.render(items,-1.1,0.32,W,H,dist=330,target=tg)
def P(x,y,z): return p((x,y,z))
rlib.label(img,(60,90),'1  Front shell + CYD board',P(50,66,5))
rlib.label(img,(60,200),'Stylus + knob',P(-12,68,11.6))
rlib.label(img,(60,860),'2  Straps and charger tabs',P(60,28,13.7+16))
rlib.label(img,(1180,90),'3  Battery, boost, charger, speaker, switch',P(60,26,18+32))
rlib.label(img,(1280,870),'4  Back shell',P(100,10,25.5+58))
save(img,'09_exploded_side')
# exploded from front-high angle
img,p=rlib.render(S(dz=dz),-0.62,0.55,W,H,dist=340,target=tg)
save(img,'10_exploded_angled')
# inside of back shell, looking straight in, no front shell
items=S(include=('bottom','straps','tabs','comps_back'))
img,p=rlib.render(items,0,0,W,H,dist=215,target=(55.3,35.6,-18))
save(img,'11_back_shell_inside_parts_in_place')
items=S(include=('bottom',))
img,p=rlib.render(items,0,0,W,H,dist=215,target=(55.3,35.6,-18))
save(img,'12_back_shell_inside_empty')
items=S(include=('bottom','comps_back'))
img,p=rlib.render(items,-0.35,0.55,W,H,dist=225,target=(55.3,35.6,-18))
save(img,'13_back_shell_inside_angled')
# front shell inside from the back
items=S(include=('top','comps_cyd'))
img,p=rlib.render(items,math.pi,0,W,H,dist=215,target=(55.3,35.6,-6))
save(img,'14_front_shell_inside_with_cyd')
items=S(include=('top',))
img,p=rlib.render(items,math.pi,0,W,H,dist=215,target=(55.3,35.6,-6))
save(img,'15_front_shell_inside_empty')
# switch close up from outside / inside
items=S(include=('bottom','comps_back','top'))
img,p=rlib.render(items,0.35,1.0,W,H,dist=75,target=(92,68,-16))
save(img,'16_switch_closeup_outside')
items=S(include=('bottom','comps_back'))
img,p=rlib.render(items,0.0,-0.9,W,H,dist=80,target=(92,60,-17))
save(img,'17_switch_closeup_inside')
# stylus parts lined up
v1=rlib.stylus(); v2=rlib.knob()
it=[(v1[0],v1[1],rlib.C['sty'],'s'),(v2[0]+np.array([-14,0,0]),v2[1],rlib.C['knob'],'k')]
img,p=rlib.render(it,0.4,0.5,W,H,dist=170,target=(32,67.6,-11.6))
save(img,'18_stylus_body_and_knob')
