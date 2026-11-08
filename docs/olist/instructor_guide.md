# 講師手冊

## 課前（D-3）

1. `uv sync && uv run python scripts/download_data.py`
2. `uv run pytest`：確認全部通過
3. 執行 5 本 `notebooks/solutions/*_solution.ipynb`，確認可重現（每本 1–5 分鐘）
4. 產生 holdout 標籤：`uv run python scripts/make_holdout.py`。檔案輸出在 `data/holdout/`，**不要發給學員**。
5. 若 `experiments/log.jsonl` 有內容，先清空
6. 修改教材後要重新產生兩樣東西：
   - notebook：`uv run python scripts/build_notebooks.py`，從 `scripts/notebook_src/` 同時產生學員版與解答版
   - skill：`uv run python scripts/sync_skills.py`，同步一份給 Codex

## 已驗證的課堂數字（2026-11，真實資料）

| 項目 | 數值 |
|---|---|
| base table | 97,917 筆，差評率 14.2% |
| 切分 | train 2017-01~2018-02 / valid 2018-03~05 / holdout 2018-06~08（18,789 筆，差評率 10.7%） |
| CV 驗證月差評率 | 2018-03: 22.6% / 04: 12.9% / 05: 11.7% |
| Dummy CV PR-AUC | 0.157 |
| raw LGBM | 0.265 |
| all_safe LGBM | 0.291（Lift@5% ≈ 2.9） |
| + leaky（Lab3） | 0.584 ← 假的 |
| holdout：raw / all_safe | 0.178 / 0.200 |
| adversarial AUC（train vs holdout, all_safe） | 0.999（時間趨勢特徵造成） |

## 每模組要點與常見卡點

### M1（2h）
- **關鍵一問**：「這個預測是給誰、在什麼時候、拿來做什麼決定？」T0 由決策時點決定，不是由資料決定。
- 卡點：學員想用 `order_approved_at`。可以討論：付款核准可能晚好幾天，但客服名單在下單後就要產生。
- 卡點：Accuracy 86% 的錯覺。對應練習 3。

### M2（3h）
- 要求學員**先寫預期**再跑程式。AI 產出的圖表如果沒有對應的假設，就退回。
- Lab1 討論重點：
  - 分層後關聯仍在，不等於因果
  - 州層級的相關，不能推論到訂單層級（生態謬誤）
- 分工：讓 AI 用 `eda-agent` 驗證假設，學員負責判斷「T0 可用的代理特徵是什麼」。

### M3（4h）
- 最重要的概念是 point-in-time 聚合（`review_answer_timestamp < T0`）。
- 對照 `seller_prior_low_rate` 與 `seller_low_rate_global` 的單特徵 PR-AUC。
- 課堂挑戰：把 `seller_past_late_rate` 原型升級進 `features/`。AI 改動 `src/` 後，PostToolUse hook 會自動跑洩漏測試。
- Lab2 討論：為什麼 fold 之間的 std 大，但配對 std 小？答案是月份難度不同。

### M4（3h）
- Lab3 劇本：先讓學員看到 PR-AUC 翻倍、宣稱勝利，再問「下單當下知道實際配送天數嗎？」
- 強調三層防線，只有最後一層擋得住：
  1. 欄位名檢查：擋不住
  2. 配對穩定性：擋不住
  3. 擾動測試：擋得住
- Adversarial validation 的 AUC 是 0.999。引導學員自己發現：累積次數與月份這類特徵帶有時間趨勢。

### M5（3h）
- 錯誤分析的核心結論：嚴重遲到造成的差評，在 T0 是**不可約**的。商業建議是增加第二個預測時點（出貨延誤時）。
- Lab ABC 見 `docs/olist/labs/lab_abc_ai_comparison.md`。
- 成果報告的範例（解答）：`reports/report.md`。課前請勿發給學員。
- 收 submission：`uv run python -m olist_course.score submissions/*.csv`，產生 `leaderboard.md`。

## Harness 行為（講師須知）

- `.claude/hooks/guard_paths.py` 會阻擋**任何提及 holdout 路徑**的 Bash 指令（寧嚴勿漏）。
  - 講師用 Claude Code 維護 repo 時，含這個字串的檔案請改用 Write/Edit 工具編輯。
  - 計分指令本身不含這個字串，可以正常執行。
- Claude 的 hook 只保護 Claude 的 session。Codex 學員靠三樣東西：`AGENTS.md` 規範、`pre-commit`（`uv run pre-commit install`）、`pytest`。
- Subagent 是 Claude Code 獨有的功能。Codex 學員依 AGENTS.md 的「角色」表自我約束，主要使用 skill。
- Holdout 是 honor system：原始評價資料是公開的，hook 只能擋 AI，擋不了人。所以評分刻意不看名次。
- 建議講師端另外保留一份不含 `.claude/settings.json` hook 的副本來準備教材；學員版 repo 則保留全部防線。
