#!/usr/bin/env python3
"""Experiment A: CRUD on instance A, then an indexed Mango query:
open orders of store01 over 100 EUR, newest first.
"""
from lib.couch import all_docs, doc_path, instances
from lib.demo import Demo, make_parser

args = make_parser(__doc__).parse_args()
A, _ = instances()
DB = "orders"
DOC_ID = "store01:order900"

demo = Demo("10_crud_mango", "Experiment A: CRUD and a Mango query", args, [
    f"Instance A ({A.url}), database `{DB}` (n=1), seeded with 100 orders",
    f"Test document id: {DOC_ID}",
])
A.wait_ready(30)
if A.get(doc_path(DB, DOC_ID)).status == 200:
    raise SystemExit(f"{DOC_ID} already exists. Run `python run.py reset` first (or `python run.py B`, which resets automatically).")

demo.part("Create")
demo.step("Create a new order with a chosen _id",
          "PUT /db/<id> stores the document. CouchDB answers with the first revision, 1-<hash>.")
order = {
    "type": "order", "tenant": "store01", "order_no": 900, "status": "open",
    "customer": {"name": "Demo Customer", "email": "demo@example.com"},
    "items": [{"sku": "SKU-KET-04", "name": "Gooseneck kettle", "qty": 2, "unit_price": 72.0}],
    "total": 144.0, "currency": "EUR", "created_at": "2026-10-30T12:00:00Z",
    "delivery": {"city": "Budapest", "street": "Fő utca 1."},
}
r = demo.call(A, "PUT", doc_path(DB, DOC_ID), order)
rev1 = r.body.get("rev", "")
demo.check("Document created with revision 1", r.status == 201 and rev1.startswith("1-"),
           "HTTP 201, rev 1-...", f"HTTP {r.status}, rev {rev1}")

demo.part("Read")
demo.step("Read it back by _id")
r = demo.call(A, "GET", doc_path(DB, DOC_ID), screen="full")
demo.check("Read returns the stored content and current _rev",
           r.ok and r.body.get("_rev") == rev1 and r.body.get("status") == "open",
           f"HTTP 200, _rev {rev1}, status open",
           f"HTTP {r.status}, _rev {r.body.get('_rev')}, status {r.body.get('status')}")

demo.part("Update")
demo.step("Update: mark the order as paid, sending the current _rev",
          "An update replaces the whole document. Sending _rev proves which version we are changing.")
updated = dict(r.body)
updated["status"] = "paid"
r = demo.call(A, "PUT", doc_path(DB, DOC_ID), updated)
rev2 = r.body.get("rev", "")
demo.check("Update accepted with a new revision 2", r.status == 201 and rev2.startswith("2-"),
           "HTTP 201, rev 2-...", f"HTTP {r.status}, rev {rev2}")
demo.step("Verify the new state")
r = demo.call(A, "GET", doc_path(DB, DOC_ID))
demo.check("Stored status is now paid", r.ok and r.body.get("status") == "paid" and r.body.get("_rev") == rev2,
           f"status paid, _rev {rev2}", f"status {r.body.get('status')}, _rev {r.body.get('_rev')}")

demo.part("Delete")
demo.step("Delete: DELETE with the current revision",
          "Deletion writes a new 'tombstone' revision, so replication can pass the delete on.")
r = demo.call(A, "DELETE", doc_path(DB, DOC_ID), params={"rev": rev2})
rev3 = r.body.get("rev", "")
demo.check("Delete accepted (tombstone revision 3)", r.ok and rev3.startswith("3-"),
           "HTTP 200, rev 3-...", f"HTTP {r.status}, rev {rev3}")
demo.step("Verify the document is gone")
r = demo.call(A, "GET", doc_path(DB, DOC_ID))
demo.check("Read after delete returns 404 deleted",
           r.status == 404 and r.body.get("reason") == "deleted",
           'HTTP 404 {"reason":"deleted"}', f"HTTP {r.status} {r.body}")

demo.part("Mango query: open orders over 100 EUR for one store, newest first")
demo.step("Create a JSON index on (tenant, status, created_at)",
          "Equality on tenant and status, then created_at gives the sort order.")
idx = {"index": {"fields": ["tenant", "status", "created_at"]},
       "name": "tenant-status-created", "type": "json", "ddoc": "idx-tenant-status-created"}
r = demo.call(A, "POST", f"/{DB}/_index", idx)
demo.check("Index exists", r.ok and r.body.get("result") in ("created", "exists"),
           'result "created" (or "exists" on re-run)', f"HTTP {r.status}, result {r.body.get('result')}")

query = {
    "selector": {"tenant": "store01", "status": "open", "total": {"$gt": 100}},
    "fields": ["_id", "customer.name", "total", "created_at"],
    "sort": [{"tenant": "desc"}, {"status": "desc"}, {"created_at": "desc"}],
    "limit": 50,
    "execution_stats": True,
}
demo.step("Ask CouchDB which index it will use (_explain)")
r = demo.call(A, "POST", f"/{DB}/_explain", {k: v for k, v in query.items() if k != "execution_stats"})
used = (r.body.get("index") or {}).get("name") if r.ok else None
demo.check("Query planner selects our index", used == "tenant-status-created",
           "index tenant-status-created", f"index {used}")

demo.step("Run the query")
r = demo.call(A, "POST", f"/{DB}/_find", query, screen="full")
docs = r.body.get("docs", []) if r.ok else []
expected = sorted((d for d in all_docs(A, DB) if d.get("tenant") == "store01"
                   and d.get("status") == "open" and d.get("total", 0) > 100),
                  key=lambda d: d["created_at"], reverse=True)
demo.check("Result equals a client-side filter of all documents, in the same order",
           [d["_id"] for d in docs] == [d["_id"] for d in expected],
           f"{len(expected)} ids: {[d['_id'] for d in expected]}",
           f"{len(docs)} ids: {[d['_id'] for d in docs]}")
stats = r.body.get("execution_stats", {}) if r.ok else {}
demo.info(f"execution_stats: {stats}")

demo.finish([
    "Every write returned a new revision (1-, 2-, 3-). An update must quote the current "
    "_rev, so a client cannot silently overwrite a version it has not seen (see experiment D1).",
    "Delete creates a tombstone revision rather than erasing the document, so a "
    "replica can learn about the deletion.",
    "The Mango query used the (tenant, status, created_at) index and returned exactly "
    "the documents a full client-side scan finds, newest first.",
])
