# Olist 方法手冊（Playbook）

> 從 Olist 差評預警專案帶走、可用於下一個表格類專案的方法。專案內的實例指向 `knowledge/log.md` 的段落與 `knowledge/findings.md` 的 FND 編號。

## Next competition checklist
下一場表格類比賽第一天就照做的清單。

**Day 0：還沒寫程式**
- [ ] 寫決策卡：誰用預測、何時、做什麼決定、容量多少
- [ ] 畫資料產生時間線，標出每個欄位「何時可被觀察」（見 Point-in-time correctness）
- [ ] 決定切分：時間切分？群組切分？holdout 鎖起來（見 Time-based validation）
- [ ] 選指標：跟決策一致（排序 → PR-AUC / Precision@K）

**Day 1：建立防線**
- [ ] 實驗只透過一個 `run_experiment()` 入口，自動記 run_id 與特徵清單
- [ ] 擾動測試先寫，再寫特徵（見 Perturbation test for leakage）
- [ ] 比較一律用同 fold 配對（見 Paired fold comparison）
- [ ] 跑一次 adversarial validation，先知道上線期長怎樣（見 Adversarial validation）

**每一輪**
- [ ] 先寫預期再跑（見 Hypothesis-driven EDA）
- [ ] 新特徵先看與既有特徵的相關（見 Marginal value of a feature）
- [ ] 分數暴漲先懷疑洩漏
- [ ] 改變決定的實驗才寫進 findings；失敗原因寫進「試過但沒用的」

**結案**
- [ ] 錯誤分析分清可約 / 不可約
- [ ] 商業建議不隱含因果（見 Prediction is not causation）

## Point-in-time correctness
**一句話**：每個特徵值，只能用「預測那一刻」已經發生的事件計算。

**什麼時候用**：任何歷史聚合、target encoding、rolling 統計、需要 join 事件表的特徵。

**檢查清單**
- [ ] 每個事件表都有「這件事何時被知道」的時間戳（不是何時發生，是何時**可被觀察**）
- [ ] 聚合用 `merge_asof(..., allow_exact_matches=False)` 或等價的嚴格小於
- [ ] 排除目標列自己的事件
- [ ] 平滑用的先驗是常數或只從訓練 fold 估計

**常見錯誤**
- 用事件「發生」時間而非「被觀察到」的時間（評價的建立 vs 回覆）
- 在全資料上做 target encoding 再切分

**專案實例**：F-005 history 群組（正確，log R3-04）vs F-007 洩漏三件組（錯誤，log R4-01）。

## Time-based validation
**一句話**：驗證集永遠在訓練集之後；holdout 在所有驗證之後，且從不用於調參。

**怎麼做**
- train / valid / holdout 依時間切
- CV 用 expanding window：每個驗證期只用它之前的資料訓練
- 前處理（填補、編碼、縮放）在 Pipeline 內，只在訓練 fold fit

**專案實例**：`knowledge/brief.md` §4。

## Paired fold comparison
**一句話**：比較兩組設定時，在**同一個 fold 內**相減，再看差值的分布，把各 fold 難度不同的變異消掉。

**判準（本專案）**：所有 fold 都進步，且平均差 > 差值的 std。

**常見錯誤**：用「增益 > fold std」當標準。fold 難度差異大時，所有真實改進都會被判無效（FND-004）。

**專案實例**：`olist_course.tracking.compare()`；`knowledge/brief.md` §4。

## Perturbation test for leakage
**一句話**：竄改「未來」，重算特徵；過去的列只要有任何值改變，這個特徵就偷看了未來。

**怎麼做**
1. 選一個 cutoff
2. 只竄改 cutoff **之後才被觀察到**的事件，且**只往更晚移**（事件仍留在未來）
3. 對 T0 < cutoff 的列，前後特徵必須完全相等
4. 對已知的洩漏特徵做反向測試：必須能偵測到（證明測試有效）

**常見錯誤**
- 把所有事件都打亂：「只用過去已發生事件」的合法特徵也會被誤判（本專案踩過，F-006 賣家過去遲到率，log R3-06）
- 只檢查欄位名：擋不住（FND-005）

**專案實例**：`tests/test_leakage.py`，由 Claude hook、pre-commit、pytest 三處觸發。

## Adversarial validation
**一句話**：訓練一個分類器分辨「樣本來自哪個時期」；AUC ≈ 0.5 代表分布一致，越接近 1 偏移越大。

**怎麼用結果**
- 看區分力最高的特徵：是特徵設計問題（累積次數、月份）還是真實世界在變？
- 前者 → 改成比率 / 近期視窗；後者 → 監控與定期重訓

**專案實例**：log R4-03 → FND-006。

## Hypothesis-driven EDA
**一句話**：先寫預期，再跑程式；沒有預期的圖不畫。

**怎麼做**：議題樹拆到可驗證的葉節點 → 假設卡（機制、預期、檢驗、結果、競爭解釋、T0 代理）→ 結論只能是 supported / refuted / inconclusive。

**為什麼**：AI 能在幾秒內產生 50 張圖；沒有預期，就分不出哪張圖改變了你的判斷。

**專案實例**：H-001 實際遲到導致差評（log R2-01）、H-003 運費占比（log R2-03，被推翻也是成果）。

## Marginal value of a feature
**一句話**：特徵的價值 = 它提供了**模型還不知道**的資訊，不是它和目標的單變量關聯有多強。

**怎麼判斷**
- 和既有特徵的相關（Spearman）
- 在既有特徵之上的 ablation 配對增益
- Permutation importance（打亂後掉多少）

**專案實例**：FND-003（log R3-06）。

## Prediction is not causation
**一句話**：模型能找出高風險個體，不代表介入能改變結果；介入的效果要用實驗量。

**檢查清單**
- [ ] 這個相關有沒有競爭解釋（混雜因素）？
- [ ] 分層後關聯還在嗎？
- [ ] 業務建議是否隱含了因果主張？若有 → 設計 A/B test

**專案實例**：FND-001；給主管的建議 1「關懷名單需要對照組」（`knowledge/findings.md`「給決策者」）。
