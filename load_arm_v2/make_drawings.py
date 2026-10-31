"""Make the A3 PDF drawing set from the STL files (run build_parts.py first)."""
import math, os
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Polygon, Rectangle
from build_parts import *

plt.rcParams["font.family"] = ["WenQuanYi Zen Hei"]
plt.rcParams["font.size"] = 8
D = os.path.dirname(os.path.abspath(__file__))
L = lambda n: trimesh.load(os.path.join(D, n))
LW, THIN = 0.9, 0.4

def section(ax, mesh, origin, normal=(0, 1, 0), axes=(0, 2), color="k", lw=LW, off=(0, 0)):
    origin = np.asarray(origin, float) + 0.05 * np.asarray(normal, float)
    for s in trimesh.intersections.mesh_plane(mesh, normal, origin):
        ax.plot(s[:, axes[0]] + off[0], s[:, axes[1]] + off[1], color=color, lw=lw, solid_capstyle="round")

def center(ax, p0, p1):
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="0.4", lw=THIN, ls=(0, (12, 3, 2, 3)))

def dim(ax, p0, p1, text, off=8, vertical=False, fs=8):
    (x0, y0), (x1, y1) = p0, p1
    kw = dict(color="k", lw=THIN)
    if not vertical:
        y = max(y0, y1) + off if off > 0 else min(y0, y1) + off
        ax.plot([x0, x0], [y0, y], **kw); ax.plot([x1, x1], [y1, y], **kw)
        ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=THIN, shrinkA=0, shrinkB=0))
        ax.text((x0 + x1) / 2, y + 1.2, text, ha="center", va="bottom", fontsize=fs)
    else:
        x = max(x0, x1) + off if off > 0 else min(x0, x1) + off
        ax.plot([x0, x], [y0, y0], **kw); ax.plot([x1, x], [y1, y1], **kw)
        ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", lw=THIN, shrinkA=0, shrinkB=0))
        ax.text(x + 1.5, (y0 + y1) / 2, text, ha="left", va="center", rotation=90, fontsize=fs)

def note(ax, xy, txt, xytext):
    ax.annotate(txt, xy, xytext, fontsize=7.5, arrowprops=dict(arrowstyle="-", lw=THIN), va="center")

def frame(fig, title, mat, scale):
    fa = fig.add_axes([0, 0, 1, 1]); fa.set_xlim(0, 420); fa.set_ylim(0, 297); fa.axis("off")
    fa.add_patch(Rectangle((10, 10), 400, 277, fill=False, lw=1.2))
    x0, y0, w = 270, 10, 140
    fa.add_patch(Rectangle((x0, y0), w, 30, fill=False, lw=1))
    fa.plot([x0, x0 + w], [y0 + 20, y0 + 20], "k", lw=.6); fa.plot([x0, x0 + w], [y0 + 10, y0 + 10], "k", lw=.6)
    fa.text(x0 + w / 2, y0 + 25, title, ha="center", va="center", fontsize=11, weight="bold")
    for i, t in enumerate([f"材料：{mat}", f"比例 {scale}", "單位 mm"]):
        fa.text(x0 + w / 6 + i * w / 3, y0 + 15, t, ha="center", va="center")
    for i, t in enumerate(["第三角法", "未註公差 ±0.3", "2026-10-31"]):
        fa.text(x0 + w / 6 + i * w / 3, y0 + 5, t, ha="center", va="center")
    return fa

def view(fig, rect, xlim, ylim, label=None):
    ax = fig.add_axes(rect); ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.axis("off")
    if label:
        ax.text((xlim[0] + xlim[1]) / 2, ylim[0] + 2, label, ha="center", va="bottom", fontsize=9, weight="bold")
    return ax

def hull_pts():
    r1, r2, d = R_MOTOR, R_LOAD, ARM_LEN
    a = math.asin((r2 - r1) / d)              # tangent-line angle
    t1 = np.linspace(math.pi / 2 + a, 3 * math.pi / 2 - a, 60)
    t2 = np.linspace(-math.pi / 2 - a, math.pi / 2 + a, 60)
    return np.vstack([np.c_[r1 * np.cos(t1), r1 * np.sin(t1)], np.c_[d + r2 * np.cos(t2), r2 * np.sin(t2)]])

def half_width(x):
    a = math.asin((R_LOAD - R_MOTOR) / ARM_LEN)
    return (R_MOTOR + (R_LOAD - R_MOTOR) * x / ARM_LEN) / math.cos(a)

pdf = PdfPages(os.path.join(D, "load_arm_v2_drawings.pdf"))

