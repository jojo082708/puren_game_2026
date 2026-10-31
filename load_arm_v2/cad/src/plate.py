"""壓板: Ø80×5 clamp washer between the weight plates and the knob."""
import build123d as bd
from cadgen import model

from params import PLATE_BORE, PLATE_D, PLATE_R_IN, PLATE_R_OUT, PLATE_T

MIN = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)


@model
def clamp_plate():
    body = bd.Cylinder(PLATE_D / 2, PLATE_T, align=MIN) - bd.Cylinder(PLATE_BORE / 2, PLATE_T, align=MIN)
    circles = body.edges().filter_by(bd.GeomType.CIRCLE)
    body = body.fillet(PLATE_R_OUT, [e for e in circles if e.radius > PLATE_D / 2 - 0.01])
    circles = body.edges().filter_by(bd.GeomType.CIRCLE)
    body = body.fillet(PLATE_R_IN, [e for e in circles if abs(e.radius - PLATE_BORE / 2) < 0.01])
    body.label = "clamp_plate"
    body.color = "#4f9a6a"
    return body


if __name__ == "__main__":
    clamp_plate()
