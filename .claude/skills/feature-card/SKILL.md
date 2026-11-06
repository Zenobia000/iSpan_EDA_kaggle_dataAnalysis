---
name: feature-card
description: 設計特徵前先寫特徵卡（來源假設、定義、T0 可得性、洩漏風險、預期方向），在 notebooks 原型驗證，有穩健增益才升級。當要新增特徵、做特徵工程、或評估某個特徵能不能用時使用。
---

# Feature Card

## 1. 先寫卡（沒有卡不寫程式）
`knowledge/40_Features/F-xxx <群組名>.md`（一個特徵群組一張卡），必填：
- 來源假設 `H-xxx`
- 精確定義（分母為 0、缺失怎麼處理）
- **T0 可得性**：每個用到的欄位為什麼在預測當下已被觀察到
- 洩漏風險與避免方式（歷史聚合只能用 `< T0` 的事件，並排除自己）
- 預期方向
- `redundant_with`：和既有特徵可能重疊的地方

## 2. 原型
在 `notebooks/` 實作成 `build(base, tables) -> DataFrame`（與 base 同 index、只回傳新欄位、不修改輸入），
再依 experiment-protocol 和「目前最佳組合」做配對比較。

## 3. 結論
- robust 增益 → promote-to-src
- 沒有增益 → `status: no-gain`，填 `fail_reason`（redundant / unstable / no-signal）——**失敗也要可檢索**
