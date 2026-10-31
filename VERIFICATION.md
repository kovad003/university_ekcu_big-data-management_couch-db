# Verification record

## Live runs on the recording machine

Two runs on 2026-10-30, both against two live CouchDB 3.5.2 containers, both 80 out of 80. The first was `python run.py`, unattended, on the earlier code. The second used the current code, one experiment at a time: `up`, `A --auto`, `B` stepped by hand (for the Fauxton screenshots), `C --auto`, `D --auto`. The files in `evidence/` come from the second run.

| Script                                                               | Checks passed |
|----------------------------------------------------------------------|--------------:|
| `01_setup.py` (readiness, membership, single-node setup, write/read) |       14 / 14 |
| `02_seed.py` (demo database, 100 orders)                             |         4 / 4 |
| `10_crud_mango.py` (experiment A)                                    |         9 / 9 |
| `20_replication_conflict.py` (experiment B)                          |       27 / 27 |
| `30_partitioned_queries.py` (experiment C)                           |       15 / 15 |
| `40_atomicity.py` (experiment D)                                     |       11 / 11 |
| total                                                                |       80 / 80 |

Each check compares a stated expected value with what CouchDB returned. The details are in `evidence/<experiment>/results.json` and `record.md`.

The machine was a Fedora 44 laptop (Intel, amd64) with Docker 29.9.2, Docker Compose v5.6.1 and Python 3.14.8 in the project `.venv`. Image `couchdb:3.5.2`, digest `sha256:5fc596110eac7f412173a7d9de14f70aa5d3e816790fb6e70642755d4a4cf464`, CouchDB git_sha 5b4d92103. Each container had a 512 MiB limit and used 103–112 MiB after setup.

Both runs produced the same revision ids, counts and query results, which is expected: the data is seeded and CouchDB derives revision ids from content. Two things differ. Experiment B now resets before it starts, so A no longer carries the index from experiment A, and the catch-up count is 100 on each side rather than 101. And because B was stepped by hand in the second run, replication had finished before each check looked, so its timings read 0 s. The times quoted in the slides and README (job running within 1 s, documents across within 0.5 s) come from the unattended first run.

## Offline tests

`python run.py test` gave 20 passed, 0 skipped. These tests don't touch CouchDB. They check:

- the generated dataset (counts, id rule, totals, same output every time, and that `data/orders.json` matches the generator)
- the winning-revision rule and our merge rule
- password masking and the generated `.env`
- a few config facts, like ports bound to 127.0.0.1

On the recording machine: Python 3.14.8, pytest 9.2.0, 20 passed in 0.11 s. Also passed in the build environment (Python 3.13.18, pytest 9.1.1).

## Screenshots

`evidence/screenshots/` holds three captures from instance B, taken mid-experiment, before the merge: Fauxton showing only the winning revision `2-d520…`, the same document with `?conflicts=true` listing `2-1f7d…`, and that losing revision fetched by id. The slide deck uses them.

## Not run

macOS (Intel, Docker Desktop) and Windows 11 (Docker Desktop with WSL 2) are planned but not done yet. `run_windows.bat` was read through, not run.

The optional timing run (`python run.py C --timing`, 10,000 orders) exists but hasn't been executed. No performance claim is made.

Stopping an instance during replication (`docker compose stop couch-b`) isn't part of the evidence. Experiment B stops the replication jobs, which is a different test from a stopped node or a network partition.

Fauxton wasn't used for any result. Everything came through the HTTP API.

## Limits

Both instances share one laptop. That shows separate processes, not surviving the loss of the machine.

Replication times (about 1 s for a job to start, about 0.5 s for a document to arrive) come from polling every 0.5 s. They are upper bounds, not latency measurements.

The partitioned database runs on one node with `n=1` and `q=2`. Experiment C shows that both queries give the same answer and that the partitioned one stays inside one store. It says nothing about spreading data over servers or about speed.

`requirements-dev.txt` gives a version range, not a lock file. The project itself needs no third-party packages.
