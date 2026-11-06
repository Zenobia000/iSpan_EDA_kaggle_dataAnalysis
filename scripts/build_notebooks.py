"""由 scripts/notebook_src/m*.py 產生講師解答版與學員版 notebook（單一來源，避免兩版漂移）。

cell 種類：
  ("md", text)                       兩版相同的 markdown
  ("code", src)                      兩版相同的程式
  ("sol", src, todo)                 解答版放 src；學員版放 todo（TODO 骨架）
  ("ans", text)                      解答版放參考答案 markdown；學員版放「✍️ 你的答案」

用法：uv run python scripts/build_notebooks.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "scripts" / "notebook_src"
OUT_STUDENT = ROOT / "notebooks"
OUT_SOLUTION = ROOT / "notebooks" / "solutions"
KERNEL = {"display_name": "Python 3", "language": "python", "name": "python3"}


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render(cells: list[tuple], solution: bool) -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook(metadata={"kernelspec": KERNEL})
    for cell in cells:
        kind = cell[0]
        if kind == "md":
            nb.cells.append(nbf.v4.new_markdown_cell(cell[1].strip()))
        elif kind == "code":
            nb.cells.append(nbf.v4.new_code_cell(cell[1].strip()))
        elif kind == "sol":
            nb.cells.append(nbf.v4.new_code_cell((cell[1] if solution else cell[2]).strip()))
        elif kind == "ans":
            body = f"**參考答案**\n\n{cell[1].strip()}" if solution else "✍️ **你的答案：**\n\n"
            nb.cells.append(nbf.v4.new_markdown_cell(body))
        else:
            raise ValueError(f"未知 cell 種類 {kind!r}")
    return nb


def main() -> None:
    import sys

    sys.path.insert(0, str(SRC_DIR))
    OUT_SOLUTION.mkdir(parents=True, exist_ok=True)
    for src in sorted(SRC_DIR.glob("m*.py")):
        mod = _load(src)
        nbf.write(render(mod.CELLS, solution=False), OUT_STUDENT / f"{mod.NAME}.ipynb")
        nbf.write(render(mod.CELLS, solution=True), OUT_SOLUTION / f"{mod.NAME}_solution.ipynb")
        print(f"[ok] {mod.NAME}")


if __name__ == "__main__":
    main()
