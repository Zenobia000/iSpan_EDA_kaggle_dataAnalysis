# src/ — 升級過的程式碼（長期維護）

只放**被證明有價值**的程式碼（升級條件見 `notebooks/README.md`）。結構不預先規定，由專案長出來，但要遵守下列分層：

| 子模組（需要時才建立） | 放什麼 | 介面約定 |
|---|---|---|
| `<pkg>/data/` | 讀原始資料、清理、組出「一列 = 一個預測單位」的 base table | `load_*() -> DataFrame`、`build_base(tables) -> DataFrame` |
| `<pkg>/features/` | 特徵群組，一個檔案一個群組 | `build(base, tables) -> DataFrame`：與 base 同 index、只回傳新欄位、不修改輸入 |
| `<pkg>/validation/` | 切分、CV、指標、配對比較 | 依 `knowledge/brief.md` §4 實作，**不得自行更改規則** |
| `<pkg>/tracking.py` | 實驗紀錄：寫入 `experiments/log.jsonl` | 欄位合約見 `experiments/README.md` |
| `<pkg>/models/` | Pipeline 與模型 | 前處理一律包在 Pipeline 內，只在訓練 fold 上 fit |

`<pkg>` = 專案的 Python 套件名稱，在第一次升級時建立。

## 升級的步驟（AI 依此執行）

1. 把 notebook 中的邏輯整理成純函式，放到上表對應的位置
2. 在 `tests/` 補測試；特徵一定要通過洩漏擾動測試（見 `tests/README.md`）
3. 把原 notebook 改成呼叫 `src/` 的函式
4. 在 `knowledge/log.md` 追加一段：升級了什麼、放在哪裡

## 本專案的套件：`olist_course`

| 模板分層 | 模組 | 主要介面 |
|---|---|---|
| `data/` | `data/load.py`、`data/build_base.py`、`data/dataset.py` | `load_tables()`、`build_base_table()`、`load_dataset(groups)` |
| `features/` | `raw` `time` `geo` `product` `history`（`leaky` 是故意洩漏的反例）、`registry.py` | `build(base, tables)`；`FEATURE_GROUPS` 登記群組、`FEATURE_SETS` 定義 ablation 組合 |
| `validation/` | `split.py`、`evaluate.py`、`diagnostics.py` | `assign_split()`、`time_cv_folds()`、`score_all()`、`permutation_importance()`、`adversarial_validation()`、`slice_report()` |
| `models/` | `pipeline.py` | `build_pipeline(model, numeric, categorical)`；`MODELS = dummy / logreg / rf / lgbm` |
| `tracking.py` | — | `run_experiment()`、`compare()`、`read_log()` |
| 其他 | `config.py`（T0、禁用欄位、切分日期的單一真相源）、`submit.py`、`score.py` | `make_submission()`；`score` 由講師對 holdout 計分 |

規則補充：要報告的分數一律經由 `run_experiment()` 產生，不要在 notebook 手寫訓練迴圈；判斷進步看 `compare()` 的 `folds_improved` 與 `robust_gain`。
