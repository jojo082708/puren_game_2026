"""Generate STL files for the load-arm system-ID rig (v2).

Parts
  1. load_arm_multi_hole.stl   – 承重桿，多個 Ø29×P3 內螺紋孔（不同力臂）
  2. load_pin_Tr24.5x3.stl     – 承重軸，外螺紋 Tr24.5×3（槓片內徑 ≤ 26.35 可通過）
  3. hex_nut_Tr24.5x3.stl      – 六角螺母 41 AF × 20，鎖緊槓片
  4. clamp_plate_80x5.stl      – 壓板 Ø80×5，內孔 Ø25.5

Run:  python3 build_parts.py   (needs: numpy, manifold3d, trimesh)
"""
import math, os
import numpy as np
import manifold3d as m3
import trimesh

OUT = os.path.dirname(os.path.abspath(__file__))
SEG = 128                      # angular segments for round features

# ---------------------------------------------------------------- params
ARM_LEN = 300.0                # motor centre -> farthest hole
R_MOTOR, R_LOAD = 30.0, 40.0   # end radii (R30 / R40)
ARM_T = 25.0                   # arm thickness
HUB_D, HUB_H = 56.0, 10.0      # motor hub below arm
HOLE_X = [100.0, 150.0, 200.0, 250.0, 300.0]   # moment-arm positions (mm)

SOCKET_D, SOCKET_P = 29.0, 3.0  # arm <-> pin thread (unchanged from v1)
SHAFT_D, SHAFT_P = 24.5, 3.0    # new plate shaft thread
BORE = 12.5                     # M12 through hole
FIT = 0.35                      # radial print clearance for internal threads

PIN_SPIGOT_L = 24.0
FLANGE_D, FLANGE_T = 80.0, 8.0
SHAFT_L = 158.0

NUT_AF, NUT_H = 41.0, 20.0
PLATE_D, PLATE_T, PLATE_BORE = 80.0, 5.0, 25.5

# fillets / rounds (durability + looks)
ARM_R_TOP, ARM_R_BOT = 5.0, 2.0   # arm outline: top edge R5, bottom edge R2 (meets Ø56 hub flush)
HUB_R = 1.5                       # hub bottom edge
FLANGE_R = 2.5                    # flange outer edges (top + bottom)
SHAFT_FILLET = 2.0                # concave fillet shaft root -> flange (stress relief)
SPIGOT_FILLET = 1.5               # concave fillet flange -> Ø29 spigot (sits in arm hole chamfer)
NUT_CORNER_R = 3.0                # rounded hex vertical edges
PLATE_R_OUT, PLATE_R_IN = 1.5, 0.8


# ---------------------------------------------------------------- helpers
def to_manifold(tm):
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(tm.vertices, np.float32),
                               tri_verts=np.asarray(tm.faces, np.uint32)))

def to_trimesh(man):
    mesh = man.to_mesh()
    return trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts, process=False)

def cyl(d, h, z0=0.0, d2=None, n=SEG):
    c = m3.Manifold.cylinder(h, d / 2, (d2 if d2 is not None else d) / 2, n)
    return c.translate((0, 0, z0))

def tr_profile(P, depth, crest_frac=0.366, extra=0.0):
    """Return f(u)->radial height in [0,depth] for u in [0,P) (30° trapezoid)."""
    f = depth * math.tan(math.radians(15))
    crest = crest_frac * P + extra
    root = P - crest - 2 * f
    assert root > 0, "thread profile too deep"
    def h(u):
        u = np.mod(u, P)
        out = np.zeros_like(u)
        a = root; b = a + f; c = b + crest; d = c + f
        m = (u >= a) & (u < b); out[m] = (u[m] - a) / f * depth
        m = (u >= b) & (u < c); out[m] = depth
        m = (u >= c) & (u < d); out[m] = (d - u[m]) / f * depth
        return out
    return h

def thread_solid(major_d, P, length, depth, z0=0.0, extra_crest=0.0, n_ang=144, dz=None):
    """Right-hand helical thread body (solid), axis Z, from z0 to z0+length."""
    dz = dz or P / 24
    nz = int(math.ceil(length / dz)) + 1
    zs = np.linspace(0, length, nz)
    th = np.linspace(0, 2 * math.pi, n_ang, endpoint=False)
    prof = tr_profile(P, depth, extra=extra_crest)
    Z, T = np.meshgrid(zs, th, indexing="ij")
    u = Z - P * T / (2 * math.pi)
    R = major_d / 2 - depth + prof(u)
    V = np.stack([R * np.cos(T), R * np.sin(T), Z + z0], -1).reshape(-1, 3)
    idx = lambda i, j: i * n_ang + (j % n_ang)
    F = []
    for i in range(nz - 1):
        for j in range(n_ang):
            a, b, c, d = idx(i, j), idx(i, j + 1), idx(i + 1, j + 1), idx(i + 1, j)
            F += [(a, b, c), (a, c, d)]
    bot = len(V); top = bot + 1
    V = np.vstack([V, [0, 0, z0], [0, 0, z0 + length]])
    for j in range(n_ang):
        F.append((bot, idx(0, j + 1), idx(0, j)))
        F.append((top, idx(nz - 1, j), idx(nz - 1, j + 1)))
    tm = trimesh.Trimesh(V, np.array(F), process=True)
    if tm.volume < 0:
        tm.invert()
    return to_manifold(tm)

