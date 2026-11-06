import pandas as pd
import pytest

from olist_course import config
from olist_course.dataset import make_dataset
from olist_course.diagnostics import adversarial_validation, permutation_importance, slice_report
from olist_course.experiment import run_experiment
from olist_course.score import score_submission, validate_submission, write_leaderboard
from olist_course.submit import make_submission


def test_submission_roundtrip(base, tables, tmp_path):
    ds = make_dataset(base, tables, "raw+time")
    path = make_submission("raw+time", model="logreg", name="me", dataset=ds, out_dir=tmp_path)
    holdout = base[base["order_id"].isin(ds.order_id[ds.split == "holdout"])]
    labels = tmp_path / "labels.csv"
    holdout[["order_id", config.TARGET]].to_csv(labels, index=False)
    s = score_submission(path, labels)
    assert s["submission"] == "me" and 0 <= s["pr_auc"] <= 1
    board = write_leaderboard([s, {**s, "submission": "b", "pr_auc": 0.0}], tmp_path / "lb.md")
    assert board.iloc[0]["submission"] == "me"


@pytest.mark.parametrize(
    "sub, msg",
    [
        (pd.DataFrame({"id": ["a"], "score": [1.0]}), "欄位"),
        (pd.DataFrame({"order_id": ["a", "a"], "score": [1.0, 1.0]}), "重複"),
        (pd.DataFrame({"order_id": ["a"], "score": [1.0]}), "缺少"),
        (pd.DataFrame({"order_id": ["a", "b"], "score": [1.0, None]}), "NaN"),
    ],
)
def test_validate_submission_errors(sub, msg):
    labels = pd.DataFrame({"order_id": ["a", "b"], config.TARGET: [0, 1]})
    with pytest.raises(ValueError, match=msg):
        validate_submission(sub, labels)


def test_diagnostics_run(base, tables, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "EXPERIMENT_LOG", tmp_path / "log.jsonl")
    ds = make_dataset(base, tables, "raw+time")
    r = run_experiment("raw+time", model="lgbm", dataset=ds, log=False)
    pi = permutation_importance(r, ds, n_repeats=2)
    assert set(pi["feature"]) == set(ds.X.columns)
    auc, imp = adversarial_validation(ds, "train", "valid")
    assert 0 <= auc <= 1 and len(imp) == ds.X.shape[1]
    rep = slice_report(r, base, "customer_state", min_size=5)
    assert {"n", "low_rate", "pr_auc"} <= set(rep.columns)
