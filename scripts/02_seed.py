#!/usr/bin/env python3
"""Creates `orders` on A and B and loads the 100 sample orders into A only.

B stays empty on purpose; replication fills it in experiment B. Re-running
doesn't overwrite anything (existing ids come back as conflicts).
Also rewrites data/orders.json.
"""
import json

from lib.couch import REPO_ROOT, instances
from lib.data import generate_orders
from lib.demo import Demo, make_parser

p = make_parser(__doc__)
p.add_argument("--stores", type=int, default=5)
p.add_argument("--per-store", type=int, default=20)
args = p.parse_args()
A, B = instances()
orders = generate_orders(args.stores, args.per_store)

out = REPO_ROOT / "data" / "orders.json"
out.write_text(json.dumps(orders, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

demo = Demo("01_seed", "Seed the demo database", args, [
    f"Dataset: {len(orders)} orders, {args.stores} stores x {args.per_store}, seed 42 "
    "(self-generated, see scripts/lib/data.py)",
    "Database `orders` on A and B, replica count n=1",
])

for c in (A, B):
    demo.step(f"Create database `orders` on {c.label} with n=1")
    r = demo.call(c, "PUT", "/orders", params={"n": 1})
    demo.check(f"`orders` exists on {c.label}", r.status in (201, 202, 412),
               "HTTP 201, or 412 if it already exists", f"HTTP {r.status}")

demo.step("Show one sample document before loading", "This is the data model (Part 3).")
demo.info(json.dumps(orders[0], ensure_ascii=False))

demo.step(f"Load {len(orders)} orders into A with one _bulk_docs request")
r = demo.call(A, "POST", "/orders/_bulk_docs", {"docs": orders})
ok = sum(1 for item in r.body if item.get("ok")) if isinstance(r.body, list) else 0
dup = sum(1 for item in r.body if item.get("error") == "conflict") if isinstance(r.body, list) else 0
demo.check("Every order is stored on A (new or already present)",
           r.status == 201 and ok + dup == len(orders),
           f"HTTP 201 and {len(orders)} items ok or already present",
           f"HTTP {r.status}, {ok} created, {dup} already present")

demo.step("Database info on A")
r = demo.call(A, "GET", "/orders")
demo.check("Document count on A", r.ok and r.body.get("doc_count", 0) >= len(orders),
           f">= {len(orders)} documents", f"{r.body.get('doc_count')} documents")

demo.finish([f"The sample dataset ({len(orders)} orders) is loaded into A and saved as data/orders.json."])
