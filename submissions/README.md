# submissions/ — 最終提交

**一個專案最後只交一份。** 這裡放的是「交出去評分」的預測檔，不是每一輪的實驗結果。

## 每一輪 vs 最後提交

| | 每一輪 | 最後提交 |
|---|---|---|
| 怎麼判斷好壞 | 本地交叉驗證（CV） | holdout（從沒看過的答案）或 Kaggle 排行榜 |
| 結果記在哪 | `experiments/log.jsonl` | 這個資料夾 |
| 要不要產生預測檔 | **不用** | 要，一份 |
| 誰決定 | AI 跑、人類在 round-review 審查 | **人類**在 round-review 決定「提交」 |

## 規則

1. **只有人類決定要提交時，才產生檔案**。AI 不會自己提交
2. **holdout 只評估一次**。看了 holdout 分數再回頭改模型，那份分數就不再可信
3. 一定要附對照組：同時交一份基準模型的預測，才知道最終模型比「什麼都不做」好多少

## 檔名與格式

- 檔名：`<輪次>-<設定名稱>.csv`，例如 `R5-final.csv`、`R5-baseline.csv`
- 欄位：`<唯一鍵>, <預測值>`，唯一鍵依 `knowledge/10_Brief/Validation Protocol.md`
- 每一列對應 holdout 的一列，不多也不少；預測值不能有空值

## 提交後要記錄

在 `experiments/log.jsonl` 寫一行 `kind: holdout`，內容包括檔名、分數、對應的 CV `run_id`。
然後更新 `knowledge/10_Brief/Decision Card.md` 的「模型能做什麼」。

## Kaggle 競賽

- Kaggle 的排行榜就是 holdout，每天能交的次數有上限
- 每次上傳都要記錄：本地 CV 分數 vs 排行榜分數。兩者落差變大，代表本地驗證方式有問題
- 比賽結束前，從中挑 1～2 份當正式成績。**挑 CV 最穩的，不是排行榜最高的**（公開排行榜只用了部分資料，容易過擬合）

## 版本控制

預測檔（`.csv`）不進 git，只有這份 README 會進。要保留哪一份作為正式成績，就在 `experiments/log.jsonl` 記下它的檔名與分數。
