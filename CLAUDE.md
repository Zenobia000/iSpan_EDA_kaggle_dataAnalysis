@AGENTS.md

# Claude Code 專屬

## Subagents（`.claude/agents/`）

| subagent | 什麼時候叫 |
|---|---|
| `eda-analyst` | M2：驗證一張假設卡、產出圖表與結論 |
| `feature-engineer` | M3：把一張 feature card 實作成 `features/` 群組＋測試 |
| `model-runner` | M4/M5：跑 ablation、比較模型、產 submission |
| `validation-auditor` | 任何「分數變好了」之後：獨立審查洩漏與增益穩健性（唯讀） |

使用方式：「請用 validation-auditor 審查剛剛 all_safe 相對 raw 的增益」。

## Hooks（`.claude/settings.json`）

- `guard_paths.py`（PreToolUse）：擋寫入 `data/raw/`、擋讀取 `data/holdout/`。被擋時請向學員說明原因，不要嘗試繞過。
- `post_edit_tests.py`（PostToolUse）：改到 `src/olist_course/**/*.py` 後自動跑 `tests/test_leakage.py`；失敗時必須先修好。
- `stop_log_check.py`（Stop）：本輪有跑實驗卻沒有新增 `experiments/log.jsonl` 紀錄時提醒。

## 注意

不要建立 `CLAUDE.local.md`（會讓 Claude Code 停止讀取 AGENTS.md 的設定）。
