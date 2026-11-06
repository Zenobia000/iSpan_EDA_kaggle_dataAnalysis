---
type: feature
id: F-007
status: leaky
group: leaky
columns: [actual_delivery_days, delivery_delay_days, seller_low_rate_global]
t0_safe: false
created: 2026-11-06
tags: [feature, leakage]
---
# F-007 洩漏特徵三件組 leaky

Lab3 的反面教材（`src/olist_course/features/leaky.py`）。

## 為什麼洩漏
- `actual_delivery_days` / `delivery_delay_days`：實際送達日在 T0 不存在
- `seller_low_rate_global`：用全部評價（含未來、含這筆自己的 label）

## 驗證紀錄
| 實驗 | PR-AUC | 進步月份 | robust |
|---|---|---|---|
| [[EXP-004 Lab3 刻意洩漏]] | 0.291 → 0.584 | 3/3 | ✓（假的） |

## 結論
欄位名檢查與配對穩健性都擋不住，只有擾動測試擋得住 → [[FND-005 洩漏特徵也能在每個月份穩定進步]]
