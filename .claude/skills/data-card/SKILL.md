---
name: data-card
description: M1 — 為 Olist 9 張表產出「真的跑過程式」的 Data Card（粒度、鍵、缺失、時間欄位在 T0 前後）。當學員要理解資料、建立資料字典、問欄位意思時使用。
---

# Data Card（實跑版）

源自武器庫 `data_card_prompt.md`。差別：**不准模擬**，每個數字都要來自實際執行的程式。

## 步驟

1. `from olist_course.data.load import load_tables; T = load_tables()`
2. 對每張表輸出：列數、粒度（一列代表什麼）、主鍵是否唯一、外鍵對應、缺失率 > 1% 的欄位。
3. 把所有日期欄位分類為「T0 前已知 / T0 後才知道」，對照 `config.POST_T0_COLUMNS`。
   有爭議的（例：`order_approved_at`、`shipping_limit_date`、`order_estimated_delivery_date`）寫出判斷理由。
4. 檢查 join 會不會放大列數：`items` 一單多列、`reviews` 一單可能多筆、`geolocation` 一個郵遞區號多列。
5. 產出到 `notebooks/` 中的 markdown cell 或 `docs/data_card.md`（學員自己的）。

## 輸出模板

```markdown
### Data Card：Olist
| 表 | 列數 | 粒度 | 主鍵唯一? | 與 orders 的關係 | 重要缺失 |
|---|---|---|---|---|---|

#### 時間欄位與 T0
| 欄位 | 表 | T0 時已知? | 理由 |
|---|---|---|---|

#### Join 風險
- <哪個 join 會一對多、怎麼處理（build_base 的作法）>

#### 給 EDA 的 3 個問題
1. ...
```

## 驗收

數字可由同一段程式重現；T0 分類與 `config.POST_T0_COLUMNS` 有差異時要指出來。