def ext_thread(d, P, L, z0=0.0, chamfer_top=True, chamfer_bot=True):
    depth = 0.5 * P + 0.25
    t = thread_solid(d, P, L, depth, z0)
    c = depth + 0.3   # 45° lead-in chamfers
    env = cyl(d + 2, L, z0)
    if chamfer_top:
        env = env - (cyl(d + 4, c + 2, z0 + L - c) - cyl(d - 2 * c, c + 2, z0 + L - c, d - 2 * c - 2 * (c + 2)))
    if chamfer_bot:
        env = env - (cyl(d + 4, c, z0) - cyl(d - 2 * c, c, z0, d))
    return t ^ env

def int_thread_cutter(d, P, L, z0=0.0, chamfer=1.5):
    """Solid to subtract for an internal thread (with print clearance + entry chamfers)."""
    depth = 0.5 * P + 0.25
    t = thread_solid(d + 2 * FIT, P, L + 2, depth, z0 - 1, extra_crest=0.15)
    top = cyl(d - 2 * depth + 2 * FIT, chamfer + 0.01, z0 + L - chamfer, d + 2 * FIT + 2 * chamfer)
    bot = cyl(d + 2 * FIT + 2 * chamfer, chamfer + 0.01, z0 - 0.01, d - 2 * depth + 2 * FIT)
    return t + top + bot



# ---------------------------------------------------------------- round-edge helpers
def arc(cx, cy, r, a0, a1, n=12):
    t = np.radians(np.linspace(a0, a1, n))
    return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in t]

def revolve(pts, n=SEG):
    """Revolve a (radius, z) polygon about Z."""
    pts = np.asarray(pts, float)
    x, y = pts[:, 0], pts[:, 1]
    if 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y) < 0:
        pts = pts[::-1]
    return m3.Manifold.revolve(m3.CrossSection([pts.tolist()]), n)

def rounded_disc(r_out, h, r_in=0.0, ro_bot=0.0, ro_top=0.0, ri_bot=0.0, ri_top=0.0, z0=0.0):
    """Annulus/disc with rounded edges: profile in (r, z)."""
    P = []
    P += arc(r_out - ro_bot, ro_bot, ro_bot, -90, 0) if ro_bot else [(r_out, 0)]
    P += arc(r_out - ro_top, h - ro_top, ro_top, 0, 90) if ro_top else [(r_out, h)]
    if r_in > 0:
        P += arc(r_in + ri_top, h - ri_top, ri_top, 90, 180) if ri_top else [(r_in, h)]
        P += arc(r_in + ri_bot, ri_bot, ri_bot, 180, 270) if ri_bot else [(r_in, 0)]
    else:
        P += [(0, h), (0, 0)]
    return revolve(P).translate((0, 0, z0))

def fillet_ring(r0, z0, R, up=True):
    """Concave fillet in the corner between a cylinder of radius r0 and a face at z0."""
    sgn = 1 if up else -1
    P = [(r0, z0), (r0 + R, z0)]
    P += [(r0 + R + R * math.cos(a), z0 + sgn * (R + R * math.sin(a)))
          for a in np.radians(np.linspace(-90, -180, 14))]
    return revolve(P)

def rounded_slab_hull(centers_radii, h, r_top, r_bot, z0=0.0, n=SEG, steps=10):
    """Convex hull of circles (x, y, R) extruded to height h, top/bottom edges rounded."""
    pts = []
    def ring(z, inset):
        for (cx, cy, R) in centers_radii:
            t = np.linspace(0, 2 * math.pi, n, endpoint=False)
            pts.extend(np.c_[cx + (R - inset) * np.cos(t), cy + (R - inset) * np.sin(t), np.full(n, z)].tolist())
    for a in np.radians(np.linspace(0, 90, steps)):
        ring(z0 + r_bot - r_bot * math.sin(a), r_bot - r_bot * math.cos(a))
        ring(z0 + h - r_top + r_top * math.sin(a), r_top - r_top * math.cos(a))
    return m3.Manifold.hull_points(pts)

