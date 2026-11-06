---
type: finding
id: FND-003
confidence: high
source: ["[[EXP-003 原型 賣家過去遲到率]]"]
concepts: ["[[Marginal value of a feature]]"]
created: 2026-11-06
tags: [finding, methodology]
---
# EDA 的強關聯不等於特徵增益

## 證據
遲到是 EDA 中最強的關聯（5.9 倍），但它的 T0 代理「賣家過去遲到率」讓 PR-AUC 下降（0/3 月份進步）。
它與已有的賣家歷史差評率 Spearman 0.44 —— 模型已經知道大部分這個資訊。

## 適用範圍
任何「單變量很強」的候選特徵；越晚加入的特徵越容易冗餘。

## 影響了哪些決定
[[D-004 以同月份配對增益判斷進步]]：每個特徵都要過 ablation 才能升級。
