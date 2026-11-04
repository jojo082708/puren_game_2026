"""承重桿 v3: 5 threaded sockets (Ø29×P3) at moment arms 100–300 mm, one motor interface per variant.

The motor's output face stands only 0.5 mm proud of its stationary housing (CubeMars STEP), so
the hub touches the motor through a boss no wider than the output face and clears the housing
by BOSS_H + 0.5 mm. Each variant carries only its own motor's screw and dowel holes.
"""
import math

import build123d as bd
from cadgen import model

from params import (ARM_LEN, ARM_R_BOT, ARM_R_TOP, ARM_T, BOSS_H, ENTRY_CHAMFER, FIT, HOLE_X,
                    HUB_D, HUB_H, HUB_R, MOTORS, R_LOAD, R_MOTOR, SOCKET_D, SOCKET_P)
from threads import countersink, internal_thread_cutter

MIN = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)


def arm_outline():
    a = bd.Circle(R_MOTOR)
    b = bd.Pos(ARM_LEN, 0) * bd.Circle(R_LOAD)
    return bd.make_hull((a + b).edges())


def polar(n, pcd, start):
    return [(pcd / 2 * math.cos(math.radians(start + 360 * k / n)),
             pcd / 2 * math.sin(math.radians(start + 360 * k / n))) for k in range(n)]


def arm_body(motor):
    m = MOTORS[motor]
    z_face = -HUB_H - BOSS_H                     # contact face with the motor's output

    slab = bd.extrude(arm_outline(), ARM_T)
    slab = slab.fillet(ARM_R_TOP, slab.edges().group_by(bd.Axis.Z)[-1])
    slab = slab.fillet(ARM_R_BOT, slab.edges().group_by(bd.Axis.Z)[0])
    hub = bd.Pos(0, 0, -HUB_H) * bd.Cylinder(HUB_D / 2, HUB_H + 1.0, align=MIN)
    hub = hub.fillet(HUB_R, hub.edges().group_by(bd.Axis.Z)[0])
    boss = bd.Pos(0, 0, z_face) * bd.Cylinder(m["boss_d"] / 2, BOSS_H + 0.5, align=MIN)
    boss = boss.chamfer(0.5, None, boss.edges().group_by(bd.Axis.Z)[0])
    body = slab + hub + boss
    if m["pilot_h"]:                             # centring spigot into the output's recess
        pilot = bd.Pos(0, 0, z_face - m["pilot_h"]) * bd.Cylinder(m["pilot_d"] / 2, m["pilot_h"] + 0.5, align=MIN)
        pilot = pilot.chamfer(0.4, None, pilot.edges().group_by(bd.Axis.Z)[0])
        body = body + pilot

    z_bot = z_face - m["pilot_h"]
    top = ARM_T
    n, pcd, start, hole, cb, grip = m["screws"]
    cuts = []
    for x, y in polar(n, pcd, start):            # through holes, heads sunk to `grip` above the face
        cuts.append(bd.Pos(x, y, z_bot - 1) * bd.Cylinder(hole / 2, top - z_bot + 2, align=MIN))
        cuts.append(bd.Pos(x, y, z_face + grip) * bd.Cylinder(cb / 2, top - z_face - grip + 1, align=MIN))
    n, pcd, start, dia, depth = m["dowels"]
    for x, y in polar(n, pcd, start):            # dowel holes from the contact face
        cuts.append(bd.Pos(x, y, z_bot - 1) * bd.Cylinder(dia / 2, depth + (z_face - z_bot) + 1, align=MIN))

    cutter = internal_thread_cutter(SOCKET_D, SOCKET_P, ARM_T, 0.0, FIT)
    for x in HOLE_X:                             # Ø29×P3 internal thread, through, 45° mouths
        cuts += [bd.Pos(x, 0, 0) * cutter,
                 bd.Pos(x, 0, 0) * countersink(SOCKET_D, ENTRY_CHAMFER, ARM_T, up=True),
                 bd.Pos(x, 0, 0) * countersink(SOCKET_D, ENTRY_CHAMFER, 0.0, up=False)]
    return body - cuts


def checked(body, motor):
    m = MOTORS[motor]
    bb = body.bounding_box()
    assert abs(bb.size.X - 370) < 0.01, bb.size
    assert abs(bb.min.Z - (-HUB_H - BOSS_H - m["pilot_h"])) < 0.01, bb.min
    assert len(body.solids()) == 1
    for x in HOLE_X:                             # each socket stays clear down its axis
        assert not bd.Pos(x, 0, ARM_T / 2) * bd.Cylinder(SOCKET_D / 2 - 1.75 - 0.2, 1) & body
    body.color = "#c2662d"
    return body


@model
def load_arm_ak70():
    body = checked(arm_body("ak70"), "ak70")
    body.label = "load_arm_ak70"
    return body


@model
def load_arm_ak60():
    body = checked(arm_body("ak60"), "ak60")
    body.label = "load_arm_ak60"
    return body


if __name__ == "__main__":
    load_arm_ak70()
    load_arm_ak60()
