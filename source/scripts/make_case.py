#!/usr/bin/env python3
"""Scrappies case v1: top shell, bottom shell, battery bar, stylus clips.
Frame: X along the long side (USB end at +X), Y up the front view (stylus on top, +Y),
Z from the front face (0) to the back face (ZT). Everything in mm.
"""
import numpy as np, sys, os
from skimage import measure

OUT = '/home/claude/out'
os.makedirs(OUT, exist_ok=True)

# ---------------- parameters ----------------
L, W, R = 110.6, 71.2, 4.0          # outer size, corner radius
WALL = 2.0
ZS, ZT = 11.6, 25.5                  # split plane, total depth
ZBI = ZT - 2.0                       # back wall inner face (23.5)
CX0, CX1, CY0, CY1 = 2.0, L - 2.0, 2.0, 64.0   # cavity
# CYD board
XP0, YP0, YP1 = 22.5, 7.9, 58.1
XP1 = XP0 + 85.9   # board slid to the USB wall (screen off-centre)
# stylus groove
YC, ZC = 67.6, ZS   # v6: groove lowered so a 1.4 mm skin closes the tunnel on top
XD = 0.0           # v6: stylus head sits at the lanyard end wall (open end)
XEND = XD + 76.5
CLIPX = (XD + 24.0, XD + 64.0)
BRIM = 6.0
BRIM_T = 0.4

class Field:
    def __init__(s, x0, x1, y0, y1, z0, z1, h):
        s.h = h
        s.x = np.arange(x0, x1 + h / 2, h, dtype=np.float32)
        s.y = np.arange(y0, y1 + h / 2, h, dtype=np.float32)
        s.z = np.arange(z0, z1 + h / 2, h, dtype=np.float32)
        s.o = (x0, y0, z0)
        s.f = np.full((len(s.x), len(s.y), len(s.z)), 5.0, np.float32)

    def _sl(s, bb, m=2):
        h = s.h
        out = []
        for a, (lo, hi) in enumerate(((bb[0], bb[1]), (bb[2], bb[3]), (bb[4], bb[5]))):
            n = s.f.shape[a]
            i0 = max(0, int(np.floor((lo - s.o[a]) / h)) - m)
            i1 = min(n, int(np.ceil((hi - s.o[a]) / h)) + m + 1)
            out.append(slice(i0, max(i0, i1)))
        return tuple(out)

    def _xyz(s, sl):
        return (s.x[sl[0]][:, None, None], s.y[sl[1]][None, :, None], s.z[sl[2]][None, None, :])

    def add(s, prim):
        bb, fn = prim
        sl = s._sl(bb)
        X, Y, Z = s._xyz(sl)
        s.f[sl] = np.minimum(s.f[sl], fn(X, Y, Z))

    def sub(s, prim):
        bb, fn = prim
        sl = s._sl(bb)
        X, Y, Z = s._xyz(sl)
        s.f[sl] = np.maximum(s.f[sl], -fn(X, Y, Z))

    def inside_count(s, prim):
        bb, fn = prim
        sl = s._sl(bb, 0)
        X, Y, Z = s._xyz(sl)
        d = fn(X, Y, Z)
        return int(np.count_nonzero((d < 0) & (s.f[sl] < 0)))

def box(x0, x1, y0, y1, z0, z1):
    bb = (x0, x1, y0, y1, z0, z1)
    def fn(X, Y, Z):
        return np.maximum(np.maximum(np.maximum(x0 - X, X - x1), np.maximum(y0 - Y, Y - y1)), np.maximum(z0 - Z, Z - z1))
    return bb, fn

def cylz(cx, cy, r, z0, z1):
    bb = (cx - r, cx + r, cy - r, cy + r, z0, z1)
    def fn(X, Y, Z):
        return np.maximum(np.hypot(X - cx, Y - cy) - r, np.maximum(z0 - Z, Z - z1))
    return bb, fn

def cylx(cy, cz, r, x0, x1):
    bb = (x0, x1, cy - r, cy + r, cz - r, cz + r)
    def fn(X, Y, Z):
        return np.maximum(np.hypot(Y - cy, Z - cz) - r, np.maximum(x0 - X, X - x1))
    return bb, fn

def cyly(cx, cz, r, y0, y1):
    bb = (cx - r, cx + r, y0, y1, cz - r, cz + r)
    def fn(X, Y, Z):
        return np.maximum(np.hypot(X - cx, Z - cz) - r, np.maximum(y0 - Y, Y - y1))
    return bb, fn

