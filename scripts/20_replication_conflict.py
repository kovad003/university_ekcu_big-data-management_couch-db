#!/usr/bin/env python3
"""Experiment B: two-way replication, a forced conflict, and our merge.

Two branches share an order. With replication stopped, A marks it paid and B
fixes the delivery address; then sync resumes and the conflict is resolved.
Needs a fresh state (python run.py B resets first).
"""
import copy

from lib.couch import doc_path, instances, wait_until
from lib.demo import Demo, make_parser
from lib.merge import expected_winner, three_way_merge

args = make_parser(__doc__).parse_args()
A, B = instances()
DB = "orders"
SHARED = "store01:order-shared"
FROM_A, FROM_B = "store02:order-from-a", "store03:order-from-b"
TIMEOUT = 60

demo = Demo("20_replication_conflict",
            "Experiment B: two-way replication, conflict and resolution", args, [
    f"Instance A {A.url} (replicator reaches it as {A.internal_url})",
    f"Instance B {B.url} (replicator reaches it as {B.internal_url})",
    f"Database `{DB}` on both, n=1. Continuous replication jobs in each instance's _replicator.",
    f"Shared document: {SHARED}",
])
for c in (A, B):
    c.wait_ready(30)
    if c.get(doc_path(DB, SHARED)).status != 404:
        raise SystemExit(f"{SHARED} already exists on {c.label}. Run `python run.py reset` first (or `python run.py B`, which resets automatically).")


def job_doc(src, tgt):
    return {"source": src.replication_endpoint(DB), "target": tgt.replication_endpoint(DB),
            "continuous": True}


JOBS = [  # (holder, name, source, target): each job is stored on its source
    (A, "a-to-b", A, B),
    (B, "b-to-a", B, A),
]


def start_jobs(generation: int):
    ids = []
    for holder, name, src, tgt in JOBS:
        job_id = f"rep-{name}-{generation}"
        demo.step(f"Create job {job_id} in {holder.label}'s _replicator ({src.label} -> {tgt.label})",
                  "Credentials are needed to read the source and write the target. "
                  "They are redacted in this output.")
        r = demo.call(holder, "PUT", f"/_replicator/{job_id}", job_doc(src, tgt))
        demo.check(f"Job document {job_id} saved", r.status in (201, 202),
                   "HTTP 201", f"HTTP {r.status}")
        ids.append((holder, job_id))
    for holder, job_id in ids:
        demo.step(f"Wait until {job_id} is running (bounded: {TIMEOUT} s)")
        ok, state, secs = wait_until(
            lambda: _state(holder, job_id) == "running" and _state(holder, job_id), TIMEOUT)
        r = demo.call(holder, "GET", f"/_scheduler/docs/_replicator/{job_id}")
        info = r.body.get("info") if r.ok else None
        demo.check(f"{job_id} is running without errors",
                   ok and not (isinstance(info, dict) and info.get("error")),
                   'state "running", no error in info',
                   f'state "{_state(holder, job_id)}" after {secs}s, info={info}')
    return ids


def _state(holder, job_id):
    r = holder.get(f"/_scheduler/docs/_replicator/{job_id}")
    return r.body.get("state") if r.ok else None


def rev_of(c, doc_id):
    r = c.get(doc_path(DB, doc_id))
    return r.body.get("_rev") if r.ok else None


demo.part("B1. Continuous replication in both directions")
jobs = start_jobs(1)
demo.save_json("replication_jobs.json", {f"{h.label}:{j}": job_doc(s, t)
                                        for (h, n, s, t), (_, j) in zip(JOBS, jobs)})
demo.info("Job settings saved to evidence/20_replication_conflict/replication_jobs.json (passwords redacted)")

demo.step("Wait until B has caught up with A's existing documents")
target = A.get(f"/{DB}").body["doc_count"]
ok, n, secs = wait_until(lambda: B.get(f"/{DB}").body.get("doc_count") == target and target, TIMEOUT)
demo.call(A, "GET", f"/{DB}", screen="trim")
demo.call(B, "GET", f"/{DB}", screen="trim")
demo.check("B holds the same number of documents as A", ok,
           f"doc_count {target} on both", f"B doc_count {B.get(f'/{DB}').body.get('doc_count')} after {secs}s")

demo.part("B2. A document created on A reaches B, and one created on B reaches A")
demo.step(f"Create {FROM_A} on A")
demo.call(A, "PUT", doc_path(DB, FROM_A), {"type": "order", "tenant": "store02", "status": "open",
                                           "total": 25.0, "note": "created on A"})
demo.step(f"Read {FROM_A} on B (polling, bounded)")
ok, _, secs = wait_until(lambda: B.get(doc_path(DB, FROM_A)).ok, TIMEOUT)
demo.call(B, "GET", doc_path(DB, FROM_A))
demo.check("A -> B replication works", ok, f"{FROM_A} readable on B", f"found={ok} after {secs}s")

demo.step(f"Create {FROM_B} on B")
demo.call(B, "PUT", doc_path(DB, FROM_B), {"type": "order", "tenant": "store03", "status": "open",
                                           "total": 31.5, "note": "created on B"})
