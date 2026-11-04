"""星形旋鈕螺母: 6-lobe hand knob, Tr24.5×3 internal thread through, Ø38 boss on the clamping side."""
import math

import build123d as bd
from cadgen import model

from params import (ENTRY_CHAMFER, FIT, KNOB_CORE_R, KNOB_D, KNOB_EDGE_R_BOT, KNOB_EDGE_R_TOP,
                    KNOB_H, KNOB_HUB_D, KNOB_HUB_FILLET, KNOB_HUB_H, KNOB_LOBE_R, KNOB_LOBES,
                    KNOB_VALLEY_R, LOCK_KNOB_H, SHAFT_D, SHAFT_P)
from threads import countersink, internal_thread_cutter

MIN = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)


def star_outline():
    rc = KNOB_D / 2 - KNOB_LOBE_R
    shape = bd.Circle(KNOB_CORE_R)
    for k in range(KNOB_LOBES):
        a = 2 * math.pi * k / KNOB_LOBES
        shape = shape + bd.Pos(rc * math.cos(a), rc * math.sin(a)) * bd.Circle(KNOB_LOBE_R)
    # finger valleys: close the outline by R3.5 (offset out, then back in), so each valley is
    # one arc tangent to both neighbouring lobes
    grown = bd.offset(shape, KNOB_VALLEY_R, kind=bd.Kind.ARC)
    return bd.offset(grown, -KNOB_VALLEY_R, kind=bd.Kind.ARC)


def knob_body(height=KNOB_H, hub=True, r_top=KNOB_EDGE_R_TOP, r_bot=KNOB_EDGE_R_BOT):
    z0 = KNOB_HUB_H if hub else 0.0
    star = bd.Pos(0, 0, z0) * bd.extrude(star_outline(), height)
    star = star.fillet(r_top, star.edges().group_by(bd.Axis.Z)[-1])
    star = star.fillet(r_bot, star.edges().group_by(bd.Axis.Z)[0])
    body = star
    if hub:
        boss = bd.Cylinder(KNOB_HUB_D / 2, KNOB_HUB_H + r_bot + 1, align=MIN)
        boss = boss.fillet(1.5, boss.edges().group_by(bd.Axis.Z)[0])
        body = star + boss
        root = [e for e in body.edges().filter_by(bd.GeomType.CIRCLE)
                if abs(e.radius - KNOB_HUB_D / 2) < 0.01 and abs(e.center().Z - KNOB_HUB_H) < 0.01]
        body = body.fillet(KNOB_HUB_FILLET, root)

    H = z0 + height
    body = body - [internal_thread_cutter(SHAFT_D, SHAFT_P, H, 0.0, FIT),
                   countersink(SHAFT_D, ENTRY_CHAMFER, H, up=True),
                   countersink(SHAFT_D, ENTRY_CHAMFER, 0.0, up=False)]
    return body


@model
def star_knob():
    body = knob_body()
    bb = body.bounding_box()
    assert abs(bb.size.Z - (KNOB_HUB_H + KNOB_H)) < 0.01, bb.size
    assert abs(bb.size.X - KNOB_D) < 0.05, bb.size
    assert len(body.solids()) == 1
    body.label = "star_knob"
    body.color = "#2b2f36"
    return body


@model
def lock_knob():
    """Thin star jam knob: turned down onto the main knob so the pair locks on the thread."""
    body = knob_body(LOCK_KNOB_H, hub=False, r_top=4.0, r_bot=2.0)
    assert abs(body.bounding_box().size.Z - LOCK_KNOB_H) < 0.01
    assert len(body.solids()) == 1
    body.label = "lock_knob"
    body.color = "#2b2f36"
    return body


if __name__ == "__main__":
    star_knob()
    lock_knob()
