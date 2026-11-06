---
name: define-boundaries
description: 專案開始時訪談人類，定義邊界：目標與決策、預測當下可用的資訊、驗證方法、停止條件，產出 knowledge/10_Brief 的四份文件並請人類核准。當專案剛開始、學員說「定義問題」「這題要預測什麼」「怎麼驗證」，或 Validation Protocol 還不是 approved 時使用。
---

# Define Boundaries（人類閘門 ①）

**你負責問與整理，人類負責決定。** 不要自行填答案再請人類「確認」——那會讓人類只是蓋章。

## 訪談順序（一次問一題，問到能填表為止）

1. **決策**：這個預測結果，**誰**會在**什麼時候**拿來做**什麼決定**？他一天能處理多少件？
2. **預測單位與目標**：一列代表什麼？目標的精確定義（門檻、時間窗）？
3. **預測時點 T0**：決策發生的那一刻是哪個事件？→ T0 由決策時點決定，不是由資料決定
4. **資訊可得性**：逐表、逐欄問「在 T0 那一刻，這個值已經**被觀察到**了嗎？」
   先畫出資料產生時間線（Data Brief §2），再填 Validation Protocol §2
5. **驗證方法**（依上線情境選，給人類建議與理由）：
   | 上線時要預測的是… | 切分 |
   |---|---|
   | 未來的事件 | 時間切分（expanding window CV + 最後一段當 holdout） |
   | 新的實體（新客戶、新病人） | 群組 K-fold |
   | 未來 h 期的序列值 | rolling-origin backtest + seasonal naive 基準 |
   | 同分布的獨立樣本（典型 Kaggle） | K-fold；官方 LB 當 holdout |
6. **指標**：跟決策一致（排名單 → PR-AUC、Precision@K；數量 → WAPE、MAE）；基準模型是什麼
7. **停止條件**：實驗上限、最小有意義增益、幾輪沒進展就停、截止日、提交門檻

## 產出

- `knowledge/10_Brief/Project Brief.md`、`Data Brief.md`、`Validation Protocol.md`、`Decision Card.md`
- 把 Validation Protocol 的 `status` 留在 `draft`，最後說：
  「請檢查 Validation Protocol，同意的話把 status 改成 approved（或告訴我由我代改並記下你的名字）。」

## 驗收
- 每一欄要嘛有內容，要嘛寫「不適用」並說明理由
- 資訊可得性表涵蓋所有原始表
- Decision Card 中「（業務填）」的欄位沒有被 AI 代填