demo.step(f"Read {FROM_B} on A (polling, bounded)")
ok, _, secs = wait_until(lambda: A.get(doc_path(DB, FROM_B)).ok, TIMEOUT)
demo.call(A, "GET", doc_path(DB, FROM_B))
demo.check("B -> A replication works", ok, f"{FROM_B} readable on A", f"found={ok} after {secs}s")

demo.part("B3. Common starting state of the shared document")
demo.step(f"Create the shared order {SHARED} on A")
base_doc = {"type": "order", "tenant": "store01", "order_no": 901, "status": "open",
            "customer": {"name": "Shared Customer", "email": "shared@example.com"},
            "items": [{"sku": "SKU-COF-01", "name": "Coffee beans 1 kg", "qty": 3, "unit_price": 18.9}],
            "total": 56.7, "currency": "EUR", "created_at": "2026-10-30T09:00:00Z",
            "delivery": {"city": "Szeged", "street": "Kossuth tér 3."}}
r = demo.call(A, "PUT", doc_path(DB, SHARED), base_doc)
base_rev = r.body.get("rev")
demo.step("Wait until B has the same revision")
ok, _, secs = wait_until(lambda: rev_of(B, SHARED) == base_rev, TIMEOUT)
ra = demo.call(A, "GET", doc_path(DB, SHARED), screen="full")
rb = demo.call(B, "GET", doc_path(DB, SHARED), screen="full")
demo.check("A and B have the same current revision",
           ok and ra.body.get("_rev") == rb.body.get("_rev") == base_rev,
           f"_rev {base_rev} on both", f"A {ra.body.get('_rev')}, B {rb.body.get('_rev')}")
base = ra.body
demo.save_json("shared_doc_common_start.json", base)

demo.part("B4. Stop both replication jobs")
for holder, job_id in jobs:
    demo.step(f"Delete job document {job_id} on {holder.label}, quoting its current _rev")
    jr = holder.get(f"/_replicator/{job_id}")
    r = demo.call(holder, "DELETE", f"/_replicator/{job_id}", params={"rev": jr.body["_rev"]})
    demo.check(f"{job_id} document deleted", r.ok, "HTTP 200", f"HTTP {r.status}")
for holder, job_id in jobs:
    demo.step(f"Confirm {job_id} has stopped on {holder.label}")
    ok, _, secs = wait_until(
        lambda: not any(j.get("doc_id") == job_id
                        for j in holder.get("/_scheduler/jobs").body.get("jobs", [])), TIMEOUT)
    demo.call(holder, "GET", "/_scheduler/jobs")
    demo.check(f"No running job for {job_id}", ok, f"{job_id} absent from /_scheduler/jobs",
               f"absent={ok} after {secs}s")

demo.part("B5. Edit the shared document independently on A and on B")
edit_a = copy.deepcopy(base)
edit_a["status"] = "paid"
edit_a["payment"] = {"method": "card", "paid_at": "2026-10-30T10:15:00Z"}
demo.step("On A (branch 1): mark the order paid", f"Based on the common revision {base_rev}.")
r = demo.call(A, "PUT", doc_path(DB, SHARED), edit_a)
rev_a = r.body.get("rev")
demo.check("Edit accepted locally on A", r.status == 201, "HTTP 201", f"HTTP {r.status}, rev {rev_a}")

edit_b = copy.deepcopy(base)
edit_b["delivery"] = {"city": "Szeged", "street": "Kárász utca 12."}
edit_b["note"] = "Customer called: new delivery address"
demo.step("On B (branch 2): correct the delivery address", f"Also based on {base_rev}.")
r = demo.call(B, "PUT", doc_path(DB, SHARED), edit_b)
rev_b = r.body.get("rev")
demo.check("Edit accepted locally on B", r.status == 201, "HTTP 201", f"HTTP {r.status}, rev {rev_b}")
demo.check("The two branches now hold different revisions",
           bool(rev_a and rev_b and rev_a != rev_b),
           "two different 2-... revisions", f"A {rev_a}, B {rev_b}")

demo.part("B6. Restart replication and inspect the conflict")
demo.info("New job documents with fresh ids, same connection settings, no old _rev or state fields.")
jobs = start_jobs(2)

def conflict_seen(c):
    r = c.get(doc_path(DB, SHARED), params={"conflicts": True})
    return r.ok and r.body.get("_conflicts") and r.body
demo.step("Wait until both instances know both revisions")
ok_a, _, s1 = wait_until(lambda: conflict_seen(A), TIMEOUT)
ok_b, _, s2 = wait_until(lambda: conflict_seen(B), TIMEOUT)
ca = demo.call(A, "GET", doc_path(DB, SHARED), params={"conflicts": True}, screen="full")
cb = demo.call(B, "GET", doc_path(DB, SHARED), params={"conflicts": True}, screen="full")
winner = ca.body.get("_rev")
losers = ca.body.get("_conflicts", [])
demo.check("Both instances report a conflict", bool(ok_a and ok_b),
           "_conflicts present on A and B", f"A after {s1}s: {bool(ok_a)}, B after {s2}s: {bool(ok_b)}")
