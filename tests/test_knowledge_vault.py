"""Obsidian 知識庫的結構檢查：斷鏈、ID 唯一、ID 與檔名一致、frontmatter type、自動區塊保留人寫筆記。"""
import importlib.util
import json
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
ID_PREFIX = {"30_Hypotheses": "H-", "40_Features": "F-", "50_Runs": "EXP-", "60_Findings": "FND-"}


def notes():
    return [p for p in VAULT.rglob("*.md") if TEMPLATES not in p.parents and ".obsidian" not in p.parts]


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    return dict(re.findall(r"^(\w+):\s*(.*?)\s*(?:#.*)?$", block, re.M))


def test_vault_has_core_structure():
    for d in ["10_Brief", "20_Data", *ID_PREFIX, "80_Playbook", "90_Meta/templates"]:
        assert (VAULT / d).is_dir(), d
    for f in ["00_Home.md", "10_Brief/Decision Card.md", "10_Brief/Project Brief.md", "10_Brief/Data Brief.md",
              "10_Brief/Validation Protocol.md", "50_Runs/ledger.md"]:
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
        for p in (VAULT / folder).glob(f"{prefix}*.md"):
            fm = frontmatter(p.read_text(encoding="utf-8"))
            assert fm.get("id", "").startswith(prefix), p.name
            assert p.stem.startswith(fm["id"] + " "), f"{p.name} 檔名需以 {fm['id']} 開頭"
            ids.append(fm["id"])
    dup = [i for i, n in Counter(ids).items() if n > 1]
    assert dup == []


@pytest.mark.parametrize("folder, pattern, type_", [
    ("30_Hypotheses", "H-*.md", "hypothesis"), ("40_Features", "F-*.md", "feature"),
    ("50_Runs", "EXP-*.md", "experiment"), ("60_Findings", "FND-*.md", "finding"), ("80_Playbook", "*.md", "concept")])
def test_notes_have_type(folder, pattern, type_):
    for p in (VAULT / folder).glob(pattern):
        assert frontmatter(p.read_text(encoding="utf-8")).get("type") == type_, p.name


def test_feature_status_and_fail_reason():
    allowed = {"proposed", "prototype", "robust", "no-gain", "leaky", "in-pipeline"}
    reasons = {"redundant", "leaky", "unstable", "no-signal"}
    for p in (VAULT / "40_Features").glob("F-*.md"):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        assert fm.get("status") in allowed, p.name
        if fm["status"] in {"no-gain", "leaky"}:
            assert fm.get("fail_reason") in reasons, f"{p.name} 失敗的特徵必須填 fail_reason"


def _log_entries() -> dict[str, dict]:
    entries = {}
    for path in (ROOT / "experiments").glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                e = json.loads(line)
                entries[e.get("run_id", "")] = e
    return entries


def test_experiment_notes_trace_to_logged_runs():
    """數字不准估計：EXP 必須引用真實 run_id；frontmatter 的 pr_auc 必須等於某個被引用的紀錄。"""
    entries = _log_entries()
    for p in (VAULT / "50_Runs").glob("EXP-*.md"):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        ids = json.loads(fm.get("run_ids") or "[]")
        assert ids, f"{p.name} 缺少 run_ids"
        missing = [i for i in ids if i not in entries]
        assert not missing, f"{p.name} 引用不存在的 run_id：{missing}"
        if fm.get("pr_auc"):
            claimed = float(fm["pr_auc"])
            logged = [entries[i].get("pr_auc_mean", entries[i].get("pr_auc")) for i in ids]
            assert any(v is not None and abs(v - claimed) < 5e-4 for v in logged), \
                f"{p.name} 的 pr_auc={claimed} 對不上任何引用的紀錄 {logged}"


def test_findings_state_ops_meaning():
    for p in (VAULT / "60_Findings").glob("FND-*.md"):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        assert fm.get("ops", "").strip('" '), f"{p.name} 缺少 ops（對營運的意義）"
        assert fm.get("confidence") in {"high", "medium", "low"}, p.name


def test_ledger_is_up_to_date():
    spec = importlib.util.spec_from_file_location("bl", ROOT / "scripts" / "build_ledger.py")
    bl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bl)
    from olist_course.experiment import read_log

    log = read_log(include_reference=True)
    if log.empty:
        pytest.skip("尚無實驗紀錄")
    expected = bl.render(log)
    assert (VAULT / "50_Runs" / "ledger.md").read_text(encoding="utf-8") == expected, \
        "請執行 uv run python scripts/build_ledger.py"


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
