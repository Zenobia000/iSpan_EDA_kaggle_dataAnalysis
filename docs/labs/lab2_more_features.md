# Lab2：增加特徵一定能提升模型嗎？（M3，約 60 分鐘）

## 目標
用控制變因的 ablation 判斷特徵的實際價值，並分清楚「平均數變高」和「穩健增益」的差別。

## 規則
- 模型（LGBM）、split、CV、指標全部固定；相鄰兩組只差一個特徵群組。
- 一律用 `run_experiment(..., note="Lab2 ...")` 執行。
- 判斷進步要看 `folds_improved` 和 `robust_gain`。

## 步驟
1. **預測（5 分鐘）**：先寫下你預期 `time / geo / product / history` 四個群組的增益排序。
2. **執行（15 分鐘）**：跑 M3 notebook 的 Lab2 cell，或請 `model-runner` 套用 ablation-run skill 的範本。
3. **逐步增益（10 分鐘）**：產出每一組相對前一組的配對增益表。
4. **你的特徵（20 分鐘）**：用 `add_features` 加入你的原型特徵，和 `all_safe` 做配對比較。
5. **討論（10 分鐘）**：見下方討論題。

## 繳交
- Ablation 表，須包含 `folds_improved`、`robust_gain`、`overfit_gap`
- 每個群組一句結論：有效 / 平均變高但不穩健 / 無效

## 討論題
- 為什麼 `pr_auc_std` 遠大於 `paired_gain_std`？
- 如果一個特徵只在 2018-03 進步、其他月份都退步，你會留下它嗎？
- `overfit_gap` 變大，但驗證分數也變高，該怎麼取捨？
