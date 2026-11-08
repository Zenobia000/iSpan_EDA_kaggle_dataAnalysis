---
status: approved       # draft | approved：approved 之後 AI 才能開始建模，且只有人類能改這份文件
approved_by: 講師（Olist 課程範例）
approved_at: 2026-11-06
---
# 專案定義：下單當下的差評風險預警（Olist）

> 由 define-boundaries 訪談你後產生。**你檢查後把 `status` 改成 `approved`。**
> 之後要改，由你直接改，或請 AI 在 `log.md` 寫一段「修改提案」等你決定。
>
> 本例由講師在課前定好、全班共用。程式上的單一真相源：`src/olist_course/config.py`。

情境：Olist 是巴西的電商平台整合商，中小商家在 Olist 上架、商品同步到各大 marketplace 販售，由**商家自行出貨**。顧客收到商品（或過了預計送達日）後收到滿意度問卷，給 1–5 星。差評直接影響商家與平台在 marketplace 上的排名與信任。

## §1 目標與決策
- 預測結果給誰用、拿來做什麼決定：
  - **客服主管**（先服務對象）：每天把前一天新訂單依風險排序，取前 K% 主動關懷
  - 商家經營團隊：哪些商家需要輔導（同一模型分數可彙總到賣家層級；是否這樣用待主管決定）
  - 物流團隊：哪些路線 / 承諾天數容易出事
- 他的容量限制：課程假設 **K = 5%**（`config.TOP_K_FRAC`；holdout 期間約每天 10 筆）。實際容量待業務確認
- 怎樣算成功：
  - 模型面：Precision@5% 明顯高於整體差評率；PR-AUC 高於基準，且同月份配對比較每個月都進步
  - 可信度：擾動測試通過（無洩漏）；holdout 表現與 CV 方向一致
  - 業務面（建模階段）：能用一句話對主管說「名單裡每 1000 筆有幾筆真的會差評、是隨機的幾倍」
  - 業務面（驗收階段）：試辦 A/B 測試，關懷組差評率顯著低於對照組，且效益 > 關懷成本
- 這次不做的事：
  - 在建模階段證明「主動關懷能降低差評」（要靠驗收時的 A/B 測試）
  - 出貨後、送達前的第二次預測（T1），列為下一階段
  - 評論文字的情緒分析（評論在 T0 不存在）
- 待業務確認：名單給誰、關懷做什麼、每次關懷成本、一則差評的代價、重訓負責人

## §2 預測任務
| 項目 | 內容 |
|---|---|
| 任務類型 | 二元分類（輸出風險分數，用於排序取前 K%） |
| 一列代表什麼 | 一筆**有評價**的訂單（`olist_course.data.build_base.build_base_table`；97,917 列） |
| 唯一鍵 | `order_id` |
| 目標（精確定義） | `is_low_review` = 該訂單**第一則**評價（依 `review_answer_timestamp`、`review_id` 排序）的 `review_score <= 2` |
| 預測時點（T0） | 顧客下單那一刻：`order_purchase_timestamp`（客服名單要在出貨前產生才有介入時間） |
| 時間序列才填：預測幾期、頻率 | 不適用 |

## §3 資訊可得性：預測當下能知道什麼
> 寫的是「何時**被觀察到**」，不是「何時發生」。這張表是洩漏檢查的依據。

時間線：下單（T0）→ 付款核准 `order_approved_at` → 交給物流 `order_delivered_carrier_date` → 送達 `order_delivered_customer_date` → 寄出問卷 `review_creation_date` → 顧客回覆 `review_answer_timestamp`。

| 表 / 欄位 | 什麼時候被觀察到 | 預測當下可用嗎？ |
|---|---|---|
| orders：`order_id`、`customer_id`、`order_purchase_timestamp` | T0 | 可用（ID 不直接進模型） |
| orders：`order_estimated_delivery_date` | T0（結帳頁即顯示給顧客） | 可用 |
| orders：`order_approved_at` | T0 後數分鐘到數天 | **不可用**（灰色地帶，課程一律不用） |
| orders：`order_status` | 訂單生命週期中持續更新 | **不可用** |
| orders：`order_delivered_carrier_date`、`order_delivered_customer_date` | 出貨 / 送達時 | **不可用** |
| order_items：`product_id`、`seller_id`、`price`、`freight_value`、`shipping_limit_date` | T0 | 可用（一單多列，需先聚合） |
| order_payments：`payment_type`、`payment_installments`、`payment_value` | T0 | 可用（一單多列，需先聚合） |
| order_reviews：`review_id`、`review_score`、`review_comment_title`、`review_comment_message`、`review_creation_date`、`review_answer_timestamp` | 送達（或預計送達日）後 | **不可用**（目標來源） |
| order_reviews（**其他訂單**的歷史評價） | 該評價的 `review_answer_timestamp` | 僅 `review_answer_timestamp < T0` 的評價可用於歷史聚合（嚴格小於，`merge_asof(allow_exact_matches=False)`），且排除本訂單 |
| orders（**其他訂單**的歷史送達結果） | 該訂單的 `order_delivered_customer_date` | 僅 `order_delivered_customer_date < T0` 的訂單可用 |
| customers：`customer_unique_id`、`customer_zip_code_prefix`、`customer_city`、`customer_state` | T0 | 可用（ID 不直接進模型） |
| sellers：`seller_zip_code_prefix`、`seller_city`、`seller_state` | T0 | 可用 |
| products：品類、名稱/描述長度、照片數、重量、尺寸 | T0（上架資料） | 可用 |
| geolocation：郵遞區號前綴座標 | 靜態 | 可用（需先依前綴取平均） |
| category_translation | 靜態 | 可用 |

