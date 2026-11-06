import json

import numpy as np
import pandas as pd
import pytest

from olist_course import config
from olist_course.dataset import make_dataset
from olist_course.evaluate import lift_at_k, precision_at_k, score_all
from olist_course.experiment import compare, run_experiment
from olist_course.pipeline import MODELS, build_pipeline


def test_precision_and_lift_at_k():
    y = np.array([1, 0, 1, 0, 0, 0, 0, 0, 0, 0])
    s = np.array([.9, .8, .7, .1, .1, .1, .1, .1, .1, .1])
    assert precision_at_k(y, s, 0.2) == 0.5
    assert lift_at_k(y, s, 0.2) == pytest.approx(2.5)
    assert set(score_all(y, s)) == {"pr_auc", "roc_auc", "p_at_k", "lift_at_k", "base_rate"}


def test_holdout_labels_are_masked(base, tables):
    ds = make_dataset(base, tables, "raw")
    assert ds.y[ds.split == "holdout"].isna().all()
    assert ds.y[ds.split != "holdout"].notna().all()


@pytest.mark.parametrize("model", MODELS)
def test_every_model_fits(base, tables, model):
    ds = make_dataset(base, tables, "raw+time")
    lab = ds.subset(ds.y.notna().to_numpy())
    num = [c for c in lab.X.columns if c not in lab.categorical]
    pipe = build_pipeline(model, num, lab.categorical).fit(lab.X, lab.y)
    assert pipe.predict_proba(lab.X)[:, 1].shape == (len(lab.X),)


def test_unknown_model_raises():
    with pytest.raises(ValueError):
        build_pipeline("xgb", ["a"], [])


def test_run_experiment_logs_and_compares(base, tables, tmp_path, monkeypatch):
    log = tmp_path / "log.jsonl"
    monkeypatch.setattr(config, "EXPERIMENT_LOG", log)
    r1 = run_experiment("raw", model="logreg", dataset=make_dataset(base, tables, "raw"), note="t")
    r2 = run_experiment("raw+time", model="logreg", dataset=make_dataset(base, tables, "raw+time"))
    lines = [json.loads(x) for x in log.read_text().splitlines()]
    assert [x["name"] for x in lines] == ["raw", "raw+time"]
    assert {"pr_auc_mean", "pr_auc_std", "overfit_gap", "git"} <= set(lines[0])
    assert len(r1.folds) == len(config.CV_FOLD_MONTHS)
    table = compare([r1, r2])
    assert table.loc["raw", "gain_vs_base"] == 0
    assert not table.loc["raw", "robust_gain"]  # 自己跟自己比不算進步
    assert table.loc["raw+time", "folds_improved"].endswith(f"/{len(config.CV_FOLD_MONTHS)}")
