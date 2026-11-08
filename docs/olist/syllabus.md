# 課綱：AI 時代的資料分析與特徵工程 — Olist Kaggle 實戰

15 小時｜3 天 × 5 小時｜對象：具 ML 基礎（用過 scikit-learn）｜工具：Claude Code 或 Codex

## 課程定位

這不是 Pandas / Scikit-learn 工具課，也不是 Prompt 課。
**學員負責問題定義、假設與驗證標準；AI Agent 負責執行大量實驗。**

結業時要能回答三個問題：
- 為什麼選這些特徵？
- 如何證明改進不是偶然？
- 換一批資料，流程能否重現？

## 任務

資料是 Olist 巴西電商約 10 萬筆訂單。任務是**在顧客下單當下，預測這筆訂單會不會拿到 1–2 星差評**，讓客服每天主動關懷風險最高的 5% 訂單。

- 主指標：PR-AUC
- 業務指標：Precision@5% / Lift@5%

## 時間配置

| 天 | 模組 | 時數 | 學員產出 | 實驗 |
|---|---|---|---|---|
| D1 | M1 資料理解與問題定義 | 2h | 問題定義書、Data Card、Baseline | — |
| D1 | M2 假設驅動 EDA | 3h | 3 張假設卡（≥1 張被推翻） | Lab1 相關 ≠ 因果 |
| D2 | M3 特徵工程實驗室 | 4h | 3–5 張特徵群組卡（`knowledge/log.md` 的特徵段落）、1 個升級進 pipeline 的特徵群組 | Lab2 增加特徵一定更好？ |
| D2–D3 | M4 特徵驗證與篩選 | 3h | Ablation 表、Permutation Importance、Adversarial Validation | Lab3 分數變高 = 變好？ |
| D3 | M5 建模、AI 對照實驗與報告 | 3h | 最終模型、錯誤分析、submission、成果報告 | Lab ABC |

每個模組的節奏：概念 30% / 引導實作 45% / 自主挑戰與討論 25%。

## Harness 對應

| 模組 | Skill | Subagent（Claude Code） |
|---|---|---|
| M1 | define-boundaries、data-card | — |
| M2 | hypothesis-eda | eda-agent |
| M3 | feature-card、leakage-audit | feature-agent |
| M4 | experiment-protocol、leakage-audit | model-agent、validation-agent |
| M5 | error-analysis、report-writer | model-agent、validation-agent |

## 評分

| 項目 | 比重 | 看什麼 |
|---|---|---|
| 問題理解 | 20% | T0、指標、驗證設計的理由是否正確 |
| EDA 與假設 | 25% | 假設卡先寫預期；有控制混雜因素；有被推翻的假設 |
| 特徵實驗 | 25% | 特徵群組卡完整（含失敗原因）；ablation 一次只改一項；至少一個特徵升級進 pipeline 且通過洩漏測試 |
| 模型驗證 | 20% | 用配對增益判斷進步；找出並排除洩漏；理解分布偏移 |
| 成果解釋 | 10% | 報告第一句話就是決策；數字可追溯到 experiments/log.jsonl |

Leaderboard 名次**不計分**。計分看的是實驗可信度：有 log、有配對比較、沒有洩漏。

## 課前準備

- Kaggle 帳號與 API token（`~/.kaggle/access_token`，設定方式見 README 步驟 3）
- Python 3.10+ 與 [uv](https://docs.astral.sh/uv/)
- Claude Code 或 Codex CLI，擇一即可
- 會用 pandas 的 groupby / merge，用過 scikit-learn 的 fit / predict
