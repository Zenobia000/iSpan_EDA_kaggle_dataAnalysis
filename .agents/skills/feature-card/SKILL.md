---
name: feature-card
description: M3 — 設計一個特徵前先寫 feature card（假設→定義→T0 可得性→洩漏風險→預期方向），再實作成 features/ 群組。當學員要新增特徵、做特徵工程、或把 notebook 裡的特徵升級進 pipeline 時使用。
---

# Feature Card → 實作

## 1. 先寫卡（沒有卡不寫程式）

```markdown
#### F<n>：<特徵名稱，snake_case，不可用 review_ / order_delivered_ 開頭>
- 來源假設：H<n>
- 定義：<精確公式，含分母為 0、缺失如何處理>
- 需要的表與欄位：<...>
- T0 可得性：<每個用到的欄位為什麼在下單當下已知>
- 洩漏風險：<無 / 有：怎麼避免（例：只用 review_answer_timestamp < T0）>
- 預期方向：<值越大 → 差評機率越高/低>
- 歸屬群組：<既有群組 or 新群組名>
```

## 2. 實作規範（AGENTS.md「程式碼分工」）

- 檔案：`src/olist_course/features/<group>.py`，介面 `build(base, tables) -> DataFrame`
  - 回傳與 `base` 相同 index、只含新欄位；不修改 `base` / `tables`（不可變）
  - 時間比較一律嚴格小於 T0；歷史聚合參考 `features/history.py` 的 `_prior_counts`（merge_asof, allow_exact_matches=False）
- 登記：`features/registry.py` 的 `FEATURE_GROUPS`，並在 `FEATURE_SETS` 加一個「前一組 + 新群組」的組合
- 測試：
  - `tests/test_leakage.py` 會**自動**對新群組跑擾動測試，必須通過
  - 在 `tests/test_features.py` 補值域 / 方向 / 缺失處理測試（用 `tests/conftest.py` 的合成資料）

## 3. 驗收

```bash
uv run pytest tests/test_leakage.py tests/test_features.py
```

通過後，交給 ablation-run 量增益；沒有增益的特徵也要保留卡片並寫「無增益」的結論。

## 沉澱
feature card 本身就存成 `knowledge/40_Features/F-xxx <名稱>.md`（模板 Feature），`hypothesis` 連到來源假設；ablation 後回寫 `status` 與驗證紀錄。
