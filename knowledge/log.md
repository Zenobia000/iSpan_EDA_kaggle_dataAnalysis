# 研究日誌

> **AI 每次回報分析或實驗結果時，在最下方追加一段。** 失敗、卡住、方向錯了也要寫。
> 舊的段落不改寫；寫錯了就在下面追加更正。

格式：

```
## R<輪次>-<序號> · <日期> · <這次想回答的問題>
- 做了什麼：（一句話 + 程式位置，例如 notebooks/R1-xxx.ipynb）
- 結果：（數字，附 run_id）
- 結論：支持 / 推翻 / 不確定 / 卡住
- 坑或困難：（沒有就寫「無」）
- 下一步：
```

> 本例輪次對應課程模組：R1 = M1 問題定義與基準、R2 = M2 假設驅動 EDA、R3 = M3 特徵、R4 = M4 驗證 / 消融 / 洩漏、R5 = M5 模型 / holdout / 報告。
> 分數一律來自 `experiments/reference_log.jsonl`（講師參考實驗，run_id 以 `REF-` 開頭）；PR-AUC 除特別註明外為 CV 3 個月份 fold 的平均。EDA 的描述統計沒有 run_id。

---

## R0-01 · 2026-11-06 · 專案開始：要預測什麼、何時預測、怎麼驗證
- 做了什麼：講師以 define-boundaries 定好專案邊界，寫入 `knowledge/brief.md`（T0 = `order_purchase_timestamp`、目標 `is_low_review`、時間切分 + 3 個月份 expanding CV + holdout、主指標 PR-AUC、業務指標 Precision@5% / Lift@5%）
- 結果：brief `status: approved`（講師，2026-11-06）
- 結論：可以開始建模
- 坑或困難：`order_approved_at` 看似下單當下，實際可能晚數天，決定一律不用
- 下一步：data-card

## R1-01 · 2026-11-06 · 9 張表各是什麼粒度？哪些欄位在 T0 之後才出現？
- 做了什麼：data-card 逐表盤點列數、主鍵、缺失與 T0 可得性，寫入 `knowledge/data.md`；組出 base table（`src/olist_course/data/build_base.py`、`notebooks/M1_problem_framing.ipynb`）
- 結果：base table 97,917 列（一列 = 一筆有評價的訂單）；差評率整體 14.2%、CV 驗證月 15.8%、holdout 10.7%
- 結論：支持既定定義；評價與送達欄位全部在 T0 之後
- 坑或困難：items / payments / geolocation 一單多列，直接 join 會重複加總；`customer_id` 不代表同一個人；欄位名 `lenght` 拼錯；多則評價要取最早回覆的一則
- 下一步：建立 Dummy 與 raw 基準；EDA 先驗證「遲到 → 差評」、「多賣家 → 差評」、「運費占比 → 差評」

## R1-02 · 2026-11-06 · 什麼都不做有多少分？只用原始欄位有多少分？（EXP-001）
- 做了什麼：Dummy（猜差評率）vs 只用 16 個原始欄位的 LGBM（F-001 raw 群組，`src/olist_course/features/raw.py`；經 `src/olist_course/tracking.py` 的 `run_experiment` 記錄；`notebooks/M1_problem_framing.ipynb`）
- 結果：Dummy PR-AUC 0.157、P@5% 0.196、Lift@5% 1.21（REF-001-dummy）；raw LGBM PR-AUC 0.265 ± 0.060、P@5% 0.379、Lift@5% 2.51、overfit gap 0.137（REF-002-raw）；增益 +0.107，3/3 月份進步
- 結論：支持。raw LGBM 成為後續所有特徵比較的對照組
- 坑或困難：全猜「不會差評」Accuracy 就有 85.8%，Accuracy 不能用
- 下一步：M2 假設驅動 EDA

