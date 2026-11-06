---
type: moc
tags: [moc]
---
# 🏠 <專案名稱>

## 👔 決策者：先看 → [[Decision Card]]
- **能做**：
- **不能做**：
- **⏳ 待你決定**：

## 🧭 新成員：上手順序
[[Project Brief]] → [[Data Brief]] → [[Validation Protocol]] → [[Glossary]]

## 📍 目前狀態（每輪 round-review 更新，≤ 5 行）
- **Now（R0）**：尚未開始。先完成 define-boundaries，讓 [[Validation Protocol]] 變成 `approved`
- **最有效**：
- **已排除**：
- **Next**：

## 🗂 資料夾
| 資料夾 | 放什麼 | 何時寫 |
|---|---|---|
| `00_Inbox` | 未整理的觀察；每輪結束前清空 | 隨時 |
| `10_Brief` | 定義文件（人類核准） | 拿到資料前 |
| `20_Data` | 每張表一頁 data card | 第一輪 |
| `30_Hypotheses` | H-xxx 假設卡（含被推翻的） | 每輪 |
| `40_Features` | F-xxx，一個特徵群組一張卡 | 每輪 |
| `50_Runs` | 只為改變決定的實驗寫 EXP-xxx（數字引用 run_id） | 每輪 |
| `60_Findings` | FND-xxx，標題即結論，附對營運的意義 | 每輪 |
| `80_Playbook` | 跨專案方法論（從上一個專案帶來，也帶到下一個） | 專案結束 |

```
Brief → H 假設 → F 特徵 → EXP 實驗（run_id）→ FND 發現 → 新的 H
                                            └→ Playbook（可帶走的方法）
```
