"""Shared dimensions (mm) for the load-arm v2 rig. Numbers only: no kernel objects here."""
# --- arm
ARM_LEN = 300.0             # motor centre -> farthest socket
R_MOTOR, R_LOAD = 30.0, 40.0
ARM_T = 25.0
HUB_D, HUB_H = 56.0, 10.0
HOLE_X = (100.0, 150.0, 200.0, 250.0, 300.0)    # moment arms P1..P5
ARM_R_TOP = 5.0
ARM_R_BOT = 1.5             # 2.0 would consume the 2 mm ledge between R30 end and Ø56 hub
HUB_R = 1.5

# --- threads
SOCKET_D, SOCKET_P = 29.0, 3.0      # arm <-> pin
SHAFT_D, SHAFT_P = 24.5, 3.0        # plate shaft (weight-plate bore 26.35)
FIT = 0.35                          # radial print clearance of internal threads
ENTRY_CHAMFER = 1.5

# --- pin
BORE = 12.5                          # M12 rod
PIN_SPIGOT_L = 24.0
FLANGE_D, FLANGE_T = 80.0, 8.0
SHAFT_L_V1 = 158.0
FLANGE_R = 2.5
SHAFT_FILLET = 2.0
SPIGOT_FILLET = 1.5

# --- star knob nut
KNOB_D = 70.0
KNOB_H = 18.0                        # star body
KNOB_LOBES = 6
KNOB_LOBE_R = 9.5
KNOB_CORE_R = 20.0
KNOB_VALLEY_R = 3.5
KNOB_EDGE_R_TOP, KNOB_EDGE_R_BOT = 5.0, 2.5
KNOB_HUB_D, KNOB_HUB_H = 38.0, 6.0   # boss on the clamping side
KNOB_HUB_FILLET = 2.0

# --- clamp plate
PLATE_D, PLATE_T, PLATE_BORE = 80.0, 5.0, 25.5
PLATE_R_OUT, PLATE_R_IN = 1.5, 0.8

# --- user's weight plates (reference only, not printed)
WEIGHT_D, WEIGHT_T, WEIGHT_BORE, WEIGHT_N = 190.0, 30.0, 26.35, 4

# --- motor interfaces (measured from CubeMars' STEP files, 2026-11-04)
# The output face stands only 0.5 mm proud of the stationary housing, so the arm touches the
# motor through a boss no wider than the output face; the rest of the hub clears the housing.
BOSS_H = 2.5                         # hub face -> housing gap = BOSS_H + 0.5 = 3.0 mm
MOTORS = {
    # screws: (count, PCD, start angle, clearance hole, counterbore Ø, grip = counterbore floor
    #          above the contact face); dowels: (count, PCD, start angle, Ø, depth)
    "ak70": dict(boss_d=29.0, pilot_d=19.7, pilot_h=1.5,          # output face Ø30, Ø20×2 recess
                 screws=(6, 25.0, 0.0, 3.3, 6.5, 8.0),             # 6×M3 (thread 6.7 deep) -> M3×12
                 dowels=(3, 25.0, 30.0, 3.0, 6.0)),                # motor: 3×Ø3×3 dowel holes
    "ak60": dict(boss_d=38.0, pilot_d=0.0, pilot_h=0.0,           # output face Ø39
                 screws=(3, 30.0, 30.0, 4.5, 8.0, 10.0),           # 3×M4 -> M4×(10 + thread depth)
                 dowels=(3, 28.5, 90.0, 4.0, 6.0)),                # motor: 3×Ø4×1.5 pockets
}

# --- S-level fixes
SHAFT_L = 170.0                      # +12 for the lock knob
SHAFT_FLAT = 11.0                    # D-flat on the shaft (distance from axis); keys the clamp plate
PLATE_FLAT = 11.3                    # clamp plate's D-bore flat (0.3 clearance)
LOCK_KNOB_H = 12.0                   # thin star lock knob (jam nut), no boss
# standard parts in the clamp path (steel)
WASHER_BIG = (37.0, 13.0, 3.0)       # DIN 9021 M12 under the arm: OD > socket mouth Ø32.7
WASHER_SMALL = (20.0, 13.0, 2.0)     # DIN 433 M12 on the pin top: OD < knob thread crest Ø21.7
