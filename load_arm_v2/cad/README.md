# text-to-cad 版（build123d B-rep，可編輯 STEP）

用 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) 的 cadgen 0.8.4 引擎建模。
每個零件是一個 `@model` Python 腳本，尺寸都在 `src/params.py`。

| 資料夾 | 內容 |
|---|---|
| `STEP/` | **可編輯實體**：6 個零件（承重桿分 AK70 / AK60 兩版）+ 兩套組合件 |
| `STL/`、`3MF/` | 列印用網格（3MF 可直接拖進 Bambu Studio / PrusaSlicer） |
| `GLB/` | 組合件預覽 |
| `src/` | 模型原始碼：`arm.py`、`pin.py`、`knob.py`、`plate.py`、`assembly.py`、`exports.py` |
| `check_fit.py` | 組合干涉 + 接觸檢查，以及對兩顆馬達原廠 STEP 的干涉檢查 |

```bash
uvx --from cadgen==0.8.4 cadgen doctor        # 第一次：安裝 cadgen
# 再把 bd_warehouse（螺紋）裝進 cadgen 的 Python（cadgen doctor 印出的 python 路徑）：
uv pip install --python <cadgen 的 python 路徑> bd_warehouse
cadgen +0.8.4 run src/assembly.py             # 重建
cadgen +0.8.4 run src/exports.py              # 重寫 STEP / STL / 3MF / GLB
```

螺紋用 bd_warehouse 的 `Thread`（Tr 梯形牙，30°）。內螺紋＝加了 0.35 mm 徑向、0.15 mm 軸向間隙的
「虛擬外螺紋」減出來。組合件裡承重軸、旋鈕都已轉到和螺紋孔同相位，檢查結果無干涉。

v3 的零件清單、標準件、組裝順序與驗證結果見上一層的 `../README.md`。
STL 由 `exports.py` 以 0.01 mm 弦差另外轉出（cadgen 內建網格約 0.3 mm，太粗不適合螺紋）。
馬達原廠 STEP 放在 `vendor/`（不納入版本控制），`check_fit.py` 會讀它們做干涉檢查。
