"""Sample orders. A fixed seed gives identical data on every machine.

Ids look like "store01:order007". The prefix is the partition key in the
partitioned database and must match `tenant`.
"""
from __future__ import annotations

import datetime as dt
import random

CATALOGUE = [
    ("SKU-COF-01", "Coffee beans 1 kg", 18.90),
    ("SKU-MUG-02", "Ceramic mug", 9.50),
    ("SKU-GRN-03", "Hand grinder", 54.00),
    ("SKU-KET-04", "Gooseneck kettle", 72.00),
    ("SKU-FIL-05", "Paper filters x100", 6.20),
    ("SKU-DRP-06", "Pour-over dripper", 24.00),
    ("SKU-SCL-07", "Coffee scale", 39.90),
    ("SKU-TEA-08", "Green tea 250 g", 12.40),
]
FIRST = ["Anna", "Bence", "Csilla", "Dániel", "Eszter", "Ferenc", "Gréta", "Hanna",
         "István", "Júlia", "Kata", "László", "Márk", "Nóra", "Olivér", "Petra"]
LAST = ["Kovács", "Nagy", "Tóth", "Szabó", "Horváth", "Varga", "Kiss", "Molnár"]
CITIES = ["Budapest", "Debrecen", "Szeged", "Pécs", "Győr", "Miskolc"]
STREETS = ["Fő utca", "Kossuth tér", "Petőfi utca", "Rákóczi út", "Dózsa György út"]
STATUSES = ["open", "paid", "shipped", "cancelled"]
STATUS_WEIGHTS = [40, 25, 25, 10]


def store_name(i: int) -> str:
    return f"store{i:02d}"


def generate_orders(stores: int = 5, per_store: int = 20, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    start = dt.datetime(2026, 9, 1, 8, 0, tzinfo=dt.timezone.utc)
    docs = []
    for s in range(1, stores + 1):
        tenant = store_name(s)
        for o in range(1, per_store + 1):
            items = []
            for sku, name, price in rng.sample(CATALOGUE, rng.randint(1, 4)):
                items.append({"sku": sku, "name": name, "qty": rng.randint(1, 3),
                              "unit_price": price})
            total = round(sum(i["qty"] * i["unit_price"] for i in items), 2)
            first, last = rng.choice(FIRST), rng.choice(LAST)
            created = start + dt.timedelta(minutes=rng.randint(0, 60 * 24 * 55))
            docs.append({
                "_id": f"{tenant}:order{o:03d}",
                "type": "order",
                "tenant": tenant,
                "order_no": o,
                "status": rng.choices(STATUSES, STATUS_WEIGHTS)[0],
                "customer": {
                    "name": f"{first} {last}",
                    "email": f"{_ascii(first)}.{_ascii(last)}{o}@example.com".lower(),
                },
                "items": items,
                "total": total,
                "currency": "EUR",
                "created_at": created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "delivery": {"city": rng.choice(CITIES),
                             "street": f"{rng.choice(STREETS)} {rng.randint(1, 120)}."},
            })
    return docs


def _ascii(s: str) -> str:
    table = str.maketrans("áéíóöőúüűÁÉÍÓÖŐÚÜŰ", "aeiooouuuAEIOOOUUU")
    return s.translate(table)
