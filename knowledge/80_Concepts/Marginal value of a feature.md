---
type: concept
aliases: [邊際價值, 特徵冗餘]
tags: [concept, feature-engineering]
---
# Marginal value of a feature

## 一句話
特徵的價值 = 它提供了**模型還不知道**的資訊，不是它和目標的單變量關聯有多強。

## 怎麼判斷
- 和既有特徵的相關（Spearman）
- 在既有特徵之上的 ablation 配對增益
- Permutation importance（打亂後掉多少）

## 在專案中的實例
[[FND-003 EDA 的強關聯不等於特徵增益]]