def rrect(x0, x1, y0, y1, r, z0, z1):
    bb = (x0, x1, y0, y1, z0, z1)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
    def fn(X, Y, Z):
        qx = np.abs(X - cx) - hx
        qy = np.abs(Y - cy) - hy
        d2 = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
        return np.maximum(d2, np.maximum(z0 - Z, Z - z1))
    return bb, fn

def frame(outer, inner):
    bb, fo = outer
    _, fi = inner
    return bb, (lambda X, Y, Z: np.maximum(fo(X, Y, Z), -fi(X, Y, Z)))

def annulus_gap(cx, cy, r0, r1, gap, z0, z1):
    """C ring in XY, opening toward +Y"""
    bb = (cx - r1, cx + r1, cy - r1, cy + r1, z0, z1)
    def fn(X, Y, Z):
        d = np.maximum(np.hypot(X - cx, Y - cy) - r1, r0 - np.hypot(X - cx, Y - cy))
        g = np.maximum(np.abs(X - cx) - gap / 2, cy - Y)   # slot region (y>cy)
        d = np.maximum(d, -g)
        return np.maximum(d, np.maximum(z0 - Z, Z - z1))
    return bb, fn


def text_prim(txt, cx, base_y, cap_h, depth, z0=-1.0, mirror=False):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    from matplotlib.path import Path
    tp = TextPath((0, 0), txt, size=10, prop=FontProperties(family='DejaVu Sans', weight='bold'))
    cap = TextPath((0, 0), 'H', size=10, prop=FontProperties(family='DejaVu Sans', weight='bold')).vertices[:, 1].max()
    k = cap_h / cap
    v = tp.vertices * k
    x0, x1 = v[:, 0].min(), v[:, 0].max()
    v[:, 0] += cx - (x0 + x1) / 2
    if mirror:
        v[:, 0] = 2 * cx - v[:, 0]
    v[:, 1] += base_y
    path = Path(v, tp.codes)
    polys = path.to_polygons(closed_only=True)
    segs = []
    for p in polys:
        a = p; b = np.roll(p, -1, axis=0)
        segs.append(np.stack([a, b], 1))
    segs = np.vstack(segs)
    bb = (v[:, 0].min() - 0.5, v[:, 0].max() + 0.5, v[:, 1].min() - 0.5, v[:, 1].max() + 0.5, z0, depth)
    def fn(X, Y, Z):
        xs = X[:, 0, 0]; ys = Y[0, :, 0]
        gx, gy = np.meshgrid(xs, ys, indexing='ij')
        P = np.stack([gx.ravel(), gy.ravel()], 1)
        inside = path.contains_points(P)
        A = segs[:, 0][None]; B = segs[:, 1][None]
        Pp = P[:, None, :]
        AB = B - A
        t = np.clip(np.sum((Pp - A) * AB, 2) / np.maximum(np.sum(AB * AB, 2), 1e-9), 0, 1)
        d = np.min(np.hypot(*(Pp - (A + t[..., None] * AB)).transpose(2, 0, 1)), axis=1)
        sd = np.where(inside, -d, d).reshape(gx.shape).astype(np.float32)
        return np.maximum(np.maximum(sd[:, :, None], Z - depth), z0 - Z)
    return bb, fn

GRIP_PITCH, GRIP_W, GRIP_D = 2.4, 1.2, 0.8

def grip_grooves(F):
    sx, sy = SPK
    for side in (0, 1):
        for k in range(6):
            xc = 9.5 + GRIP_PITCH * k
            if side:
                xc = L - xc
            segs = [(9.0, 63.0)]
            dx = abs(xc - sx)
            if side == 0 and dx < 12.5:
                h = np.sqrt(12.5 ** 2 - dx ** 2)
                segs = [(9.0, sy - h), (sy + h, 63.0)]
            for (ya, yb) in segs:
                if yb - ya > 1.0:
                    F.sub(box(xc - GRIP_W / 2, xc + GRIP_W / 2, ya, yb, ZT - GRIP_D, ZT + 1))

# ---------------- feature groups ----------------
CORNERS = [(CX0 + 2.4, CY0 + 2.4), (CX1 - 2.4, CY0 + 2.4), (CX0 + 2.4, CY1 - 2.4), (CX1 - 2.4, CY1 - 2.4)]