# ======================================================= page 1 : arm
fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
frame(fig, "承重桿 v2（多力臂孔，Ø29×P3 內螺紋 ×5）", "PETG", "1:1.5")
# top view
ax = view(fig, [0.04, 0.50, 0.66, 0.44], (-50, 360), (-75, 70), "俯視圖")
ax.add_patch(Polygon(hull_pts(), closed=True, fill=False, lw=LW))
center(ax, (-40, 0), (350, 0))
for k in range(6):
    t = math.radians(60 * k); c = (12.5 * math.cos(t), 12.5 * math.sin(t))
    ax.add_patch(Circle(c, 3.3 / 2, fill=False, lw=THIN)); ax.add_patch(Circle(c, 6.5 / 2, fill=False, lw=THIN))
for k in range(3):
    t = math.radians(30 + 120 * k); ax.add_patch(Circle((15 * math.cos(t), 15 * math.sin(t)), 2.25, fill=False, lw=THIN))
    t = math.radians(90 + 120 * k); ax.add_patch(Circle((14.25 * math.cos(t), 14.25 * math.sin(t)), 2.05, fill=False, lw=THIN, ls="--"))
for i, x in enumerate(HOLE_X):
    ax.add_patch(Circle((x, 0), SOCKET_D / 2, fill=False, lw=LW))
    ax.add_patch(Circle((x, 0), SOCKET_D / 2 - 1.75, fill=False, lw=THIN, ls=(0, (3, 2))))
    center(ax, (x, -20), (x, 20))
    ax.text(x, 23, f"P{i+1}", ha="center", fontsize=9, weight="bold", color="tab:red")
for i, x in enumerate(HOLE_X):
    dim(ax, (0, 0), (x, 0), f"r{i+1} = {x:.0f}", off=-(42 + 6 * i) + 0, fs=7.5)
note(ax, (HOLE_X[1] + 10, -10), "5 × 內螺紋 Ø29 × P3 右旋（梯形牙）\n貫穿 25，兩端倒角 1.5\n（與 v1 相同，舊承重軸也可直接鎖入）", (175, 50))
note(ax, (-6, -8), "馬達介面同 v1：\nAK70：6×Ø3.3 PCD25，沉頭 Ø6.5（底留 8）\nAK60：3×Ø4.5 PCD30 貫穿、3×Ø4.1 PCD28.5 深 8", (-45, 58))
ax.text(-38, 40, "R30", fontsize=7.5); ax.text(342, 35, "R40", fontsize=7.5)
# front view
ax = view(fig, [0.04, 0.24, 0.66, 0.24], (-50, 360), (-35, 45), "前視圖")
ax.add_patch(Rectangle((-R_MOTOR, 0), ARM_LEN + R_MOTOR + R_LOAD, ARM_T, fill=False, lw=LW))
ax.add_patch(Rectangle((-HUB_D / 2, -HUB_H), HUB_D, HUB_H, fill=False, lw=LW))
for x in HOLE_X:
    for s in (-1, 1):
        ax.plot([x + s * SOCKET_D / 2] * 2, [0, ARM_T], color="0.3", lw=THIN, ls=(0, (3, 2)))
    center(ax, (x, -5), (x, 30))
center(ax, (0, -15), (0, 30))
dim(ax, (-R_MOTOR, ARM_T), (ARM_LEN + R_LOAD, ARM_T), "370", off=10)
dim(ax, (ARM_LEN + R_LOAD, 0), (ARM_LEN + R_LOAD, ARM_T), "25", off=6, vertical=True)
dim(ax, (-R_MOTOR, -HUB_H), (-R_MOTOR, ARM_T), "35", off=-10, vertical=True)
dim(ax, (-HUB_D / 2, -HUB_H), (HUB_D / 2, -HUB_H), "Ø56 輪轂", off=-8)
# right view
ax = view(fig, [0.70, 0.27, 0.27, 0.22], (-60, 60), (-30, 45), "右視圖")
ax.add_patch(Rectangle((-R_LOAD, 0), 2 * R_LOAD, ARM_T, fill=False, lw=LW))
ax.add_patch(Rectangle((-HUB_D / 2, -HUB_H), HUB_D, HUB_H, fill=False, lw=LW))
dim(ax, (-R_LOAD, ARM_T), (R_LOAD, ARM_T), "80", off=8)
# hole table
ax = fig.add_axes([0.72, 0.55, 0.25, 0.36]); ax.axis("off")
rows = [["孔位", "力臂 r (mm)", "孔處桿寬", "孔邊壁厚"]]
for i, x in enumerate(HOLE_X):
    w = 2 * half_width(x); rows.append([f"P{i+1}", f"{x:.0f}", f"{w:.1f}", f"{(w - SOCKET_D) / 2:.1f}"])
