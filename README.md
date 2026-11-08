# Olist Kaggle 實戰：資料科學模板的第一個實例

15 小時課程｜Claude Code ✕ Codex 雙相容｜notebook 做實驗、`.py` 寫 pipeline

> 讓 AI 執行重複工作，讓人類制定驗證標準，用可靠實驗決定成敗。

**任務**：在顧客**下單當下**，預測這筆 Olist 訂單會不會拿到 1–2 星差評，讓客服每天主動關懷風險最高的 5%。
完整定義見 [`knowledge/brief.md`](knowledge/brief.md)（已核准），課綱見 [`docs/olist/syllabus.md`](docs/olist/syllabus.md)。

## 第一次來？先看資料導覽

[**Olist 資料導覽**](docs/olist/data_intro.html)：給初學者的互動網頁，5 分鐘看懂資料內容與任務目標。

- 訂單從下單到評價的時間線，以及最重要的規則：只能用下單當下（T0）已知的資訊
- 九張表的關係圖，點任一張表看它是什麼、能不能用
- 哪些欄位可以用、資料怎麼依時間切分、動手前要知道的坑

怎麼打開：clone 之後用瀏覽器開 `docs/olist/data_intro.html`；或不用下載，直接看[線上預覽](https://htmlpreview.github.io/?https://github.com/Zenobia000/iSpan_EDA_kaggle_dataAnalysis/blob/course/olist/docs/olist/data_intro.html)（GitHub 本身只會顯示 HTML 原始碼）。
文字版細節在 [`knowledge/data.md`](knowledge/data.md)（資料）與 [`knowledge/brief.md`](knowledge/brief.md)（任務）。

## 這個分支和 `main` 的關係

`main` 是**空模板**：資料夾分層、說明文件、知識文件模板、agents/skills/hooks。
這個分支（`course/olist`）= `main` 模板 + 照模板流程長出來的 Olist 內容。AI 規範（`AGENTS.md`、`.claude/`、`.agents/`）與 `main` 完全相同，
專案專屬的規則（T0、禁用欄位、切分日期）都寫在 `knowledge/brief.md`。

```bash
git diff --stat main..course/olist   # 只會看到「長出來的內容」
```

每個模板資料夾裝了什麼，見 [`docs/olist/folder_structure.md`](docs/olist/folder_structure.md)。

## 快速開始

還沒看過的話，先看上面的[資料導覽](docs/olist/data_intro.html)。

### 0. 事前準備

| 需要 | 檢查指令 | 沒有的話 |
|---|---|---|
| Python 3.10 以上 | `python3 --version` | 到 python.org 安裝，或用 pyenv |
| uv（套件管理） | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh`（Windows 見 uv 官方文件） |
| git | `git --version` | 到 git-scm.com 安裝 |
| Kaggle 帳號 | — | 到 kaggle.com 免費註冊 |

### 1. 取得程式碼

```bash
git clone https://github.com/Zenobia000/iSpan_EDA_kaggle_dataAnalysis.git
cd iSpan_EDA_kaggle_dataAnalysis
git switch course/olist        # Olist 課程在這個分支；main 是空模板
```

### 2. 安裝套件

```bash
uv sync                        # 依 uv.lock 建立 .venv 並安裝所有套件
source .venv/bin/activate      # Windows：.venv\Scripts\activate
```

之後的指令都在**已啟用環境**的終端機執行。Claude Code 的 hook 與 pre-commit 會用這個環境的 `python3` 跑測試，沒啟用就會失敗。

### 3. 設定 Kaggle API 金鑰

1. 登入 Kaggle → 右上角頭像 → **Settings** → **API** → **Create New Token**，畫面會顯示一串 `KGAT_` 開頭的 token（只顯示一次，先複製起來）
2. 把它存到固定位置（把 `KGAT_xxx` 換成你的 token）：

```bash
mkdir -p ~/.kaggle && chmod 700 ~/.kaggle
printf '%s' 'KGAT_xxx' > ~/.kaggle/access_token
chmod 600 ~/.kaggle/access_token   # 只有自己能讀
```

3. 確認認證成功（會列出 9 個 CSV 檔名）：

```bash
kaggle datasets files olistbr/brazilian-ecommerce
```

Windows 存成 `C:\Users\<你的帳號>\.kaggle\access_token`（純文字、只有 token 一行）。不想存檔也可以每次開終端機設環境變數：`export KAGGLE_API_TOKEN=KGAT_xxx`（PowerShell：`$env:KAGGLE_API_TOKEN="KGAT_xxx"`）。

**舊帳號已經有 `kaggle.json`？** 放在 `~/.kaggle/kaggle.json` 並 `chmod 600` 也能用，不必換。

token 等同你的密碼：**不要提交到 git、不要貼到聊天室或給 AI 看**。外流了就回 Kaggle Settings → API 撤銷，再產生新的。

### 4. 下載資料

```bash
python scripts/download_data.py
```

腳本會從 Kaggle 下載 [olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)，解壓到 `data/raw/`，並檢查 9 個 CSV 是否齊全。已經下載過會直接跳過。成功時印出 `[ok] 已下載到 .../data/raw`。

| 錯誤訊息 | 原因與處理 |
|---|---|
| `Kaggle 認證失敗` | `~/.kaggle/access_token`（或 `kaggle.json`）不存在、路徑錯或 token 已撤銷，回到步驟 3 |
| `請先 uv sync 安裝 kaggle 套件` | 沒啟用環境或沒跑 `uv sync`，回到步驟 2 |
| `下載後仍缺：[...]` | 下載中斷，刪掉 `data/raw/` 裡的檔案重跑 |

**沒辦法用 API 時（例如公司網路擋住）**：到上面的 Kaggle 頁面按 **Download** 取得 zip，把裡面 9 個 CSV 解壓到 `data/raw/`，再跑一次腳本確認齊全。

`data/raw/` 是唯讀的原始資料：不要修改、不要提交（`.gitignore` 已排除）。

### 5. 確認環境

```bash
pytest                         # 全部通過才繼續；測試用合成資料，不需要下載也能跑
pre-commit install             # 選用：commit 時自動跑洩漏測試
```

### 6. 講師：切出 holdout（學員跳過）

```bash
python scripts/make_holdout.py   # 產生 data/holdout/labels.csv（2018-06～08 的答案）
```

這份答案只有講師能看。Claude Code 的 hook 會擋 AI 讀取 `data/holdout/`，請不要把它發給學員。

### 7. 開始上課

```bash
jupyter lab notebooks/M1_problem_framing.ipynb   # 第一堂課
claude                                            # 或 codex；在 repo 根目錄、同一個已啟用環境的終端機開啟
```

**用 VS Code 開 notebook**：右上角 kernel 要選專案的 `.venv`（**Select Kernel → Python Environments → `.venv`**）。如果跳出「requires the ipykernel package… `pip install ipykernel --user`」，代表選到了系統 Python，**不要照它的指令裝**，改選 `.venv` 即可（`uv sync` 已裝好 ipykernel）。

AI 會自動讀到 `AGENTS.md` 的規範，以及 `knowledge/brief.md`（任務定義，已核准）。第一句可以對它說：「用 data-card 帶我看一遍資料」。

## 課程地圖

| 模組 | 時數 | 核心問題 | Notebook | Skill | 知識文件 |
|---|---|---|---|---|---|
| M1 | 2h | 下單那一秒，我們知道什麼？ | `M1_problem_framing`（課前先看[資料導覽](docs/olist/data_intro.html)） | define-boundaries、data-card | `brief.md`、`data.md` |
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
