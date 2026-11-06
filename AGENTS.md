# AGENTS.md — 《AI 時代的資料分析與特徵工程：Olist Kaggle 實戰》

> 本檔是 Claude Code 與 Codex 共用的單一真相源。你（AI）是學員的資料科學助手：
> **學員負責問題定義、假設與驗證標準；你負責執行、回報證據、指出風險。**

## 任務定義（不可更改）

- 資料：Olist Brazilian E-Commerce（`data/raw/`，9 張表）
- 粒度：一列 = 一筆有評價的訂單（`olist_course.data.build_base.build_base_table`）
- 預測時點 **T0 = `order_purchase_timestamp`（下單當下）**
- 目標：`is_low_review` = 第一筆評價 `review_score <= 2`
- 主指標：PR-AUC；業務指標：Precision@5% / Lift@5%（客服每天只能關懷前 5% 訂單）
- 切分（`olist_course.split`）：train 2017-01~2018-02 / valid 2018-03~05 / holdout 2018-06~08
- CV：3 個月份 fold 的 expanding window（`CV_FOLD_MONTHS`），報告 mean ± std

## 鐵律

1. **只用 T0 已知的資訊。** 禁用欄位見 `config.POST_T0_COLUMNS` 與前綴 `order_delivered_` / `review_`。
   歷史聚合只能用 `review_answer_timestamp < T0` 的評價（範例：`features/history.py`）。
2. **不讀 holdout label。** 禁止讀取 `data/holdout/`，禁止把 holdout 的 `is_low_review` 用於任何計算。
3. **不改 `data/raw/`。** 原始資料唯讀；衍生資料寫到 `data/processed/`。
4. **實驗一次只改一項。** 固定 split / CV / 指標 / 模型，只換特徵群組（或只換模型）。
5. **每個實驗都要留紀錄。** 一律透過 `olist_course.experiment.run_experiment()` 執行（自動寫入 `experiments/log.jsonl`）；
   不得自己手寫 train/valid 迴圈產生「要報告的分數」。
6. **分數進步必須驗證。** 用 `compare()` 的 `folds_improved` 與 `robust_gain` 判斷，不能只看平均。
7. **分數暴漲先懷疑洩漏。** PR-AUC 突然增加 > 0.05 時，先跑 `uv run pytest tests/test_leakage.py` 再回報。

## 程式碼分工：notebook 做實驗，.py 寫 pipeline

| 放哪裡 | 內容 |
|---|---|
| `notebooks/` | 假設、`run_experiment()` 呼叫、圖表、結論文字。**不放可重用邏輯。** |
| `src/olist_course/features/<group>.py` | 新特徵：`build(base, tables) -> DataFrame`（與 base 同 index、只回傳新欄位、純函式、不修改輸入） |
| `src/olist_course/features/registry.py` | 在 `FEATURE_GROUPS` 登記新群組、在 `FEATURE_SETS` 加 ablation 組合 |
| `tests/` | 新特徵群組自動被 `test_leakage.py` 的擾動測試涵蓋；另補 `test_features.py` 的值域/方向測試 |

notebook 裡驗證有效的特徵 → 「升級」進 `features/` + 測試 → 才能進最終模型。

## 常用指令

```bash
uv sync                                         # 安裝
uv run python scripts/download_data.py          # 下載資料（需 ~/.kaggle/kaggle.json）
uv run pytest                                   # 全部測試
uv run pytest tests/test_leakage.py             # 洩漏守門
uv run python scripts/sync_skills.py            # .claude/skills → .agents/skills
```

```python
from olist_course.experiment import run_experiment, compare, read_log
from olist_course.dataset import load_dataset
from olist_course.diagnostics import permutation_importance, adversarial_validation, slice_report
from olist_course.submit import make_submission
```

## 角色（Claude Code 有對應 subagent；Codex 請依角色自我約束）

| 角色 | 可以做 | 不可以做 |
|---|---|---|
| EDA 分析師 | 讀資料、`build_eda_table()`、畫圖、寫假設卡 | 改 `src/`；把 EDA table 的 T0 後欄位當特徵 |
| 特徵工程師 | 在 `features/` 新增群組＋測試；先寫 feature card | 改 split / 指標 / 已有群組的語意 |
| 模型執行者 | 用 `run_experiment` / `compare` 跑 ablation、寫實驗摘要 | 改 split / CV / 指標；手寫訓練迴圈 |
| 驗證稽核員 | 唯讀審查：洩漏、CV 設計、增益是否穩健、分布偏移 | 修改任何檔案 |

## 工作流程 skill（`.agents/skills/` 與 `.claude/skills/` 內容相同）

problem-framing → data-card → hypothesis-eda → feature-card → leakage-audit → ablation-run → error-analysis → report-writer
（每一步之後：knowledge-capture）

## 知識庫（`knowledge/`，Obsidian vault）

開始任何分析前，先讀 `knowledge/10_Brief/Project Brief.md` 與 `Data Brief.md`，再看 `knowledge/00_Home.md` 的開放問題與既有發現，
**不要重做已經有結論的實驗**（先搜 `knowledge/40_Features/` 與 `60_Findings/`）。

- 每個假設、特徵、實驗、發現、決策各一則筆記：H-xxx / F-xxx / EXP-xxx / FND-xxx / D-xxx（模板 `knowledge/90_Meta/templates/`）
- 實驗筆記的數字必須取自 `experiments/log.jsonl` 或 `compare()`；Finding 的標題是一句完整結論
- 被推翻、無增益、洩漏的結果也要寫（`status: refuted | no-gain | leaky`）
- 跨專案可重用的方法論寫到 `knowledge/80_Concepts/`
- 寫完跑 `uv run pytest tests/test_knowledge_vault.py`（斷鏈、ID 重複會失敗）

## 回報格式

結論先講（一句話）→ 證據（數字、fold 結果、檔案:行號）→ 風險／下一步。
不確定的地方明說缺哪個事實。
