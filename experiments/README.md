# experiments/ — 實驗紀錄（只追加）

`log.jsonl`：每次比較一行 JSON。程式由 AI 在第一次需要時寫進 `src/<pkg>/tracking.py`，**欄位合約如下**（knowledge 筆記與報告靠它追溯數字）：

| 欄位 | 必填 | 說明 |
|---|---|---|
| `run_id` | ✓ | 唯一 ID，例如 `R20261106T0325-3fa9c1` |
| `time` | ✓ | UTC ISO 時間 |
| `git` | ✓ | 當下的 commit；有未提交的修改時加 `-dirty` |
| `round` | ✓ | 輪次，例如 `R2` |
| `kind` | ✓ | `cv` / `holdout` / `diagnostic` |
| `name` | ✓ | 實驗設定名稱（特徵組合 / 模型） |
| `features` | ✓ | 完整特徵欄位清單（可重現） |
| `model`、`params`、`seed` | ✓ | 模型與參數 |
| `metric` | ✓ | 主指標名稱，與 `knowledge/brief.md` §4 一致 |
| `fold_scores` | ✓ | 每個 fold 的主指標（配對比較要用） |
| `mean`、`std` | ✓ | 主指標彙總 |
| `train_mean` | 建議 | 訓練分數，用來看過擬合 |
| `note` | 建議 | 對應的 `knowledge/log.md` 段落（例：R2-03） |

## 本專案（Olist）的實作

- 寫入程式：`src/olist_course/tracking.py` 的 `run_experiment()`，一律經由它產生要報告的分數；`round_="R3"` 指定輪次
- 除了上表的合約欄位，另外保留 `pr_auc_mean`、`p_at_k_mean`、`lift_at_k_mean`、`overfit_gap` 等課程用欄位
- `reference_log.jsonl`：講師參考跑分（run_id `REF-xxx`），`knowledge/log.md` 與 `findings.md` 的數字都對得到它；
  由 `scripts/reproduce_reference_runs.py` 產生。舊紀錄只補了能推導的合約欄位，`fold_scores` 要重跑該腳本才會有

## 規則

- 一律追加，不改寫、不刪除舊紀錄（錯的實驗也是紀錄）
- 報告與 knowledge 中的每個分數都要能對到一個 `run_id`
- **判斷進步用同 fold 配對比較**：每個 fold 都進步，且平均增益 > 增益的標準差
