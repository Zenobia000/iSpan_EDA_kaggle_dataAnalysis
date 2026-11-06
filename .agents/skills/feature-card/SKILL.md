---
name: feature-card
description: 做特徵之前先說清楚（來源問題、定義、預測當下拿得到嗎、洩漏風險、預期方向），在 notebooks 原型驗證，有穩健增益才升級。當要新增特徵、做特徵工程、或評估某個特徵能不能用時使用。
---

# Feature Card

## 1. 動手前先說清楚（寫在 `knowledge/log.md` 這一段的「做了什麼」之前，給人類確認）
- 來自哪個問題或發現
- 精確定義（分母為 0、缺失怎麼處理）
- **預測當下拿得到嗎**：每個用到的欄位，對照 `knowledge/brief.md` §3
- 洩漏風險與避免方式（歷史聚合只能用預測時點之前的事件，並排除自己）
- 預期方向；可能和哪些既有特徵重疊

## 2. 原型
在 `notebooks/` 實作成 `build(base, tables) -> DataFrame`（與 base 同 index、只回傳新欄位、不修改輸入），
再依 experiment-protocol 和「目前最佳組合」做配對比較。

## 3. 結論（追加到 `knowledge/log.md`）
- 穩健進步 → promote-to-src
- 沒有進步 → 寫明原因（和既有特徵重疊 / 不穩定 / 沒有訊號），round-review 時列為「試過但沒用的」候選
