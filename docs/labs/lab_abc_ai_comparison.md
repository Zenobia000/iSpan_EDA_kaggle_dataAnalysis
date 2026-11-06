# Lab ABC：AI Only vs Human Guided vs Validated AI（M5，約 75 分鐘）

## 目標
親自驗證三件事：
- AI 自己能找出多少有效特徵？
- 領域知識能不能改善結果？
- 驗證設計能擋下多少錯誤結論？

## 共同規則（三組相同）
- 起點：`all_safe` 特徵、LGBM、相同的 split / CV
- 每組限時 **25 分鐘**，與 AI 互動次數不限
- 所有分數都必須來自 `run_experiment(..., author="<組名>-<A|B|C>")`
- 結束時各組用 `make_submission(..., name="<組名>-<A|B|C>")` 產出一份 submission

## 三種做法

### A — AI Only
只給 AI 下面這段指令，不得補充任何領域提示：
> 這是 Olist 差評預測任務，規則在 AGENTS.md。請自主探索並新增特徵，目標是提升 CV PR-AUC，
> 最後回報你的最佳特徵組合與分數。

### B — Human Guided
學員從 M2/M3 的假設卡中挑 3 張 feature card，指示 AI **只實作這三個**，再跑 ablation。

### C — Validated AI
做法同 B，另外加三條規則：
- 每個特徵實作後都必須通過 `uv run pytest tests/test_leakage.py`
- 最終組合交給 `validation-auditor` 審查。Codex 使用者改為依 leakage-audit + ablation-run skill 自我審查，並附上證據。
- 只保留 `robust_gain=True` 的群組

## 比較表（填入 M5 notebook）

| 指標 | A | B | C |
|---|---|---|---|
| CV PR-AUC（mean ± std） | | | |
| robust 增益的特徵數 | | | |
| 被擋下 / 發現的洩漏數 | | | |
| 實驗次數（log 筆數） | | | |
| 你能解釋的特徵比例 | | | |
| holdout PR-AUC（講師公布） | | | |

## 預期觀察（講師參考，不要事先告訴學員）
- **A 組**：特徵數量多，CV 分數最高或接近最高，但能解釋的比例低。它也常會嘗試使用 T0 之後的欄位，hook 或測試會擋下，請記錄被擋的次數。
- **B 組**：特徵少、容易解釋，但增益不一定最大。
- **C 組**：分數不一定最高，但 CV 與 holdout 的落差最小。這就是本課的核心訊息。

## 討論題
- 哪一組的 CV 與 holdout 落差最大？為什麼？
- A 組 AI 提出的特徵中，有哪些是你在 M2 沒想到、但確實合理的？
- 如果只能留一道防線（AGENTS.md 規範 / hook / 擾動測試 / 稽核 subagent），你會留哪一道？
