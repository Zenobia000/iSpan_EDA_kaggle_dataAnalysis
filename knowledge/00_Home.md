---
type: moc
tags: [moc]
---
# 🏠 Olist 差評預警

## 👔 主管：先看 → [[Decision Card]]
- **能做**：下單當下列出風險最高的 5%（每天約 10 筆），約 3 成真的會差評，是隨機的 2.8 倍
- **不能做**：只抓到約 14% 的差評；嚴重遲到與缺貨在下單時看不出來；不能證明關懷有效（需試辦）
- **⏳ 待你決定**：是否試辦、名單大小、名單給客服或賣家輔導、是否做「出貨延誤時」的第二次預測

## 🧭 新成員：上手順序
[[Project Brief]] → [[Data Brief]] → [[Validation Protocol]] → [[Glossary]] → 下方「目前狀態」

## 📍 目前狀態（Now / Next）
- **Now（R5）**：all_safe LGBM；CV PR-AUC 0.291、holdout Lift 2.85（[[ledger]]）
- **最有效**：[[F-005 歷史群組 history]] → [[FND-002 賣家歷史差評率是最穩健的增益來源]]
- **已排除**：[[F-006 賣家過去遲到率 seller_past_late_rate]]（冗餘）、[[F-007 洩漏特徵三件組 leaky]]（洩漏）、[[H-003 運費占比越高越容易差評]]（推翻）
- **Next**：
  - 累積次數改近 90 天比率，降低分布偏移（[[FND-006 訓練期與上線期幾乎可完全區分]]）
  - 品類層級 point-in-time 差評率
  - 出貨延誤時點（T1）模型

## 🗂 資料夾
| 資料夾 | 放什麼 | 誰寫、何時寫 |
|---|---|---|
| `00_Inbox` | 未整理的觀察；**每個模組結束前清空**（歸檔或刪除） | 任何人，隨時 |
| `10_Brief` | 決策卡、專案背景、資料說明、驗證規則、名詞 | 拿到資料前；規則變動時 |
| `20_Data` | 每張表一頁（AUTO 區塊 + 人寫筆記） | `scripts/build_data_notes.py` + M1 |
| `30_Hypotheses` | H-xxx 假設卡（含被推翻的） | M2 起 |
| `40_Features` | F-xxx，**一個特徵群組一張卡** | M3 起 |
| `50_Runs` | [[ledger]]（自動）+ 只為**改變決定的**實驗寫 EXP-xxx | 每輪 |
| `60_Findings` | FND-xxx，標題即結論，附「對營運的意義」 | 實驗後 |
| `80_Playbook` | 跨專案方法論 + [[Next competition checklist]] | 模組結束 |

迭代輪次（R1…R5）記在每則筆記的 `round` 欄位，不另開資料夾。

```
Brief → H 假設 → F 特徵 → EXP 實驗（run_id → ledger）→ FND 發現 → 新的 H
                                                       └→ Playbook（可帶走的方法）
```
