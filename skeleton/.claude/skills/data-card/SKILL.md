---
name: data-card
description: 為每張原始表產出「真的跑過程式」的 data card（粒度、主鍵、缺失、欄位在預測當下是否可得、join 風險），寫入 knowledge/20_Data。當拿到新資料、學員問欄位意思、或要建立資料字典時使用。
---

# Data Card

**不准模擬**：每個數字都來自實際執行的程式（程式放 `notebooks/R1-data-card.py`，用完即丟）。

## 每張表要回答
1. 一列代表什麼（粒度）？主鍵是否唯一？
2. 與分析單位的關係：一對一、一對多？join 會不會放大列數？
3. 每個欄位：型別、缺失率、唯一值數、範例、**在 T0 是否可得**（對照 Validation Protocol §2；有差異要指出來）
4. 奇怪的值：負數、未來日期、重複、編碼不一致

## 產出
- `knowledge/20_Data/<table>.md`：上述內容 + 「筆記（人寫）」段落
- 在 `data/README.md` 的來源登記表補一列
- 給 EDA 的 3 個問題 → 寫進 `knowledge/00_Inbox/`
