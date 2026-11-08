"""前處理 + 模型的 sklearn Pipeline。所有填補/編碼參數只在訓練 fold 上 fit。"""
from __future__ import annotations

from collections.abc import Sequence

from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from olist_course.config import SEED

MODELS = ("dummy", "logreg", "rf", "lgbm")


def _preprocessor(model: str, numeric: Sequence[str], categorical: Sequence[str]) -> ColumnTransformer:
    cat_imputer = SimpleImputer(strategy="constant", fill_value="missing")
    if model == "lgbm":
        num = SimpleImputer(strategy="median")
        cat = make_pipeline(cat_imputer, OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
    else:
        num_steps = [SimpleImputer(strategy="median")] + ([StandardScaler()] if model == "logreg" else [])
        num = make_pipeline(*num_steps)
        cat = make_pipeline(cat_imputer, OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=50))
    return ColumnTransformer([("num", num, list(numeric)), ("cat", cat, list(categorical))])


def _estimator(model: str, seed: int):
    if model == "dummy":
        return DummyClassifier(strategy="prior")
    if model == "logreg":
        return LogisticRegression(max_iter=2000, class_weight="balanced")
    if model == "rf":
        return RandomForestClassifier(n_estimators=300, min_samples_leaf=20, n_jobs=-1,
                                      class_weight="balanced_subsample", random_state=seed)
    if model == "lgbm":
        return LGBMClassifier(n_estimators=400, learning_rate=0.03, num_leaves=31, min_child_samples=50,
                              subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                              random_state=seed, verbose=-1)
    raise ValueError(f"未知模型 {model!r}；可用：{MODELS}")


def build_pipeline(model: str, numeric: Sequence[str], categorical: Sequence[str], seed: int = SEED) -> Pipeline:
    return Pipeline([("prep", _preprocessor(model, numeric, categorical)), ("model", _estimator(model, seed))])
