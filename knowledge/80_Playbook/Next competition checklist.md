---
type: concept
aliases: [下一場比賽檢查清單]
tags: [concept, playbook]
---
# Next competition checklist

> 從這個專案帶走、下一場表格類比賽第一天就照做的清單。

## Day 0：還沒寫程式
- [ ] 寫 Decision Card：誰用預測、何時、做什麼決定、容量多少
- [ ] 畫資料產生時間線，標出每個欄位「何時可被觀察」→ [[Point-in-time correctness]]
- [ ] 決定切分：時間切分？群組切分？holdout 鎖起來 → [[Time-based validation]]
- [ ] 選指標：跟決策一致（排序 → PR-AUC / Precision@K）

## Day 1：建立防線
- [ ] 實驗只透過一個 `run_experiment()` 入口，自動記 run_id 與特徵清單
- [ ] 擾動測試先寫，再寫特徵 → [[Perturbation test for leakage]]
- [ ] 比較一律用同 fold 配對 → [[Paired fold comparison]]
- [ ] 跑一次 adversarial validation，先知道上線期長怎樣 → [[Adversarial validation]]

## 每一輪
- [ ] 先寫預期再跑 → [[Hypothesis-driven EDA]]
- [ ] 新特徵先看與既有特徵的相關 → [[Marginal value of a feature]]
- [ ] 分數暴漲先懷疑洩漏
- [ ] 改變決定的實驗才寫筆記；失敗原因寫進 `fail_reason`

## 結案
- [ ] 錯誤分析分清可約 / 不可約
- [ ] 商業建議不隱含因果 → [[Prediction is not causation]]

## 在本專案中的實例
- 
