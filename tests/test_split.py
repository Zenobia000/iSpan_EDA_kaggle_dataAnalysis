import pandas as pd

from olist_course import config
from olist_course.split import assign_split, time_cv_folds


def test_assign_split_boundaries_are_left_closed():
    t = pd.Series(pd.to_datetime([
        "2016-12-31 00:00", "2017-01-01 00:00", "2018-02-28 23:59", "2018-03-01 00:00",
        "2018-05-31 00:00", "2018-06-01 00:00", "2018-08-31 00:00", "2018-09-01 00:00",
    ]))
    got = assign_split(t).tolist()
    assert got == ["out_of_range", "train", "train", "valid", "valid", "holdout", "holdout", "out_of_range"]


def test_splits_do_not_overlap_in_time(base):
    s = assign_split(base[config.T0_COL])
    train_max = base.loc[s == "train", config.T0_COL].max()
    valid_min = base.loc[s == "valid", config.T0_COL].min()
    assert pd.isna(valid_min) or train_max < valid_min


def test_time_cv_folds_are_expanding_and_forward_only():
    t = pd.Series(pd.date_range("2017-01-01", "2018-05-31", freq="D"))
    folds = time_cv_folds(t)
    assert len(folds) == len(config.CV_FOLD_MONTHS)
    for (tr, va), month in zip(folds, config.CV_FOLD_MONTHS):
        assert t[tr].max() < t[va].min()
        assert (t[va].dt.strftime("%Y-%m") == month).all()
    assert len(folds[0][0]) < len(folds[1][0]) < len(folds[2][0])
