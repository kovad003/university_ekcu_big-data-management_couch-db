#!/usr/bin/env python3
"""Experiment C: the same question asked of a normal and a partitioned database on A.

Both get the same q and n so the comparison is fair. --timing adds the optional
10,000-order run; raw samples go to timing.csv.
"""
import statistics
import time

from lib.couch import all_docs, instances
from lib.data import generate_orders
from lib.demo import Demo, make_parser

p = make_parser(__doc__)
p.add_argument("--q", type=int, default=2, help="shard count for BOTH databases (default 2)")
p.add_argument("--page", type=int, default=3, help="page size for the bookmark comparison")
p.add_argument("--timing", action="store_true", help="also run the optional timing experiment")
p.add_argument("--big-stores", type=int, default=50)
p.add_argument("--big-per-store", type=int, default=200)
p.add_argument("--repeats", type=int, default=30)
args = p.parse_args()
A, _ = instances()
GLOBAL, PART = "orders_global", "orders_partitioned"
TENANT = "store01"

demo = Demo("30_partitioned_queries", "Experiment C: partitioned vs global queries", args, [
    f"Instance A ({A.url}) only",
    f"`{GLOBAL}`: normal database, n=1, q={args.q}",
    f"`{PART}`: partitioned=true, n=1, q={args.q}",
    "Data: the same 100 generated orders in both (5 stores = 5 partitions)",
    "Index: json on [tenant, status]: global in the normal db, partitioned in the partitioned db",
])
A.wait_ready(30)
orders = generate_orders()


def create_db(name, partitioned, docs):
    demo.step(f"Create fresh database {name}" + (" with partitioned=true" if partitioned else ""),
              "Deleted first if it exists, so every run starts from the same state.")
    A.delete(f"/{name}")
    params = {"n": 1, "q": args.q}
    if partitioned:
        params["partitioned"] = True
    r = demo.call(A, "PUT", f"/{name}", params=params)
    demo.check(f"{name} created", r.status in (201, 202), "HTTP 201", f"HTTP {r.status}")
    info = demo.call(A, "GET", f"/{name}").body
    props, cluster = info.get("props", {}), info.get("cluster", {})
    demo.check(f"{name} settings", bool(props.get("partitioned")) == partitioned
               and cluster.get("q") == args.q and cluster.get("n") == 1,
               f"partitioned={partitioned}, q={args.q}, n=1",
               f"partitioned={bool(props.get('partitioned'))}, q={cluster.get('q')}, n={cluster.get('n')}")
    demo.step(f"Load {len(docs)} documents into {name}")
    r = demo.call(A, "POST", f"/{name}/_bulk_docs", {"docs": docs}, screen="status")
    ok = sum(1 for i in r.body if i.get("ok")) if isinstance(r.body, list) else 0
    demo.check(f"All documents stored in {name}", ok == len(docs),
               f"{len(docs)} ok items", f"{ok} ok items")


def make_index(db, partitioned):
    body = {"index": {"fields": ["tenant", "status"]}, "name": "tenant-status",
            "type": "json", "partitioned": partitioned}
    demo.step(f"Create {'partitioned' if partitioned else 'global'} index tenant-status on {db}")
    r = demo.call(A, "POST", f"/{db}/_index", body)
    demo.check(f"Index on {db}", r.ok, 'result "created"', f"HTTP {r.status} {r.body}")


def fetch_all(path, selector, page):
    """A bookmark is returned even on the last page, so stop on a short page instead."""
    ids, bookmark, pages = [], None, 0
    while True:
        body = {"selector": selector, "limit": page, "fields": ["_id"]}
        if bookmark:
            body["bookmark"] = bookmark
        r = A.post(path, body)
        docs = r.body.get("docs", [])
        pages += 1
        ids += [d["_id"] for d in docs]
        bookmark = r.body.get("bookmark")
        if len(docs) < page:
            return ids, pages


demo.part("C1. Two fresh databases with equal settings")
create_db(GLOBAL, False, orders)
create_db(PART, True, orders)

demo.step("Example ids from different partitions")
for t in ("store01", "store02", "store05"):
    demo.call(A, "GET", f"/{PART}/_partition/{t}")
demo.step("A partitioned database rejects an id without a partition prefix")
r = demo.call(A, "PUT", f"/{PART}/no-prefix-id", {"tenant": "x"})
demo.check("Id without 'partition:' prefix is rejected", r.status == 400,
           "HTTP 400 (illegal docid)", f"HTTP {r.status} {r.body}")

demo.part("C2. Equivalent indexes")
make_index(GLOBAL, False)
make_index(PART, True)

demo.part(f"C3. Same question, two endpoints: open orders of {TENANT}")
query = {"selector": {"tenant": TENANT, "status": "open"}, "limit": 100, "execution_stats": True}
count_before = {db: A.get(f"/{db}").body["doc_count"] for db in (GLOBAL, PART)}
paths = {"global": f"/{GLOBAL}/_find", "partition": f"/{PART}/_partition/{TENANT}/_find"}
explains = {"global": f"/{GLOBAL}/_explain", "partition": f"/{PART}/_partition/{TENANT}/_explain"}
results = {}
for k in ("global", "partition"):
    demo.step(f"Explain the {k} query: which index is selected?")
    r = demo.call(A, "POST", explains[k], {kk: v for kk, v in query.items() if kk != "execution_stats"})
    idx = r.body.get("index", {}) if r.ok else {}
    demo.check(f"{k} query uses the tenant-status index", idx.get("name") == "tenant-status",
               "index tenant-status", f"index {idx.get('name')} (partitioned={idx.get('partitioned')})")
    demo.step(f"Run the {k} query", f"POST {paths[k]}")
    r = demo.call(A, "POST", paths[k], query)
    results[k] = r.body
    demo.info(f"{k}: {len(r.body.get('docs', []))} docs, execution_stats={r.body.get('execution_stats')}")

