"""承重軸: Tr24.5×3 plate shaft on an Ø80 flange, Ø29×P3 spigot screws into the arm, Ø12.5 M12 bore.

The shaft carries a D-flat over its threads: it keys the clamp plate, so the plates' alternating
torque goes into the pin through friction on keyed faces and never turns the knobs.
"""
import build123d as bd
from cadgen import model

from params import (BORE, FLANGE_D, FLANGE_R, FLANGE_T, PIN_SPIGOT_L, SHAFT_D, SHAFT_FILLET,
                    SHAFT_FLAT, SHAFT_L, SHAFT_P, SOCKET_D, SOCKET_P, SPIGOT_FILLET)
from threads import external_thread, tr_dims

MIN = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)


def pin_body():
    r_shaft = SHAFT_D / 2 - tr_dims(SHAFT_D, SHAFT_P)[0]      # thread root radius 10.5
    r_spig = SOCKET_D / 2 - tr_dims(SOCKET_D, SOCKET_P)[0]    # 12.75
    flange = bd.Cylinder(FLANGE_D / 2, FLANGE_T, align=MIN)
    flange = flange.fillet(FLANGE_R, flange.edges())          # both outer edges
    shaft = bd.Pos(0, 0, FLANGE_T - 1) * bd.Cylinder(r_shaft, SHAFT_L + 1, align=MIN)
    spigot = bd.Pos(0, 0, -PIN_SPIGOT_L) * bd.Cylinder(r_spig, PIN_SPIGOT_L + 1, align=MIN)
    body = flange + shaft + spigot

    # concave root fillets where shaft and spigot leave the flange faces
    root_top = body.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, FLANGE_T - 0.01, FLANGE_T + 0.01)
    root_top = [e for e in root_top if abs(e.radius - r_shaft) < 0.01]
    body = body.fillet(SHAFT_FILLET, root_top)
    root_bot = body.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, -0.01, 0.01)
    root_bot = [e for e in root_bot if abs(e.radius - r_spig) < 0.01]
    body = body.fillet(SPIGOT_FILLET, root_bot)

    # 45° lead-in on the core ends, then the thread ridges (chamfered/faded ends)
    top = body.edges().filter_by(bd.GeomType.CIRCLE).group_by(bd.Axis.Z)[-1]
    body = body.chamfer(1.0, None, top)
    bot = body.edges().filter_by(bd.GeomType.CIRCLE).group_by(bd.Axis.Z)[0]
    body = body.chamfer(1.0, None, bot)
    body = body + external_thread(SHAFT_D, SHAFT_P, SHAFT_L - 0.5, FLANGE_T + 0.5, ends=("fade", "chamfer"))
    body = body + external_thread(SOCKET_D, SOCKET_P, PIN_SPIGOT_L - 0.5, -PIN_SPIGOT_L, ends=("chamfer", "fade"))

    total = PIN_SPIGOT_L + FLANGE_T + SHAFT_L
    z_flat = FLANGE_T + SHAFT_FILLET + 1.0          # flat starts just above the root fillet
    flat = bd.Pos(SHAFT_FLAT, -SHAFT_D, z_flat) * bd.Box(SHAFT_D, 2 * SHAFT_D, SHAFT_L, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN))
    body = body - [bd.Pos(0, 0, -PIN_SPIGOT_L - 1) * bd.Cylinder(BORE / 2, total + 2, align=MIN), flat]
    return body


@model
def load_pin():
    body = pin_body()
    bb = body.bounding_box()
    assert abs(bb.size.Z - (PIN_SPIGOT_L + FLANGE_T + SHAFT_L)) < 0.01, bb.size
    assert abs(bb.size.X - FLANGE_D) < 0.01, bb.size
    assert len(body.solids()) == 1, len(body.solids())
    body.label = "load_pin"
    body.color = "#b8915a"
    return body


if __name__ == "__main__":
    load_pin()
