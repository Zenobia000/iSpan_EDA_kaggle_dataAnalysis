"""合成的小型 Olist 資料：測試不依賴 Kaggle 下載，CI / 學員機器都能跑。"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

N_ORDERS = 600
STATES = ["SP", "RJ", "MG", "RS", "BA"]
ZIPS = {"SP": "01000", "RJ": "20000", "MG": "30000", "RS": "90000", "BA": "40000"}
LATLNG = {"SP": (-23.5, -46.6), "RJ": (-22.9, -43.2), "MG": (-19.9, -43.9), "RS": (-30.0, -51.2), "BA": (-12.9, -38.5)}


def make_tables(seed: int = 0) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    order_ids = [f"o{i:04d}" for i in range(N_ORDERS)]
    purchase = pd.Timestamp("2017-01-01") + pd.to_timedelta(
        np.sort(rng.uniform(0, 600, N_ORDERS)), unit="D"
    )
    cust_ids = [f"c{i:04d}" for i in range(N_ORDERS)]
    unique_ids = [f"u{rng.integers(0, 400):04d}" for _ in range(N_ORDERS)]
    cust_state = rng.choice(STATES, N_ORDERS)
    est_days = rng.integers(10, 40, N_ORDERS)
    deliver_days = est_days + rng.integers(-10, 15, N_ORDERS)
    orders = pd.DataFrame(
        {
            "order_id": order_ids,
            "customer_id": cust_ids,
            "order_status": "delivered",
            "order_purchase_timestamp": purchase,
            "order_approved_at": purchase + pd.Timedelta(hours=2),
            "order_delivered_carrier_date": purchase + pd.Timedelta(days=3),
            "order_delivered_customer_date": purchase + pd.to_timedelta(deliver_days, unit="D"),
            "order_estimated_delivery_date": purchase + pd.to_timedelta(est_days, unit="D"),
        }
    )
    customers = pd.DataFrame(
        {
            "customer_id": cust_ids,
            "customer_unique_id": unique_ids,
            "customer_zip_code_prefix": [ZIPS[s] for s in cust_state],
            "customer_city": "x",
            "customer_state": cust_state,
        }
    )
    seller_ids = [f"s{i:02d}" for i in range(20)]
    seller_state = rng.choice(STATES, 20)
    sellers = pd.DataFrame(
        {
            "seller_id": seller_ids,
            "seller_zip_code_prefix": [ZIPS[s] for s in seller_state],
            "seller_city": "y",
            "seller_state": seller_state,
        }
    )
    product_ids = [f"p{i:03d}" for i in range(50)]
    products = pd.DataFrame(
        {
            "product_id": product_ids,
            "product_category_name": rng.choice(["cama_mesa_banho", "beleza_saude", "esporte_lazer"], 50),
            "product_name_lenght": rng.integers(10, 60, 50).astype(float),
            "product_description_lenght": rng.integers(50, 2000, 50).astype(float),
            "product_photos_qty": rng.integers(1, 6, 50).astype(float),
            "product_weight_g": rng.integers(100, 10000, 50).astype(float),
            "product_length_cm": rng.integers(10, 60, 50).astype(float),
            "product_height_cm": rng.integers(2, 40, 50).astype(float),
            "product_width_cm": rng.integers(10, 50, 50).astype(float),
        }
    )
    translation = pd.DataFrame(
        {
            "product_category_name": ["cama_mesa_banho", "beleza_saude", "esporte_lazer"],
            "product_category_name_english": ["bed_bath_table", "health_beauty", "sports_leisure"],
        }
    )
    n_lines = rng.integers(1, 3, N_ORDERS)
    rows = []
    for oid, n, t in zip(order_ids, n_lines, purchase):
        for k in range(1, n + 1):
            rows.append(
                {
                    "order_id": oid,
                    "order_item_id": k,
                    "product_id": product_ids[rng.integers(0, 50)],
                    "seller_id": seller_ids[rng.integers(0, 20)],
                    "shipping_limit_date": t + pd.Timedelta(days=5),
                    "price": float(rng.uniform(10, 300)),
                    "freight_value": float(rng.uniform(5, 50)),
                }
            )
    items = pd.DataFrame(rows)
    payments = pd.DataFrame(
        {
            "order_id": order_ids,
            "payment_sequential": 1,
            "payment_type": rng.choice(["credit_card", "boleto"], N_ORDERS),
            "payment_installments": rng.integers(1, 10, N_ORDERS),
            "payment_value": rng.uniform(20, 600, N_ORDERS),
        }
    )
    late = deliver_days > est_days
    score = np.where(late, rng.choice([1, 2, 5], N_ORDERS), rng.choice([3, 4, 5], N_ORDERS))
    answer = orders["order_delivered_customer_date"] + pd.to_timedelta(rng.integers(1, 5, N_ORDERS), unit="D")
    reviews = pd.DataFrame(
        {
            "review_id": [f"r{i:04d}" for i in range(N_ORDERS)],
            "order_id": order_ids,
            "review_score": score,
            "review_comment_title": None,
            "review_comment_message": None,
            "review_creation_date": answer - pd.Timedelta(days=1),
            "review_answer_timestamp": answer,
        }
    )
    geo = pd.DataFrame(
        [
            {"geolocation_zip_code_prefix": ZIPS[s], "geolocation_lat": lat, "geolocation_lng": lng,
             "geolocation_city": "z", "geolocation_state": s}
            for s, (lat, lng) in LATLNG.items()
        ]
    )
    for col in ("customer_zip_code_prefix",):
        customers[col] = customers[col].astype("string")
    sellers["seller_zip_code_prefix"] = sellers["seller_zip_code_prefix"].astype("string")
    geo["geolocation_zip_code_prefix"] = geo["geolocation_zip_code_prefix"].astype("string")
    return {
        "customers": customers, "geolocation": geo, "items": items, "payments": payments,
        "reviews": reviews, "orders": orders, "products": products, "sellers": sellers,
        "category_translation": translation,
    }


@pytest.fixture
def tables() -> dict[str, pd.DataFrame]:
    return make_tables()


@pytest.fixture
def base(tables) -> pd.DataFrame:
    from olist_course.data.build_base import build_base_table

    return build_base_table(tables)
