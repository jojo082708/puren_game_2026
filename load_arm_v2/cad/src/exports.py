"""Write the deliverables: STEP (editable B-rep), STL / 3MF (print), GLB (assembly preview)."""
from pathlib import Path

from cadgen import export

from arm import load_arm
from assembly import load_arm_assembly
from knob import star_knob
from pin import load_pin
from plate import clamp_plate

ROOT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    for part, name in [(load_arm, "load_arm_multi_hole"), (load_pin, "load_pin_Tr24.5x3"),
                       (star_knob, "star_knob_Tr24.5x3"), (clamp_plate, "clamp_plate_80x5")]:
        export(part(), ROOT / f"STEP/{name}.step", ROOT / f"STL/{name}.stl", ROOT / f"3MF/{name}.3mf")
    export(load_arm_assembly(), ROOT / "STEP/load_arm_assembly.step", ROOT / "GLB/load_arm_assembly.glb")