## R2-01 · 2026-11-06 · H-001 實際遲到會導致差評嗎？
- 做了什麼：依 `is_late` 分組比差評率，再依承諾送達天數四分位分層比較（控制混雜）；`notebooks/M2_hypothesis_eda.ipynb`（EDA table 含 T0 後欄位，只用於 EDA）
- 結果：準時 88,168 筆差評率 9.2%；遲到 7,662 筆差評率 54.0%，倍數 5.9；分層後各層 5.4–6.5 倍（EDA 描述統計）
- 結論：支持（關聯，非因果）
- 坑或困難：遲到在 T0 不可得，只能找代理；競爭解釋：賣家品質差同時造成出貨慢與商品不符、偏遠地區同時造成遲到與期待落差（州層級相關有生態謬誤風險）
- 下一步：找遲到的 T0 代理：承諾天數（time 群組）、買賣雙方距離（geo 群組）、賣家過去遲到率

## R2-02 · 2026-11-06 · H-002 多賣家訂單比較容易差評嗎？
- 做了什麼：依訂單賣家數分組比較差評率；`notebooks/M2_hypothesis_eda.ipynb`
- 結果：1 個賣家 96,653 筆 13.7%；2 個 1,205 筆 46.9%；≥3 個 59 筆 64.4%（EDA 描述統計）
- 結論：支持，但多賣家只占約 1.3% 訂單，對整體排序貢獻有限
- 坑或困難：樣本少
- 下一步：特徵 `n_sellers`（raw）、`is_multi_seller`（product 群組）

## R2-03 · 2026-11-06 · H-003 運費占比越高越容易差評嗎？
- 做了什麼：運費占比五分位數比較差評率；`notebooks/M2_hypothesis_eda.ipynb`
- 結果：五個分位 14.2% / 13.7% / 13.6% / 14.8% / 14.6%，幾乎平坦、不單調（EDA 描述統計）
- 結論：推翻
- 坑或困難：無。被推翻也是成果，避免再花時間在這裡
- 下一步：product 群組中的 `freight_ratio` 預期增益小，ablation 時驗證

## R3-01 · 2026-11-06 · 加入時間群組（F-002 time）是否穩健進步？
- 做了什麼：在 raw 上加入下單時段與平台承諾天數（`purchase_hour`、`purchase_dow`、`purchase_month`、`is_weekend`、`est_delivery_days`、`shipping_limit_days`；`src/olist_course/features/time.py`），Lab2 逐步 ablation（`notebooks/M3_feature_lab.ipynb`）
- 結果：PR-AUC 0.2646 → 0.2734（REF-002-raw → REF-002-raw+time），增益 +0.009，配對 std 0.009，2/3 月份進步，robust ✗；overfit gap 0.177
- 結論：不確定。保留，但不能宣稱穩健有效
- 坑或困難：單看平均像有效，配對比較顯示有一個月份退步；`purchase_month` 帶時間趨勢
- 下一步：加 geo 群組

## R3-02 · 2026-11-06 · 加入地理群組（F-003 geo）是否穩健進步？
- 做了什麼：加入 `same_state`、`customer_seller_km`（郵遞區號前綴中心點的 haversine 距離，遲到風險的 T0 代理；`src/olist_course/features/geo.py`）
- 結果：PR-AUC 0.2734 → 0.2757（REF-002-raw+time → REF-002-raw+time+geo），逐步增益 +0.002，3/3 月份進步，robust ✓（小）
- 結論：支持，但增益小
- 坑或困難：geolocation 一個前綴多列，要先取平均
- 下一步：加 product 群組

## R3-03 · 2026-11-06 · 加入商品群組（F-004 product）是否穩健進步？
- 做了什麼：加入 `product_volume_cm3`、`product_density`、`freight_ratio`、`price_per_item`、`is_multi_seller`（`src/olist_course/features/product.py`）
- 結果：PR-AUC 0.2757 → 0.2768（REF-002-raw+time+geo → REF-002-raw+time+geo+product），逐步增益 +0.001，2/3 月份進步，robust ✗
- 結論：推翻（不穩健），與 H-003 被推翻一致
- 坑或困難：保留的理由只有「沒有傷害」，精簡時可優先移除
- 下一步：驗證 H-004，建 history 群組

