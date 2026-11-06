# 資料科學專案骨架：人類定邊界，AI 跑實驗

```bash
cp -r skeleton ../my-project && cd ../my-project && git init
```

這個骨架**不附任何分析程式碼**。真正有價值、跨專案可重用的資產是三樣東西：

1. **資料夾分層**：每一層的 `README.md` 寫清楚放什麼、不放什麼
2. **定義文件**：`knowledge/10_Brief/`，由人類填寫專案的邊界
3. **Agents 與 skills**：`.claude/`（Claude Code）與 `.agents/`（Codex），規範 AI 怎麼工作

程式碼由 AI 在對話中當場產生，大多用完即丟。**被證明有價值的程式碼才「升級」進 `src/`**，並且要附上測試。

---

## 工作流（一輪 = 一次「探索 → 收斂」）

```
① 人類：定邊界（define-boundaries）
   目標與決策 / 預測當下可用的資訊 / 驗證方法 / 停止條件
   → 寫進 knowledge/10_Brief/，之後所有 agent 都以這裡為準
        │
        ▼
② AI 執行（每一輪）
   EDA Agent      探索資料與異常、驗證假設          → notebooks/、knowledge/30_Hypotheses
   Feature Agent  提出並建構特徵、自我檢查洩漏      → notebooks/ → (升級) src/、knowledge/40_Features
   Model Agent    建模、ablation、參數搜尋          → experiments/log.jsonl
   Validation     CV / OOF / Ablation / 洩漏檢查（唯讀，負責質疑）
        │
        ▼
③ 人類審查（round-review）
   這輪改變了什麼、哪些增益是穩健的、有沒有洩漏、停止條件達成沒
   → 決定：下一輪 / 停止 / 提交      → knowledge/60_Findings、00_Home
```

| 誰 | 負責 | 不負責 |
|---|---|---|
| 人類 | 邊界（10_Brief）、每輪的去留決定、驗收 | 寫重複的分析程式碼 |
| AI agents | 探索、實作、實驗、記錄、提出下一步 | 修改邊界、讀取 holdout 答案、自行宣布「完成」 |

## 資料夾地圖

| 資料夾 | 放什麼 | 程式碼的生命週期 |
|---|---|---|
| `knowledge/` | 定義文件、假設、特徵、實驗、發現（Obsidian vault） | — |
| `data/` | 原始資料（唯讀）→ 中間產物 → 建模資料；holdout 由人類保管 | — |
| `notebooks/` | 探索、原型、一次性分析（notebook 或 .py 都可以） | **用完即丟** |
| `src/` | 升級過的程式碼：被重用、或會影響最終模型的程式 | 長期維護、必須有測試 |
| `tests/` | `src/` 的測試，特別是洩漏擾動測試 | 長期維護 |
| `experiments/` | 實驗紀錄 `log.jsonl`（每次比較一行） | 只追加 |
| `reports/` | 給決策者看的產出（報告、圖） | 每輪更新 |

每個資料夾都有自己的 `README.md`，AI 依照那份文件決定程式碼與檔案的位置。

## 第一天要做的事

1. 把資料放進 `data/raw/`，在 `data/README.md` 登記來源
2. 開啟 Claude Code 或 Codex，對它說：「**用 define-boundaries 幫我定義這個專案**」
   AI 會訪談你，並產出 `knowledge/10_Brief/` 的四份文件。**這一步必須由人類拍板。**
3. 對 AI 說：「**用 data-card 整理資料**」，接著「**開始第一輪 EDA**」
4. 每輪結束時說：「**round-review**」

## 適用的問題類型

| 類型 | 驗證方法（在 Validation Protocol 中選定） | 特別注意 |
|---|---|---|
| 二元 / 多元分類、迴歸 | 時間切分、群組 K-fold、K-fold | 預測時點 T0；群組洩漏（同一個人出現在 train 與 valid） |
| 時間序列預測 | rolling-origin backtest | 特徵只能用預測起點之前的值；必須和 seasonal naive 基準比較 |
| Kaggle 競賽 | 本地 CV + 官方 LB 當 holdout | CV 與 LB 的落差要追蹤 |

## Obsidian

用 Obsidian「Open folder as vault」開啟 `knowledge/`，從 `00_Home.md` 進入。

## 跨平台與工具
- Hooks 用 `python3` 執行；Windows 若沒有 `python3` 指令，把 `.claude/settings.json` 中的 `python3` 改成 `py`
- 修改 skill 一律改 `.claude/skills/`，再執行 `rm -rf .agents/skills && cp -r .claude/skills .agents/skills` 同步給 Codex
- `pre-commit install` 之後，Codex 與手動 commit 也會跑洩漏測試
