---
type: ledger
tags: [ledger]
---
# 實驗帳本（自動產生，請勿手改）

> 來源：`experiments/reference_log.jsonl`（講師參考，REF-）與 `experiments/log.jsonl`（學員）。
> 重建：`uv run python scripts/build_ledger.py`。CV 與 holdout 分開列：兩段期間差評率不同，PR-AUC 不可直接比較。

## CV（2018-03～05，3 個月份 fold）

| run_id | 設定 | 模型 | 特徵數 | PR-AUC | std | P@5% | Lift@5% | overfit gap | leaky | 備註 |
|---|---|---|---|---|---|---|---|---|---|---|
| REF-001-dummy | raw | dummy | 16 | 0.1574 | 0.0489 | 0.1955 | 1.2135 | -0.0060 |  | EXP-001 baseline prior |
| REF-002-raw | raw | lgbm | 16 | 0.2646 | 0.0604 | 0.3792 | 2.5076 | 0.1367 |  | EXP-002 Lab2 ablation |
| REF-002-raw+time | raw+time | lgbm | 22 | 0.2734 | 0.0515 | 0.3850 | 2.5459 | 0.1765 |  | EXP-002 Lab2 ablation |
| REF-002-raw+time+geo | raw+time+geo | lgbm | 24 | 0.2757 | 0.0523 | 0.3934 | 2.5831 | 0.1796 |  | EXP-002 Lab2 ablation |
| REF-002-raw+time+geo+product | raw+time+geo+product | lgbm | 29 | 0.2768 | 0.0514 | 0.3946 | 2.6151 | 0.1907 |  | EXP-002 Lab2 ablation |
| REF-002-all_safe | all_safe | lgbm | 33 | 0.2908 | 0.0439 | 0.4344 | 2.9251 | 0.1899 |  | EXP-002 Lab2 ablation |
| REF-003-seller_past_late | all_safe+seller_past_late | lgbm | 34 | 0.2867 | 0.0437 | 0.4173 | 2.8294 | 0.1983 |  | EXP-003 prototype |
| REF-004-leaky | raw+time+geo+product+history+leaky | lgbm | 36 | 0.5837 | 0.0960 | 0.7615 | 5.1373 | 0.1191 | ⛔ | EXP-004 deliberate leakage |
| REF-005-drop_weak | all_safe-weak | lgbm | 23 | 0.2888 | 0.0466 | 0.4232 | 2.8771 | 0.1709 |  | EXP-005 drop non-positive PI: ['purchase_month', 'is_weekend', 'n_payment_methods', 'product_weight_g', 'items_price', 'product_name_length', 'n_products', 'price_per_item', 'product_volume_cm3', 'is_multi_seller'] |
| REF-006-drop_trending | all_safe-trending | lgbm | 29 | 0.2859 | 0.0461 | 0.4104 | 2.7608 | 0.1734 |  | EXP-006 drop ['purchase_month', 'seller_prior_orders', 'seller_prior_reviews', 'customer_prior_orders'] |
| REF-007-dummy | all_safe | dummy | 33 | 0.1574 | 0.0489 | 0.1955 | 1.2135 | -0.0060 |  | EXP-007 model comparison |
| REF-007-logreg | all_safe | logreg | 33 | 0.2774 | 0.0496 | 0.4074 | 2.7356 | -0.0150 |  | EXP-007 model comparison |
| REF-007-rf | all_safe | rf | 33 | 0.2778 | 0.0508 | 0.3815 | 2.5529 | 0.3064 |  | EXP-007 model comparison |
| REF-007-lgbm | all_safe | lgbm | 33 | 0.2908 | 0.0439 | 0.4344 | 2.9251 | 0.1899 |  | EXP-007 model comparison |

## Adversarial validation（train vs holdout）

| run_id | 設定 | AUC |
|---|---|---|
| REF-006-adv-all_safe | all_safe | 0.9985 |
| REF-006-adv-all_safe-trending | all_safe-trending | 0.9828 |

## Holdout（2018-06～08，從不調參）

| run_id | 設定 | 模型 | PR-AUC | P@5% | Lift@5% | 差評率 |
|---|---|---|---|---|---|---|
| REF-008-raw | raw | lgbm | 0.1783 | 0.2897 | 2.7159 | 0.1067 |
| REF-008-all_safe | all_safe | lgbm | 0.2003 | 0.3035 | 2.8457 | 0.1067 |

## 名單容量取捨（holdout，all_safe LGBM）

| run_id | 名單比例 K | 每天筆數 | 命中率 | Lift | 涵蓋差評比例 |
|---|---|---|---|---|---|
| REF-009-k01 | 0.0100 | 2.1000 | 0.4149 | 3.8899 | 0.0389 |
| REF-009-k02 | 0.0200 | 4.2000 | 0.4096 | 3.8401 | 0.0768 |
| REF-009-k05 | 0.0500 | 10.4000 | 0.3035 | 2.8457 | 0.1422 |
| REF-009-k10 | 0.1000 | 20.9000 | 0.2469 | 2.3152 | 0.2315 |
| REF-009-k20 | 0.2000 | 41.8000 | 0.1929 | 1.8088 | 0.3618 |
