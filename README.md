# 資料科學專案模板：人類定邊界，AI 跑實驗

這是一個**空模板**。裡面沒有分析程式碼，只有三樣東西：

- **資料夾分層**：每個資料夾的 `README.md` 規定這裡放什麼
- **專案知識**：`knowledge/` 的 4 份文件（定義、資料、研究日誌、發現）
- **AI 的工作規範**：`AGENTS.md`、`.claude/`（Claude Code）、`.agents/`（Codex）

程式碼由 AI 在對話中產生；被證明有價值的，才放進 `src/`。

## 範例專案：Olist Kaggle 實戰（上課參考）

想看這個模板「填滿之後」長什麼樣子，請切到分支 **`course/olist`**：一個完整的 Olist 差評預測課程，含 pipeline、M1–M5 notebooks、課綱、已填好的知識庫與講師範例報告。

```bash
git switch course/olist        # 範例分支（可能持續修訂）
git switch -d olist-course-v1  # 固定版本（上課以此為準，不會變動）
```

> 範例分支只供參考，不要合併回 `main`。

---

## 使用步驟

### 1. 建立新專案
```bash
git clone <這個 repo> my-project
cd my-project
rm -rf .git && git init
```

### 2. 放資料
把原始資料放進 `data/raw/`，並在 `data/README.md` 登記來源。

### 3. 定義專案（人類決定）
開啟 Claude Code 或 Codex，輸入：
> 用 define-boundaries 幫我定義這個專案

AI 會問你：預測給誰用、做什麼決定、預測當下知道哪些資訊、怎麼驗證、何時停止。
問完後，它會寫好 `knowledge/brief.md`。
**你檢查 `brief.md`，同意後把 `status` 改成 `approved`**，AI 才會開始建模。

### 4. 跑一輪
> 用 data-card 整理資料，然後開始第一輪 EDA

AI 會探索資料、提出假設、做特徵、跑實驗。**每次回報結果，它都會自動記到 `knowledge/log.md`**，你不用提醒。

### 5. 每輪結束時審查
> round-review

AI 會整理這一輪的結果、對照停止條件，並列出「值得留下的發現」。
**由你決定：留哪幾條（寫進 `knowledge/findings.md`），以及下一輪 / 停止 / 提交。**

> 整個流程中，你只需要記得在每輪結束時說「round-review」。

重複第 4、5 步，直到你決定停止。

---

## 資料夾

| 資料夾 | 放什麼 |
|---|---|
| `knowledge/` | 4 份文件：專案定義、資料說明、研究日誌、發現 |
| `data/` | `raw/` 原始資料（唯讀）、`processed/` 建模資料、`holdout/` 最終答案（只有人類能碰） |
| `notebooks/` | 探索用的程式，用完即丟 |
| `src/` | 被證明有價值的程式碼，必須附測試 |
| `tests/` | 測試，一定要有洩漏測試 |
| `experiments/` | 實驗紀錄 `log.jsonl`（每一輪） |
| `submissions/` | 最終提交的預測檔，**只交一份**（見資料夾內說明） |
| `reports/` | 給決策者看的報告 |

## 你和 AI 的分工

| 人類 | AI |
|---|---|
| 定義目標、可用資訊、驗證方法、停止條件 | 探索、做特徵、建模、記錄 |
| 每輪決定下一步 | 每輪整理證據、給建議 |
| 保管 holdout | 不能讀 holdout、不能改原始資料 |

## 常用指令

| 想做什麼 | 對 AI 說 |
|---|---|
| 定義專案 | 用 define-boundaries |
| 理解資料 | 用 data-card |
| 驗證一個猜測 | 用 hypothesis-eda 驗證「…」 |
| 做一個特徵 | 用 feature-card 做「…」 |
| 檢查有沒有洩漏 | 用 validation-agent 審查這一輪 |
| 整理成報告 | 用 report-writer |

## 備註

- Windows 使用者：如果沒有 `python3` 指令，把 `.claude/settings.json` 裡的 `python3` 改成 `py`
- 修改 skill 時改 `.claude/skills/`，再複製一份到 `.agents/skills/`，讓 Codex 也能用
- 執行 `pre-commit install` 後，commit 時會自動跑洩漏測試
