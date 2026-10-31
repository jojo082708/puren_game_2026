"""承重桿 v2 組合: pin screwed into socket P3 (r = 200), 4 weight plates, clamp plate, star knob, M12 rod."""
import math

import build123d as bd
from cadgen import model

from arm import load_arm
from knob import star_knob
from params import (ARM_T, FLANGE_T, HOLE_X, PIN_SPIGOT_L, PLATE_T, SHAFT_L, SHAFT_P,
                    SOCKET_P, WEIGHT_BORE, WEIGHT_D, WEIGHT_N, WEIGHT_T)
from pin import load_pin
from plate import clamp_plate

MIN = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
SOCKET = 2                  # P3


def thread_turn(z_have, z_want, pitch):
    """Rotation (deg) about Z that moves a right-hand thread starting at z_have onto the
    helix of one starting at z_want: z = z0 + P·θ/2π, so turn by 360·(z_have − z_want)/P."""
    return 360.0 * (((z_have - z_want) / pitch) % 1.0)


def weight_plate():
    w = bd.Cylinder(WEIGHT_D / 2, WEIGHT_T, align=MIN) - bd.Cylinder(WEIGHT_BORE / 2, WEIGHT_T, align=MIN)
    w = w.fillet(3.0, [e for e in w.edges().filter_by(bd.GeomType.CIRCLE) if e.radius > WEIGHT_D / 2 - 0.1])
    w.color = "#1c1d1f"
    return w


def m12_nut():
    n = bd.extrude(bd.RegularPolygon(18 / math.sqrt(3), 6), 10) - bd.Cylinder(6, 10, align=MIN)
    n.color = "#9aa3ab"
    return n


@model
def load_arm_assembly():
    x = HOLE_X[SOCKET]
    # the pin's flange underside (its z = 0) sits on the arm top; its spigot ridge starts at
    # pin z −24, the arm's socket cutter at arm z −3: turn the pin so the two helices coincide
    turn_pin = thread_turn(ARM_T - PIN_SPIGOT_L, -3.0, SOCKET_P)
    arm = load_arm().shape
    pin = bd.Pos(x, 0, ARM_T) * bd.Rot(0, 0, turn_pin) * load_pin().shape

    z_stack = ARM_T + FLANGE_T
    weights = []
    for i in range(WEIGHT_N):
        w = bd.Pos(x, 0, z_stack + i * WEIGHT_T) * weight_plate()
        w.label = "weight_plate"
        weights.append(w)
    z_plate = z_stack + WEIGHT_N * WEIGHT_T
    plate = bd.Pos(x, 0, z_plate) * clamp_plate().shape
    z_knob = z_plate + PLATE_T
    # shaft ridge: pin z 8.5 → world ARM_T + 8.5, then turned with the pin
    shaft_start = ARM_T + FLANGE_T + 0.5 - SHAFT_P * turn_pin / 360.0
    turn_knob = thread_turn(z_knob - 3.0, shaft_start, SHAFT_P)
    knob = bd.Pos(x, 0, z_knob) * bd.Rot(0, 0, turn_knob) * star_knob().shape

    pin_top = ARM_T + FLANGE_T + SHAFT_L
    rod = bd.Pos(x, 0, -14) * bd.Cylinder(6, pin_top + 14 + 14, align=MIN)
    rod.color = "#9aa3ab"
    rod.label = "m12_rod"
    nut_bot = bd.Pos(x, 0, -10) * m12_nut()
    nut_top = bd.Pos(x, 0, pin_top) * m12_nut()
    nut_bot.label = nut_top.label = "m12_nut"

    hardware = bd.Compound(children=[rod, nut_bot, nut_top], label="m12_hardware")
    plates = bd.Compound(children=weights, label="weight_plates")
    return bd.Compound(children=[arm, pin, plates, plate, knob, hardware], label="load_arm_assembly")


if __name__ == "__main__":
    load_arm_assembly()
