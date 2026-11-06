"""Obsidian 知識庫的結構檢查：斷鏈、ID 唯一、ID 與檔名一致、frontmatter type、自動區塊保留人寫筆記。"""
import importlib.util
import re
from collections import Counter
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "knowledge"
TEMPLATES = VAULT / "90_Meta" / "templates"
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
FENCE = re.compile(r"```.*?```|`[^`\n]*`", re.S)  # 程式碼區塊與行內程式碼不算連結
ID_PREFIX = {"30_Hypotheses": "H-", "40_Features": "F-", "50_Experiments": "EXP-",
             "60_Findings": "FND-", "70_Decisions": "D-"}


def notes():
    return [p for p in VAULT.rglob("*.md") if TEMPLATES not in p.parents and ".obsidian" not in p.parts]


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    return dict(re.findall(r"^(\w+):\s*(.*?)\s*(?:#.*)?$", block, re.M))


def test_vault_has_core_structure():
    for d in ["10_Brief", "20_Data", *ID_PREFIX, "80_Concepts", "90_Meta/templates"]:
        assert (VAULT / d).is_dir(), d
    for f in ["00_Home.md", "10_Brief/Project Brief.md", "10_Brief/Data Brief.md"]:
        assert (VAULT / f).exists(), f


def test_no_broken_wikilinks():
    names = {p.stem for p in notes()}
    broken = []
    for p in notes():
        body = FENCE.sub("", p.read_text(encoding="utf-8"))
        broken += [f"{p.relative_to(VAULT)} → [[{t}]]" for t in LINK.findall(body) if t.strip() not in names]
    assert broken == [], "\n".join(broken)


def test_ids_unique_and_match_filename():
    ids = []
    for folder, prefix in ID_PREFIX.items():
        for p in (VAULT / folder).glob("*.md"):
            fm = frontmatter(p.read_text(encoding="utf-8"))
            assert fm.get("id", "").startswith(prefix), p.name
            assert p.stem.startswith(fm["id"] + " "), f"{p.name} 檔名需以 {fm['id']} 開頭"
            ids.append(fm["id"])
    dup = [i for i, n in Counter(ids).items() if n > 1]
    assert dup == []


@pytest.mark.parametrize("folder, type_", [("30_Hypotheses", "hypothesis"), ("40_Features", "feature"),
                                           ("50_Experiments", "experiment"), ("60_Findings", "finding"),
                                           ("70_Decisions", "decision"), ("80_Concepts", "concept")])
def test_notes_have_type(folder, type_):
    for p in (VAULT / folder).glob("*.md"):
        assert frontmatter(p.read_text(encoding="utf-8")).get("type") == type_, p.name


def test_feature_status_is_valid():
    allowed = {"proposed", "prototype", "robust", "no-gain", "leaky", "in-pipeline"}
    for p in (VAULT / "40_Features").glob("*.md"):
        assert frontmatter(p.read_text(encoding="utf-8")).get("status") in allowed, p.name


def test_data_notes_preserve_human_section(tmp_path):
    spec = importlib.util.spec_from_file_location("bdn", ROOT / "scripts" / "build_data_notes.py")
    bdn = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bdn)
    df = pd.DataFrame({"order_id": ["a", "b"], "order_status": ["delivered", None]})
    path = bdn.write_note("orders", df, tmp_path)
    path.write_text(path.read_text(encoding="utf-8").replace("- 奇怪的值：", "- 奇怪的值：我的觀察"), encoding="utf-8")
    bdn.write_note("orders", pd.concat([df, df.assign(order_id=["c", "d"])]), tmp_path)
    text = path.read_text(encoding="utf-8")
    assert "我的觀察" in text and "列數：4" in text and "⛔ T0 之後" in text