ids = {k: sorted(d["_id"] for d in v.get("docs", [])) for k, v in results.items()}
expected = sorted(d["_id"] for d in orders if d["tenant"] == TENANT and d["status"] == "open")
demo.check("Both endpoints return the same document ids (limit 100, one page)",
           ids["global"] == ids["partition"] == expected,
           f"{len(expected)} ids, equal to a client-side filter",
           f"global {len(ids['global'])}, partition {len(ids['partition'])}, equal={ids['global'] == ids['partition']}")
demo.save_json("query_results.json", {k: {"ids": ids[k], "execution_stats": results[k].get("execution_stats"),
                                          "warning": results[k].get("warning")} for k in results})

demo.part(f"C4. Complete result sets via bookmarks (page size {args.page})")
full = {}
for k in ("global", "partition"):
    demo.step(f"Page through the {k} endpoint until a page has fewer than {args.page} docs")
    full[k], pages = fetch_all(paths[k], query["selector"], args.page)
    demo.info(f"{k}: {len(full[k])} ids over {pages} pages: {full[k]}")
demo.check("Complete paged result sets are identical",
           sorted(full["global"]) == sorted(full["partition"]) == expected
           and len(set(full["global"])) == len(full["global"]),
           f"{len(expected)} unique ids on both endpoints",
           f"global {len(full['global'])}, partition {len(full['partition'])}, "
           f"equal={sorted(full['global']) == sorted(full['partition'])}")
count_after = {db: A.get(f"/{db}").body["doc_count"] for db in (GLOBAL, PART)}
demo.check("Data unchanged during the comparison", count_before == count_after,
           f"{count_before}", f"{count_after}")

demo.part("C5. A question that needs a global view")
demo.step("Open orders of ALL stores, asked on the partitioned database's global endpoint",
          "Only a partitioned index exists, so the global query has no usable index.")
cross = {"selector": {"status": "open"}, "limit": 1000, "execution_stats": True}
r = demo.call(A, "POST", f"/{PART}/_find", cross)
st = r.body.get("execution_stats", {}) if r.ok else {}
demo.info(f"warning: {r.body.get('warning')}; docs examined: {st.get('total_docs_examined')}")
n_open = sum(1 for d in orders if d["status"] == "open")
demo.check("Cross-store query is answered, but by scanning", r.ok and len(r.body.get("docs", [])) == n_open,
           f"{n_open} docs, examined ~ all {len(orders)} documents (no global index)",
           f"{len(r.body.get('docs', []))} docs, examined {st.get('total_docs_examined')}")
demo.info("Fix if this query mattered: add a global index (partitioned: false) to the partitioned database.")

if args.timing:
    demo.part("C6 (optional). Timing on a larger dataset")
    big = generate_orders(args.big_stores, args.big_per_store, seed=7)
    gb, pb = GLOBAL + "_big", PART + "_big"
    for name, part in ((gb, False), (pb, True)):
        A.delete(f"/{name}")
        prm = {"n": 1, "q": args.q, **({"partitioned": True} if part else {})}
        A.put(f"/{name}", params=prm)
        for i in range(0, len(big), 2000):
            A.post(f"/{name}/_bulk_docs", {"docs": big[i:i + 2000]}, timeout=120)
        A.post(f"/{name}/_index", {"index": {"fields": ["tenant", "status"]}, "name": "tenant-status",
                                   "type": "json", "partitioned": part})
    qb = {"selector": {"tenant": TENANT, "status": "open"}, "limit": 1000}
    pth = {"global": f"/{gb}/_find", "partition": f"/{pb}/_partition/{TENANT}/_find"}
    demo.step(f"Warm up, then time {args.repeats} alternating runs per endpoint on {len(big)} docs")
    for k in pth:  # first queries build the index, keep them out of the samples
        for _ in range(5):
            A.post(pth[k], qb, timeout=300)
    samples = {k: [] for k in pth}
    ref = None
    for _ in range(args.repeats):
        for k in pth:
            t0 = time.perf_counter()
            r = A.post(pth[k], qb, timeout=300)
            samples[k].append((time.perf_counter() - t0) * 1000)
            got = sorted(d["_id"] for d in r.body["docs"])
            ref = ref or got
            assert got == ref, "endpoints disagree"
    rows = ["endpoint,run,ms"] + [f"{k},{i},{v:.3f}" for k in samples for i, v in enumerate(samples[k], 1)]
    (demo.dir / "timing.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    for k, v in samples.items():
        q = statistics.quantiles(v, n=10)
        demo.info(f"{k}: median {statistics.median(v):.2f} ms, p10 {q[0]:.2f}, p90 {q[-1]:.2f}, "
                  f"min {min(v):.2f}, max {max(v):.2f} (n={len(v)})")
    demo.check("Timed endpoints returned identical result sets", True,
               "same ids every run", f"{len(ref)} ids each run")
    demo.info("Raw samples: evidence/30_partitioned_queries/timing.csv. "
              "One laptop, one node: this says nothing about production scalability.")

demo.finish([
    "Both endpoints answered the same one-store question with the same complete set of ids, "
    "checked over all bookmark pages and against a client-side filter.",
    "The partitioned query is limited to one partition by construction (/_partition/<store>/_find) and "
    "uses the partitioned index. The global query must consider every shard of the database.",
    "Queries across stores (C5) need a global view. In the partitioned database they need a separate "
    "global index, or they fall back to scanning.",
    "A partition groups related documents (all of one store's orders) so they are stored together. "
    "On this single node it does not show physical distribution across servers, and no speed-up is claimed.",
])