def stylus_cuts(F):
    """v6.1 DS-style stylus tunnel: closed channel along the top edge, open at the lanyard end wall.
    Stylus slides in tip first until its collar (3.5 mm sticks out, thumb handle) touches the end wall.
    A small ridge on the stylus clicks into a groove (detent) when seated; a narrow ring in front of the
    groove makes the click. Tunnel is closed at the tip end."""
    F.sub(cylx(YC, ZC, 2.2, XD - 1.0, XEND + 0.5))        # barrel tunnel, 4.4 mm
    F.sub(cylx(YC, ZC, 2.4, XD + 1.7, XD + 5.0))          # detent groove, 4.8 mm
    F.add(cylx(YC, ZC, 2.7, XD + 5.2, XD + 8.2))          # click ring, 4.1 mm bore
    F.sub(cylx(YC, ZC, 2.05, XD + 5.0, XD + 8.5))

def usb_recess_outer(F):
    # open channel from the CYD's USB-C port through the right wall for the cable plug, both shells
    F.sub(box(XP1 + 0.2, L + 2, 24.35, 38.35, 5.4, 12.6))

def brim_plate(F, z0, z1):
    F.add(rrect(-BRIM, L + BRIM, -BRIM, W + BRIM, R + BRIM, z0, z1))

def grid_for(z0, z1, h, brim):
    m = (BRIM + 1.5) if brim else 1.5
    return Field(-m, L + m, -m, W + m, z0, z1, h)

def build_top(h=0.3, brim=False):
    F = grid_for(-1.0, ZS + 1.0, h, brim)
    F.add(rrect(0, L, 0, W, R, 0, ZS))
    if brim:
        brim_plate(F, 0, BRIM_T)
    F.sub(box(CX0, CX1, CY0, CY1, 2.0, ZS + 2))
    # corner screw posts with heat-set insert pockets
    for (cx, cy) in CORNERS:
        F.add(cylz(cx, cy, 3.0, 2.0, ZS))
    for (cx, cy) in CORNERS:
        F.sub(cylz(cx, cy, 2.15, 5.0, ZS + 1))
    # CYD posts
    hx = (XP0 + 3.7, XP0 + 3.7 + 78.5)
    hy = (YP0 + 4.1, YP0 + 4.1 + 42.0)
    for x in hx:
        for y in hy:
            F.add(cylz(x, y, 3.0, 2.0, 6.0))
    for x in hx:
        for y in hy:
            F.sub(cylz(x, y, 1.35, 2.5, 6.5))
    # glass locating ribs (corner L's)
    gx0, gx1, gy0, gy1 = XP0 + 9 - 0.2, XP0 + 9 + 69 + 0.2, YP0 + 0.1 - 0.2, YP1 - 0.1 + 0.2
    t, arm = 1.2, 8.0
    for (cx, sx) in ((gx0, -1), (gx1, 1)):
        for (cy, sy) in ((gy0, -1), (gy1, 1)):
            xa = (cx, cx + sx * arm) if sx > 0 else (cx - arm, cx)
            ya = (cy - t, cy) if sy < 0 else (cy, cy + t)
            F.add(box(min(xa), max(xa), ya[0], ya[1], 2.0, 6.0))
            xb = (cx - t, cx) if sx < 0 else (cx, cx + t)
            yb = (cy, cy + sy * arm) if sy > 0 else (cy - arm, cy)
            F.add(box(xb[0], xb[1], min(yb), max(yb), 2.0, 6.0))
    # window (lit area 33.9-92.5 x 10.9-55.4, plus 0.2 slack)
    F.sub(rrect(XP0 + 11.5 - 0.2, XP0 + 70.1 + 0.2, YP0 + 3 - 0.2, YP0 + 47.5 + 0.2, 1.0, -1.0, 2.2))
    usb_recess_outer(F)
    # engraved name under the screen (paint it white)
    F.sub(text_prim('CYDaddy', XP0 + 40.7, 2.9, 5.6, 1.0, z0=-1.0))
    # lanyard: closed-off recess in the far end wall with a bar across it
    F.add(box(1.9, 11.0, 24.0, 42.0, 1.9, ZS))
    F.sub(box(-1, 9.0, 28.0, 38.0, 3.0, 10.8))
    F.add(box(2.6, 5.4, 27.9, 38.1, 5.5, 8.3))
    stylus_cuts(F)
    F.sub(box(-20, L + 20, -20, W + 20, ZS, ZS + 5))
    return F