不能當特徵的欄位：
- `config.POST_T0_COLUMNS`：`order_status`、`order_approved_at`、`order_delivered_carrier_date`、`order_delivered_customer_date`、`review_id`、`review_score`、`review_comment_title`、`review_comment_message`、`review_creation_date`、`review_answer_timestamp`
- 前綴規則 `config.FORBIDDEN_PREFIXES`：任何以 `order_delivered_` 或 `review_` 開頭的欄位
- 由上述欄位衍生的值，例如 `actual_delivery_days`、`delivery_delay_days`、用全部評價算的 `seller_low_rate_global`（`src/olist_course/features/leaky.py`，只作反面教材）
- 識別欄位不是洩漏但不進模型：`order_id`、`customer_id`、`customer_unique_id`、`main_seller_id`、`main_product_id`
- 欄位名檢查不足以防洩漏：新特徵必須通過 `tests/test_leakage.py` 的擾動測試

## §4 驗證與指標
| 項目 | 選擇與理由 |
|---|---|
| 切分方式 | 時間切分（上線時要預測的是未來的訂單）。train 2017-01～2018-02、valid 2018-03～05（左閉右開，`config.TRAIN_END` / `VALID_END`）。CV = 3 個月份 fold 的 expanding window（`CV_FOLD_MONTHS` = 2018-03 / 04 / 05），每個 fold 只用它之前的資料訓練，報告 mean ± std |
| holdout（最後才看一次的答案） | 2018-06～08（`HOLDOUT_END` = 2018-09-01），只在 M5 評估一次；label 由講師保管，`data/holdout/` 只有人類能存取 |
| 主指標 | PR-AUC（正例約 14%；全猜「不會差評」Accuracy 就有 85.8%，對決策無用）。業務指標：Precision@5% / Lift@5% |
| 基準模型 | 不學習的基準：Dummy（猜差評率）。簡單模型基準：只用原始欄位（raw 群組）的 LGBM |
| 怎樣算進步 | 同月份配對比較：`compare()` 的 `robust_gain` = 3 個月份都進步，且平均配對增益 > 配對增益的 std。穩健 ≠ 合法，另需擾動測試 |

三種差評率不要混用：14.2%（全部有評價訂單，2016-09～2018-10）、15.8%（CV 3 個驗證月平均，含 3 月異常高的 22.6%）、10.7%（holdout）。PR-AUC 隨差評率變動，**CV 與 holdout 的 PR-AUC 不能直接比較**，跨期間比 Lift。

## §5 停止條件
| 條件 | 值 |
|---|---|
| 最多跑幾輪或幾次實驗 | 5 輪，對應課程模組 M1–M5（R1 問題定義與基準 → R5 建模、holdout、報告） |
| 增益小於多少就不算進展 | 未達 `robust_gain`（任一月份退步，或平均配對增益 ≤ 配對 std）即不算進展；單次增益 > 0.05 先做 leakage-audit 再回報 |
| 截止日 | 課程 M5 結束 |
| 達到什麼就提交 | 最終設定通過擾動測試、CV 穩健勝過 raw 基準後，在 M5 對 holdout 評估一次並撰寫報告；之後由人類決定是否試辦 |

## 附錄：名詞
| 名詞 | 意思 |
|---|---|
| T0 | 預測時點 = 下單當下；只能用此刻已知的資訊 |
| 低評價 / 差評 | 第一則評價 ≤ 2 星 |
| PR-AUC | Precision-Recall 曲線下面積；類別不平衡時比 ROC-AUC 敏感 |
| Precision@5% | 分數前 5% 名單中真正差評的比例（客服名單命中率） |
| Lift@5% | Precision@5% ÷ 整體差評率 |
| 配對增益 | 同一個驗證月份內兩組設定的分數差 |
| 擾動測試 | 竄改未來資訊後，T0 之前的列特徵不得改變的測試 |
| Holdout | 2018-06～08 的最終評估資料；答案由講師保管，開發期間任何人都不能用來調整 |
| CV 差評率 vs holdout 差評率 | 15.8% vs 10.7%；PR-AUC 不可跨期間直接比較 |
| M1–M5 | 課程 5 個模組：問題定義 / EDA / 特徵工程 / 驗證 / 建模報告（對應輪次 R1–R5） |
| Lab1/2/3 | 課堂實驗：相關≠因果 / 逐步加入特徵 / 刻意洩漏 |
| run_id | 每次實驗在 `experiments/*.jsonl` 的編號；`REF-` 開頭為講師參考實驗 |
| Adversarial validation | 分辨兩個時期資料的分類器，用來量分布偏移 |
