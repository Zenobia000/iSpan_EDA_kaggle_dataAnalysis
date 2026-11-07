"""組裝 deck：掃描 slides/*.html → 更新 index.html 的 MANIFEST，並產生 print.html（給 PDF 用）。

用法：uv run python build.py            # 只組裝
      uv run python build.py --pdf      # 組裝並用本機 Chrome 輸出 deck.pdf
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
TITLE = re.compile(r"<title>(.*?)</title>", re.S)


def slides() -> list[dict]:
    out = []
    for f in sorted((ROOT / "slides").glob("*.html")):
        m = TITLE.search(f.read_text(encoding="utf-8"))
        out.append({"file": f"slides/{f.name}", "label": m.group(1).strip() if m else f.stem})
    return out


def write_index(items: list[dict]) -> None:
    idx = ROOT / "index.html"
    text = idx.read_text(encoding="utf-8")
    manifest = "window.DECK_MANIFEST = " + json.dumps(items, ensure_ascii=False, indent=2) + ";"
    text = re.sub(r"window\.DECK_MANIFEST = \[.*?\];", lambda _: manifest, text, count=1, flags=re.S)
    text = re.sub(r"<title>.*?</title>", "<title>資料科學心法：從問題定義到模型落地</title>", text, count=1, flags=re.S)
    idx.write_text(text, encoding="utf-8")


def write_print(items: list[dict]) -> None:
    frames = "\n".join(f'<iframe src="{i["file"]}" width="1920" height="1080" scrolling="no"></iframe>' for i in items)
    (ROOT / "print.html").write_text(f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>print</title>
<style>@page{{size:1920px 1080px;margin:0}}html,body{{margin:0;padding:0}}
iframe{{display:block;border:0;width:1920px;height:1080px;page-break-after:always;break-after:page}}</style>
</head><body>{frames}</body></html>""", encoding="utf-8")


def export_pdf() -> None:
    out = ROOT / "deck.pdf"
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=60000", f"--print-to-pdf={out}", (ROOT / "print.html").as_uri()],
                   check=True, capture_output=True, timeout=600)
    print(f"[ok] {out}")


def main() -> None:
    items = slides()
    write_index(items)
    write_print(items)
    print(f"[ok] {len(items)} slides → index.html, print.html")
    if "--pdf" in sys.argv:
        export_pdf()


if __name__ == "__main__":
    main()
