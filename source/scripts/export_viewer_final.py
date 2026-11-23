import numpy as np, os, json, math
from make_case import *
from skimage import measure
D='/home/claude/final/pkg/viewer'; os.makedirs(D,exist_ok=True)
CACHE={}
def arrays(F):
    v,fc,_,_=measure.marching_cubes(-F.f,0.0,spacing=(F.h,F.h,F.h),allow_degenerate=False)
    v=(v+np.array(F.o,np.float32)).astype(np.float32)
    tri=v[fc]; vol=np.sum(tri[:,0]*np.cross(tri[:,1],tri[:,2]))/6
    if vol<0: fc=fc[:,::-1]
    return v,fc.astype(np.uint32)
def save(name,v,fc):
    CACHE[name+'_v']=v; CACHE[name+'_f']=fc
    lo=v.min(0); hi=v.max(0); sc=(hi-lo); sc[sc==0]=1
    q=np.round((v-lo)/sc*65535).astype('<u2')
    with open(f'{D}/{name}.bin','wb') as f:
        f.write(q.tobytes())
        if q.nbytes%4: f.write(b'\0\0')
        f.write(fc.astype('<u4').tobytes())
    return dict(name=name,nv=len(v),nf=len(fc),lo=lo.tolist(),sc=sc.tolist())
meta=[]
meta.append(save('top',*arrays(build_top(h=0.35))))
meta.append(save('bottom',*arrays(build_bottom(h=0.35))))
meta.append(save('bar',*arrays(build_strap(STRAP_BAT,0.25))))
meta.append(save('bstrap',*arrays(build_strap(STRAP_BOOST,0.25))))
Ft=Field(-1,9,-1,10.5,-1,2.7,0.1)
Ft.add(cylz(3.7,3.7,3.7,0,1.5)); Ft.add(box(0,7.4,3.7,7.3,0,1.5)); Ft.add(rrect(0,7.4,5.3,9.3,2.0,0,1.5)); Ft.sub(cylz(3.7,3.7,1.35,-1,3))
meta.append(save('tab',*arrays(Ft)))
BR=(math.pi*3.5+1.2)/math.pi/2
meta.append(save('stylus',*arrays(build_stylus(BR=BR,rx0=9.0,ridge_r=2.08,flat_cut=0.15,knobless=True,h=0.12))))
meta.append(save('knob',*arrays(build_knob(0.08))))
json.dump(meta,open(f'{D}/parts.json','w'))
np.savez_compressed('/home/claude/final/meshes.npz',**CACHE)
for m in meta: print(m['name'],m['nv'],m['nf'])
print(sum(os.path.getsize(f'{D}/{f}') for f in os.listdir(D))/1e6,'MB')
print('SPK',SPK, 'SW',SW_X,SW_Z,SW_YT)
