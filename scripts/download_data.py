"""下載 Olist Brazilian E-Commerce 資料集到 data/raw/。

前置：~/.kaggle/access_token（Kaggle → Settings → API → Create New Token；舊版 kaggle.json 亦可）。
用法：uv run python scripts/download_data.py
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

DATASET = "olistbr/brazilian-ecommerce"
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
EXPECTED_FILES = {
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
}


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    missing = EXPECTED_FILES - {p.name for p in RAW_DIR.glob("*.csv")}
    if not missing:
        print(f"[skip] 9 個檔案都已存在於 {RAW_DIR}")
        return 0
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("請先 `uv sync` 安裝 kaggle 套件", file=sys.stderr)
        return 1
    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as exc:  # noqa: BLE001 - 轉成友善訊息
        print(f"Kaggle 認證失敗：{exc}\n請確認 ~/.kaggle/access_token（或 kaggle.json）存在，詳見 README 步驟 3", file=sys.stderr)
        return 1
    api.dataset_download_files(DATASET, path=str(RAW_DIR), quiet=False)
    for zip_path in RAW_DIR.glob("*.zip"):
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(RAW_DIR)
        zip_path.unlink()
    still_missing = EXPECTED_FILES - {p.name for p in RAW_DIR.glob("*.csv")}
    if still_missing:
        print(f"下載後仍缺：{sorted(still_missing)}", file=sys.stderr)
        return 1
    print(f"[ok] 已下載到 {RAW_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
