import rlib, numpy as np, math
from PIL import Image, ImageDraw
O='/home/claude/final/pkg/images'
def one(v,f,col,az,el,tg,dist,zoom,size=(800,560)):
    return rlib.render([(v,f,col,'x')],az,el,size[0],size[1],dist=dist,target=tg,zoom=zoom)[0]
tiles=[]
t=rlib.part('top'); tiles.append(('01  Front shell (top)  x1',one(*t,rlib.C['top'],0.3,0.5,(55.3,35.6,-6),220,1.0)))
b=rlib.part('bottom'); tiles.append(('02  Back shell (bottom)  x1',one(*b,rlib.C['bottom'],0.3,-0.5,(55.3,35.6,-18),220,1.0)))
v,f=rlib.strap('bar',(45,5.2),(93.5,49),6,13.7,1.7); tiles.append(('03  Battery strap  x1',one(v,f,rlib.C['strap'],0,0.7,(69,27,-13),120,1.0)))
v,f=rlib.strap('bstrap',(37.9,58.5),(80.4,58.5),10,16.55,1.5); tiles.append(('04  Booster strap  x1',one(v,f,rlib.C['strap'],0,0.7,(59,58.5,-16),100,1.0)))
v,f=rlib.part('tab'); tiles.append(('05  Charger tab  (print 4, use 2)',one(v,f,rlib.C['tab'],0.0,0.0,(3.7,4.65,-0.75),45,1.0)))
k=rlib.knob(); tiles.append(('06  Stylus knob  x1',one(*k,rlib.C['knob'],-0.6,0.5,(-1.7,67.6,-11.6),30,1.0)))
s=rlib.stylus(); tiles.append(('07  Stylus body  (3 sizes A/B/C)',one(*s,rlib.C['sty'],0.0,0.7,(37,67.6,-11.6),120,1.2)))
W,H=800,560
sheet=Image.new('RGB',(W*2,(H+50)*4),(246,246,242))
d=ImageDraw.Draw(sheet); fnt=rlib.font(30,True)
for i,(cap,im) in enumerate(tiles):
    x=(i%2)*W; y=(i//2)*(H+50)
    sheet.paste(im,(x,y+50)); d.text((x+20,y+8),cap,font=fnt,fill=(30,30,30))
sheet.save(O+'/19_printed_parts_overview.png',optimize=True)
