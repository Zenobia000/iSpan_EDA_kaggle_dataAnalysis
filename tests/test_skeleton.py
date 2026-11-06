"""skeleton/ 是給新專案複製的骨架：結構完整、內容通用（不含 Olist）、skills/agents 一致、hooks 可用。"""
import filecmp
import importlib.util
import json
import re
from pathlib import Path

import pytest

SK = Path(__file__).resolve().parents[1] / "skeleton"
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
PROJECT_TERMS = re.compile(r"olist|order_id|差評|訂單|review_score", re.I)


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SK / ".claude" / "hooks" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("folder", ["data", "notebooks", "src", "tests", "experiments", "reports", "knowledge"])
def test_every_layer_has_readme(folder):
    assert (SK / folder / "README.md").exists()


def test_core_documents_exist():
    for f in ["README.md", "AGENTS.md", "CLAUDE.md", ".claude/settings.json", ".gitignore",
              "knowledge/00_Home.md", "knowledge/10_Brief/Validation Protocol.md",
              "knowledge/10_Brief/Project Brief.md", "knowledge/10_Brief/Data Brief.md",
              "knowledge/10_Brief/Decision Card.md"]:
        assert (SK / f).exists(), f
    assert (SK / "CLAUDE.md").read_text(encoding="utf-8").startswith("@AGENTS.md")


def test_skeleton_ships_no_analysis_code():
    code = [p for p in SK.rglob("*.py") if ".claude" not in p.parts] + list(SK.rglob("*.ipynb"))
    assert code == [], f"骨架不應附分析程式碼：{code}"


def test_skeleton_is_project_neutral():
    hits = [f"{p.relative_to(SK)}:{m.group()}" for p in SK.rglob("*")
            if p.is_file() and p.suffix in {".md", ".py", ".json", ".yaml"}
            for m in PROJECT_TERMS.finditer(p.read_text(encoding="utf-8"))]
    assert hits == []


def test_codex_skills_mirror_claude_skills():
    def diffs(c):
        return c.left_only + c.right_only + c.diff_files + [x for s in c.subdirs.values() for x in diffs(s)]
    assert diffs(filecmp.dircmp(SK / ".claude" / "skills", SK / ".agents" / "skills")) == []


def test_skills_and_agents_are_consistent():
    skills = {p.parent.name for p in (SK / ".claude" / "skills").glob("*/SKILL.md")}
    for p in (SK / ".claude" / "skills").glob("*/SKILL.md"):
        head = p.read_text(encoding="utf-8").split("---")[1]
        assert re.search(rf"^name:\s*{p.parent.name}\s*$", head, re.M) and "description:" in head, p
    for a in (SK / ".claude" / "agents").glob("*.md"):
        line = re.search(r"^skills:\s*(.+)$", a.read_text(encoding="utf-8"), re.M).group(1)
        used = {s.strip() for s in line.split(",")}
        assert used <= skills, f"{a.name}: {used - skills}"
    agents_md = (SK / "AGENTS.md").read_text(encoding="utf-8")
    assert all(s in agents_md for s in skills), "AGENTS.md 的 skill 表要列出所有 skill"


def test_validation_agent_is_read_only():
    head = (SK / ".claude" / "agents" / "validation-agent.md").read_text(encoding="utf-8").split("---")[1]
    tools = re.search(r"^tools:\s*(.+)$", head, re.M).group(1)
    assert "Write" not in tools and "Edit" not in tools


def test_vault_links_resolve():
    vault = SK / "knowledge"
    names = {p.stem for p in vault.rglob("*.md")}
    broken = [f"{p.name} → {t}" for p in vault.rglob("*.md") if "templates" not in p.parts
              for t in LINK.findall(CODE.sub("", p.read_text(encoding="utf-8"))) if t.strip() not in names]
    assert broken == []


def test_settings_json_is_valid():
    s = json.loads((SK / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert {"PreToolUse", "PostToolUse"} <= set(s["hooks"])


H = "data/" + "holdout"
R = "data/" + "raw"


@pytest.mark.parametrize("tool, tin, blocked", [
    ("Write", {"file_path": f"/p/{R}/x.csv"}, True),
    ("Read", {"file_path": f"/p/{H}/labels.csv"}, True),
    ("Bash", {"command": f"rm {R}/a.csv"}, True),
    ("Read", {"file_path": f"/p/{R}/x.csv"}, False),
    ("Write", {"file_path": "/p/data/processed/x.parquet"}, False),
    ("Bash", {"command": "python -m pytest"}, False),
])
def test_guard_hook(tool, tin, blocked):
    guard = _load("guard_paths")
    assert (guard.check({"tool_name": tool, "tool_input": tin}) is not None) is blocked


def test_post_edit_hook_watches_src_only():
    post = _load("post_edit_tests")
    assert post.should_run({"tool_input": {"file_path": "/p/src/pkg/features/a.py"}})
    assert not post.should_run({"tool_input": {"file_path": "/p/notebooks/R1-x.py"}})
