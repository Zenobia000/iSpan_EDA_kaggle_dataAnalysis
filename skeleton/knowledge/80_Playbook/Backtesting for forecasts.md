---
type: concept
aliases: [時間序列回測, rolling-origin backtest]
tags: [concept, validation, forecast]
---
# Backtesting for forecasts

## 一句話
時間序列預測的驗證 = 站在過去的某個「預測起點」，只用起點之前的資料，預測之後 h 期，重複多個起點。

## 怎麼做（檢查清單）
- [ ] 一列 = (序列, 預測起點 origin, 預測步數 h)；目標 = 起點後第 h 期的值
- [ ] 所有特徵（lag、rolling、季節性）只能用 **origin 之前**已觀察到的值
- [ ] 驗證窗：最後 N 個長度為 step 的窗；訓練列的**目標時間**必須早於驗證窗開始（不只是起點）
- [ ] 一定要有 **seasonal naive** 基準（上週同一天 / 去年同期）；打不贏它的模型沒有價值
- [ ] 指標用 WAPE / MAE（對 0 值穩定）；MAPE 遇到 0 會爆掉
- [ ] 依 h 分開報告誤差：h=1 和 h=14 的難度不同

## 常見錯誤
- rolling mean 視窗包含預測起點當天（或之後）
- 用整段資料做標準化或計算假日效應後才切分
- 只在一個驗證窗上評估 → 換個月份結論就翻盤

## 在本專案中的實例
- 
