---
name: promote-to-src
description: 把 notebooks 中證明有價值的程式碼升級進 src/（分層放置、純函式化、補測試、回寫特徵卡）。當同一段邏輯第二次被用到、特徵有穩健增益要進最終模型、或結果要交付重現時使用。
---

# Promote to src

## 升級條件（任一）
1. 同一段邏輯第二次被用到
2. 會影響最終模型（特徵、清理、切分、指標）
3. 要交付、排程或重現報告數字

都不符合 → 留在 `notebooks/`，不要升級。

## 步驟
1. 讀 `src/README.md`，決定位置（data / features / validation / tracking / models）；第一次升級時建立 `src/<pkg>/` 與 `pyproject.toml`
2. 改寫成純函式：輸入 → 輸出，不修改輸入、不讀全域狀態、不寫死路徑
3. 補測試（合成小資料）：
   - 特徵 → 洩漏擾動測試 + 值域 / 方向測試
   - 驗證 / 指標 → 與 Validation Protocol 一致的邊界測試
4. 把原本的 notebook 改成 import `src/` 的函式，確認結果一致
5. 回寫 `knowledge/40_Features/F-xxx` 的 `status: in-pipeline`

## 不要做
- 預先建立「也許用得到」的框架或抽象層
- 一次升級整個 notebook；只升級符合條件的那一段
