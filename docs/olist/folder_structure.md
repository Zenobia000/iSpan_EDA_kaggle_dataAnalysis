# 資料夾結構：`main` 模板 → Olist 實例

`main` 規定了每個資料夾放什麼（各資料夾的 `README.md`）；這個分支照那些規定把 Olist 課程填進去。
下表逐一對照，「Olist 額外」一欄是模板沒有、課程才需要的東西。

> 模板原文：`git show main:<資料夾>/README.md`；兩邊差異：`git diff --stat main..course/olist`。

## 總覽

```
.
├── AGENTS.md  CLAUDE.md     與 main 相同（通用規範）
├── .claude/  .agents/       與 main 相同（skills、subagents、hooks）
├── knowledge/               4 份文件，已填入 Olist 內容；brief.md 已核准
├── data/                    raw/ 9 張 Kaggle 表；holdout/ 由講師切出
├── notebooks/               M1–M5 課程教材 + solutions/
├── src/olist_course/        照模板分層：data/ features/ validation/ models/ tracking.py
├── tests/                   洩漏擾動測試 + pipeline / hooks / 教材同步測試
├── experiments/             log.jsonl（學員）、reference_log.jsonl（講師參考跑分）
├── reports/report.md        範例成果報告（M5 解答）
├── submissions/             最終提交檔
├── scripts/                 Olist 額外：下載、切 holdout、產生 notebook、重跑參考實驗
└── docs/                    main 的教科書與落地手冊 + Olist 額外的 docs/olist/
```

## 逐資料夾對照

| 資料夾 | 模板規定 | Olist 填了什麼 | Olist 額外 |
|---|---|---|---|
| `knowledge/` | `brief.md` `data.md` `log.md` `findings.md` | 任務定義與 T0 規則、9 張表的 data card、R1–R5 的研究日誌、9 條發現 | — |
| `data/` | `raw/` `external/` `interim/` `processed/` `holdout/` | `raw/` 9 張表、`holdout/` 2018-06~08；來源登記在 `data/README.md` | 沒用到 `external/`、`interim/` |
| `notebooks/` | 拋棄式探索，升級條件 | `M1`–`M5` 與 `solutions/` | 這些是教材，由 `scripts/notebook_src/` 產生 |
| `src/` | `<pkg>/data` `features` `validation` `models` `tracking.py` | `olist_course/` 依此分層（細節見 `src/README.md`） | `config.py`、`submit.py`、`score.py` |
| `tests/` | 洩漏擾動測試 | `test_leakage.py`（含故意洩漏的反例 `features/leaky.py`）、features、split、pipeline、submit | `test_hooks.py`、`test_notebooks_in_sync.py`、`test_skills_in_sync.py` |
| `experiments/` | `log.jsonl` 欄位合約 | `run_experiment()` 依合約寫入，另保留課程用欄位 | `reference_log.jsonl` |
| `reports/` | `report.md` + `figures/` | `report.md` = 範例成果報告 | — |
| `submissions/` | 只交一份 | `make_submission()` 產生，講師用 `olist_course.score` 計分 | — |
| `scripts/` | （模板沒有） | — | 下載資料、切 holdout、產生 notebook、同步 skill、重跑參考實驗 |
| `docs/` | 教科書 `textbook/`、落地手冊 `practice/`、投影片與網站 | 原封不動 | `docs/olist/`：課綱、講師手冊、Labs、playbook、本文件 |

## `src/olist_course/` 分層

| 模板分層 | 模組 |
|---|---|
| `data/` | `load.py`（讀 9 張表）、`build_base.py`（一列 = 一筆有評價的訂單）、`dataset.py` |
| `features/` | `raw` `time` `geo` `product` `history`、`leaky`（反例）、`registry.py` |
| `validation/` | `split.py`（時間切分、CV fold）、`evaluate.py`（PR-AUC、Precision@5%）、`diagnostics.py` |
| `models/` | `pipeline.py` |
| `tracking.py` | `run_experiment()`、`compare()`、`read_log()` |

## 從舊版 `course/olist` 搬過來時改了什麼

| 舊版 | 現在 |
|---|---|
| `knowledge/` Obsidian vault（Brief / Data / H / F / EXP / FND / Playbook） | 收斂成 4 份文件；Playbook 移到 `docs/olist/playbook.md` |
| `olist_course.split` / `evaluate` / `diagnostics` | `olist_course.validation.*` |
| `olist_course.pipeline` | `olist_course.models.pipeline` |
| `olist_course.experiment` | `olist_course.tracking` |
| `olist_course.dataset` | `olist_course.data.dataset` |
| skill：problem-framing、ablation-run | define-boundaries、experiment-protocol（另有 promote-to-src、round-review） |
| subagent：eda-analyst、feature-engineer、model-runner、validation-auditor | eda-agent、feature-agent、model-agent、validation-agent |
| `docs/syllabus.md`、`instructor_guide.md`、`labs/` | `docs/olist/` |
| `docs/sample_report.md` | `reports/report.md` |
| `skeleton/` | 刪除（模板以 `main` 為準） |

舊版完整保留在 tag `olist-course-v1`。
