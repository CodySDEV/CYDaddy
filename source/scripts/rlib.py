import numpy as np, math
from PIL import Image, ImageDraw, ImageFont
YC,ZC=67.6,11.6
M=np.load('/home/claude/final/meshes.npz')
def part(name): return M[name+'_v'].astype(np.float64), M[name+'_f'].astype(np.int64)
def boxmesh(x0,x1,y0,y1,z0,z1,step=2.5):
    V=[];F=[]
    def face(o,a,b_):
        o=np.array(o,float);a=np.array(a,float);b_=np.array(b_,float)
        na=max(1,int(math.ceil(np.linalg.norm(a)/step)));nb=max(1,int(math.ceil(np.linalg.norm(b_)/step)))
        base=len(V)
        for i in range(na+1):
            for j in range(nb+1):
                V.append(o+a*i/na+b_*j/nb)
        for i in range(na):
            for j in range(nb):
                p=base+i*(nb+1)+j; q=p+1; r=p+nb+1; s_=r+1
                F.append((p,r,s_));F.append((p,s_,q))
    dx,dy,dz=x1-x0,y1-y0,z1-z0
    face((x0,y0,z0),(dx,0,0),(0,dy,0)); face((x0,y0,z1),(dx,0,0),(0,dy,0))
    face((x0,y0,z0),(dx,0,0),(0,0,dz)); face((x0,y1,z0),(dx,0,0),(0,0,dz))
    face((x0,y0,z0),(0,dy,0),(0,0,dz)); face((x1,y0,z0),(0,dy,0),(0,0,dz))
    v=np.array(V);f=np.array(F);ctr=np.array([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2])
    for i,t in enumerate(f):
        n=np.cross(v[t[1]]-v[t[0]],v[t[2]]-v[t[0]])
        if np.dot(n,v[t[0]]-ctr)<0: f[i]=t[[0,2,1]]
    return v,f
def rotz(v,th,c0,pivot,zshift):
    pass
def strap(name,p0,p1,w,zr,t):
    v,f=part(name); th=math.atan2(p1[1]-p0[1],p1[0]-p0[0]); c,s=math.cos(th),math.sin(th)
    lx=v[:,0]-w/2; ly=v[:,1]-w/2
    return np.stack([p0[0]+lx*c-ly*s,p0[1]+lx*s+ly*c,zr-t+v[:,2]],1),f
def tab(px,py,dx,dy,zp):
    v,f=part('tab'); th=math.atan2(-dx,dy); c,s=math.cos(th),math.sin(th)
    lx=v[:,0]-3.7; ly=v[:,1]-3.7
    return np.stack([px+lx*c-ly*s,py+lx*s+ly*c,zp-1.5+v[:,2]],1),f
def stylus():
    v,f=part('stylus'); return np.stack([v[:,0],YC+v[:,1],ZC+v[:,2]],1),f
def knob():
    v,f=part('knob'); return np.stack([-v[:,2],YC+v[:,1],ZC+v[:,0]],1),f
C=dict(top=(150,160,178),bottom=(120,138,170),strap=(214,164,58),tab=(214,164,58),sty=(232,133,43),knob=(201,99,28),
  glass=(40,40,44),pcb=(47,125,79),boost=(45,111,191),chg=(138,79,191),bat=(201,162,39),spk=(85,85,85),sw=(192,192,192),usb=(184,184,184))
def scene(include=('top','bottom','straps','tabs','sty','comps_cyd','comps_back'),dz=None):
    """returns list of (v,f,color,group). design coordinates."""
    dz=dz or {}
    out=[]
    def add(v,f,col,g):
        v=v.copy(); v[:,2]+=dz.get(g,0); out.append((v,f,col,g))
    if 'top' in include: add(*part('top'),C['top'],'top')
    if 'bottom' in include: add(*part('bottom'),C['bottom'],'bottom')
    if 'straps' in include:
        add(*strap('bar',(45,5.2),(93.5,49),6,13.7,1.7),C['strap'],'small')
        add(*strap('bstrap',(37.9,58.5),(80.4,58.5),10,16.55,1.5),C['strap'],'small')
    if 'tabs' in include:
        add(*tab(11.6,59.2,0,-1,18.2),C['tab'],'small'); add(*tab(23.2,50.55,-1,0,18.2),C['tab'],'small')
    if 'sty' in include:
        v,f=stylus(); v=v.copy(); v[:,0]+=dz.get('sty_x',0); out.append((v,f,C['sty'],'sty'))
        v,f=knob(); v=v.copy(); v[:,0]+=dz.get('sty_x',0); out.append((v,f,C['knob'],'sty'))
    if 'comps_cyd' in include:
        add(*boxmesh(31.5,100.5,8,58,2,6),C['glass'],'cyd')
        add(*boxmesh(22.5,108.4,7.9,58.1,6,7.6),C['pcb'],'cyd')
        add(*boxmesh(108.4,110.0,23.5,33,6,9.6),C['usb'],'cyd')
    if 'comps_back' in include:
        add(*boxmesh(40.5,77.8,46.2,63.5,15.7,23.2),C['boost'],'backc')
        add(*boxmesh(2.6,20.6,44.5,56.6,18.5,22.5),C['chg'],'backc')
        add(*boxmesh(33.4,98.8,8.5,44.5,13.8,23.5),C['bat'],'backc')
        add(*boxmesh(3.55,30.55,13.45,40.45,13.5,23.5),C['spk'],'backc')
        add(*boxmesh(92-5.25,92+5.25,61.8,66.8,14.6,20.5),C['sw'],'backc')
        add(*boxmesh(92-9.8,92+9.8,66.4,66.8,14.6,20.5),C['sw'],'backc')
    return out
