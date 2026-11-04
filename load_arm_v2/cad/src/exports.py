"""Write the deliverables.

STEP (editable B-rep), 3MF and GLB come from cadgen's exporter. STL is tessellated here at a
0.01 mm chord tolerance: cadgen's fixed mesh tolerance (~0.25 % of the part size, ~0.3 mm on the
pin) is close to the threads' 0.35 mm print clearance.
"""
from pathlib import Path

import build123d as bd
from cadgen import export

from arm import load_arm_ak60, load_arm_ak70
from assembly import load_arm_assembly_ak60, load_arm_assembly_ak70
from knob import lock_knob, star_knob
from pin import load_pin
from plate import clamp_plate

ROOT = Path(__file__).resolve().parent.parent
STL_TOL, STL_ANGLE = 0.01, 0.1          # mm, rad

PARTS = [(load_arm_ak70, "load_arm_ak70"), (load_arm_ak60, "load_arm_ak60"),
         (load_pin, "load_pin_Tr24.5x3"), (star_knob, "star_knob_Tr24.5x3"),
         (lock_knob, "lock_knob_Tr24.5x3"), (clamp_plate, "clamp_plate_80x5_keyed")]

if __name__ == "__main__":
    (ROOT / "STL").mkdir(exist_ok=True)
    for part, name in PARTS:
        doc = part()
        export(doc, ROOT / f"STEP/{name}.step", ROOT / f"3MF/{name}.3mf")
        bd.export_stl(doc.shape, str(ROOT / f"STL/{name}.stl"), tolerance=STL_TOL, angular_tolerance=STL_ANGLE)
        print("wrote", ROOT / f"STL/{name}.stl")
    for asm, name in [(load_arm_assembly_ak70, "load_arm_assembly_ak70"),
                      (load_arm_assembly_ak60, "load_arm_assembly_ak60")]:
        export(asm(), ROOT / f"STEP/{name}.step", ROOT / f"GLB/{name}.glb")
