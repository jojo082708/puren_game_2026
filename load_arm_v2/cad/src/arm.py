"""承重桿 v2: motor hub + 5 threaded sockets (Ø29×P3) at moment arms 100–300 mm."""
import math

import build123d as bd
from cadgen import model

from params import (ARM_LEN, ARM_R_BOT, ARM_R_TOP, ARM_T, ENTRY_CHAMFER, FIT, HOLE_X, HUB_D,
                    HUB_H, HUB_R, R_LOAD, R_MOTOR, SOCKET_D, SOCKET_P)
from threads import countersink, internal_thread_cutter

MIN = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)


def arm_outline():
    a = bd.Circle(R_MOTOR)
    b = bd.Pos(ARM_LEN, 0) * bd.Circle(R_LOAD)
    return bd.make_hull((a + b).edges())


def arm_body():
    slab = bd.extrude(arm_outline(), ARM_T)
    zs = slab.edges().group_by(bd.Axis.Z)
    slab = slab.fillet(ARM_R_TOP, zs[-1])
    slab = slab.fillet(ARM_R_BOT, slab.edges().group_by(bd.Axis.Z)[0])

    hub = bd.Pos(0, 0, -HUB_H) * bd.Cylinder(HUB_D / 2, HUB_H + 1.0, align=MIN)
    hub = hub.fillet(HUB_R, hub.edges().group_by(bd.Axis.Z)[0])
    body = slab + hub

    zb, H = -HUB_H, ARM_T + HUB_H
    cuts = []
    for k in range(6):          # AK70: 6×Ø3.3 PCD25, counterbore Ø6.5 from top, 8 left at the hub face
        a = math.radians(60 * k)
        p = bd.Pos(12.5 * math.cos(a), 12.5 * math.sin(a), zb - 1)
        cuts += [p * bd.Cylinder(1.65, H + 2, align=MIN),
                 bd.Pos(0, 0, 9) * p * bd.Cylinder(3.25, H - 8 + 1, align=MIN)]
    for k in range(3):          # AK60: 3×Ø4.5 PCD30 through
        a = math.radians(30 + 120 * k)
        cuts.append(bd.Pos(15 * math.cos(a), 15 * math.sin(a), zb - 1) * bd.Cylinder(2.25, H + 2, align=MIN))
    for k in range(3):          # AK60: 3×Ø4.1 PCD28.5, 8 deep from the hub face
        a = math.radians(90 + 120 * k)
        cuts.append(bd.Pos(14.25 * math.cos(a), 14.25 * math.sin(a), zb - 1) * bd.Cylinder(2.05, 9, align=MIN))
    cutter = internal_thread_cutter(SOCKET_D, SOCKET_P, ARM_T, 0.0, FIT)
    for x in HOLE_X:            # Ø29×P3 internal thread, through, with 45° entry chamfers
        cuts += [bd.Pos(x, 0, 0) * cutter,
                 bd.Pos(x, 0, 0) * countersink(SOCKET_D, ENTRY_CHAMFER, ARM_T, up=True),
                 bd.Pos(x, 0, 0) * countersink(SOCKET_D, ENTRY_CHAMFER, 0.0, up=False)]
    body = body - cuts

    for x in HOLE_X:            # the body is meant to keep each socket clear down its axis
        assert not bd.Pos(x, 0, ARM_T / 2) * bd.Cylinder(SOCKET_D / 2 - 1.75 - 0.2, 1) & body
    return body


@model
def load_arm():
    body = arm_body()
    bb = body.bounding_box()
    assert abs(bb.size.X - 370) < 0.01 and abs(bb.size.Z - 35) < 0.01, bb.size
    body.label = "load_arm"
    body.color = "#c2662d"
    return body


if __name__ == "__main__":
    load_arm()