t = ax.table(rows, loc="upper center", cellLoc="center"); t.scale(1, 1.6); t.set_fontsize(8.5)
ax.text(0.0, 0.35,
        "系統鑑別用法：\n"
        "・ 承重軸可鎖入 P1–P5 任一孔，力臂 r = 100–300 mm，每檔差 50。\n"
        "・ 慣量 J ≈ J_arm + m·r² + J_load,cm；固定質量 m、只改 r，\n"
        "  就能分離 m·r² 項，再用回歸求出 J_arm 與摩擦/阻尼。\n"
        "・ 重力負載 τ = m·g·r·cosθ，同樣隨 r 線性變化。\n"
        "・ 相鄰孔中心距 50，孔間殘留壁 ≈ 20 mm。\n"
        "・ 未使用的孔不影響強度計算；可加 M12 螺帽堵住防異物。",
        fontsize=8, va="top", transform=ax.transAxes)
fig.text(0.03, 0.045, "註：PETG、填充 ≥ 50%、牆 5 圈；平放列印（輪轂朝下需支撐，或翻面輪轂朝上）。螺紋請以 STL 列印檔為準（load_arm_multi_hole.stl）。", fontsize=8)
pdf.savefig(fig); plt.close(fig)

# ======================================================= page 2 : pin / nut / plate / assembly
pin, nut, plate, arm = L("load_pin_Tr24.5x3.stl"), L("hex_nut_Tr24.5x3.stl"), L("clamp_plate_80x5.stl"), L("load_arm_multi_hole.stl")
fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
frame(fig, "承重軸 Tr24.5×3 ＋ 六角螺母 ＋ 壓板", "PETG", "1:1.5")
# pin section
ax = view(fig, [0.03, 0.17, 0.25, 0.80], (-60, 60), (-50, 200), "承重軸 剖面 A-A")
section(ax, pin, (0, 0, 0))
center(ax, (0, -32), (0, 175))
top = FLANGE_T + SHAFT_L
dim(ax, (-SHAFT_D / 2, top), (SHAFT_D / 2, top), "Ø24.5（大徑）", off=8)
dim(ax, (-FLANGE_D / 2, 0), (FLANGE_D / 2, 0), "Ø80", off=-38)
dim(ax, (SHAFT_D / 2, FLANGE_T), (SHAFT_D / 2, top), "158", off=20, vertical=True)
dim(ax, (FLANGE_D / 2, 0), (FLANGE_D / 2, FLANGE_T), "8", off=4, vertical=True)
dim(ax, (SOCKET_D / 2, -PIN_SPIGOT_L), (SOCKET_D / 2, 0), "24", off=6, vertical=True)
dim(ax, (-FLANGE_D / 2, -PIN_SPIGOT_L), (-FLANGE_D / 2, top), "190", off=-8, vertical=True)
note(ax, (12, 100), "外螺紋 Tr24.5×3 右旋\n小徑 Ø21.0，牙深 1.75\n全長 158，兩端導角", (-58, 120))
note(ax, (-6, 60), "中心孔 Ø12.5 貫穿\n（M12 全牙螺桿）", (-58, 70))
note(ax, (-14, -12), "外螺紋 Ø29×P3\n長 24（鎖入承重桿）", (-58, -18))
# nut views
ax = view(fig, [0.30, 0.56, 0.22, 0.38], (-35, 35), (-38, 45), "六角螺母 俯視")
hexr = NUT_AF / 2 / math.cos(math.radians(30))
ax.add_patch(Polygon([(hexr * math.cos(math.radians(30 + 60 * k)), hexr * math.sin(math.radians(30 + 60 * k))) for k in range(6)], fill=False, lw=LW))
ax.add_patch(Circle((0, 0), NUT_AF / 2, fill=False, lw=THIN))
ax.add_patch(Circle((0, 0), (SHAFT_D + 2 * FIT) / 2, fill=False, lw=THIN, ls=(0, (3, 2))))
ax.add_patch(Circle((0, 0), (SHAFT_D - 3.5 + 2 * FIT) / 2, fill=False, lw=LW))
center(ax, (-30, 0), (30, 0)); center(ax, (0, -28), (0, 28))
dim(ax, (-NUT_AF / 2, 0), (NUT_AF / 2, 0), "對邊 41（41 mm 扳手）", off=27)
ax = view(fig, [0.30, 0.30, 0.22, 0.28], (-35, 35), (-22, 36), "六角螺母 剖面")
section(ax, nut, (0, 0, 0), normal=(0, 1, 0))
center(ax, (0, -4), (0, 24))
dim(ax, (hexr, 0), (hexr, NUT_H), "20", off=4, vertical=True)
ax.text(0, -12, "內螺紋 Tr24.5×3 右旋（含列印間隙 0.35/邊）\n兩面 30° 倒角、孔口倒角 1.0", ha="center", fontsize=7.5)
# plate
ax = view(fig, [0.30, 0.15, 0.22, 0.16], (-48, 48), (-16, 20), "壓板 Ø80×5")
ax.add_patch(Rectangle((-PLATE_D / 2, 0), (PLATE_D - PLATE_BORE) / 2, PLATE_T, fill=True, fc="0.85", ec="k", lw=LW))
ax.add_patch(Rectangle((PLATE_BORE / 2, 0), (PLATE_D - PLATE_BORE) / 2, PLATE_T, fill=True, fc="0.85", ec="k", lw=LW))
dim(ax, (-PLATE_D / 2, PLATE_T), (PLATE_D / 2, PLATE_T), "Ø80", off=8)
dim(ax, (-PLATE_BORE / 2, 0), (PLATE_BORE / 2, 0), "內孔 Ø25.5", off=-7)
# assembly section (all from STL)
ax = view(fig, [0.53, 0.18, 0.45, 0.78], (-120, 120), (-60, 210), "組合剖面（承重軸鎖在 P3，r = 200）")
xo = 200
section(ax, arm, (xo, 0, 0), color="tab:orange", off=(-xo, 0))
section(ax, pin, (0, 0, 0), color="tab:blue", off=(0, ARM_T))
z = ARM_T + FLANGE_T
for i in range(4):   # user's plates, illustrative 25 mm each, bore 26.35
    for s in (-1, 1):
        ax.add_patch(Rectangle((s * 26.35 / 2 if s > 0 else -60, z), 60 - 26.35 / 2, 25, fc="0.25", ec="k", lw=THIN))
    z += 25
