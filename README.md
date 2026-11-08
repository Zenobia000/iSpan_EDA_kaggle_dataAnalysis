# Olist Kaggle 實戰：資料科學模板的第一個實例

15 小時課程｜Claude Code ✕ Codex 雙相容｜notebook 做實驗、`.py` 寫 pipeline

> 讓 AI 執行重複工作，讓人類制定驗證標準，用可靠實驗決定成敗。

**任務**：在顧客**下單當下**，預測這筆 Olist 訂單會不會拿到 1–2 星差評，讓客服每天主動關懷風險最高的 5%。
完整定義見 [`knowledge/brief.md`](knowledge/brief.md)（已核准），課綱見 [`docs/olist/syllabus.md`](docs/olist/syllabus.md)。

## 這個分支和 `main` 的關係

`main` 是**空模板**：資料夾分層、說明文件、知識文件模板、agents/skills/hooks。
這個分支（`course/olist`）= `main` 模板 + 照模板流程長出來的 Olist 內容。AI 規範（`AGENTS.md`、`.claude/`、`.agents/`）與 `main` 完全相同，
專案專屬的規則（T0、禁用欄位、切分日期）都寫在 `knowledge/brief.md`。

```bash
git diff --stat main..course/olist   # 只會看到「長出來的內容」
```

每個模板資料夾裝了什麼，見 [`docs/olist/folder_structure.md`](docs/olist/folder_structure.md)。

## 快速開始

```bash
# 1. 安裝（需要 Python 3.10+ 與 uv）
uv sync
source .venv/bin/activate   # hooks 與 pre-commit 用 python3 執行測試，需要這個環境

# 2. 下載資料（需要 ~/.kaggle/kaggle.json：Kaggle → Settings → API → Create New Token）
python scripts/download_data.py

# 3. 確認環境
pytest

# 4.（選用）安裝 pre-commit 防線
pre-commit install

# 5. 開始上課
jupyter lab notebooks/M1_problem_framing.ipynb
```

接著在 repo 根目錄（同一個已啟用環境的終端機）開啟 `claude` 或 `codex`，AI 會自動讀到 `AGENTS.md`。

## 課程地圖

| 模組 | 時數 | 核心問題 | Notebook | Skill | 知識文件 |
|---|---|---|---|---|---|
| M1 | 2h | 下單那一秒，我們知道什麼？ | `M1_problem_framing` | define-boundaries、data-card | `brief.md`、`data.md` |
| M2 | 3h | 相關性代表因果嗎？ | `M2_hypothesis_eda` | hypothesis-eda | `log.md` R2 |
| M3 | 4h | 增加特徵一定更好嗎？ | `M3_feature_lab` | feature-card、leakage-audit、promote-to-src | `log.md` R3 |
| M4 | 3h | 分數變高，模型真的變好了嗎？ | `M4_validation_ablation` | experiment-protocol、leakage-audit | `log.md` R4 |
| M5 | 3h | AI Only vs Human Guided vs Validated AI | `M5_model_and_report` | error-analysis、report-writer、round-review | `findings.md`、`reports/report.md` |

每一輪（模組）結束都說「round-review」，由人類決定留哪些發現、下一輪做什麼。

## 三道洩漏防線

| 防線 | 作用範圍 | 擋得住 `features/leaky.py` 嗎？ |
|---|---|---|
| `validate_columns()` 欄位名檢查 | 所有工具 | ✗（欄位名合法） |
| `compare()` 配對穩健性 | 所有工具 | ✗（每個 fold 都「進步」） |
| `tests/test_leakage.py` 擾動測試 | 所有工具（pytest / pre-commit / Claude hook） | ✓ |

## 講師

- 講師手冊：[`docs/olist/instructor_guide.md`](docs/olist/instructor_guide.md)
- 範例成果報告（M5 解答，課前不要發給學員）：[`reports/report.md`](reports/report.md)
- 改 notebook：編輯 `scripts/notebook_src/m*.py`，再執行 `python scripts/build_notebooks.py`
- 改 skill：先改 `main` 的模板，再合併進這個分支，維持兩邊規範一致
- 重跑參考實驗：`python scripts/reproduce_reference_runs.py`（需要原始資料與 holdout）

## 前作

本課程延伸自 [python-DA-vibe-coding-fundamentals](https://github.com/sunnyDataScience/python-DA-vibe-coding-fundamentals) 的「分析師 Prompt 武器庫」。差別在於這次的 prompt 變成了 skill，角色變成了 subagent，口頭規範則變成 hook 與測試。
