"""從實際資料產生 knowledge/20_Data/<table>.md（Data Card 的自動部分）。

只覆寫 <!-- AUTO:START --> ~ <!-- AUTO:END --> 之間；其餘段落是人寫的筆記，重跑不會被覆蓋。
用法：uv run python scripts/build_data_notes.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from olist_course.config import POST_T0_COLUMNS, ROOT
from olist_course.data.load import load_tables

OUT = ROOT / "knowledge" / "20_Data"
START, END = "<!-- AUTO:START -->", "<!-- AUTO:END -->"

GRAIN = {
    "orders": ("一筆訂單", ["order_id"]),
    "items": ("訂單中的一件商品", ["order_id", "order_item_id"]),
    "payments": ("一次付款", ["order_id", "payment_sequential"]),
    "reviews": ("一則評價", ["review_id", "order_id"]),
    "customers": ("一個訂單客戶 ID（真正的人是 customer_unique_id）", ["customer_id"]),
    "sellers": ("一個商家", ["seller_id"]),
    "products": ("一個商品", ["product_id"]),
    "geolocation": ("一個郵遞區號前綴的一個座標", []),
    "category_translation": ("一個品類的葡英對照", ["product_category_name"]),
}
GRAY = {"order_approved_at"}


def t0_status(col: str) -> str:
    if col in GRAY:
        return "⚠️ 灰色（不用）"
    if col in POST_T0_COLUMNS:
        return "⛔ T0 之後"
    return "✅ T0 已知"


def _example(s: pd.Series) -> str:
    v = s.dropna()
    return "" if v.empty else str(v.iloc[0])[:30].replace("|", "/")


def render_auto(name: str, df: pd.DataFrame) -> str:
    grain, key = GRAIN[name]
    unique = "—" if not key else ("✅ 唯一" if not df.duplicated(key).any() else "❌ 有重複")
    rows = [
        f"| `{c}` | {df[c].dtype} | {df[c].isna().mean():.1%} | {df[c].nunique():,} | {t0_status(c)} | {_example(df[c])} |"
        for c in df.columns
    ]
    return "\n".join([
        START,
        f"- 一列代表：**{grain}**",
        f"- 列數：{len(df):,}　欄數：{df.shape[1]}",
        f"- 鍵 `{', '.join(key) or '無'}`：{unique}",
        "",
        "| 欄位 | 型別 | 缺失 | 唯一值 | T0 | 範例 |",
        "|---|---|---|---|---|---|",
        *rows,
        END,
    ])


def write_note(name: str, df: pd.DataFrame, out_dir: Path = OUT) -> Path:
    path = out_dir / f"{name}.md"
    auto = render_auto(name, df)
    if path.exists() and START in (text := path.read_text(encoding="utf-8")):
        head, rest = text.split(START, 1)
        tail = rest.split(END, 1)[1] if END in rest else ""
        body = head + auto + tail
    else:
        body = (f"---\ntype: table\ntable: {name}\ntags: [data]\n---\n# {name}\n\n"
                f"> 回到 [[Data Brief]]\n\n## 自動產生的 Data Card\n{auto}\n\n"
                "## 筆記（人寫）\n- 粒度與 join 風險：\n- 奇怪的值：\n- 相關假設 / 特徵：\n")
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def main() -> None:
    for name, df in load_tables().items():
        print(f"[ok] {write_note(name, df).relative_to(ROOT)}  rows={len(df):,}")


if __name__ == "__main__":
    main()