zp = z
section(ax, plate, (0, 0, 0), color="tab:green", off=(0, zp))
zn = zp + PLATE_T
section(ax, nut, (0, 0, 0), color="tab:red", off=(0, zn))
rod_bot, rod_top = -10 - 12, ARM_T + FLANGE_T + SHAFT_L + 12
ax.add_patch(Rectangle((-6, rod_bot), 12, rod_top - rod_bot, fc="none", ec="0.3", lw=THIN, hatch="////"))
for zz in (-10, ARM_T + FLANGE_T + SHAFT_L):
    ax.add_patch(Rectangle((-9, zz), 18, 10, fc="0.6", ec="k", lw=THIN))
note(ax, (40, ARM_T + FLANGE_T + 50), "你的槓片 ×4（內徑 ≤ 26.35，Ø24.5 可滑入）\n圖示每片 25 厚，僅示意", (62, 150))
note(ax, (30, zp + 2.5), "壓板 Ø80×5", (62, 125))
note(ax, (20, zn + 10), "六角螺母 41AF×20：鎖緊槓片", (62, 140))
note(ax, (8, ARM_T + FLANGE_T + SHAFT_L + 5), "M12 螺帽（頂）", (40, 200))
note(ax, (8, -5), "M12 螺帽（底，桿件下方）", (30, -40))
note(ax, (-6, 80), "M12 全牙螺桿\nL ≈ 200（190 + 兩端螺帽）", (-118, 95))
note(ax, (-40, 15), "承重桿 P3 孔", (-118, 30))
fig.text(0.03, 0.035,
         "註：① 原 Tr31 版頂端沉頭孔 Ø22 已取消（Ø24.5 軸小徑僅 21，放不下）→ M12 螺帽直接壓在軸端面；\n"
         "　　　M12 螺帽對角 ≈ 20.8 < 六角螺母牙頂孔 Ø21.7，螺母可從上方通過。\n"
         "② 組裝：承重軸鎖入孔位 → 穿 M12 螺桿、兩端螺帽鎖緊（預壓）→ 套槓片 → 壓板 → 六角螺母鎖緊；需防鬆可再印一顆做雙螺帽。\n"
         "③ 列印：承重軸法蘭朝下直立、Ø29 凸柱需支撐（或軸尖朝下）；螺母平放；填充 ≥ 50%、牆 5 圈。\n"
         "　　　Ø24.5 軸牙底到中心孔壁厚約 4.25 mm，彎矩主要由 M12 鋼螺桿承受。",
         fontsize=7.6, va="bottom", linespacing=1.5)
pdf.savefig(fig); plt.close(fig)
pdf.close()
print("ok")
