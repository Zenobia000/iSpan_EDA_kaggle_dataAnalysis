# data/

| 子資料夾 | 放什麼 | 誰可以寫 | 進 git？ |
|---|---|---|---|
| `raw/` | 原始資料，**永遠唯讀** | 只有下載腳本 / 人類 | ✗ |
| `external/` | 外部補充資料（假日表、匯率、地理資料） | 人類 / AI（需登記來源） | ✗ |
| `interim/` | 清理、合併後的中間產物，可隨時重建 | AI | ✗ |
| `processed/` | 建模用資料表（一列 = 一個預測單位） | AI（由 `src/` 的程式產生） | ✗ |
| `holdout/` | 最終評估的答案，**由人類保管** | 只有人類 | ✗ |

## 規則

- `raw/` 與 `holdout/` 受 hook 保護：AI 無法寫入 `raw/`，也無法讀取 `holdout/`
- `interim/` 與 `processed/` 的檔案都必須能用 `src/` 裡的程式重建。只存在 notebook 裡的中間檔不算數
- 每個新資料來源都要在下表登記一列，並更新 `knowledge/data.md`

## 資料來源登記

| 檔案 / 表 | 來源（URL、系統、負責人） | 取得日期 | 授權 / 限制 | 下載方式 |
|---|---|---|---|---|
| `raw/olist_*_dataset.csv` 等 9 張表 | Kaggle [olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | 執行下載腳本當天 | CC BY-NC-SA 4.0（非商業） | `uv run python scripts/download_data.py`（需要 `~/.kaggle/kaggle.json`） |
| `holdout/`（2018-06~08 的答案） | 由 `raw/` 切出 | 講師上課前 | 只有講師可以讀 | `uv run python scripts/make_holdout.py`（講師端） |