SPK = (17.05, 26.95)
SPK_POST = 6.3   # v6.2: measured ear underside 6.3 mm from the sound face (owner caliper), body 10 mm thick, ears 1.7 thick
SPK_D = 12.0     # v6.5: was 11.8 (centres 33.4 apart, too tight); now about 33.9 apart, +0.5 mm
SW_X, SW_Z, SW_YT = 92.0, 17.55, 66.8   # v6.2 switch centre X, Z, and the face the ears press against
BAT = dict(x0=33.2, x1=99.0, y0=8.1, y1=44.9)
CHG = dict(x0=2.6, x1=20.6, y0=44.5, y1=56.6, thk=4.0, st=1.0)
BST = dict(x0=40.5, x1=77.8, y0=46.2, y1=63.5, thk=7.5, st=0.3)
STRAP_BOOST = dict(p0=(37.9, 58.5), p1=(80.4, 58.5), w=10.0, t=1.5)
STRAP_BAT = dict(p0=(45.0, 5.2), p1=(93.5, 49.0), w=6.0, t=1.7)
BST_STRAP_Z = ZBI - BST['st'] - BST['thk'] - 0.15 + 1.0   # rear face of boost strap (v6: posts 1 mm shorter)
BAT_STRAP_Z = 13.7                                 # rear face of battery strap

CHG_ZPT = ZBI - CHG['st'] - CHG['thk'] - 0.3
BST_ZPT = ZBI - BST['st'] - BST['thk'] - 0.3
# post centres; tab direction: charger tabs reach +Y over the lower long edge, boost tabs reach +X (left) / -X (right)
TAB_POSTS = [(11.6, 59.2), (23.2, 50.55)]   # v6: one on the top long edge, one on the end opposite the USB-C end
TAB_Z = {(11.6, 59.2): CHG_ZPT, (23.2, 50.55): CHG_ZPT}

def corner_blocks(F, b, zlo, g=0.15, t=1.2, arm=6.0):
    x0, x1, y0, y1 = b['x0'], b['x1'], b['y0'], b['y1']
    for (cx, sx) in ((x0, -1), (x1, 1)):
        for (cy, sy) in ((y0, -1), (y1, 1)):
            ex = cx + sx * g
            ey = cy + sy * g
            # arm along X
            xa = sorted((ex + sx * t, cx - sx * arm))
            ya = sorted((ey, ey + sy * t))
            F.add(box(xa[0], xa[1], ya[0], ya[1], zlo, ZBI))
            xb = sorted((ex, ex + sx * t))
            yb = sorted((ey + sy * t, cy - sy * arm))
            F.add(box(xb[0], xb[1], yb[0], yb[1], zlo, ZBI))