def render(items,az,el,W=1600,H=1000,dist=200,target=(55.3,35.6,-12.75),fov=35,ss=2,bg=(246,246,242),light=(-0.4,0.6,0.7),zoom=1.0):
    tg=np.array(target,float)
    cp=tg+dist*np.array([math.cos(el)*math.sin(az),math.sin(el),math.cos(el)*math.cos(az)])
    f_=(tg-cp); f_/=np.linalg.norm(f_)
    r_=np.cross(f_,[0,1,0]); r_/=np.linalg.norm(r_); u_=np.cross(r_,f_)
    Rm=np.stack([r_,u_,-f_])   # camera space: x right, y up, z toward viewer
    Ws,Hs=W*ss,H*ss
    fl=(Hs/2)/math.tan(math.radians(fov)/2)*zoom
    img=Image.new('RGB',(Ws,Hs),bg); dr=ImageDraw.Draw(img)
    L=np.array(light,float); L/=np.linalg.norm(L)
    P=[];D=[];COL=[]
    for v,f,col,g in items:
        w=np.stack([v[:,0],v[:,1],-v[:,2]],1)   # design -> three coords
        c=(w-cp)@Rm.T
        tri=c[f]
        n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        # three coords flipped z => winding flips; compensate by sign of handedness
        n=-n
        nn=np.linalg.norm(n,axis=1,keepdims=True); nn[nn==0]=1; n=n/nn
        ctr=tri.mean(1)
        vis=(n*(-ctr)).sum(1)>0
        # cull using view vector
        tri=tri[vis]; n=n[vis]; ctr=ctr[vis]
        z=-tri[:,:,2]
        ok=(z>1).all(1)
        tri=tri[ok]; n=n[ok]; ctr=ctr[ok]; z=z[ok]
        sx=Ws/2+fl*tri[:,:,0]/z; sy=Hs/2-fl*tri[:,:,1]/z
        lam=np.clip(n@L,0,1)
        sh=0.38+0.68*lam
        colr=np.clip(np.array(col,float)[None,:]*sh[:,None],0,255).astype(np.uint8)
        P.append(np.stack([sx,sy],2)); D.append(z.mean(1)); COL.append(colr)
    P=np.concatenate(P);D=np.concatenate(D);COL=np.concatenate(COL)
    order=np.argsort(-D)
    for i in order:
        p=P[i]
        dr.polygon([(p[0,0],p[0,1]),(p[1,0],p[1,1]),(p[2,0],p[2,1])],fill=tuple(int(x) for x in COL[i]))
    def proj(pt):
        w=np.array([pt[0],pt[1],-pt[2]],float); c=Rm@(w-cp); z=-c[2]
        return (Ws/2+fl*c[0]/z)/ss,(Hs/2-fl*c[1]/z)/ss
    return img.resize((W,H),Image.LANCZOS),proj

import glob,os
def font(sz,bold=False):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if bold else ''),'/usr/share/fonts/dejavu/DejaVuSans%s.ttf'%('-Bold' if bold else '')):
        if os.path.exists(p): return ImageFont.truetype(p,sz)
    return ImageFont.load_default()
def label(img,xy,text,anchor_pt,sz=26,col=(30,30,30)):
    d=ImageDraw.Draw(img); f=font(sz,True)
    tb=d.textbbox(xy,text,font=f)
    pad=6
    d.rectangle((tb[0]-pad,tb[1]-pad,tb[2]+pad,tb[3]+pad),fill=(255,255,255),outline=(60,60,60),width=2)
    d.text(xy,text,font=f,fill=col)
    cx=(tb[0]+tb[2])/2; cy=(tb[1]+tb[3])/2
    # leader from nearest box edge point to the anchor
    ex=min(max(anchor_pt[0],tb[0]-pad),tb[2]+pad); ey=min(max(anchor_pt[1],tb[1]-pad),tb[3]+pad)
    d.line((ex,ey,anchor_pt[0],anchor_pt[1]),fill=(60,60,60),width=3)
    d.ellipse((anchor_pt[0]-6,anchor_pt[1]-6,anchor_pt[0]+6,anchor_pt[1]+6),fill=(220,40,40),outline=(255,255,255))