## R3-04 · 2026-11-06 · H-004 賣家過去的品質能預測未來差評嗎？（F-005 history）
- 做了什麼：建立 point-in-time 的賣家 / 顧客歷史（`seller_prior_orders`、`seller_prior_reviews`、`seller_prior_low_rate`、`customer_prior_orders`；`src/olist_course/features/history.py`）。`seller_prior_low_rate` =（T0 前已回覆的該賣家差評數 + 0.15×10）/（T0 前已回覆的該賣家評價數 + 10），只計入 `review_answer_timestamp < T0`，用 `merge_asof(allow_exact_matches=False)` 實作
- 結果：PR-AUC 0.2768 → 0.2908 ± 0.044（REF-002-raw+time+geo+product → REF-002-all_safe），逐步增益 +0.014，3/3 月份進步，robust ✓，是所有群組中最大且最穩健的；all_safe P@5% 0.434、Lift@5% 2.93
- 結論：支持
- 坑或困難：若改用全部評價就成了洩漏特徵 `seller_low_rate_global`。單獨當分數時 point-in-time 版 PR-AUC 0.203、全資料版 0.293，多出來的是偷看答案（此對照未記入 reference_log，無 run_id）；新賣家沒有歷史，退回平滑先驗
- 下一步：all_safe（raw+time+geo+product+history）定為目前最佳設定

## R3-05 · 2026-11-06 · 逐步加入特徵群組，整體增益與 fold 變異怎麼解讀？（EXP-002）
- 做了什麼：彙整 R3-01～R3-04 的累計增益（相對 raw）與 fold 變異
- 結果：累計增益 +time +0.009（2/3 ✗）、+geo +0.011（3/3 ✓）、+product +0.012（3/3 ✓）、+history +0.026（配對 std 0.020，3/3 ✓）（REF-002-raw、REF-002-raw+time、REF-002-raw+time+geo、REF-002-raw+time+geo+product、REF-002-all_safe）。fold std 約 0.05，同月份配對差的 std 約 0.01；3 個驗證月差評率 22.6% / 12.9% / 11.7%，PR-AUC 約 0.35 / 0.24 / 0.24
- 結論：支持「用同月份配對比較判斷進步」；fold 間標準差主要反映月份難度，不是模型雜訊
- 坑或困難：若用「增益 > fold std」當標準，所有特徵群組都會被判無效；reference_log 沒有存 `fold_scores`，各月份數字無法從 log 重算
- 下一步：試 H-001 的 T0 代理：賣家過去遲到率

## R3-06 · 2026-11-06 · 賣家過去遲到率（F-006）能提升 all_safe 嗎？（EXP-003）
- 做了什麼：在 notebook 用 `add_features` 原型 `seller_past_late_rate` = 賣家在 T0 前**已送達**訂單中遲到的比例（只用 `order_delivered_customer_date < T0`，平滑先驗 0.08、強度 10）；`notebooks/M3_feature_lab.ipynb`
- 結果：PR-AUC 0.2908 → 0.2867（REF-002-all_safe → REF-003-seller_past_late），增益 −0.004，0/3 月份進步，robust ✗；與 `seller_prior_low_rate` Spearman 0.44
- 結論：推翻。不升級進 `src/`（冗餘）
- 坑或困難：EDA 最強的關聯（遲到 5.9 倍）不等於特徵增益，模型已從賣家歷史差評率知道大部分資訊；擾動測試一開始把所有事件都打亂，會誤判這種「只用已發生事件」的合法特徵，必須改成只把 cutoff 之後的事件往更晚移
- 下一步：M4 驗證：洩漏稽核、精簡特徵、分布偏移