def build_bottom(h=0.4, brim=False):
    F = grid_for(ZS - 1.0, ZT + 1.0, h, brim)
    F.add(rrect(0, L, 0, W, R, ZS, ZT))
    if brim:
        brim_plate(F, ZT - BRIM_T, ZT)
    F.sub(box(CX0, CX1, CY0, CY1, ZS - 1.0, ZBI))
    # corner posts, through holes, counterbores
    for (cx, cy) in CORNERS:
        F.add(cylz(cx, cy, 3.6, ZS, ZBI))
    for (cx, cy) in CORNERS:
        F.sub(cylz(cx, cy, 1.7, ZS - 1, ZT + 1))
        F.sub(cylz(cx, cy, 3.0, ZT - 3.2, ZT + 1))
    # speaker standoffs (flange sits on them), pilots for M2.5, rear grille
    sx, sy = SPK
    for (dx, dy) in ((-SPK_D, -SPK_D), (SPK_D, SPK_D)):   # only two ears, opposite corners
        F.add(cylz(sx + dx, sy + dy, 2.0, ZBI - SPK_POST, ZBI))
        F.sub(cylz(sx + dx, sy + dy, 1.05, ZBI - SPK_POST - 0.5, ZBI + 0.8))
    pitch = 3.4
    for j in range(-4, 5):
        for i in range(-4, 5):
            px = sx + i * pitch + (pitch / 2 if j % 2 else 0)
            py = sy + j * pitch * 0.866
            if np.hypot(px - sx, py - sy) <= 10.2:
                F.sub(cylz(px, py, 1.0, ZBI - 0.5, ZT + 1))
    # battery pocket rim with wire notch
    F.add(frame(box(BAT['x0'] - 1.2, BAT['x1'] + 1.2, BAT['y0'] - 1.2, BAT['y1'] + 1.2, 16.5, ZBI),
                box(BAT['x0'], BAT['x1'], BAT['y0'], BAT['y1'], 16.0, ZBI + 1)))
    F.sub(box(BAT['x0'] - 1.5, BAT['x0'] + 0.1, BAT['y1'] - 8, BAT['y1'], 16.0, ZBI))
    # battery strap posts (strap runs diagonally)
    for (px, py) in (STRAP_BAT['p0'], STRAP_BAT['p1']):
        F.add(cylz(px, py, 2.6, BAT_STRAP_Z, ZBI))
    for (px, py) in (STRAP_BAT['p0'], STRAP_BAT['p1']):
        F.sub(cylz(px, py, 1.05, BAT_STRAP_Z - 0.5, 21.5))
    # boost strap posts
    for (px, py) in (STRAP_BOOST['p0'], STRAP_BOOST['p1']):
        F.add(cylz(px, py, 2.3, BST_STRAP_Z, ZBI))
    for (px, py) in (STRAP_BOOST['p0'], STRAP_BOOST['p1']):
        F.sub(cylz(px, py, 1.05, BST_STRAP_Z - 0.5, 21.5))
    # charger and boost pockets
    for b in (CHG, BST):
        zb = ZBI - b['st'] - b['thk']
        corner_blocks(F, b, zb + 1.5)
        for fx in (0.25, 0.75):
            F.add(cylz(b['x0'] + fx * (b['x1'] - b['x0']), b['y0'] + 2.0, 1.2, ZBI - b['st'], ZBI))
            F.add(cylz(b['x0'] + fx * (b['x1'] - b['x0']), b['y1'] - 2.0, 1.2, ZBI - b['st'], ZBI))
    # retaining tabs: posts (M2.5 pilots) beside each board, tab overlaps the board edge by 3 mm
    for (px, py) in TAB_POSTS:
        zpt = TAB_Z[(px, py)]
        F.add(cylz(px, py, 2.2, zpt, ZBI))
        F.sub(cylz(px, py, 1.05, zpt - 0.5, zpt + 5.0))
    # BOOT / RST pin guide and slot
    # v6: guide shortened to about half (starts 5.5 mm behind the split plane) so it never touches the buttons
    F.add(box(XP0 + 6.5, XP0 + 17.5, 50.5, 54.1, ZS + 5.5, ZBI))
    F.sub(box(XP0 + 7.5, XP0 + 16.5, 51.7, 52.9, ZS + 5.5 - 1, ZT + 1))
    # v6: engraved B (boot, viewer's left from the back) and R (reset, viewer's right); text mirrored because it is read from the back
    F.sub(text_prim('R', XP0 + 5.0, 50.3, 4.0, ZT + 1.0, z0=ZT - 0.6, mirror=True))
    F.sub(text_prim('B', XP0 + 19.0, 50.3, 4.0, ZT + 1.0, z0=ZT - 0.6, mirror=True))
    # v6.2: slide switch SS12F15 (5 mm nub) moved to the top edge, USB end. Ears (0.4 thick, on top of the body)
    # press up against the ceiling of a recess; two pegs through the 2.5 mm ear holes; nub comes out through a slot.
    F.sub(box(SW_X - 10.2, SW_X + 10.2, SW_YT - 5.0 - 3.0, SW_YT, SW_Z - 3.2, SW_Z + 3.2))
    F.sub(box(SW_X - 4.9, SW_X + 4.9, SW_YT - 1, W + 1, SW_Z - 1.9, SW_Z + 1.9))
    # v6.5: the bare pegs held nothing. Now two screw pilots (1.8 mm, for M2 x 4) go up into the wall through the ear holes.
    # Wall above the recess ceiling is 4.4 mm; pilot 3.6 deep leaves 0.8 mm skin, so use M2 x 4 (ear 0.5 + 3.5 thread).
    for ex in (-7.65, 7.65):
        F.sub(cyly(SW_X + ex, SW_Z, 0.9, SW_YT - 0.5, SW_YT + 3.6))
    # v6.5b: the nub (5 mm above the ear plane) was only 0.6 mm proud of the outside, too little to push.
    # A finger notch around the nub lowers the wall there to Y 69.2 so the nub stands about 2.6 mm proud.
    # Notch is 11.2 mm wide (kept clear of the screw pilots at +/-7.65) and 7 mm deep in Z.
    F.sub(box(SW_X - 5.6, SW_X + 5.6, SW_YT + 2.4, W + 1, SW_Z - 3.5, SW_Z + 3.5))
    usb_recess_outer(F)
    grip_grooves(F)
    stylus_cuts(F)
    F.sub(box(-20, L + 20, -20, W + 20, ZS - 5, ZS))
    return F

