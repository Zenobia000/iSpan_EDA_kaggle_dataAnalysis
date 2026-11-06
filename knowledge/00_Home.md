---
type: moc
tags: [moc]
---
# 🏠 Olist 差評預警 — 知識地圖

> 新成員先讀：[[Project Brief]] → [[Data Brief]] → [[Glossary]]

## 知識是怎麼長出來的（Kaggle 迭代迴圈）

```
問題(Brief) → 假設(H) → 特徵(F) → 實驗(EXP) → 發現(FND) → 決定(D)
                 ↑                                  │
                 └────────── 新假設 ←───────────────┘
                              發現中可跨專案的 → 概念(Concepts)
```

| 資料夾 | 放什麼 | 何時寫 | 模板 |
|---|---|---|---|
| `00_Inbox` | 還沒整理的觀察、AI 對話摘錄 | 隨時 | — |
| `10_Brief` | 情境、資料說明、名詞 | 拿到資料前 | — |
| `20_Data` | 每張表一頁（自動 + 人寫筆記） | M1 | `scripts/build_data_notes.py` |
| `30_Hypotheses` | 假設卡 H-xxx | M2 起 | Hypothesis |
| `40_Features` | 特徵卡 F-xxx（含 status） | M3 起 | Feature |
| `50_Experiments` | 一次 run_experiment 比較 = 一則 | 每次實驗 | Experiment |
| `60_Findings` | 一則一個結論，標題就是結論 | 實驗後 | Finding |
| `70_Decisions` | 為什麼這樣設計（可被推翻） | 有取捨時 | Decision |
| `80_Concepts` | **跨專案**方法論 —— 下一場比賽直接帶走 | 模組結束時 | Concept |

## 分數演進
| 實驗 | 設定 | CV PR-AUC | 判定 |
|---|---|---|---|
| [[EXP-001 Baseline Dummy vs raw LGBM]] | Dummy → raw | 0.157 → 0.265 | baseline |
| [[EXP-002 Lab2 逐步加入特徵群組]] | → all_safe | 0.291 | ✓ robust |
| [[EXP-003 原型 賣家過去遲到率]] | + 過去遲到率 | 0.287 | ✗ 不升級 |
| [[EXP-004 Lab3 刻意洩漏]] | + leaky | 0.584 | ⛔ 洩漏 |
| [[EXP-007 模型比較]] | LGBM vs LogReg/RF | 0.291 | ✓ |
| [[EXP-008 Holdout 提交]] | holdout | 0.200（Lift 2.85） | 上線估計 |

## 目前最重要的發現
- [[FND-002 賣家歷史差評率是最穩健的增益來源]]
- [[FND-003 EDA 的強關聯不等於特徵增益]]
- [[FND-005 洩漏特徵也能在每個月份穩定進步]]
- [[FND-009 嚴重遲到造成的差評在 T0 不可約]]

## 開放問題（下一輪假設的來源）
- 累積次數改成近 90 天比率，能否降低偏移又保留增益？（[[FND-006 訓練期與上線期幾乎可完全區分]]）
- 品類層級的 point-in-time 差評率有沒有邊際價值？
- T1（出貨延誤時）模型能把名單命中率提高多少？

## 動態清單（需安裝社群外掛 Dataview；未安裝時顯示為程式碼區塊）

```dataview
TABLE status, group, t0_safe AS "T0 safe", hypothesis
FROM "40_Features"
SORT id ASC
```

```dataview
TABLE pr_auc AS "PR-AUC", gain_vs_base AS "增益", folds_improved AS "進步月份", robust
FROM "50_Experiments"
SORT id ASC
```

```dataview
TABLE status
FROM "30_Hypotheses"
SORT id ASC
```
