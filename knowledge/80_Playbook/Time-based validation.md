---
type: concept
aliases: [時間切分, expanding window CV]
tags: [concept, validation]
---
# Time-based validation

## 一句話
驗證集永遠在訓練集之後；holdout 在所有驗證之後、且從不用於調參。

## 怎麼做
- train / valid / holdout 依時間切
- CV 用 expanding window：每個驗證期只用它之前的資料訓練
- 前處理（填補、編碼、縮放）在 Pipeline 內，只在訓練 fold fit

## 在專案中的實例
[[Validation Protocol]]
