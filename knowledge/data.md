# 資料說明

> 由 data-card 產生。每個數字都來自真的跑過的程式。
>
> 來源：Kaggle `olistbr/brazilian-ecommerce`（Olist 發布的真實商業資料，已匿名化）。資料集不是競賽：沒有官方 test set 與 leaderboard，holdout 由課程自行切出。
> 期間：2016-09～2018-10 下單的約 10 萬筆訂單，有效月份 2017-01～2018-08。顧客、商家、商品皆為雜湊 ID；品類與評論為葡萄牙文（有英文品類對照表）。
> 程式：`src/olist_course/data/load.py`（讀表）、`src/olist_course/data/build_base.py`（base table 與 EDA table）。

## 資料怎麼產生的（時間線）
```
顧客下單 ──► 付款核准 ──► 商家交給物流 ──► 送達顧客 ──► 寄出滿意度問卷 ──► 顧客回覆評價（目標被觀察到）
  T0        approved_at   delivered_carrier  delivered_customer  review_creation   review_answer
 (T0)      （灰色，不用）    （T0 之後）         （T0 之後）         （T0 之後）       （T0 之後）
```
問卷在送達（或預計送達日）之後才寄出，所以評價和「實際送達狀況」高度相關，但這些事在 T0 全都還沒發生。這是這份資料最重要的陷阱。

## 表
| 表 | 一列代表什麼 | 列數 | 主鍵唯一？ | 與分析單位的關係 | 預測當下不可用的欄位 |
|---|---|---|---|---|---|
| orders | 一筆訂單 | 99,441 | `order_id` 唯一 | 主表，一對一 | `order_status`、`order_approved_at`（灰色）、`order_delivered_carrier_date`、`order_delivered_customer_date` |
| order_items | 訂單中的一件商品 | 112,650 | (`order_id`, `order_item_id`) 唯一 | 一單多列（`order_item_id` 最多 21） | 無（`shipping_limit_date` 在 T0 已知） |
| order_payments | 一次付款 | 103,886 | (`order_id`, `payment_sequential`) 唯一 | 一單可多列（多種付款方式） | 無 |
| order_reviews | 一則評價 | 99,224 | (`review_id`, `order_id`) 唯一；`review_id` 只有 98,410 個 | 少數訂單有多則評價；目標來源 | 除 `order_id` 外全部：`review_id`、`review_score`、`review_comment_title`、`review_comment_message`、`review_creation_date`、`review_answer_timestamp` |
| customers | 一個「訂單客戶 ID」 | 99,441 | `customer_id` 唯一 | 一對一；真正的人是 `customer_unique_id`（96,096 個） | 無 |
| sellers | 一個商家 | 3,095 | `seller_id` 唯一 | 經 order_items 連到訂單 | 無 |
| products | 一個商品 | 32,951 | `product_id` 唯一 | 經 order_items 連到訂單 | 無 |
| geolocation | 一個郵遞區號前綴的一個座標 | 1,000,163 | 無主鍵 | 一個前綴多列（19,015 個前綴） | 無 |
| category_translation | 一個品類的葡英對照 | 71 | `product_category_name` 唯一 | 對照表 | 無 |

缺失率（非零者）：
- orders：`order_approved_at` 0.2%、`order_delivered_carrier_date` 1.8%、`order_delivered_customer_date` 3.0%
- products：`product_category_name`、`product_name_lenght`、`product_description_lenght`、`product_photos_qty` 各 1.9%
- order_reviews：`review_comment_title` 88.3%、`review_comment_message` 58.7%
- 其餘欄位 0.0%

分析單位：一筆有評價的訂單，97,917 列。目標 `is_low_review` 整體 14.2%（CV 驗證月平均 15.8%、holdout 10.7%，見 `brief.md` §4）。

## 怎麼串表
```sql
-- 一列 = 一筆有評價的訂單（對應 build_base_table）
WITH first_review AS (               -- 多則評價取最早回覆的一則
  SELECT order_id, review_score,
         ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp, review_id) AS rn
  FROM order_reviews
),
main_item AS (                       -- 主商品 / 主賣家 = order_item_id 最小者
  SELECT order_id, product_id, seller_id,
         ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_item_id) AS rn
  FROM order_items
)
SELECT o.order_id, o.order_purchase_timestamp, o.order_estimated_delivery_date,
       c.customer_unique_id, c.customer_state, s.seller_state, p.product_category_name,
       CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END AS is_low_review
FROM orders o
JOIN customers c    ON c.customer_id = o.customer_id
JOIN main_item mi   ON mi.order_id = o.order_id AND mi.rn = 1
JOIN sellers s      ON s.seller_id = mi.seller_id
JOIN products p     ON p.product_id = mi.product_id
JOIN first_review r ON r.order_id = o.order_id AND r.rn = 1;
-- 件數、金額、運費、付款：先在 order_items / order_payments 依 order_id 聚合再 join
-- 座標：geolocation 先依郵遞區號前綴取平均再 join
```

## 坑（踩過或發現的）
- 不要直接 JOIN order_items / order_payments / geolocation：一單多列，金額會重複加總、列數會爆炸
- `customer_id` 每筆訂單都不同，要找回購請用 `customer_unique_id`
- 少數訂單有多則評價 → 取最早回覆的一則（`review_answer_timestamp`，同時間再依 `review_id`）
- 有評價早於下單時間的異常紀錄（極少數）
- `product_name_lenght` / `product_description_lenght` 原始欄位名拼錯（lenght）；base table 改名為 `product_name_length` / `product_description_length`
- 評論文字中的公司 / 夥伴名稱被匿名化替換成其他名稱
- 頭尾月份（2016、2018-09 之後）樣本極少，課程只用 2017-01～2018-08
- 2018-02～03 差評率異常偏高（約 21–23%）；3 個 CV 驗證月差評率 22.6% / 12.9% / 11.7%，fold 間分數差異主要來自月份難度
- 訓練期與上線期分布差很多：運費、承諾天數、出貨期限本身隨時間改變（adversarial AUC 0.999，見 `log.md` R4-03）
- 歷史聚合要用評價**被觀察到**的時間 `review_answer_timestamp`，不是 `review_creation_date`；送達類歷史要用 `order_delivered_customer_date < T0`
- `order_approved_at` 看似下單當下，實際可能晚數天 → 灰色地帶，不用
