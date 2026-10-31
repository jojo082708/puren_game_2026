"""ISO-style 30° trapezoidal threads (Tr) built with bd_warehouse's ruled-surface Thread."""
import math

import build123d as bd
from bd_warehouse.thread import Thread


def tr_dims(d_major, pitch):
    """Tr profile: depth h3 = P/2 + ac (ac 0.25), crest 0.366 P, root = crest + 2 h tan15."""
    depth = 0.5 * pitch + 0.25
    crest = 0.366 * pitch
    root = crest + 2 * depth * math.tan(math.radians(15))
    return depth, crest, root


def external_thread(d_major, pitch, length, z0=0.0, ends=("raw", "chamfer")):
    """Thread ridge (no core) for an external Tr thread from z0 to z0 + length."""
    depth, crest, root = tr_dims(d_major, pitch)
    t = Thread(apex_radius=d_major / 2, apex_width=crest,
               root_radius=d_major / 2 - depth, root_width=root,
               pitch=pitch, length=length, end_finishes=ends)
    return bd.Pos(0, 0, z0) * t


def internal_thread_cutter(d_major, pitch, length, z0=0.0, fit=0.35, extra=3.0):
    """Tool to subtract for an internal Tr thread (nut/socket) from z0 to z0 + length.

    It is the mating screw grown by `fit` radially and 0.15 mm axially, run `extra` past both
    ends so no face of it lies on the part's faces; trim the mouths with `countersink`.
    """
    depth, crest, root = tr_dims(d_major, pitch)
    D = d_major + 2 * fit
    r_min = D / 2 - depth
    L = length + 2 * extra
    ridge = Thread(apex_radius=D / 2, apex_width=crest + 0.15,
                   root_radius=r_min, root_width=root + 0.15,
                   pitch=pitch, length=L, end_finishes=("raw", "raw"))
    core = bd.Cylinder(r_min, L, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    return bd.Pos(0, 0, z0 - extra) * (core + ridge)


def countersink(d_major, chamfer, z, up, fit=0.35, pitch=3.0, extra=3.0):
    """45° entry chamfer of a threaded bore's mouth at height z, run `extra` past the face."""
    depth, _, _ = tr_dims(d_major, pitch)
    D = d_major + 2 * fit
    r_small = D / 2 - depth
    r_big = D / 2 + chamfer
    h = r_big - r_small
    MIN = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    if up:      # opens toward +Z, face at z
        cone = bd.Pos(0, 0, z - h) * bd.Cone(r_small, r_big, h, align=MIN)
        cap = bd.Pos(0, 0, z) * bd.Cylinder(r_big, extra, align=MIN)
    else:       # opens toward -Z, face at z
        cone = bd.Pos(0, 0, z) * bd.Cone(r_big, r_small, h, align=MIN)
        cap = bd.Pos(0, 0, z - extra) * bd.Cylinder(r_big, extra, align=MIN)
    return cone + cap
