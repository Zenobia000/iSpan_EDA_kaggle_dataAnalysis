# knowledge/ — Obsidian 知識庫

用 Obsidian「Open folder as vault」開啟**這個資料夾**（不是 repo 根目錄，避免 .venv、src 等雜訊進入圖譜）。

- 入口：`00_Home.md`
- 模板：`90_Meta/templates/`（核心外掛 Templates 已設定）
- 選用外掛：Dataview（`00_Home` 的動態表格）
- 命名：`<ID> <標題>.md`，例如 `F-005 賣家歷史差評率 seller_prior_low_rate.md`；Finding 的標題要是一句完整的結論
- 連結一律用 `[[ ]]`；程式碼位置用反引號寫 repo 相對路徑（Obsidian 不能連到 vault 外）
- `20_Data/` 由 `uv run python scripts/build_data_notes.py` 產生；只會覆寫 `AUTO` 區塊，人寫的筆記會保留
- AI（Claude Code / Codex）依 `knowledge-capture` skill 寫入；規則見 repo 根目錄 `AGENTS.md`「知識庫」一節