def build_strap(S, h=0.2):
    d = float(np.hypot(S['p1'][0] - S['p0'][0], S['p1'][1] - S['p0'][1]))
    w, t = S['w'], S['t']
    F = Field(-1, d + w + 1, -1, w + 1, -1, t + 1, h)
    F.add(rrect(0, d + w, 0, w, min(3.0, w / 2 - 0.1), 0, t))
    F.sub(cylz(w / 2, w / 2, 1.35, -1, t + 1))
    F.sub(cylz(w / 2 + d, w / 2, 1.35, -1, t + 1))
    return F

def build_bar(h=0.2):
    return build_strap(STRAP_BAT, h)

def build_bstrap(h=0.2):
    return build_strap(STRAP_BOOST, h)

def build_clips(h=0.2):
    F = Field(-5, 17, -5, 5, -1, 5.8, h)
    for cx in (0.0, 11.0):
        F.add(annulus_gap(cx, 0.0, 2.2, 3.3, 3.3, 0, 4.98))
    return F

def build_stylus(ridge_r=2.15, h=0.1, flat=True, BR=1.975, rx0=2.0, flat_cut=0.125, knobless=False):
    """DS-style printable stylus. Axis along X from -3.5 (collar end) to 76.5 (tip), centred on Y=Z=0.
    Collar 6.4 mm sticks out of the case 3.5 mm; barrel 3.95 mm; ridge at x 2..4.5 clicks into the detent groove;
    taper from x 55 to a rounded tip of radius 0.9 mm. A small flat on the bottom (z=-1.85) helps it stick to the bed."""
    FLATZ = BR - flat_cut
    def prof(x):
        r = np.zeros_like(x)
        # collar
        c = (x >= -3.5) & (x < 0)
        if knobless:   # v6.3: no collar; neck and flange lock into a separate round knob
            r = np.where((x >= -2.4) & (x < -1.2), 1.7, r)
            r = np.where((x >= -1.2) & (x < 0), 1.0, r)
            c = np.zeros_like(c)
        rc = np.full_like(x, 3.2)
        rc = np.where(x < -3.0, 2.7 + (x + 3.5) * 1.0, rc)                       # chamfer at the outer end
        rc = np.where(((x > -2.7) & (x < -2.2)) | ((x > -1.7) & (x < -1.2)), 2.8, rc)  # two grip grooves
        r = np.where(c, rc, r)
        # barrel
        b = (x >= 0) & (x < 55)
        rb = np.full_like(x, BR)
        bump = (x > rx0) & (x < rx0 + 2.5)
        rb = np.where(bump, BR + (ridge_r - BR) * np.sin(np.pi * (x - rx0) / 2.5), rb)
        r = np.where(b, rb, r)
        # taper and rounded tip
        t = (x >= 55) & (x < 75.6)
        r = np.where(t, BR + (0.9 - BR) * (x - 55) / 20.6, r)
        tip = (x >= 75.6) & (x <= 76.5)
        r = np.where(tip, np.sqrt(np.maximum(0.9 ** 2 - (x - 75.6) ** 2, 0)), r)
        return r
    F = Field(-4.5, 77.5, -3.8, 3.8, -3.8, 3.8, h)
    def fn(X, Y, Z):
        Xb = np.broadcast_to(X, (X.shape[0], Y.shape[1], Y.shape[2])).copy()
        pr = prof(Xb)
        # v6.2: where the taper gets thinner than the flat (r < 1.85) the centre line drops so the underside stays on the bed
        zc = np.where(Xb > 50, np.minimum(0.0, pr - FLATZ), 0.0) if (flat and knobless) else (np.minimum(0.0, pr - FLATZ) if flat else 0.0)
        if knobless:   # v6.6: on a fatter barrel the 1.7 mm flange floated above the flat bed; drop its centre so it touches
            zc = np.where(Xb < -1.2, np.minimum(0.0, 1.7 - FLATZ), zc)
        rr = np.hypot(Y, Z - zc)
        d = rr - pr
        d = np.maximum(d, np.maximum((-2.4 if knobless else -3.5) - Xb, Xb - 76.5))
        if flat:
            d = np.maximum(d, -FLATZ - Z)
        return d.astype(np.float32)
    F.add(((-4.5, 77.5, -3.8, 3.8, -3.8, 3.8), fn))
    return F

