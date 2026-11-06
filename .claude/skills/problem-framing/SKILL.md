---
name: problem-framing
description: M1 — 把模糊的商業需求轉成可驗證的預測任務（分析問題定義書）。當學員說「我想知道為什麼差評多」「要預測什麼」「這題怎麼定義」或開始新專案時使用。
---

# 問題定義書（Problem Framing）

源自分析師武器庫「階段一：問題定義」，升級為**預測任務**版本。

## 做法

1. 先問學員一題：「這個預測結果，誰會在什麼時候拿來做什麼決定？」— 答案決定 T0 與指標。
2. 依下列模板產出定義書，每一欄都要能對應到 `src/olist_course/config.py` 的設定或說明為何不同。
3. 列出 3 個「看起來有用但 T0 時不存在」的欄位，作為洩漏警示（至少包含實際送達日）。

## 輸出模板

```markdown
### 分析問題定義書
1. 決策情境：<誰、何時、用預測做什麼，例：客服每天開工前，挑出前 5% 高風險訂單主動關懷>
2. 預測時點 T0：<order_purchase_timestamp — 為什麼不是出貨或送達時>
3. 分析單位：<一列 = 一筆訂單；多筆評價取第一筆>
4. 目標變數：<is_low_review = review_score <= 2；正例比例約 14%>
5. 評估指標：主 PR-AUC（類別不平衡）；業務 Precision@5% / Lift@5%；為什麼不用 Accuracy
6. 驗證設計：時間切分 + 月份 CV；為什麼不能隨機切分
7. 基準模型：Dummy（=正例比例）與 raw LGBM 的分數（跑 run_experiment 取得）
8. T0 不可得欄位（洩漏警示）：<至少 3 個，附理由>
9. 初步假設：<2–3 個，交給 hypothesis-eda>
```

## 驗收

- T0、指標、切分三項與 `config.py` 一致，或寫明刻意不同的理由
- 有 Dummy 與 raw 兩個 baseline 數字（`run_experiment("raw", model="dummy")`、`run_experiment("raw")`）
