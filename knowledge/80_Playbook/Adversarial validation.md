---
type: concept
aliases: [分布偏移檢測]
tags: [concept, drift]
---
# Adversarial validation

## 一句話
訓練一個分類器分辨「樣本來自哪個時期」；AUC ≈ 0.5 代表分布一致，越接近 1 偏移越大。

## 怎麼用結果
- 看區分力最高的特徵：是特徵設計問題（累積次數、月份）還是真實世界在變？
- 前者 → 改成比率 / 近期視窗；後者 → 監控與定期重訓

## 在專案中的實例
[[EXP-006 Adversarial validation 與時間趨勢特徵]] → [[FND-006 訓練期與上線期幾乎可完全區分]]
