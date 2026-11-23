import rlib, math, numpy as np, os, sys
from PIL import Image
O='/home/claude/final/pkg/images'; os.makedirs(O,exist_ok=True)
def save(img,name): img.save(f'{O}/{name}.png',optimize=True); print(name)
S=rlib.scene
CEN=(55.3,35.6,-12.75)
W,H=1600,1000
# 01 hero
save(rlib.render(S(),-0.55,0.30,W,H,dist=210)[0],'01_case_front_angled')
save(rlib.render(S(),0,0,W,H,dist=215)[0],'02_case_front')
save(rlib.render(S(),math.pi,0,W,H,dist=215)[0],'03_case_back')
save(rlib.render(S(),math.pi+0.6,0.3,W,H,dist=215)[0],'04_case_back_angled')
save(rlib.render(S(),0,1.35,W,H,dist=200)[0],'05_case_top_edge_switch_stylus')
save(rlib.render(S(),math.pi/2,0.12,W,H,dist=200)[0],'06_case_usb_end')
save(rlib.render(S(),-math.pi/2,0.12,W,H,dist=200)[0],'07_case_lanyard_end_stylus')
save(rlib.render(S(),0,-1.35,W,H,dist=200)[0],'08_case_bottom_edge_sd_slot')
