# text-to-cad 版（build123d B-rep，可編輯 STEP）

用 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) 的 cadgen 0.8.4 引擎建模。
每個零件是一個 `@model` Python 腳本，尺寸都在 `src/params.py`。

| 資料夾 | 內容 |
|---|---|
| `STEP/` | **可編輯實體**：4 個零件 + 組合件（Fusion 360 / SolidWorks / Onshape 直接開） |
| `STL/`、`3MF/` | 列印用網格（3MF 可直接拖進 Bambu Studio / PrusaSlicer） |
| `GLB/` | 組合件預覽 |
| `src/` | 模型原始碼：`arm.py`、`pin.py`、`knob.py`、`plate.py`、`assembly.py`、`exports.py` |
| `check_fit.py` | 組合干涉檢查（全部零件兩兩重疊體積 = 0） |

```bash
uvx --from cadgen==0.8.4 cadgen doctor        # 第一次：安裝 cadgen
# 再把 bd_warehouse（螺紋）裝進 cadgen 的 Python（cadgen doctor 印出的 python 路徑）：
uv pip install --python <cadgen 的 python 路徑> bd_warehouse
cadgen +0.8.4 run src/assembly.py             # 重建
cadgen +0.8.4 run src/exports.py              # 重寫 STEP / STL / 3MF / GLB
```

螺紋用 bd_warehouse 的 `Thread`（Tr 梯形牙，30°）。內螺紋＝加了 0.35 mm 徑向、0.15 mm 軸向間隙的
「虛擬外螺紋」減出來。組合件裡承重軸、旋鈕都已轉到和螺紋孔同相位，檢查結果無干涉。

與網格版（上一層資料夾的 STL）的差異：桿件下緣圓角 R2 → R1.5（R2 會把 R30 端和 Ø56 輪轂之間僅 2 mm 的台階吃光），
旋鈕凸台 Ø42 → Ø38（讓凸台根部 R2 內圓角不超出指槽底 Ø42.2）。
