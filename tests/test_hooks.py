"""Claude Code hooks 的行為測試（直接呼叫 check / should_run，不需啟動 Claude）。"""
import importlib.util
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parents[1] / ".claude" / "hooks"
H = "data/" + "holdout"  # 拆開寫，避免本檔內容觸發守門 hook 的字串比對


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HOOKS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


guard = _load("guard_paths")
post = _load("post_edit_tests")


@pytest.mark.parametrize(
    "tool, tin",
    [
        ("Write", {"file_path": "/repo/data/raw/x.csv"}),
        ("Edit", {"file_path": "C:\\repo\\data\\raw\\olist_orders_dataset.csv"}),
        ("Read", {"file_path": f"/repo/{H}/labels.csv"}),
        ("Grep", {"pattern": "1", "path": f"/repo/{H}"}),
        ("Bash", {"command": f"cat {H}/labels.csv"}),
        ("Bash", {"command": "echo x > data/raw/a.csv"}),
        ("Bash", {"command": "rm -f data/raw/olist_orders_dataset.csv"}),
        ("Bash", {"command": "sed -i 's/a/b/' data/raw/x.csv"}),
        ("Bash", {"command": "cp /tmp/x.csv data/raw/x.csv"}),
    ],
)
def test_guard_blocks(tool, tin):
    assert guard.check({"tool_name": tool, "tool_input": tin}) is not None


@pytest.mark.parametrize(
    "tool, tin",
    [
        ("Read", {"file_path": "/repo/data/raw/olist_orders_dataset.csv"}),
        ("Write", {"file_path": "/repo/data/processed/base.parquet"}),
        ("Bash", {"command": "head -3 data/raw/olist_orders_dataset.csv"}),
        ("Bash", {"command": "cp data/raw/olist_orders_dataset.csv /tmp/o.csv"}),
        ("Bash", {"command": "uv run python scripts/download_data.py"}),
        ("Bash", {"command": "uv run pytest"}),
    ],
)
def test_guard_allows(tool, tin):
    assert guard.check({"tool_name": tool, "tool_input": tin}) is None


def test_post_edit_only_watches_package_python():
    assert post.should_run({"tool_input": {"file_path": "/r/src/olist_course/features/geo.py"}})
    assert not post.should_run({"tool_input": {"file_path": "/r/notebooks/M3.ipynb"}})
    assert not post.should_run({"tool_input": {"file_path": "/r/docs/x.md"}})
