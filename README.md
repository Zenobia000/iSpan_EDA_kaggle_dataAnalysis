# AI 時代的資料分析與特徵工程：Olist Kaggle 實戰

15 小時課程｜Claude Code ✕ Codex 雙相容｜notebook 做實驗、`.py` 寫 pipeline

> 讓 AI 執行重複工作，讓人類制定驗證標準，用可靠實驗決定成敗。

**任務**：在顧客**下單當下**，預測這筆 Olist 訂單會不會拿到 1–2 星差評，讓客服每天主動關懷風險最高的 5%。
完整課綱見 [`docs/syllabus.md`](docs/syllabus.md)。

## 快速開始

```bash
# 1. 安裝（需要 Python 3.10+ 與 uv）
uv sync

# 2. 下載資料（需要 ~/.kaggle/kaggle.json：Kaggle → Settings → API → Create New Token）
uv run python scripts/download_data.py

# 3. 確認環境
uv run pytest

# 4.（選用）安裝 pre-commit 防線
uv run pre-commit install

# 5. 開始上課
uv run jupyter lab notebooks/M1_problem_framing.ipynb
```

接著在 repo 根目錄開啟 `claude` 或 `codex`，AI 會自動讀到課程規則（`AGENTS.md`）。

## 為什麼在本地寫，不在 Kaggle Notebook 上寫？

- Olist 是 Kaggle **資料集**，不是競賽，所以沒有官方 submission。計分在本地進行：講師用 holdout 期間的 label 跑 `olist_course.score`。
- AI agent（Claude Code / Codex）需要本地檔案系統、測試與 hook 才能發揮作用。
- 可重用邏輯放在 `src/olist_course/` 並附測試；Kaggle Notebook 無法直接 import 本地套件。

## 專案結構

```
AGENTS.md                 # 課程鐵律（Claude Code 與 Codex 共用的單一真相源）
CLAUDE.md                 # @AGENTS.md + Claude 專屬說明（subagents / hooks）
.claude/
  skills/                 # 8 個工作流程 skill（源頭）
  agents/                 # eda-analyst / feature-engineer / model-runner / validation-auditor
  hooks/                  # 擋寫原始資料、擋讀 holdout、改 src 後自動跑洩漏測試
  settings.json
.agents/skills/           # 給 Codex 的 skill（由 scripts/sync_skills.py 複製，勿手改）
src/olist_course/         # pipeline：資料、切分、特徵群組、模型、評估、實驗紀錄
tests/                    # 含洩漏擾動測試 test_leakage.py
notebooks/                # 學員版 M1–M5（solutions/ 為講師解答）
scripts/                  # 下載、holdout、skill 同步、notebook 產生器
docs/                     # 課綱、講師手冊、4 份 Lab
experiments/log.jsonl     # 每次 run_experiment 自動寫入
```

## 課程地圖

| 模組 | 時數 | 核心問題 | Notebook | Skill |
|---|---|---|---|---|
| M1 | 2h | 下單那一秒，我們知道什麼？ | `M1_problem_framing` | problem-framing、data-card |
| M2 | 3h | 相關性代表因果嗎？ | `M2_hypothesis_eda` | hypothesis-eda |
| M3 | 4h | 增加特徵一定更好嗎？ | `M3_feature_lab` | feature-card、leakage-audit |
| M4 | 3h | 分數變高，模型真的變好了嗎？ | `M4_validation_ablation` | ablation-run、leakage-audit |
| M5 | 3h | AI Only vs Human Guided vs Validated AI | `M5_model_and_report` | error-analysis、report-writer |

## 三道洩漏防線

| 防線 | 作用範圍 | 擋得住 `features/leaky.py` 嗎？ |
|---|---|---|
| `validate_columns()` 欄位名檢查 | 所有工具 | ✗（欄位名合法） |
| `compare()` 配對穩健性 | 所有工具 | ✗（每個 fold 都「進步」） |
| `tests/test_leakage.py` 擾動測試 | 所有工具（pytest / pre-commit / Claude hook） | ✓ |

## 講師

見 [`docs/instructor_guide.md`](docs/instructor_guide.md)；範例成果報告（M5 解答）見 [`docs/sample_report.md`](docs/sample_report.md)。修改教材的流程：
- 改 notebook：編輯 `scripts/notebook_src/m*.py`，再執行 `uv run python scripts/build_notebooks.py`
- 改 skill：編輯 `.claude/skills/`，再執行 `uv run python scripts/sync_skills.py`

## 前作

本課程延伸自 [python-DA-vibe-coding-fundamentals](https://github.com/sunnyDataScience/python-DA-vibe-coding-fundamentals) 的「分析師 Prompt 武器庫」。差別在於這次的 prompt 變成了 skill，角色變成了 subagent，口頭規範則變成 hook 與測試。
