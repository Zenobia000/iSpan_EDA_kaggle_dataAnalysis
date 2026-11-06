---
name: knowledge-capture
description: 把探索與實驗的結果沉澱進 Obsidian 知識庫（knowledge/）：假設卡、特徵群組卡、會改變決定的實驗筆記、發現（含對營運的意義）、跨專案 playbook。當一輪實驗有結論、一個假設被驗證或推翻、一個模組結束、或學員說「記下來」「整理筆記」「沉澱」時使用。
---

# Knowledge Capture

Kaggle 是「探索 → 收斂 → 發現新特徵 → 拉高分數」的迴圈。**沒寫下來的發現，下一輪會重做；寫太多，沒人會讀。**

## 寫之前（必做）
1. **先搜尋**：`grep -ril "<關鍵字>" knowledge/` —— 已有筆記就更新它，不要新建
2. **取號**：同資料夾最大號 + 1；寫完跑測試，ID 重複會失敗
3. 讀 `knowledge/00_Home.md` 的 Now / Next，確認這件事還沒有結論

## 寫什麼、寫到哪

| 事件 | 動作 |
|---|---|
| 跑了任何實驗 | **不用寫筆記**。`run_experiment()` 已自動進 `experiments/log.jsonl`；執行 `uv run python scripts/build_ledger.py` 更新 [[ledger]] |
| 實驗**改變了決定**（採用/放棄特徵、換模型、發現洩漏） | `knowledge/50_Runs/EXP-xxx`，`run_ids` 必填 |
| 有可驗證的猜測 | `knowledge/30_Hypotheses/H-xxx` |
| 決定做一個特徵群組 | `knowledge/40_Features/F-xxx`（一個 registry 群組一張卡） |
| 得到下次還會用到的結論 | `knowledge/60_Findings/FND-xxx`，標題即結論，`ops` 必填 |
| 方法論可帶去下一場比賽 | `knowledge/80_Playbook/` |
| 還沒想清楚 | `knowledge/00_Inbox/`（模組結束前清空） |

模板：`knowledge/90_Meta/templates/`。

## 規則
1. **數字不重抄**：EXP 只寫 `run_ids` 與解讀；若在 frontmatter 寫 `pr_auc`，必須等於某個 run_id 的紀錄（測試會比對）
2. **EXP 寫完即鎖定**：之後只能在文末 `## 追記` 追加，不改寫原文
3. **失敗要可檢索**：F 卡 `status: no-gain | leaky` 時必填 `fail_reason: redundant | leaky | unstable | no-signal`；冗餘填 `redundant_with`
4. **confidence**：`high` 需要 ≥ 2 個獨立證據，或 holdout 也成立；只有一個 CV 實驗 → `medium`
5. **Finding 要對業務說話**：`ops` 欄位一句話說明對營運的意義，並連到 [[Decision Card]]
6. **更新 Home 的 Now / Next**（≤ 5 行），不要在 Home 抄分數表
7. 寫完執行 `uv run pytest tests/test_knowledge_vault.py`

## 模組結束清單
- [ ] 本模組假設都有 status
- [ ] 改變決定的實驗都有 EXP；`ledger` 已重建
- [ ] ≥ 1 則 Finding（含 ops）；有可帶走的方法 → Playbook
- [ ] `00_Inbox` 已清空；Home 的 Now / Next 已更新
