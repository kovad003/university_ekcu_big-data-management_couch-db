"""Conflict logic for experiment B, kept out of the HTTP code so the tests can reach it.

CouchDB picks the same winner on every replica: highest generation, then the
highest revision id as a string. It never merges bodies. three_way_merge is our rule.
"""
from __future__ import annotations

SYSTEM_FIELDS = {"_id", "_rev", "_conflicts", "_deleted_conflicts", "_revisions", "_revs_info"}


def rev_key(rev: str) -> tuple[int, str]:
    generation, digest = rev.split("-", 1)
    return int(generation), digest


def expected_winner(revs: list[str]) -> str:
    """Only valid for live (not deleted) leaf revisions."""
    return max(revs, key=rev_key)


def three_way_merge(base: dict, winner: dict, loser: dict) -> tuple[dict, list[str]]:
    """Per top-level field, compared with the common ancestor `base`.

    A field changed on one side takes that side's value, removals included.
    Changed differently on both sides: the winner's value wins and a note is added.
    Underscore fields are dropped; the caller sets _id and _rev.
    """
    merged: dict = {}
    notes: list[str] = []
    missing = object()  # tells a removed field apart from one set to null
    fields = (set(base) | set(winner) | set(loser)) - SYSTEM_FIELDS
    for field in sorted(fields):
        b = base.get(field, missing)
        w = winner.get(field, missing)
        l = loser.get(field, missing)
        if w == l:
            value = w
        elif w == b:
            value = l
        elif l == b:
            value = w
        else:
            value = w
            notes.append(f"{field}: both sides changed, kept winner's value")
        if value is not missing:
            merged[field] = value
    return merged, notes