# ---------------------------------------------------------------- 1. arm
def arm():
    body = rounded_slab_hull([(0, 0, R_MOTOR), (ARM_LEN, 0, R_LOAD)], ARM_T, ARM_R_TOP, ARM_R_BOT)
    body = body + rounded_slab_hull([(0, 0, HUB_D / 2)], HUB_H + 0.5, 0.0, HUB_R, z0=-HUB_H)
    zb, zt = -HUB_H, ARM_T
    H = zt - zb
    # motor interface (same as v1 drawing)
    for k in range(6):                      # AK70: 6×Ø3.3 PCD25, counterbore Ø6.5 from top, 8 mm left at bottom
        ang = math.radians(60 * k)
        x, y = 12.5 * math.cos(ang), 12.5 * math.sin(ang)
        body -= cyl(3.3, H + 2, zb - 1, n=32).translate((x, y, 0))
        body -= cyl(6.5, H - 8 + 1, zb + 8, n=32).translate((x, y, 0))
    for k in range(3):                      # AK60: 3×Ø4.5 PCD30 through
        ang = math.radians(30 + 120 * k)
        body -= cyl(4.5, H + 2, zb - 1, n=32).translate((15 * math.cos(ang), 15 * math.sin(ang), 0))
    for k in range(3):                      # AK60: 3×Ø4.1 PCD28.5 depth 8 from hub face
        ang = math.radians(90 + 120 * k)
        body -= cyl(4.1, 8 + 1, zb - 1, n=32).translate((14.25 * math.cos(ang), 14.25 * math.sin(ang), 0))
    # load sockets: Ø29×P3 internal thread, through, 1.5 chamfers
    cutter = int_thread_cutter(SOCKET_D, SOCKET_P, ARM_T, 0.0)
    for x in HOLE_X:
        body -= cutter.translate((x, 0, 0))
    return body

# ---------------------------------------------------------------- 2. pin
def pin():
    spigot = ext_thread(SOCKET_D, SOCKET_P, PIN_SPIGOT_L, -PIN_SPIGOT_L, chamfer_top=False)
    flange = rounded_disc(FLANGE_D / 2, FLANGE_T, ro_bot=FLANGE_R, ro_top=FLANGE_R)
    shaft = ext_thread(SHAFT_D, SHAFT_P, SHAFT_L + 0.5, FLANGE_T - 0.5, chamfer_bot=False)
    root_shaft = SHAFT_D / 2 - (0.5 * SHAFT_P + 0.25)
    root_spigot = SOCKET_D / 2 - (0.5 * SOCKET_P + 0.25)
    fil = (fillet_ring(root_shaft - 0.05, FLANGE_T, SHAFT_FILLET, up=True)
           + fillet_ring(root_spigot - 0.05, 0.0, SPIGOT_FILLET, up=False))
    body = spigot + flange + shaft + fil
    total = PIN_SPIGOT_L + FLANGE_T + SHAFT_L
    body -= cyl(BORE, total + 4, -PIN_SPIGOT_L - 2, n=64)
    return body

# ---------------------------------------------------------------- 3. nut
def hex_nut():
    hexr = NUT_AF / 2 / math.cos(math.radians(30))
    c = NUT_CORNER_R
    d = hexr - c / math.cos(math.radians(30))          # corner-circle centre distance
    corners = [(d * math.cos(math.radians(60 * k)), d * math.sin(math.radians(60 * k))) for k in range(6)]
    hx = m3.Manifold.batch_hull([cyl(2 * c, NUT_H, n=24).translate((x, y, 0)) for x, y in corners])
    # 30° corner chamfer on both faces (standard nut look; chamfer circle = AF)
    cr = 2 * hexr + 0.2
    ch = (cr - NUT_AF) / 2 * math.tan(math.radians(60))
    env = (cyl(NUT_AF, ch, 0, cr) + cyl(cr, NUT_H - 2 * ch, ch)
           + cyl(cr, ch, NUT_H - ch, NUT_AF))
    nut = hx ^ env
    nut -= int_thread_cutter(SHAFT_D, SHAFT_P, NUT_H, 0.0, chamfer=1.5)
    return nut

# ---------------------------------------------------------------- 4. plate
def clamp_plate():
    return rounded_disc(PLATE_D / 2, PLATE_T, PLATE_BORE / 2,
                        PLATE_R_OUT, PLATE_R_OUT, PLATE_R_IN, PLATE_R_IN)

if __name__ == "__main__":
    parts = {
        "load_arm_multi_hole.stl": arm,
        "load_pin_Tr24.5x3.stl": pin,
        "hex_nut_Tr24.5x3.stl": hex_nut,
        "clamp_plate_80x5.stl": clamp_plate,
    }
    for name, fn in parts.items():
        man = fn()
        assert man.status() == m3.Error.NoError, (name, man.status())
        tm = to_trimesh(man)
        tm.export(os.path.join(OUT, name))
        lo, hi = tm.bounds
        print(f"{name:28s} watertight={tm.is_watertight} vol={tm.volume/1000:8.1f} cm3 "
              f"bbox={np.round(hi-lo,2)} faces={len(tm.faces)}")
