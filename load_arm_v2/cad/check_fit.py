"""Fit check for the v3 rig.

1. Inside the assembly: no pair of parts overlaps, and every part on the M12 clamp path and the
   plate stack touches its neighbour (gap 0) -- a part that hangs free is a failed clamp.
2. Against the motors (CubeMars STEP files in vendor/, not committed): the arm touches only the
   rotating output, and clears the stationary housing.
"""
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
import build123d as bd
from cadgen.geometry import closest_points, overlap_volume

from arm import load_arm_ak60, load_arm_ak70
from assembly import load_arm_assembly_ak70
from params import BOSS_H, HUB_H

failures = []


def leaves(node, path=""):
    kids = list(getattr(node, "children", []) or [])
    if not kids:
        yield path, node
    seen = {}
    for k in kids:
        seen[k.label] = seen.get(k.label, 0) + 1
        yield from leaves(k, f"{path}/{k.label}.{seen[k.label]}")


kit = load_arm_assembly_ak70().shape
P = {p.split("/")[-1]: s for p, s in leaves(kit)}
print("parts:", ", ".join(P))


def pair(a, b, want_touch):
    A, B = P[a], P[b]
    ov = sum(overlap_volume(x, y) for x in A.solids() for y in B.solids())
    gap = closest_points(A, B).distance
    ok = ov < 1e-3 and (gap < 1e-3 if want_touch else True)
    print(f"{'OK ' if ok else 'BAD'} {a:22s} {b:22s} overlap {ov:8.3f} mm3  gap {gap:6.3f} mm"
          f"{'  (must touch)' if want_touch else ''}")
    if not ok:
        failures.append((a, b))


print("\n-- clamp path (must touch, no overlap)")
for a, b in [("m12_nut.1", "washer_din9021.1"), ("washer_din9021.1", "load_arm_ak70.1"),
             ("load_arm_ak70.1", "load_pin.1"), ("load_pin.1", "washer_din433.1"),
             ("washer_din433.1", "m12_nut.2")]:
    pair(a, b, True)
print("-- plate stack (must touch, no overlap)")
for a, b in [("load_pin.1", "weight_plate.1"), ("weight_plate.1", "weight_plate.2"),
             ("weight_plate.4", "clamp_plate.1"), ("clamp_plate.1", "star_knob.1"),
             ("star_knob.1", "lock_knob.1")]:
    pair(a, b, True)
print("-- threads and keys (no overlap)")
for a, b in [("load_pin.1", "star_knob.1"), ("load_pin.1", "lock_knob.1"), ("load_pin.1", "clamp_plate.1"),
             ("load_pin.1", "m12_rod.1"), ("load_arm_ak70.1", "m12_rod.1")]:
    pair(a, b, False)

# the keyed clamp plate cannot turn on the pin: rotate it 4° (free play is ~2.2°) and it must collide with the flat
cp = P["clamp_plate.1"]
c = cp.bounding_box().center()
turned = bd.Pos(c.X, c.Y, 0) * bd.Rot(0, 0, 4) * bd.Pos(-c.X, -c.Y, 0) * cp
ov = sum(overlap_volume(x, y) for x in turned.solids() for y in P["load_pin.1"].solids())
print(f"{'OK ' if ov > 0.01 else 'BAD'} clamp plate turned 4° hits the D-flat: {ov:.3f} mm3")
if ov <= 0.01:
    failures.append(("clamp_plate", "key"))

print("\n-- motors (vendor STEP)")
motors = {
    "ak70": (load_arm_ak70, ROOT / "vendor/AK70-9_KV60.step", 112,
             lambda s: bd.Pos(0, -9.5 - HUB_H - BOSS_H, 0) * bd.Rot(90, 0, 0) * bd.Rot(0, 0, 9) * s),
    "ak60": (load_arm_ak60, ROOT / "vendor/AK60-39_V3.0_KV80.step", 3,
             lambda s: bd.Pos(0, 0, 38 + HUB_H + BOSS_H) * bd.Rot(0, 0, 28) * s),
}
for name, (fn, path, output_idx, place) in motors.items():
    if not path.exists():
        print(f"skip {name}: {path} missing"); continue
    m = bd.import_step(str(path))
    parts = m.solids() or m.shells()
    arm = place(fn().shape).solids()[0]
    near = sorted((closest_points(arm, p).distance, i) for i, p in enumerate(parts))
    contact = [i for d, i in near if d < 1e-3]
    housing_gap = min(d for d, i in near if i != output_idx)
    ok = contact == [output_idx] and housing_gap >= 1.0
    print(f"{'OK ' if ok else 'BAD'} {name}: touches parts {contact} (output = {output_idx}); "
          f"nearest stationary part {housing_gap:.2f} mm")
    if not ok:
        failures.append((name, "motor"))

print("\nRESULT:", "all checks passed" if not failures else f"FAILED {failures}")