def build_stylus_test(h=0.1):
    """three short test pieces (ridge 4.2, 4.3, 4.4 mm) with the real collar, to find the best click fit"""
    F = Field(-4.5, 17.5, -3.8, 31.0, -3.8, 3.8, h)
    for i, rr in enumerate((2.10, 2.15, 2.20)):
        S = build_stylus(ridge_r=rr, h=h)
        # copy only the first 14 mm of each stylus into this plate, row i
        yo = i * 10.0
        sx0 = int(round((S.x[0] - F.x[0]) / h))
        cut = (S.x <= 13.5)
        jy0 = int(round((-3.8 + yo - F.y[0]) / h))
        sub = S.f[cut]
        F.f[sx0:sx0 + sub.shape[0], jy0:jy0 + sub.shape[1], :] = np.minimum(
            F.f[sx0:sx0 + sub.shape[0], jy0:jy0 + sub.shape[1], :], sub)
    return F

def build_stylus_heads(h=0.1):
    """v6.3 test heads: slim 3.5 mm barrel, ridge sits BEHIND the case bump (x 9.0-11.5). Two ridge sizes, long enough to push through the test block."""
    F = Field(-4.5, 24.5, -3.8, 12.8, -3.8, 3.8, h)
    for i, rr in enumerate((2.15, 2.08)):
        S = build_stylus(ridge_r=rr, h=h, BR=1.75, rx0=9.0, flat_cut=0.15)
        cut = (S.x <= 24.0)
        yo = i * 9.0
        sx0 = int(round((S.x[0] - F.x[0]) / h))
        jy0 = int(round((-3.8 + yo - F.y[0]) / h))
        sub = S.f[cut]
        F.f[sx0:sx0 + sub.shape[0], jy0:jy0 + sub.shape[1], :] = np.minimum(
            F.f[sx0:sx0 + sub.shape[0], jy0:jy0 + sub.shape[1], :], sub)
    return F

RING_TEST = (2.05, 1.95, 1.85)   # bump bore radius: 1 = same as the current case, 2 and 3 = tighter
def build_ring_block(h=0.1):
    """v6.3: three vertical tunnels, same 4.4 mm bore and same bump position (5.0-8.5 mm in from the top) as the case,
    with a tighter and tighter bump. Print standing up. Dots on top: 1, 2, 3 = loosest to tightest."""
    P, H = 7.8, 22.0
    F = Field(-1, 3 * P + 1, -1, P + 1, -1, H + 1, h)
    F.add(box(0, 3 * P, 0, P, 0, H))
    for i, ri in enumerate(RING_TEST):
        cx, cy = P / 2 + i * P, P / 2
        F.sub(cylz(cx, cy, 2.2, -1, H + 1))
        F.add(cylz(cx, cy, 3.1, H - 8.5, H - 5.0))
        F.sub(cylz(cx, cy, ri, H - 9.0, H - 4.5))
        for k in range(i + 1):
            F.sub(cylz(cx - 1.2 * i + 2.4 * k, cy + 3.35, 0.45, H - 0.6, H + 1))
    return F

def knob_radius(x):
    """collar outline, x = -3.5 (outer end) .. 0 (face against the case)"""
    rc = np.full_like(x, 3.2)
    rc = np.where(x < -3.0, 2.7 + (x + 3.5) * 1.0, rc)
    rc = np.where(((x > -2.7) & (x < -2.2)) | ((x > -1.7) & (x < -1.2)), 2.8, rc)
    return rc

def build_knob(h=0.1):
    """v6.3 round knob, printed standing with the case-side face (x=0) on the bed. Z = -x.
    Lip (z 0-1.2) holds the stylus flange from behind, so pulling the knob pulls the stylus. T-slot opens toward +Y."""
    R = 3.4
    F = Field(-R - 1, R + 1, -R - 1, R + 1, -1, 4.5, h)
    def body(X, Y, Z):
        rr = np.hypot(X, Y)
        r = knob_radius(-Z)
        return np.maximum(rr - r, np.maximum(-Z, Z - 3.5)).astype(np.float32)
    F.add(((-R, R, -R, R, 0, 3.5), body))
    F.sub(cylz(0, 0, 1.15, -1, 1.2))                      # neck hole through the lip
    F.sub(box(-1.15, 1.15, 0, R + 1, -1, 1.2))            # neck slit to the side
    F.sub(cylz(0, 0, 1.85, 1.2, 2.6))                     # flange pocket
    F.sub(box(-1.9, 1.9, 0, R + 1, 1.2, 2.6))             # flange channel to the side
    return F

