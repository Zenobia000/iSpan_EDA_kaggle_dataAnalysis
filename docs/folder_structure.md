# 資料夾結構：Olist 範例 vs 模板骨架

`main` 分支是**空模板**（資料夾分層 + 說明文件 + agents/skills）；本分支 `course/olist` 是把這套骨架**填滿之後**的第一個實例。
本文件逐一對照：模板規定這個資料夾放什麼 → Olist 實際放了什麼 → 兩者有哪些差異。

> 模板各資料夾的原始規定：`git show main:<資料夾>/README.md`（例如 `git show main:src/README.md`）。

## 總覽

```
.
├── AGENTS.md / CLAUDE.md   AI 工作規範（Olist 版：任務定義、T0、禁用欄位寫死在這裡）
├── .claude/  .agents/      skills、subagents、hooks（.agents/ 由 scripts/sync_skills.py 產生）
├── data/                   raw/ 唯讀、processed/ 建模資料、holdout/ 只有人類能碰
├── knowledge/              Obsidian 知識庫：brief → 資料 → 假設 → 特徵 → 實驗 → 發現
├── notebooks/              M1–M5 學員版；solutions/ 講師解答
├── src/olist_course/       升級過的 pipeline（資料、切分、特徵群組、模型、評估、實驗紀錄）
├── tests/                  洩漏擾動測試 + pipeline / hooks / 教材同步測試
├── experiments/            log.jsonl 實驗紀錄（reference_log.jsonl 為講師參考跑分）
├── submissions/            最終提交檔
├── scripts/                下載資料、切 holdout、產生 notebook、同步 skill、產生帳本
├── docs/                   課綱、講師手冊、Labs、範例報告、本文件
└── skeleton/               空模板的早期副本（新版模板以 main 分支為準）
```

## 逐資料夾對照

| 資料夾 | 模板（main）規定 | Olist 實際內容 | 差異 |
|---|---|---|---|
| `data/` | `raw/` `external/` `interim/` `processed/` `holdout/` | `raw/`（Kaggle 9 張表）、`processed/`、`holdout/`（2018-06~08，由 `scripts/make_holdout.py` 切出） | 沒用到 `external/`、`interim/` |
| `knowledge/` | 4 份文件：`brief.md` `data.md` `log.md` `findings.md` | 編號資料夾的 Obsidian vault（見下表） | 範例拆得比模板細；概念一一對應 |
| `notebooks/` | 拋棄式探索，`<輪次>-<主題>.ipynb` | 依課程模組 `M1`–`M5` 命名的教材；`solutions/` 為解答 | 這裡是**教材**，不是拋棄式；由 `scripts/notebook_src/m*.py` 產生，不要直接手改 |
| `src/` | `<pkg>/data` `features` `validation` `models` `tracking.py` | `src/olist_course/`（見下表） | 驗證與模型沒有拆子資料夾，以單檔放在套件根目錄 |
| `tests/` | 至少要有洩漏擾動測試 | `test_leakage.py`（擾動測試，`features/leaky.py` 是故意洩漏的反例）＋ features / split / pipeline / submit / hooks / 教材同步測試 | 多了教材一致性測試（notebooks、skills、knowledge vault） |
| `experiments/` | `log.jsonl` 只追加 | `log.jsonl`（`run_experiment()` 自動寫入）、`reference_log.jsonl` | 帳本 `knowledge/50_Runs/ledger.md` 由 `scripts/build_ledger.py` 從紀錄產生 |
| `submissions/` | 只交一份最終預測檔 | 由 `olist_course.submit.make_submission()` 產生；講師用 `olist_course.score` 評分 | — |
| `reports/` | 給決策者的報告與圖 | **沒有這個資料夾**；範例報告在 `docs/sample_report.md` | 課程把報告當教材放在 `docs/` |
| `scripts/` | （模板沒有） | 下載、切 holdout、產生 notebook、同步 skill、產生帳本、重現參考跑分 | 課程維護用 |
| `docs/` | （模板沒有） | `syllabus.md`、`instructor_guide.md`、`labs/`、`sample_report.md` | 課程教材 |

### `knowledge/`：模板 4 份文件 ↔ Olist vault

| 模板文件 | Olist 對應位置 | 內容 |
|---|---|---|
| `brief.md` | `10_Brief/` | `Project Brief`、`Data Brief`、`Validation Protocol`、`Decision Card`、`Glossary` |
| `data.md` | `20_Data/` | 每張原始表一頁（orders、items、reviews、sellers…） |
| `log.md` | `30_Hypotheses/`、`40_Features/`、`50_Runs/` | 假設卡 H-xxx、特徵卡 F-xxx、實驗筆記 EXP-xxx 與 `ledger.md` |
| `findings.md` | `60_Findings/`、`00_Home.md` | 結論 FND-xxx；`00_Home.md` 為現況（Now / Next） |
| （模板沒有） | `80_Playbook/` | 跨專案可重用的方法（時間切分、配對比較、擾動測試…） |
| （模板沒有） | `90_Meta/templates/` | 各類筆記的範本 |

### `src/olist_course/`：模板分層 ↔ Olist 模組

| 模板分層 | Olist 模組 |
|---|---|
| `<pkg>/data/` | `data/load.py`（讀 9 張表）、`data/build_base.py`（一列 = 一筆有評價的訂單）、`dataset.py` |
| `<pkg>/features/` | `features/raw.py` `time.py` `geo.py` `product.py` `history.py`、`leaky.py`（反例）、`registry.py`（群組登記與 ablation 組合） |
| `<pkg>/validation/` | `split.py`（時間切分與 CV fold）、`evaluate.py`（PR-AUC、Precision@5%）、`diagnostics.py`（permutation importance、adversarial validation、切片） |
| `<pkg>/models/` | `pipeline.py` |
| `<pkg>/tracking.py` | `experiment.py`（`run_experiment()`、`compare()`、`read_log()`） |
| （其他） | `config.py`（T0、禁用欄位、日期範圍）、`submit.py`、`score.py` |
