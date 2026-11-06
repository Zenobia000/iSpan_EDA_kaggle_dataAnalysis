---
type: brief
tags: [brief]
---
# Glossary

| 名詞 | 意思 | 相關 |
|---|---|---|
| T0 | 預測時點 = 下單當下；只能用此刻已知的資訊 | [[Validation Protocol]] |
| 低評價 / 差評 | 第一則評價 ≤ 2 星 | [[Data Brief]] |
| PR-AUC | Precision-Recall 曲線下面積；類別不平衡時比 ROC-AUC 敏感 | [[Validation Protocol]] |
| Precision@5% | 分數前 5% 名單中真正差評的比例（客服名單命中率） | |
| Lift@5% | Precision@5% ÷ 整體差評率 | |
| 配對增益 | 同一個驗證月份內兩組設定的分數差 | [[Paired fold comparison]] |
| 擾動測試 | 竄改未來資訊後特徵不得改變的測試 | [[Perturbation test for leakage]] |
| Holdout | 2018-06~08 的最終評估資料；正確答案由講師保管，模型開發期間任何人都不能用來調整 | [[Time-based validation]] |
| CV 差評率 vs holdout 差評率 | 15.8% vs 10.7%：不同期間的差評率，PR-AUC 不可跨期間直接比較 | [[Validation Protocol]] |
| M1–M5 | 課程的 5 個模組：問題定義 / EDA / 特徵工程 / 驗證 / 建模報告 | `docs/syllabus.md` |
| Lab1/2/3/ABC | 課堂實驗：相關≠因果 / 增加特徵 / 洩漏 / AI 協作對照 | `docs/labs/` |
| run_id | 每次實驗在 `experiments/*.jsonl` 的編號；REF- 開頭為講師參考實驗 | [[ledger]] |
| Adversarial validation | 分辨兩個時期資料的分類器，用來量分布偏移 | [[Adversarial validation]] |
