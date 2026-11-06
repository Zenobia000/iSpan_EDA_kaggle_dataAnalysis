@AGENTS.md

# Claude Code 專屬

## Subagents（`.claude/agents/`）
`eda-agent` / `feature-agent` / `model-agent` / `validation-agent`。
用法：「請用 validation-agent 審查這一輪 F-003 的增益」。

## Hooks（`.claude/settings.json`）
- `guard_paths.py`（PreToolUse）：擋寫入 `data/raw/`、擋讀取 holdout 資料夾。被擋時向人類說明原因，不要嘗試繞過
- `post_edit_tests.py`（PostToolUse）：改到 `src/**/*.py` 之後，自動執行 `tests/test_leakage*.py`；失敗必須先修好

## 注意
不要建立 `CLAUDE.local.md`，它會讓 Claude Code 停止讀取 AGENTS.md。
