---
name: experiment-protocol
description: 控制變因的實驗與紀錄規範：固定切分/CV/指標/seed，一次只改一項，寫 experiments/log.jsonl，以同 fold 配對比較判斷是否穩健進步。當要比較特徵組合、模型、參數，或問「這個進步是真的嗎」時使用。
---

# Experiment Protocol

## 第一次跑實驗前
若 `src/<pkg>/tracking.py` 不存在，依 `experiments/README.md` 的欄位合約建立：
- `log_run(...)`：追加一行 JSON 到 `experiments/log.jsonl`（含 `fold_scores`、`features`、`git`、`round`）
- `compare(runs, baseline)`：同 fold 配對比較 → `gain`、`gain_std`、`folds_improved`、`robust`

切分與 CV 依 Validation Protocol 實作在 `src/<pkg>/validation/`，**不准自行更改規則**。

## 每次比較
1. 寫下這次**只改了什麼**（一個特徵群組 / 一個模型 / 一組參數）與預期
2. 先跑基準模型（多數類 / 平均值 / seasonal naive），沒有基準的比較不成立
3. 跑完立刻 `log_run`
4. 用 `compare` 判斷：
   - 每個 fold 都進步，且平均增益 > 增益的 std → robust
   - 只有平均變好 → 不能宣稱有效
   - 單次大幅進步 → 先做 leakage-audit
5. 額外檢查：overfit gap（train − valid）是否變大

## 回報
一句話結論 → 比較表（附 run_id）→ 最可疑的一個結果 → 下一個實驗。
會改變決定的比較才寫 `knowledge/50_Runs/EXP-xxx`（knowledge-capture）。
