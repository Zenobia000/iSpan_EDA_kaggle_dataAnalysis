---
type: concept
aliases: [群組洩漏, group k-fold]
tags: [concept, validation, leakage]
---
# Group leakage

## 一句話
同一個實體（同一個人、同一間店、同一個病人）的多筆資料同時出現在訓練與驗證，模型就是在「認人」，不是在預測。

## 什麼時候用群組切分
- 上線時要預測的是**新的**實體（新顧客、新商品、新病人）
- 同一實體的資料高度相似（多次就診、同一使用者的多筆交易）

## 怎麼做
- [ ] 在 Validation Protocol 寫明群組欄位（例：customer_id）
- [ ] 用 GroupKFold；holdout 也要以群組為單位切
- [ ] 實體層級的聚合特徵（該客戶的平均消費）只能用訓練 fold 計算 → 放進 Pipeline

## 常見錯誤
- 隨機 K-fold 分數很高、上線後崩盤
- 以列為單位切 holdout，同一個人同時出現在 CV 與 holdout

## 在本專案中的實例
- 
