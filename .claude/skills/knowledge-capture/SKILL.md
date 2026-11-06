---
name: knowledge-capture
description: 把探索與實驗的結果沉澱進 Obsidian 知識庫（knowledge/）：假設卡、特徵卡、實驗筆記、發現、決策、跨專案概念，並維護雙向連結與分數演進。當一個實驗跑完、一個假設有結論、一個模組結束、或學員說「記下來」「整理筆記」「沉澱」時使用。
---

# Knowledge Capture

Kaggle 是「探索 → 收斂 → 發現新特徵 → 拉高分數」的迴圈。**沒有寫下來的發現，下一輪就會重做一次。**

## 知識鏈（每則筆記都要往前、往後各連一個）

```
H-xxx 假設 → F-xxx 特徵 → EXP-xxx 實驗 → FND-xxx 發現 → D-xxx 決定
                                            └→ 80_Concepts（跨專案方法論）
```

## 什麼時候寫哪一種

| 事件 | 寫到 | 模板 |
|---|---|---|
| 想到一個可驗證的猜測 | `knowledge/30_Hypotheses/H-xxx <標題>.md` | Hypothesis |
| 決定做一個特徵 | `knowledge/40_Features/F-xxx <名稱>.md` | Feature |
| 跑完一次 `run_experiment` / `compare` | `knowledge/50_Experiments/EXP-xxx <標題>.md` | Experiment |
| 實驗告訴你一件「下次還會用到」的事 | `knowledge/60_Findings/FND-xxx <一句完整結論>.md` | Finding |
| 做了有取捨的設計選擇 | `knowledge/70_Decisions/D-xxx <標題>.md` | Decision |
| 發現可以帶去下一場比賽的方法 | `knowledge/80_Concepts/<英文名>.md` | Concept |
| 還沒想清楚 | `knowledge/00_Inbox/` | — |

模板在 `knowledge/90_Meta/templates/`。編號：同類最大號 + 1。

## 規則

1. **數字必須可追溯**：實驗筆記的 frontmatter 填 `git`、`pr_auc`、`gain_vs_base`、`folds_improved`、`robust`，取自 `experiments/log.jsonl` 或 `compare()` 輸出；不准估計
2. **Finding 標題就是結論**：「賣家歷史差評率是最穩健的增益來源」✓；「關於賣家的觀察」✗
3. **被推翻的也要寫**：`status: refuted` / `no-gain` / `leaky` 是成果，避免下一輪重踩
4. **狀態要回寫**：實驗結束後更新對應 F-xxx 的 `status` 與驗證紀錄表、H-xxx 的 `status`
5. **更新 `knowledge/00_Home.md`**：分數演進表加一列；最重要的發現與開放問題視情況更新
6. **Concept 不寫專案細節**：寫成下一場比賽也用得到的樣子，專案實例只放連結
7. 連結用 `[[檔名]]`（不含 .md）；寫完執行 `uv run pytest tests/test_knowledge_vault.py` 確認沒有斷鏈

## 模組結束時的沉澱清單

- [ ] 本模組的假設都有結論（supported / refuted / inconclusive）
- [ ] 每個實驗都有 EXP 筆記且連到它測的特徵
- [ ] 至少 1 則 Finding；檢查是否有可提升為 Concept 的方法論
- [ ] `00_Home` 的分數演進與開放問題已更新