## R4-01 · 2026-11-06 · 加入看似合理的配送與賣家特徵，分數翻倍是真的嗎？（EXP-004，Lab3）
- 做了什麼：刻意加入洩漏三件組 F-007（`actual_delivery_days`、`delivery_delay_days`、`seller_low_rate_global`；`src/olist_course/features/leaky.py`，`allow_leaky=True`），再跑三道防線；`notebooks/M4_validation_ablation.ipynb`
- 結果：PR-AUC 0.291 → 0.584、P@5% 0.434 → 0.762、Lift@5% 2.93 → 5.14（REF-002-all_safe → REF-004-leaky），3/3 月份進步，`robust_gain` = True
- 結論：洩漏。validation-auditor 駁回
- 坑或困難：`validate_columns`（欄位名檢查）擋不住，`robust_gain` 反而為 True，只有擾動測試（`tests/test_leakage.py`）抓得到。實際送達日在 T0 不存在；`seller_low_rate_global` 用了全部評價，含未來與本筆自己的 label
- 下一步：單次增益 > 0.05 一律先做 leakage-audit；回到 all_safe 做精簡

## R4-02 · 2026-11-06 · 拿掉 permutation importance ≤ 0 的特徵會變差嗎？（EXP-005）
- 做了什麼：all_safe 33 → 23 個特徵，移除 `purchase_month`、`is_weekend`、`n_payment_methods`、`product_weight_g`、`items_price`、`product_name_length`、`n_products`、`price_per_item`、`product_volume_cm3`、`is_multi_seller`（`src/olist_course/validation/diagnostics.py` 的 `permutation_importance`）
- 結果：PR-AUC 0.2908 → 0.2888（REF-002-all_safe → REF-005-drop_weak），−0.002，2/3 月份，robust ✗；overfit gap 0.190 → 0.171
- 結論：不確定。分數幾乎不變、模型更精簡、過擬合較低，但不構成穩健進步
- 坑或困難：無
- 下一步：檢查訓練期與上線期分布是否一致

## R4-03 · 2026-11-06 · 訓練期與上線期的特徵分布一樣嗎？（EXP-006）
- 做了什麼：adversarial validation（train vs holdout 特徵，不用 label），並試拿掉時間趨勢特徵 `purchase_month`、`seller_prior_orders`、`seller_prior_reviews`、`customer_prior_orders`；`notebooks/M4_validation_ablation.ipynb`
- 結果：all_safe adversarial AUC 0.999（REF-006-adv-all_safe）；拿掉趨勢特徵後仍 0.983（REF-006-adv-all_safe-trending），但 CV PR-AUC 0.2908 → 0.2859（REF-006-drop_trending），−0.005，0/3 月份
- 結論：支持「分布嚴重偏移」；直接拿掉趨勢特徵不可行
- 坑或困難：區分力最高的特徵是 `items_freight`、`est_delivery_days`、`shipping_limit_days`、`purchase_month`、`seller_prior_reviews`：運費、承諾天數、出貨期限本身隨時間改變，平台在變，不只是特徵設計問題
- 下一步：累積次數改近 90 天比率（待做）；上線後每月重訓、每月監控命中率

## R5-01 · 2026-11-06 · 同一組特徵下，哪個模型值得它的複雜度？（EXP-007）
- 做了什麼：固定 all_safe 特徵，比較 Dummy / LogReg / RF / LGBM（`src/olist_course/models/pipeline.py`；`notebooks/M5_model_and_report.ipynb`）
- 結果：Dummy 0.157（REF-007-dummy）；LogReg 0.277、P@5% 0.407、overfit gap −0.015（REF-007-logreg）；RF 0.278、P@5% 0.382、overfit gap 0.306（REF-007-rf）；LGBM 0.291、P@5% 0.434、Lift@5% 2.93、overfit gap 0.190（REF-007-lgbm）；LGBM 相對 LogReg +0.013，3/3 月份勝出
- 結論：支持選 LGBM；需要可解釋性時 LogReg 是合理替代（只差 0.014、幾乎不過擬合）
- 坑或困難：RF 過擬合最重
- 下一步：錯誤分析：模型抓不到哪些差評

