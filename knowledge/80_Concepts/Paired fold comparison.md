---
type: concept
aliases: [配對比較, paired CV]
tags: [concept, validation]
---
# Paired fold comparison

## 一句話
比較兩組設定時，在**同一個 fold 內**相減，再看差值的分布 —— 把各 fold 難度不同的變異消掉。

## 判準（本專案）
所有 fold 都進步，且平均差 > 差值的 std。

## 常見錯誤
「增益 > fold std」：fold 難度差異大時，所有真實改進都會被判無效（[[FND-004 fold 間標準差主要反映月份難度]]）。

## 在專案中的實例
`olist_course.experiment.compare()`；[[D-004 以同月份配對增益判斷進步]]