demo.check("Both instances pick the same winning revision",
           winner == cb.body.get("_rev") and set(losers) == set(cb.body.get("_conflicts", [])),
           "same _rev and same _conflicts on A and B",
           f"A {winner} / {losers}; B {cb.body.get('_rev')} / {cb.body.get('_conflicts')}")

predicted = expected_winner([rev_a, rev_b])
demo.check("Winner follows the documented deterministic rule",
           winner == predicted,
           f"equal revision depth, so the higher revision id wins: {predicted}", f"{winner}")

loser = losers[0] if losers else None
demo.step("Fetch the losing revision by its revision id", "It is not lost, just hidden from ordinary reads.")
lr = demo.call(A, "GET", doc_path(DB, SHARED), params={"rev": loser}, screen="full")
win_doc, lose_doc = ca.body, lr.body
demo.check("Losing revision is still readable", lr.ok and lr.body.get("_rev") == loser,
           f"HTTP 200, _rev {loser}", f"HTTP {lr.status}, _rev {lr.body.get('_rev')}")
demo.info(f"Winning revision status={win_doc.get('status')} street={win_doc.get('delivery', {}).get('street')}; "
          f"losing revision status={lose_doc.get('status')} street={lose_doc.get('delivery', {}).get('street')}. "
          "CouchDB did not merge them.")
demo.save_json("conflict_revisions.json", {"winner": win_doc, "loser": lose_doc, "common_start": base})

demo.part("B7. Resolve the conflict with an explicit merge rule")
demo.info("Rule: three-way merge per top-level field against the common start. A field changed on "
          "only one side takes that side's value. A field changed differently on both sides keeps "
          "the winner's value and is recorded in merge_notes.")
merged, notes = three_way_merge(base, win_doc, lose_doc)
merged["merge_notes"] = notes or ["no overlapping field changes"]
merged["_id"] = SHARED
merged["_rev"] = winner
demo.step("Save the merged content as a new revision of the WINNING branch")
r = demo.call(A, "PUT", doc_path(DB, SHARED), merged, screen="full")
resolved_rev = r.body.get("rev")
demo.check("Merged revision saved on the winning branch", r.status == 201,
           f"HTTP 201, rev 3-... (child of {winner})", f"HTTP {r.status}, rev {resolved_rev}")
demo.step("Delete the LOSING leaf, using the loser's own revision id",
          "Not the new merged revision: that would delete the resolved document.")
r = demo.call(A, "DELETE", doc_path(DB, SHARED), params={"rev": loser})
demo.check("Losing leaf marked deleted", r.ok, "HTTP 200", f"HTTP {r.status}")

demo.step("Wait until the resolution has replicated to B")
def resolved_on(c):
    r = c.get(doc_path(DB, SHARED), params={"conflicts": True})
    return r.ok and r.body.get("_rev") == resolved_rev and not r.body.get("_conflicts")
ok, _, secs = wait_until(lambda: resolved_on(A) and resolved_on(B), TIMEOUT)
fa = demo.call(A, "GET", doc_path(DB, SHARED), params={"conflicts": True, "deleted_conflicts": True}, screen="full")
fb = demo.call(B, "GET", doc_path(DB, SHARED), params={"conflicts": True, "deleted_conflicts": True}, screen="full")
for c, f in ((A, fa), (B, fb)):
    body = f.body
    demo.check(f"{c.label}: merged data, no live conflicts",
               ok and body.get("_rev") == resolved_rev and not body.get("_conflicts")
               and body.get("status") == "paid"
               and body.get("delivery", {}).get("street") == "Kárász utca 12.",
               f"_rev {resolved_rev}, no _conflicts, status paid, street Kárász utca 12.",
               f"_rev {body.get('_rev')}, _conflicts {body.get('_conflicts')}, status {body.get('status')}, "
               f"street {body.get('delivery', {}).get('street')}, _deleted_conflicts {body.get('_deleted_conflicts')}")
demo.save_json("resolved_doc.json", {"A": fa.body, "B": fb.body})
demo.info("The two jobs from step B6 keep running. 90_reset.py stops them.")

demo.finish([
    "Replication is directional: two jobs (A->B stored on A, B->A stored on B) gave two-way sync, "
    "shown by documents created on each side appearing on the other.",
    "With replication stopped, both instances accepted an edit based on the same revision. "
    "This is not an HTTP 409: each edit was valid locally.",
    "After replication resumed, both instances chose the same winner by a deterministic rule. "
    "The other edit survived as a conflicting revision. CouchDB did not merge the application data.",
    "The application resolved it: the merged content became a new revision of the winning branch, "
    "and the losing leaf was deleted with its own revision id. Afterwards neither instance shows live conflicts.",
    "Limitation: the resolution is two separate writes (save, then delete), so another reader can briefly "
    "see the merged winner while the losing leaf still exists. The merge rule is our application's choice.",
])
