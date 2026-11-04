"""承重桿 v3 組合: pin screwed into P3 (r = 200), 4 weight plates, keyed clamp plate, star knob +
lock knob, M12 rod clamping arm–pin through a DIN 9021 washer under the arm.

Clamp path (steel M12 preload): bottom nut → DIN 9021 Ø37 washer → arm underside → arm → pin
flange → pin → DIN 433 Ø20 washer → top nut. The Ø37 washer spans the socket mouth (Ø32.7),
so the bottom nut can no longer sink into the socket.
"""
import math

import build123d as bd
from cadgen import model

from arm import load_arm_ak60, load_arm_ak70
from knob import lock_knob, star_knob
from params import (ARM_T, FLANGE_T, HOLE_X, KNOB_H, KNOB_HUB_H, LOCK_KNOB_H, PIN_SPIGOT_L,
                    PLATE_T, SHAFT_L, SHAFT_P, SOCKET_P, WASHER_BIG, WASHER_SMALL, WEIGHT_BORE,
                    WEIGHT_D, WEIGHT_N, WEIGHT_T)
from pin import load_pin
from plate import clamp_plate

MIN = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
SOCKET = 2                  # P3


def thread_turn(z_have, z_want, pitch):
    """Turn (deg) about Z that puts a right-hand thread starting at z_have on the helix of one
    starting at z_want (z = z0 + P·θ/2π)."""
    return 360.0 * (((z_have - z_want) / pitch) % 1.0)


def weight_plate():
    w = bd.Cylinder(WEIGHT_D / 2, WEIGHT_T, align=MIN) - bd.Cylinder(WEIGHT_BORE / 2, WEIGHT_T, align=MIN)
    w = w.fillet(3.0, [e for e in w.edges().filter_by(bd.GeomType.CIRCLE) if e.radius > WEIGHT_D / 2 - 0.1])
    w.color = "#1c1d1f"
    return w


def washer(od, id_, t):
    w = bd.Cylinder(od / 2, t, align=MIN) - bd.Cylinder(id_ / 2, t, align=MIN)
    w.color = "#b9c0c7"
    return w


def m12_nut():
    n = bd.extrude(bd.RegularPolygon(18 / math.sqrt(3), 6), 10) - bd.Cylinder(6, 10, align=MIN)
    n.color = "#9aa3ab"
    return n


def rig(arm_shape, name):
    x = HOLE_X[SOCKET]
    # the pin's spigot ridge starts at pin z −24, the socket cutter at arm z −3
    turn_pin = thread_turn(ARM_T - PIN_SPIGOT_L, -3.0, SOCKET_P)
    pin = bd.Pos(x, 0, ARM_T) * bd.Rot(0, 0, turn_pin) * load_pin().shape

    z_stack = ARM_T + FLANGE_T
    weights = []
    for i in range(WEIGHT_N):
        w = bd.Pos(x, 0, z_stack + i * WEIGHT_T) * weight_plate()
        w.label = "weight_plate"
        weights.append(w)
    z_plate = z_stack + WEIGHT_N * WEIGHT_T
    plate = bd.Pos(x, 0, z_plate) * bd.Rot(0, 0, turn_pin) * clamp_plate().shape   # key on the flat
    shaft_start = ARM_T + FLANGE_T + 0.5 - SHAFT_P * turn_pin / 360.0
    z_knob = z_plate + PLATE_T
    knob = bd.Pos(x, 0, z_knob) * bd.Rot(0, 0, thread_turn(z_knob - 3.0, shaft_start, SHAFT_P)) * star_knob().shape
    z_lock = z_knob + KNOB_HUB_H + KNOB_H
    lock = bd.Pos(x, 0, z_lock) * bd.Rot(0, 0, thread_turn(z_lock - 3.0, shaft_start, SHAFT_P)) * lock_knob().shape

    pin_top = ARM_T + FLANGE_T + SHAFT_L
    big = bd.Pos(x, 0, -WASHER_BIG[2]) * washer(*WASHER_BIG)
    small = bd.Pos(x, 0, pin_top) * washer(*WASHER_SMALL)
    nut_bot = bd.Pos(x, 0, -WASHER_BIG[2] - 10) * m12_nut()
    nut_top = bd.Pos(x, 0, pin_top + WASHER_SMALL[2]) * m12_nut()
    z0 = -WASHER_BIG[2] - 14
    rod = bd.Pos(x, 0, z0) * bd.Cylinder(6, pin_top + WASHER_SMALL[2] + 14 - z0, align=MIN)
    rod.color = "#9aa3ab"
    big.label, small.label, rod.label = "washer_din9021", "washer_din433", "m12_rod"
    nut_bot.label = nut_top.label = "m12_nut"

    hardware = bd.Compound(children=[rod, big, small, nut_bot, nut_top], label="m12_hardware")
    plates = bd.Compound(children=weights, label="weight_plates")
    return bd.Compound(children=[arm_shape, pin, plates, plate, knob, lock, hardware], label=name)


@model
def load_arm_assembly_ak70():
    return rig(load_arm_ak70().shape, "load_arm_assembly_ak70")


@model
def load_arm_assembly_ak60():
    return rig(load_arm_ak60().shape, "load_arm_assembly_ak60")


if __name__ == "__main__":
    load_arm_assembly_ak70()
    load_arm_assembly_ak60()
