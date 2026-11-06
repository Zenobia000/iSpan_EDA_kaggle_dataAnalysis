---
type: brief
tags: [brief, validation]
---
# Validation Protocol：這個專案「怎樣算進步」的規則

> 由講師在課前定好、全班共用的技術規則（原 D-001～D-004）。學員不需要另外寫決策筆記；
> 要挑戰規則，在 `00_Inbox` 寫提案並在課堂討論。程式實作：`src/olist_course/config.py`、`split.py`、`experiment.py`。

## 1. 預測時點 T0 = 下單當下（`order_purchase_timestamp`）
- 決策時點決定預測時點：客服名單要在出貨前產生才有介入時間
- `order_approved_at` 可能晚數天 → 灰色地帶，不用
- 越晚預測越準（[[FND-009 嚴重遲到造成的差評在 T0 不可約]]），但介入時間越少 → 需要時另建 T1 模型，不改 T0

## 2. 指標：PR-AUC（主）＋ Precision@5% / Lift@5%（業務）
- 正例約 14%；全猜「不會差評」Accuracy 就有 85.8%，對決策無用
- 決策是「從排序最前面取 K%」→ 看排序品質與名單命中率；K 由 [[Decision Card]] 決定（預設 5%）

## 3. 切分：時間切分 + 3 個月份 expanding CV + 從不調參的 holdout
| 區段 | 期間 | 用途 |
|---|---|---|
| train | 2017-01～2018-02 | 訓練 |
| valid（CV 3 個 fold） | 2018-03 / 04 / 05 | 比較設定、選特徵 |
| holdout | 2018-06～08 | 只在最後評估一次；label 由講師保管 |
概念：[[Time-based validation]]

## 4. 進步的判準：同月份配對增益
- `compare()` 的 `robust_gain` = 每個月份都進步，且平均配對增益 > 配對增益的 std
- 理由：[[FND-004 fold 間標準差主要反映月份難度]]；概念：[[Paired fold comparison]]
- 穩健 ≠ 合法 → 另需擾動測試（[[FND-005 洩漏特徵也能在每個月份穩定進步]]）

## 5. 三種差評率，不要混用
| 數字 | 範圍 | 用在哪 |
|---|---|---|
| 14.2% | 全部有評價訂單（2016-09～2018-10） | [[Data Brief]] 的整體描述 |
| 15.8% | CV 3 個驗證月的平均（2018-03～05，含 3 月異常高的 22.6%） | CV 的 Lift 分母 |
| 10.7% | holdout（2018-06～08） | 上線估計的 Lift 分母 |
PR-AUC 會隨差評率高低變動，**CV 與 holdout 的 PR-AUC 不能直接比較**；跨期間比 Lift。
