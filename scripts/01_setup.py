#!/usr/bin/env python3
"""Part 2: readiness and single-node setup of A and B. Safe to re-run.

Waits for both nodes (60 s max), shows that each lists only itself in
/_membership, sets n=1, creates _users and _replicator, does a write/read,
and saves the image digest and container stats if the docker cli is there.
"""
import subprocess

from lib.couch import doc_path, instances
from lib.demo import Demo, make_parser

args = make_parser(__doc__).parse_args()
A, B = instances()

demo = Demo("00_setup", "Part 2: Setup and readiness of instances A and B", args, [
    f"Instance A: {A.url} (inside Docker: {A.internal_url})",
    f"Instance B: {B.url} (inside Docker: {B.internal_url})",
    "Image: couchdb:3.5.2 (Apache License 2.0), two containers, two named volumes",
])

demo.part("Readiness")
for c in (A, B):
    demo.step(f"Wait until instance {c.label} answers (bounded: 60 s)")
    c.wait_ready(60)
    r = demo.call(c, "GET", "/")
    demo.check(f"{c.label} runs CouchDB 3.5.x",
               r.ok and str(r.body.get("version", "")).startswith("3.5"),
               "HTTP 200, version 3.5.x", f"HTTP {r.status}, version {r.body.get('version')}")

demo.part("Topology: two independent single nodes")
nodes = {}
for c in (A, B):
    demo.step(f"Membership of {c.label}: which nodes does it know?",
              "A cluster would list both nodes. Independent instances list only themselves.")
    r = demo.call(c, "GET", "/_membership")
    nodes[c.label] = r.body.get("cluster_nodes", [])
    demo.check(f"{c.label} is a single-node instance", len(nodes[c.label]) == 1,
               "cluster_nodes has exactly 1 entry", f"{nodes[c.label]}")

demo.part("Single-node setup")
for c in (A, B):
    demo.step(f"Set the default replica count n=1 on {c.label}",
              "One node can hold only one copy of each shard, so n=1 is the honest setting.")
    r = demo.call(c, "PUT", "/_node/_local/_config/cluster/n", "1")
    demo.check(f"{c.label} accepted cluster/n=1", r.ok, "HTTP 200", f"HTTP {r.status}")
    for sysdb in ("_users", "_replicator"):
        demo.step(f"Create system database {sysdb} on {c.label}")
        r = demo.call(c, "PUT", f"/{sysdb}", params={"n": 1})
        demo.check(f"{sysdb} exists on {c.label}", r.status in (201, 202, 412),
                   "HTTP 201 (created) or 412 (already exists)", f"HTTP {r.status}")
    demo.step(f"Health endpoint of {c.label}")
    r = demo.call(c, "GET", "/_up")
    demo.check(f"{c.label} reports status ok", r.ok and r.body.get("status") == "ok",
               'HTTP 200 {"status":"ok"}', f"HTTP {r.status} {r.body}")

demo.part("Test write and read")
for c in (A, B):
    demo.step(f"Write then read a test document on {c.label}")
    demo.call(c, "PUT", "/setup_check", params={"n": 1})
    w = demo.call(c, "PUT", doc_path("setup_check", "hello"), {"written_by": "01_setup.py"})
    r = demo.call(c, "GET", doc_path("setup_check", "hello"))
    demo.check(f"Read-back on {c.label} matches the write",
               w.status == 201 and r.ok and r.body.get("written_by") == "01_setup.py",
               "HTTP 201 then HTTP 200 with the same content",
               f"HTTP {w.status} then HTTP {r.status}, written_by={r.body.get('written_by') if r.ok else None}")
    demo.call(c, "DELETE", "/setup_check", screen="status")

demo.part("Versions and container state (best effort)")
demo.step("Record image digest and container state for the README")
lines = []
for cmd in (["docker", "image", "inspect", "couchdb:3.5.2", "--format", "{{index .RepoDigests 0}}  {{.Architecture}}"],
            ["docker", "compose", "ps", "--format", "table {{.Name}}\t{{.Status}}\t{{.Ports}}"],
            ["docker", "stats", "--no-stream", "--format", "table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}", "couch-a", "couch-b"]):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as exc:  # no docker cli in this shell, record that and move on
        out = f"(not available: {exc})"
    lines.append(f"$ {' '.join(cmd)}\n{out}\n")
    print("\n".join("      " + l for l in lines[-1].splitlines()))
(demo.dir / "versions.txt").write_text("\n".join(lines), encoding="utf-8")
demo.info("Saved to evidence/00_setup/versions.txt")

demo.finish([
    "Both instances answer, run CouchDB 3.5.x and each lists only itself in "
    "cluster_nodes, so A and B are two independent single-node instances, not one cluster.",
    "Single-node setup is complete: default n=1 and the _users and _replicator system databases exist.",
    "A write followed by a read succeeds on each instance.",
])
