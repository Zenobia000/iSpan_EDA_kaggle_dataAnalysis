---
name: leakage-audit
description: M3/M4 — 資料洩漏稽核清單＋擾動測試。當分數突然變好、新增歷史/聚合特徵、使用 target encoding、或學員問「這個特徵可以用嗎」時使用。
---

# Leakage Audit

## 一句話原則

**下單那一秒，這個值存在嗎？算出這個值用到的每一筆資料，那一秒都已經發生了嗎？**

## 清單（逐項回答，附證據）

| # | 檢查 | 怎麼查 |
|---|---|---|
| 1 | 欄位名：有沒有 `POST_T0_COLUMNS` 或 `review_` / `order_delivered_` 前綴 | `validate_columns()` |
| 2 | 計算過程：有沒有用到 T0 後才發生的事件（送達、評價、取消） | 讀 `build()` 原始碼 |
| 3 | 聚合範圍：歷史統計是否只用 `< T0` 的資料，且排除這筆訂單自己 | 擾動測試 |
| 4 | Target encoding / 平滑先驗：是否用全資料估計（含 valid/holdout label） | 讀程式；先驗應為常數或只用 train fold |
| 5 | 前處理：填補、縮放、編碼是否只在訓練 fold 上 fit | 確認走 `build_pipeline`（Pipeline 內 fit） |
| 6 | 切分：是否有隨機切分或用到 holdout label | `split.py`、`dataset.py` 的遮蔽 |
| 7 | 異常增益：PR-AUC 增加 > 0.05 或單一特徵 permutation importance 遠超其他 | `compare()`、`permutation_importance()` |

## 必跑

```bash
uv run pytest tests/test_leakage.py -q
```

擾動測試原理：把「未來」打亂（送達日、cutoff 之後才回覆的評價、訂單狀態），重建特徵；
cutoff 之前的訂單特徵值只要有任何改變 → 該群組偷看了未來。

## 回報格式

`判定：乾淨 / 洩漏 / 可疑` → 證據（清單項目 + 測試輸出 + 檔案:行號）→ 修法。

## 參考反例

`src/olist_course/features/leaky.py`：欄位名全部合法，但三個特徵都偷看未來 — 只檢查欄位名擋不住。
