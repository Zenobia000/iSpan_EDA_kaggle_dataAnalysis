---
type: brief
tags: [brief, data]
source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
---
# Data Brief：Olist Brazilian E-Commerce 是什麼資料

> 讀完這頁，你應該知道：資料**怎麼產生的**、**一列代表什麼**、**哪些欄位在下單當下還不存在**。
> 情境與決策見 [[Project Brief]]。

## 1. 來源與性質

- 發布者：Olist（Kaggle `olistbr/brazilian-ecommerce`），真實商業資料、已匿名化
- 期間：2016-09 ~ 2018-10 下單的約 10 萬筆訂單（有效月份：2017-01 ~ 2018-08）
- 性質：**資料集，不是競賽** → 沒有官方 test set 與 leaderboard；本課程自行切出 holdout
- 匿名化：顧客、商家、商品都是雜湊 ID；評論文字中的公司/夥伴名稱被替換成其他名稱
- 語言：品類名稱與評論為葡萄牙文（有英文品類對照表）

## 2. 資料是怎麼產生的（data generating process）

```
顧客下單 ──► 付款核准 ──► 商家交給物流 ──► 送達顧客 ──► 寄出滿意度問卷 ──► 顧客回覆評價
  T0        approved_at   delivered_carrier  delivered_customer  review_creation   review_answer
```

**理解這條時間線，就理解了這份資料最重要的陷阱**：問卷在送達（或預計送達日）之後才寄出，
所以評價和「實際送達狀況」高度相關 —— 但這些事在 T0 全都還沒發生。

## 3. 九張表

| 表 | 一列代表 | 列數（約） | 與訂單的關係 | 詳細 |
|---|---|---|---|---|
| orders | 一筆訂單 | 99k | 主表 | [[orders]] |
| order_items | 訂單中的一件商品 | 113k | 一單多列 | [[items]] |
| order_payments | 一次付款 | 104k | 一單可多種付款 | [[payments]] |
| order_reviews | 一則評價 | 99k | 少數訂單有多則 | [[reviews]] |
| customers | 一個「訂單客戶 ID」 | 99k | 一對一；`customer_unique_id` 才是真正的人 | [[customers]] |
| sellers | 一個商家 | 3k | 經 items 連到訂單 | [[sellers]] |
| products | 一個商品 | 33k | 經 items 連到訂單 | [[products]] |
| geolocation | 一個郵遞區號前綴的一個座標 | 1M | 一個前綴多列 | [[geolocation]] |
| category_translation | 品類葡→英 | 71 | 對照表 | [[category_translation]] |

（各表的欄位、缺失率、T0 分類由 `scripts/build_data_notes.py` 從實際資料產生。）

## 4. 分析單位與目標

- 分析單位：**一筆有評價的訂單**（97,917 筆）
- 目標 `is_low_review`：該訂單**第一則**評價 ≤ 2 星；整體約 14.2%
  （CV 驗證月 15.8%、holdout 10.7% —— 三個數字的差別見 [[Validation Protocol]] §5）

## 5. 欄位在 T0 是否可得（最重要的一張表）

| 已知（可當特徵） | 灰色地帶（課程不用） | T0 之後（只能用於 EDA） |
|---|---|---|
| 下單時間、預計送達日、出貨期限、商品屬性、價格運費、付款方式與期數、顧客/商家地區 | `order_approved_at`（可能晚數天） | 實際出貨/送達日、訂單狀態、所有評價欄位 |

規則實作在 `src/olist_course/config.py` 的 `POST_T0_COLUMNS`。概念見 [[Point-in-time correctness]]。

## 6. 表格怎麼串（SQL 寫法，給新成員）

```sql
-- 一列 = 一筆有評價的訂單（對應 build_base_table）
WITH first_review AS (
  SELECT order_id, review_score,
         ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp, review_id) AS rn
  FROM order_reviews
),
main_item AS (                       -- 主商品/主賣家 = order_item_id 最小者
  SELECT order_id, product_id, seller_id,
         ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_item_id) AS rn
  FROM order_items
)
SELECT o.order_id, o.order_purchase_timestamp, o.order_estimated_delivery_date,
       c.customer_unique_id, c.customer_state, s.seller_state, p.product_category_name,
       CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END AS is_low_review
FROM orders o
JOIN customers c   ON c.customer_id = o.customer_id
JOIN main_item mi  ON mi.order_id = o.order_id AND mi.rn = 1
JOIN sellers s     ON s.seller_id = mi.seller_id
JOIN products p    ON p.product_id = mi.product_id
JOIN first_review r ON r.order_id = o.order_id AND r.rn = 1;
-- ⚠️ 不要直接 JOIN order_items / order_payments / geolocation：一單多列，金額會重複加總
```

## 7. 已知的資料怪癖

- `customer_id` 每筆訂單都不同，要找回購請用 `customer_unique_id`
- 少數訂單有多則評價 → 取最早回覆的一則
- 有評價早於下單時間的異常紀錄（極少數）
- `product_name_lenght` / `product_description_lenght` 原始欄位名拼錯（lenght）
- geolocation 一個郵遞區號前綴對應很多座標，直接 join 會讓列數爆炸 → 先取平均

## 8. 讀完之後

先寫 [[Project Brief]] 的問題定義書（problem-framing skill），再開始 [[00_Home|探索]]。
