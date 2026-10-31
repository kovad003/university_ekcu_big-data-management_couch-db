#!/usr/bin/env python3
"""DESTRUCTIVE: return both instances to the documented starting state.

Deletes on BOTH instances:
  - the demo databases: orders, orders_global, orders_partitioned,
    orders_global_big, orders_partitioned_big, txn_test, setup_check
  - every replication job document in _replicator whose id starts with "rep-"
Then re-runs the seed (unless --no-seed).

It does NOT delete the containers or volumes. For a full wipe:
  docker compose down -v      # -v DELETES BOTH VOLUMES AND ALL DATA
  docker compose up -d && python scripts/01_setup.py
"""
import argparse
import subprocess
import sys
from pathlib import Path

from lib.couch import instances

DEMO_DBS = ["orders", "orders_global", "orders_partitioned", "orders_global_big",
            "orders_partitioned_big", "txn_test", "setup_check"]

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("--yes", action="store_true", help="do not ask for confirmation")
p.add_argument("--no-seed", action="store_true", help="do not re-seed after the reset")
args = p.parse_args()

if not args.yes:
    answer = input("This DELETES the demo databases and replication jobs on A and B. Type 'reset': ")
    if answer.strip() != "reset":
        sys.exit("Aborted.")

both = instances()
# stop jobs on both sides before deleting, or a running job keeps writing
for c in both:
    c.wait_ready(60)
    r = c.get("/_replicator/_all_docs")
    rows = r.body.get("rows", []) if r.ok else []
    for row in rows:
        if row["id"].startswith("rep-"):
            r = c.delete(f"/_replicator/{row['id']}", params={"rev": row["value"]["rev"]})
            print(f"{c.label}: stopped job {row['id']} -> HTTP {r.status}")
for c in both:
    for db in DEMO_DBS:
        r = c.delete(f"/{db}")
        if r.status != 404:
            print(f"{c.label}: deleted {db} -> HTTP {r.status}")

print("Reset complete.")
if not args.no_seed:
    seed = Path(__file__).with_name("02_seed.py")
    sys.exit(subprocess.call([sys.executable, str(seed), "--auto"]))
