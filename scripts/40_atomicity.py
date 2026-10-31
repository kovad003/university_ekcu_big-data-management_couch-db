#!/usr/bin/env python3
"""Experiment D on instance A, in its own txn_test database.

D1 stale update gets 409. D2 one _bulk_docs request half succeeds.
D3 the shop version: an order saved without its stock change.
"""
from lib.couch import doc_path, instances
from lib.demo import Demo, make_parser

args = make_parser(__doc__).parse_args()
A, _ = instances()
DB = "txn_test"

demo = Demo("40_atomicity", "Experiment D: update conflicts and non-atomic bulk operations", args, [
    f"Instance A ({A.url}), database `{DB}`: normal, n=1, no replication, recreated each run",
])
A.wait_ready(30)
A.delete(f"/{DB}")
r = A.put(f"/{DB}", params={"n": 1})
assert r.status in (201, 202), r


def get(doc_id):
    return demo.call(A, "GET", doc_path(DB, doc_id), screen="full")


demo.part("D1. Rejecting a stale document update")
demo.step("Create a document and save its initial _rev")
r = demo.call(A, "PUT", doc_path(DB, "stock-SKU-KET-04"), {"type": "stock", "sku": "SKU-KET-04", "on_hand": 10})
rev1 = r.body.get("rev")
demo.check("Created", r.status == 201, "HTTP 201, rev 1-...", f"HTTP {r.status}, rev {rev1}")

demo.step("Client 1 updates it (on_hand 10 -> 8) using rev 1")
r = demo.call(A, "PUT", doc_path(DB, "stock-SKU-KET-04"),
              {"_rev": rev1, "type": "stock", "sku": "SKU-KET-04", "on_hand": 8})
rev2 = r.body.get("rev")
demo.check("Update accepted", r.status == 201 and str(rev2).startswith("2-"),
           "HTTP 201, rev 2-...", f"HTTP {r.status}, rev {rev2}")

demo.step("Client 2 still holds rev 1 and tries to set on_hand 10 -> 9",
          "This is the lost-update case. CouchDB must refuse it.")
r = demo.call(A, "PUT", doc_path(DB, "stock-SKU-KET-04"),
              {"_rev": rev1, "type": "stock", "sku": "SKU-KET-04", "on_hand": 9})
demo.check("Stale update rejected with 409", r.status == 409 and r.body.get("error") == "conflict",
           'HTTP 409 {"error":"conflict"}', f"HTTP {r.status} {r.body}")

demo.step("Read: the successful update is untouched")
r = get("stock-SKU-KET-04")
demo.check("Document still holds client 1's value", r.body.get("_rev") == rev2 and r.body.get("on_hand") == 8,
           f"_rev {rev2}, on_hand 8", f"_rev {r.body.get('_rev')}, on_hand {r.body.get('on_hand')}")

demo.part("D2. Partial success in one _bulk_docs request")
demo.step("Create bulk-a and bulk-b, save their revisions")
ra = demo.call(A, "PUT", doc_path(DB, "bulk-a"), {"value": "a-v1"})
rb = demo.call(A, "PUT", doc_path(DB, "bulk-b"), {"value": "b-v1"})
a1, b1 = ra.body.get("rev"), rb.body.get("rev")

demo.step("Update bulk-b once, so the saved revision of bulk-b becomes stale")
r = demo.call(A, "PUT", doc_path(DB, "bulk-b"), {"_rev": b1, "value": "b-v2"})
b2 = r.body.get("rev")

demo.step("One _bulk_docs request: valid update of bulk-a + stale update of bulk-b")
r = demo.call(A, "POST", f"/{DB}/_bulk_docs", {"docs": [
    {"_id": "bulk-a", "_rev": a1, "value": "a-v2"},
    {"_id": "bulk-b", "_rev": b1, "value": "b-v3-from-stale-rev"},
]}, screen="full")
items = {i.get("id"): i for i in (r.body if isinstance(r.body, list) else [])}
demo.check("The request as a whole reports success", r.status == 201,
           "HTTP 201 (even though one item fails)", f"HTTP {r.status}")
demo.check("Item bulk-a succeeded", items.get("bulk-a", {}).get("ok") is True,
           '{"ok": true, "rev": "2-..."}', f"{items.get('bulk-a')}")
demo.check("Item bulk-b rejected", items.get("bulk-b", {}).get("error") == "conflict",
           '{"error": "conflict"}', f"{items.get('bulk-b')}")

demo.step("Read both documents")
ga, gb = get("bulk-a"), get("bulk-b")
demo.check("bulk-a holds the new value", ga.body.get("value") == "a-v2",
           "value a-v2", f"value {ga.body.get('value')}, _rev {ga.body.get('_rev')}")
demo.check("bulk-b keeps its previous valid value", gb.body.get("value") == "b-v2" and gb.body.get("_rev") == b2,
           f"value b-v2, _rev {b2}", f"value {gb.body.get('value')}, _rev {gb.body.get('_rev')}")

demo.part("D3. What this means for the shop: order + stock are not atomic")
demo.info("A checkout writes two documents: the new order and the decremented stock count. "
          "Here the stock revision is stale, because another checkout just changed it.")
demo.step("Send both writes in one _bulk_docs request, the stock update with a stale _rev")
stock = A.get(doc_path(DB, "stock-SKU-KET-04")).body  # on_hand 8 at this point
A.put(doc_path(DB, "stock-SKU-KET-04"), {**stock, "on_hand": 7})  # another checkout gets in first
r = demo.call(A, "POST", f"/{DB}/_bulk_docs", {"docs": [
    {"_id": "store01:order777", "type": "order", "sku": "SKU-KET-04", "qty": 1, "status": "paid"},
    {**stock, "on_hand": stock["on_hand"] - 1},  # still carries the old _rev
]}, screen="full")
res = r.body if isinstance(r.body, list) else []
order_ok = any(i.get("id") == "store01:order777" and i.get("ok") for i in res)
stock_conflict = any(i.get("id") == "stock-SKU-KET-04" and i.get("error") == "conflict" for i in res)
demo.check("Order written, stock update rejected", order_ok and stock_conflict,
           "order ok, stock conflict", f"{res}")
s = get("stock-SKU-KET-04")
demo.check("Stock was NOT decremented for this order", s.body.get("on_hand") == 7,
           "on_hand 7 (only the concurrent checkout counted)", f"on_hand {s.body.get('on_hand')}")
demo.info("The application must detect the failed item and retry or compensate. "
          "A design that avoids the problem keeps each business event in ONE document "
          "(e.g. the order itself carries the reservation) and derives stock with a view.")

demo.finish([
    "D1: an update that names a stale revision gets HTTP 409, and the earlier successful update "
    "stays. Optimistic concurrency per document prevents lost updates.",
    "D2: _bulk_docs returned HTTP 201 overall but reported per item: bulk-a saved, bulk-b "
    "rejected with a conflict. A bulk request is a batch, not an all-or-nothing transaction.",
    "D3: in the shop, 'create order + decrement stock' sent together can half-succeed. "
    "Invariants spanning two documents need application logic (retry, compensation) or a "
    "single-document design.",
    "This is about the local transaction boundary. How fast revisions reach another instance "
    "is a separate question (experiment B).",
])