def build_tabs(h=0.2):
    # v7 final: tabs were snapping at the screw. Now 7.4 wide with a round 3.7 mm end behind the hole: the ring around the
    # screw hole is 2.35 mm each side (was 1.65) and 3.7 mm behind the hole (was 1.45). Overhang past the hole is unchanged
    # (5.6 mm). Not wider, because the corner screw post sits 0.3 mm from the top tab.
    F = Field(-1, 35.4, -1, 10.5, -1, 2.7, h)
    for i in range(4):
        x0 = 0.0 + i * 8.6
        F.add(cylz(x0 + 3.7, 3.7, 3.7, 0, 1.5))
        F.add(box(x0, x0 + 7.4, 3.7, 7.3, 0, 1.5))
        F.add(rrect(x0, x0 + 7.4, 5.3, 9.3, 2.0, 0, 1.5))
        F.sub(cylz(x0 + 3.7, 3.7, 1.35, -1, 3))
    return F

def mesh(F, name, mirror=False):
    f = -F.f
    v, fc, nrm, _ = measure.marching_cubes(f, 0.0, spacing=(F.h, F.h, F.h), allow_degenerate=False)
    v = v + np.array(F.o, np.float32)
    if mirror:
        v[:, 0] = L - v[:, 0]
        fc = fc[:, ::-1]
    tri = v[fc]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    vol = np.sum(tri[:, 0] * np.cross(tri[:, 1], tri[:, 2])) / 6.0
    if vol < 0:
        fc = fc[:, ::-1]
        tri = v[fc]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        vol = -vol
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1
    n = (n / ln).astype(np.float32)
    rec = np.zeros(len(fc), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    rec['n'] = n
    rec['v'] = tri
    path = os.path.join(OUT, name)
    with open(path, 'wb') as fh:
        fh.write(b'Scrappies case'.ljust(80, b' '))
        fh.write(np.uint32(len(fc)).tobytes())
        fh.write(rec.tobytes())
    # manifold check
    e = np.sort(np.concatenate([fc[:, [0, 1]], fc[:, [1, 2]], fc[:, [2, 0]]]), axis=1)
    _, cnt = np.unique(e, axis=0, return_counts=True)
    bad = int(np.count_nonzero(cnt != 2))
    print(f'{name}: {len(fc)} tris, {os.path.getsize(path)/1e6:.1f} MB, volume {vol:.0f} mm3, '
          f'bbox {v.min(0).round(1)} -> {v.max(0).round(1)}, non-manifold edges {bad}')
    return path

if __name__ == '__main__':
    what = sys.argv[1:] or ['top', 'bottom', 'bar', 'clips', 'tabs']
    if 'top' in what:
        mesh(build_top(h=0.25), 'Scrappies_case_top_shell.stl', mirror=True)
    if 'bottom' in what:
        mesh(build_bottom(), 'Scrappies_case_bottom_shell.stl', mirror=True)
    if 'bar' in what:
        mesh(build_bar(), 'Scrappies_battery_strap_diagonal.stl')
        mesh(build_bstrap(), 'Scrappies_booster_strap.stl')
    if 'tabs' in what:
        mesh(build_tabs(), 'Scrappies_board_tabs_x4.stl')
    if 'v63' in what:
        mesh(build_ring_block(), 'Scrappies_ring_test_block.stl')
        mesh(build_stylus_heads(), 'Scrappies_stylus_head_tests_x2.stl')
        mesh(build_stylus(BR=1.75, rx0=9.0, ridge_r=2.15, flat_cut=0.15), 'Scrappies_stylus_slim_PROVISIONAL.stl')
    if 'v63b' in what:
        mesh(build_stylus(BR=1.75, rx0=9.0, ridge_r=2.08, flat_cut=0.15, knobless=True), 'Scrappies_stylus_body_for_knob.stl')
        mesh(build_knob(), 'Scrappies_stylus_knob.stl')
        mesh(build_stylus(BR=1.75, rx0=9.0, ridge_r=2.08, flat_cut=0.15), 'Scrappies_stylus_onepiece.stl')
    if 'stylus' in what:
        mesh(build_stylus(), 'Scrappies_stylus.stl')
        mesh(build_stylus_test(), 'Scrappies_stylus_fit_test_x3.stl')
    if 'clips' in what:
        mesh(build_clips(), 'Scrappies_stylus_clips_x2.stl')
