# notebooks/ — 探索區（用完即丟）

這裡的程式碼**預設是拋棄式的**：AI 在對話中產生、跑完、看結果，結論寫進 `knowledge/`，程式就可以不要了。

## 命名

`<輪次>-<主題>.ipynb` 或 `.py`，例如 `R2-customer-history.ipynb`、`R3-leak-check.py`。
同一主題要改版就開新檔，不要覆蓋已經被 knowledge 筆記引用的檔案。

## 什麼時候要「升級」到 `src/`（任一條成立）

1. **第二次被用到**：同一段邏輯在第二個 notebook 又寫了一次
2. **影響最終模型**：特徵、資料清理、切分、評估指標
3. **要給別人跑**：排程、交付、重現報告數字

升級的方式見 `src/README.md`。沒升級的程式碼**不能**用來產生報告中的最終數字。

## 本專案（Olist 課程）的例外

`M1_*` … `M5_*` 與 `solutions/` 是**課程教材**，不是拋棄式探索：它們由 `scripts/notebook_src/m*.py` 產生，
要修改請改原始檔，再執行 `uv run python scripts/build_notebooks.py`（`tests/test_notebooks_in_sync.py` 會檢查兩邊一致）。
學員自己的探索仍依上面的命名規則另開新檔。

## 規則

- notebook 開頭第一個 cell 寫：這個 notebook 要回答什麼問題（對應 `knowledge/log.md` 的段落）
- 讀資料用 `data/processed/` 或 `src/` 的函式，不要在 notebook 內重寫一份清理邏輯
- 跑實驗要寫一行紀錄到 `experiments/log.jsonl`（格式見 `experiments/README.md`）
