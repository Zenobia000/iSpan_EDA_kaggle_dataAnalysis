"""notebooks/ 必須由 scripts/notebook_src/ 產生；手改 .ipynb 會被抓到。"""
import importlib.util
import sys
from pathlib import Path

import nbformat
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "notebook_src"
spec = importlib.util.spec_from_file_location("build_notebooks", ROOT / "scripts" / "build_notebooks.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
sys.path.insert(0, str(SRC))


def _sources(nb):
    return [(c.cell_type, c.source) for c in nb.cells]


@pytest.mark.parametrize("src", sorted(SRC.glob("m*.py")), ids=lambda p: p.stem)
def test_generated_notebooks_match_source(src):
    mod = build._load(src)
    student = nbformat.read(ROOT / "notebooks" / f"{mod.NAME}.ipynb", 4)
    solution = nbformat.read(ROOT / "notebooks" / "solutions" / f"{mod.NAME}_solution.ipynb", 4)
    assert _sources(student) == _sources(build.render(mod.CELLS, solution=False)), "請執行 scripts/build_notebooks.py"
    assert _sources(solution) == _sources(build.render(mod.CELLS, solution=True)), "請執行 scripts/build_notebooks.py"


def test_student_version_hides_solutions():
    for nb_path in (ROOT / "notebooks").glob("M*.ipynb"):
        text = nb_path.read_text(encoding="utf-8")
        assert "**參考答案**" not in text, nb_path.name
