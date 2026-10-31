# 承重桿 v2：多力臂孔＋Tr24.5 承重軸＋星形旋鈕螺母

| 檔案 | 內容 |
|---|---|
| `load_arm_multi_hole.stl` | 承重桿：P1–P5 五個 Ø29×P3 內螺紋孔，力臂 r = 100 / 150 / 200 / 250 / 300 mm |
| `load_pin_Tr24.5x3.stl` | 承重軸：外螺紋 Tr24.5×3（槓片內徑 ≤ 26.35 可滑入），底部 Ø29×P3 鎖入桿件，中心 Ø12.5 穿 M12 |
| `star_knob_Tr24.5x3.stl` | 星形旋鈕螺母：Ø70 六瓣 × 高 24（含 Ø42 凸台），內螺紋 Tr24.5×3（含 0.35 mm/邊列印間隙），手鎖不需工具 |
| `clamp_plate_80x5.stl` | 壓板 Ø80×5，內孔 Ø25.5 |
| `load_arm_v2_drawings.pdf` | A3 圖面兩張（承重桿；承重軸、螺母、壓板與組合剖面） |
| `build_parts.py` / `make_drawings.py` | 產生上面檔案的程式（改參數後重跑） |
| `cad/` | **text-to-cad 版**：build123d B-rep 模型、可編輯 **STEP** 檔、3MF、組合件（見 `cad/README.md`） |

```bash
pip install numpy manifold3d trimesh scipy matplotlib
python3 build_parts.py && python3 make_drawings.py
```

組裝：承重軸鎖入 P1–P5 任一孔 → 穿 M12 全牙螺桿（L≈200）兩端鎖螺帽預壓 → 套槓片 → 壓板 → 星形旋鈕螺母用手鎖緊。
