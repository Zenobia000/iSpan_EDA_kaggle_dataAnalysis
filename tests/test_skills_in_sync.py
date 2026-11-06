import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sync_skills", ROOT / "scripts" / "sync_skills.py")
sync_skills = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_skills)


def test_agents_skills_match_claude_skills():
    problems = sync_skills.diff()
    assert problems == [], "請執行 uv run python scripts/sync_skills.py：\n" + "\n".join(problems)


def test_every_skill_has_name_and_description():
    skills = list((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
    assert len(skills) >= 8
    for skill in skills:
        head = skill.read_text(encoding="utf-8").split("---")[1]
        assert re.search(r"^name:\s*" + skill.parent.name + r"\s*$", head, re.M), skill
        assert re.search(r"^description:\s*\S", head, re.M), skill


def test_agents_reference_existing_skills():
    names = {p.parent.name for p in (ROOT / ".claude" / "skills").glob("*/SKILL.md")}
    for agent in (ROOT / ".claude" / "agents").glob("*.md"):
        m = re.search(r"^skills:\s*(.+)$", agent.read_text(encoding="utf-8"), re.M)
        if m:
            used = {s.strip() for s in m.group(1).split(",")}
            assert used <= names, f"{agent.name} 引用不存在的 skill：{used - names}"


def test_sync_roundtrip(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    (src / "a").mkdir(parents=True)
    (src / "a" / "SKILL.md").write_text("x")
    assert sync_skills.diff(src, dst)
    sync_skills.sync(src, dst)
    assert sync_skills.diff(src, dst) == []
