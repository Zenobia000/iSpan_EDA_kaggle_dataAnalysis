---
name: error-analysis
description: M5 — 模型錯誤分析：依切片找出模型最弱的群體、檢視 Top-K 名單的誤報與漏報，提出下一輪特徵假設。當學員問「模型錯在哪」「哪些訂單抓不到」「下一步做什麼」時使用。
---

# Error Analysis

## 步驟

1. 取 OOF 預測：`r = run_experiment("all_safe")` → `r.oof`（order_id, fold, y, score）
2. 切片：`slice_report(r, eda_table, by=...)`，`eda_table = build_eda_table(load_tables_cached())`
   - 建議切片：`customer_state`、`product_category`、`order_status`、`delivery_delay_days` 分箱
   - 事後分析**可以**用 T0 後欄位（這裡是解釋錯誤，不是當特徵）
3. Top-K 檢視：取每個 fold 分數前 5%，看 FP（高分但沒差評）與 FN（差評但低分）各 20 筆的共同點
4. 每個發現寫成「錯誤 → 可能原因 → T0 可用的新特徵假設 → 預期增益」

## 輸出模板

```markdown
### 錯誤分析
- 最弱切片：<切片, n, low_rate, pr_auc>
- FN 共同點：<例：大多是最後實際遲到、但承諾天數很短的訂單 → T0 無法得知遲到，屬不可約誤差>
- FP 共同點：<...>
- 可約 vs 不可約：<哪些錯誤再多特徵也救不了，為什麼>
- 下一輪假設：H<n> → F<n>（交給 feature-card）
```

## 重點

區分**可約誤差**（缺特徵）與**不可約誤差**（T0 時資訊本來就不存在）。後者是商業結論，不是模型失敗。

## 沉澱
可約誤差 → 新的 H-xxx；不可約誤差 → 一則 Finding（例：`FND-009 嚴重遲到造成的差評在 T0 不可約`）。
