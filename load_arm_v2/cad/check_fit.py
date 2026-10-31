"""Fit check: no part of the assembly interferes, and the stack rests where it should."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from cadgen.geometry import closest_points, overlap_volume
from assembly import load_arm_assembly

kit = load_arm_assembly().shape
parts = {}
def walk(node, path=""):
    kids = list(getattr(node, "children", []) or [])
    if not kids:
        parts[path] = node
    for i, k in enumerate(kids):
        walk(k, f"{path}/{k.label or i}#{i}")
walk(kit)
print({k: round(v.volume) for k, v in parts.items()})
P = {k.split("/")[-1].split("#")[0] + ("" if "weight" not in k else k[-1]): v for k, v in parts.items()}
pairs = [("load_arm", "load_pin"), ("load_pin", "star_knob"), ("load_pin", "clamp_plate"),
         ("load_pin", "weight_plate0"), ("weight_plate0", "weight_plate1"), ("weight_plate3", "clamp_plate"),
         ("clamp_plate", "star_knob"), ("load_pin", "m12_rod")]
for a, b in pairs:
    A, B = P[a], P[b]
    ov = sum(overlap_volume(sa, sb) for sa in A.solids() for sb in B.solids())
    d = closest_points(A, B).distance
    print(f"{a:16s} {b:16s} overlap {ov:8.3f} mm3   gap {d:6.3f} mm")
