---
type: experiment
id: EXP-000
date: {{date}}
question:               # 這個實驗要回答什麼
baseline:               # compare() 的 baseline 名稱
model: lgbm
feature_set:
git:                    # experiments/log.jsonl 的 git 欄位
pr_auc:                 # mean
pr_auc_std:
gain_vs_base:
folds_improved:         # 例 3/3
robust: false
tests: [ "[[F-000 ...]]" ]
tags: [experiment]
---
# {{title}}

## 問題
<一次只改一項：改了什麼？>

## 設定
固定：split / 3 個月份 CV / 指標 / seed。變動：<...>

## 結果
<compare() 表格貼這裡>

## 解讀
<為什麼會這樣；最可疑的地方>

## 產生的發現
- [[...]]

## 下一個實驗
-
