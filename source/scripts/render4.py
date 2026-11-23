import rlib, math, numpy as np
O='/home/claude/final/pkg/images'
def save(img,name): img.save(f'{O}/{name}.png',optimize=True); print(name)
S=rlib.scene
W,H=1600,900
img,p=rlib.render(S(include=('bottom','comps_back','top','tabs','straps','sty')),0,1.5,W,H,dist=130,target=(88,70,-14),zoom=3.2)
save(img,'16_switch_closeup_top_edge')
img,p=rlib.render(S(include=('bottom','comps_back')),0,0.0,W,H,dist=130,target=(85,58,-18),zoom=3.4)
rlib.label(img,(90,640),'switch ears (M2 x 4 screws here)',p((83,66.6,17.5)),sz=28)
rlib.label(img,(900,640),'switch body + 5 mm nub',p((92,64,15)),sz=28)
save(img,'17_switch_closeup_inside')
v1=rlib.stylus(); v2=rlib.knob()
it=[(v1[0],v1[1],rlib.C['sty'],'s'),(v2[0]+np.array([-8,0,0]),v2[1],rlib.C['knob'],'k')]
img,p=rlib.render(it,0.25,0.45,W,H,dist=140,target=(36,67.6,-11.6),zoom=2.0)
rlib.label(img,(60,700),'knob (print standing)',p((-8-1.7,67.6,11.6)),sz=28)
rlib.label(img,(700,120),'stylus body (print lying flat)',p((60,67.6,11.6)),sz=28)
save(img,'18_stylus_body_and_knob')
