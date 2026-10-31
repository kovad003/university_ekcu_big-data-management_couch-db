"""No database needed. CouchDB itself is tested by the experiment scripts (python run.py)."""
import json
import string
from collections import Counter
from pathlib import Path

import pytest

from lib.couch import doc_path, load_env, redact
from lib.data import generate_orders
from lib.env import PASSWORD_ALPHABET, ensure_env, make_password
from lib.merge import expected_winner, rev_key, three_way_merge

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def orders():
    return generate_orders()


def test_dataset_size_and_status_counts(orders):
    assert len(orders) == 100
    assert Counter(d["status"] for d in orders) == {"open": 42, "shipped": 30, "paid": 20, "cancelled": 8}


def test_ids_unique_and_prefix_equals_tenant(orders):
    ids = [d["_id"] for d in orders]
    assert len(set(ids)) == len(ids)
    for d in orders:
        partition, _, rest = d["_id"].partition(":")
        assert partition == d["tenant"] and rest  # partitioned dbs reject ids without a prefix


def test_totals_match_line_items(orders):
    for d in orders:
        assert d["total"] == round(sum(i["qty"] * i["unit_price"] for i in d["items"]), 2)
        assert d["total"] > 0 and d["currency"] == "EUR"


def test_generator_is_deterministic():
    assert generate_orders() == generate_orders()
    assert generate_orders(seed=7) != generate_orders()


def test_committed_sample_matches_generator(orders):
    committed = json.loads((ROOT / "data" / "orders.json").read_text(encoding="utf-8"))
    assert committed == orders


def test_expected_query_answers(orders):
    # the slides and evidence quote these two numbers
    open01 = [d for d in orders if d["tenant"] == "store01" and d["status"] == "open"]
    assert len(open01) == 10  # experiment c
    assert sum(1 for d in open01 if d["total"] > 100) == 6  # experiment a


def test_timestamps_sort_as_text(orders):
    stamps = [d["created_at"] for d in orders]
    assert all(len(s) == 20 and s.endswith("Z") for s in stamps)  # fixed width, so text order = time order


def test_rev_key_orders_generation_before_hash():
    assert rev_key("10-aaa") > rev_key("9-fff")
    assert rev_key("2-b") > rev_key("2-a")


def test_expected_winner_matches_couchdb_rule():
    assert expected_winner(["2-03c9", "2-8fc0"]) == "2-8fc0"  # same depth, higher id
    assert expected_winner(["3-0000", "2-ffff"]) == "3-0000"  # depth beats id


BASE = {"_id": "s:o", "_rev": "1-x", "status": "open", "delivery": {"street": "Old 1."}, "total": 10}


def test_merge_takes_each_sides_own_change():
    winner = {**BASE, "_rev": "2-b", "status": "paid", "payment": {"method": "card"}}
    loser = {**BASE, "_rev": "2-a", "delivery": {"street": "New 2."}, "note": "address fixed"}
    merged, notes = three_way_merge(BASE, winner, loser)
    assert merged == {"status": "paid", "payment": {"method": "card"},
                      "delivery": {"street": "New 2."}, "note": "address fixed", "total": 10}
    assert notes == []


def test_merge_conflicting_field_keeps_winner_and_notes_it():
    winner = {**BASE, "total": 12}
    loser = {**BASE, "total": 15}
    merged, notes = three_way_merge(BASE, winner, loser)
    assert merged["total"] == 12
    assert notes == ["total: both sides changed, kept winner's value"]


def test_merge_respects_a_one_sided_removal():
    winner = {k: v for k, v in BASE.items() if k != "total"}
    merged, _ = three_way_merge(BASE, winner, dict(BASE))
    assert "total" not in merged


def test_merge_never_copies_system_fields():
    winner = {**BASE, "_rev": "2-b", "_conflicts": ["2-a"]}
    merged, _ = three_way_merge(BASE, winner, {**BASE, "_rev": "2-a"})
    assert not any(k.startswith("_") for k in merged)


def test_redact_hides_every_password_at_any_depth():
    job = {"source": {"url": "http://couch-a:5984/orders",
                      "auth": {"basic": {"username": "admin_a", "password": "s3cret"}}},
           "list": [{"Password": "x"}]}
    out = json.dumps(redact(job))
    assert "s3cret" not in out and '"x"' not in out
    assert "admin_a" in out


def test_generated_passwords_are_compose_safe():
    for _ in range(50):
        pw = make_password()
        assert len(pw) == 20 and set(pw) <= set(PASSWORD_ALPHABET)
    assert set(PASSWORD_ALPHABET) == set(string.ascii_letters + string.digits)


def test_ensure_env_creates_once_and_never_overwrites(tmp_path):
    template = ROOT / ".env.example"
    env_file = tmp_path / ".env"
    ensure_env(env_file, template)
    first = env_file.read_text(encoding="utf-8")
    values = load_env(env_file)
    assert values["COUCH_A_PASSWORD"] != values["COUCH_B_PASSWORD"]
    assert "change-me" not in first
    assert values["COUCH_A_INTERNAL_URL"] == "http://couch-a:5984"
    ensure_env(env_file, template)
    assert env_file.read_text(encoding="utf-8") == first


def test_env_files_are_git_ignored():
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").split()
    assert ".env" in ignored and ".venv/" in ignored


def test_load_env_parses_quotes_and_comments(tmp_path, monkeypatch):
    f = tmp_path / ".env"
    f.write_text('# comment\nA="x y"\nB=\'z\'\n\nC=1=2\n', encoding="utf-8")
    monkeypatch.delenv("A", raising=False)
    assert load_env(f) == {"A": "x y", "B": "z", "C": "1=2"}


def test_doc_path_keeps_partition_colon_and_escapes_the_rest():
    assert doc_path("orders", "store01:order001") == "/orders/store01:order001"
    assert doc_path("db", "a b/c") == "/db/a%20b%2Fc"


def test_compose_binds_ports_to_localhost_only():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert '"127.0.0.1:${COUCH_A_PORT:-5984}:5984"' in compose
    assert '"127.0.0.1:${COUCH_B_PORT:-5985}:5984"' in compose
    assert "image: couchdb:3.5.2" in compose