## R5-02 · 2026-11-06 · 模型抓不到哪些差評？（錯誤分析）
- 做了什麼：用 LGBM all_safe 的 OOF 分數（REF-007-lgbm 設定），依實際送達相對預計送達日切片（`src/olist_course/validation/diagnostics.py` 的 `slice_report`；`notebooks/M5_model_and_report.ipynb`）
- 結果（切片表無獨立 run_id）：提早 10 天以上 10,703 筆差評率 9.3%、平均分數 0.153；提早 3–10 天 6,262 筆 8.9%、0.139；遲到 0–7 天 1,316 筆 37.3%、0.160；遲到 > 7 天 1,048 筆 78.4%、0.175；未送達（取消等）400 筆 77.2%、0.177。差評率差 8 倍，模型分數只差約 1.2 倍
- 結論：支持「嚴重遲到與取消造成的差評在 T0 不可約」，這是預測時點的限制，不是模型失敗
- 坑或困難：下單當下沒有可辨識的訊號；繼續優化 T0 模型的邊際效益有限
- 下一步：商業建議加出貨延誤時的第二個預測時點（T1）；提交 holdout

## R5-03 · 2026-11-06 · 從未用於調參的 2018-06～08，表現是否延續？（EXP-008）
- 做了什麼：raw 與 all_safe LGBM 各對 holdout 評估一次（`src/olist_course/submit.py`、`src/olist_course/score.py`）
- 結果：all_safe PR-AUC 0.200、ROC-AUC 0.632、P@5% 0.304、Lift@5% 2.85（REF-008-all_safe）；raw PR-AUC 0.178、ROC-AUC 0.594、P@5% 0.290、Lift@5% 2.72（REF-008-raw）；holdout 差評率 10.7%
- 結論：支持。PR-AUC 隨基準率下降（CV 驗證月差評率 11.7–22.6%），但 Lift 延續，all_safe 仍勝 raw
- 坑或困難：CV 與 holdout 的 PR-AUC 不能直接比較，跨期間比 Lift
- 下一步：名單容量取捨

## R5-04 · 2026-11-06 · 名單要多大？（容量取捨）
- 做了什麼：在 holdout 上對 all_safe LGBM 計算不同名單比例 K 的命中率、Lift 與涵蓋率
- 結果：K=1% 每天 2.1 筆、命中 41.5%、Lift 3.89、涵蓋 3.9%（REF-009-k01）；K=2% 4.2 筆、41.0%、3.84、7.7%（REF-009-k02）；K=5% 10.4 筆、30.4%、2.85、14.2%（REF-009-k05）；K=10% 20.9 筆、24.7%、2.32、23.2%（REF-009-k10）；K=20% 41.8 筆、19.3%、1.81、36.2%（REF-009-k20）。對照 CV：前 5% 命中 43.4%（整體 15.8%，REF-002-all_safe），涵蓋全部差評 13.7%（vault 記載，reference_log 無涵蓋率欄位）
- 結論：名單是「優先順序工具」而非「差評攔截器」：K=5% 約 3 成命中、是隨機的 2.8 倍，但只涵蓋約 14% 差評；名單約 7 成是誤報
- 坑或困難：選 K 取決於關懷成本與一則差評的代價，這兩個數字待營運填寫
- 下一步：round-review，交主管決定

## R5-05 · 2026-11-06 · R5 結束：決定 待主管決定
- 做了什麼：round-review，整理 findings.md 與給主管的決策事項
- 結果：目前最佳 all_safe LGBM：CV PR-AUC 0.291（REF-002-all_safe）、holdout Lift@5% 2.85（REF-008-all_safe）
- 結論：建模階段結束，停在待人類決定
- 坑或困難：關懷是否有效無法從模型證明，需要試辦 A/B 測試
- 下一步：待決：(1) 是否試辦（建議 4 週、含對照組）(2) 名單容量 K（人力少選 2%，試辦先 5%）(3) 名單給客服關懷、賣家輔導或兩者（建議兩者）(4) 是否投資出貨延誤時（T1）的第二次預測（建議是）。技術待辦：累積次數改近 90 天比率、品類層級 point-in-time 差評率、T1 模型
