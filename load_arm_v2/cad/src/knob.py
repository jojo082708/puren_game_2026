"""星形旋鈕螺母: 6-lobe hand knob, Tr24.5×3 internal thread through, Ø38 boss on the clamping side."""
import math

import build123d as bd
from cadgen import model

from params import (ENTRY_CHAMFER, FIT, KNOB_CORE_R, KNOB_D, KNOB_EDGE_R_BOT, KNOB_EDGE_R_TOP,
                    KNOB_H, KNOB_HUB_D, KNOB_HUB_FILLET, KNOB_HUB_H, KNOB_LOBE_R, KNOB_LOBES,
                    KNOB_VALLEY_R, SHAFT_D, SHAFT_P)
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


def knob_body():
    star = bd.Pos(0, 0, KNOB_HUB_H) * bd.extrude(star_outline(), KNOB_H)
    ez = star.edges().group_by(bd.Axis.Z)
    star = star.fillet(KNOB_EDGE_R_TOP, ez[-1])
    star = star.fillet(KNOB_EDGE_R_BOT, star.edges().group_by(bd.Axis.Z)[0])
    hub = bd.Cylinder(KNOB_HUB_D / 2, KNOB_HUB_H + KNOB_EDGE_R_BOT + 1, align=MIN)
    hub = hub.fillet(1.5, hub.edges().group_by(bd.Axis.Z)[0])
    body = star + hub
    root = [e for e in body.edges().filter_by(bd.GeomType.CIRCLE)
            if abs(e.radius - KNOB_HUB_D / 2) < 0.01 and abs(e.center().Z - KNOB_HUB_H) < 0.01]
    body = body.fillet(KNOB_HUB_FILLET, root)

    H = KNOB_HUB_H + KNOB_H
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


if __name__ == "__main__":
    star_knob()
