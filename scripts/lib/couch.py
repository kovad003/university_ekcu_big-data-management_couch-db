"""CouchDB over HTTP with the standard library only, so nothing needs pip on any of our machines."""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

# all traffic is local, never route it through a system proxy
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def load_env(path: Path = REPO_ROOT / ".env") -> dict:
    """Environment variables override values from the file."""
    values: dict = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            values[key.strip()] = val.strip().strip('"').strip("'")
    for key in list(values):
        if key in os.environ:
            values[key] = os.environ[key]
    return values


def _require(env: dict, key: str) -> str:
    if not env.get(key):
        raise SystemExit(
            f"Missing {key} in .env. Delete .env and run `python run.py` to regenerate it."
        )
    return env[key]


@dataclass
class Resp:
    status: int
    reason: str
    body: Any  # parsed json, raw text if it isn't json

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300


class Couch:
    def __init__(self, label: str, url: str, user: str, password: str,
                 internal_url: str):
        self.label = label
        self.url = url.rstrip("/")
        self.user = user
        self.password = password
        # the replicator runs inside docker, where localhost is the container itself
        self.internal_url = internal_url.rstrip("/")
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        self._auth_header = f"Basic {token}"

    def replication_endpoint(self, db: str) -> dict:
        return {
            "url": f"{self.internal_url}/{db}",
            "auth": {"basic": {"username": self.user, "password": self.password}},
        }

    def request(self, method: str, path: str, body: Any = None,
                params: Optional[dict] = None, timeout: float = 30) -> Resp:
        url = self.url + path
        if params:
            enc = {k: (json.dumps(v) if isinstance(v, bool) else v)
                   for k, v in params.items()}
            url += "?" + urllib.parse.urlencode(enc)
        data = None
        headers = {"Authorization": self._auth_header, "Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with _OPENER.open(req, timeout=timeout) as r:
                return Resp(r.status, r.reason, _parse(r.read()))
        except urllib.error.HTTPError as e:  # 409, 404 etc. are results we check
            return Resp(e.code, e.reason, _parse(e.read()))

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def put(self, path, body=None, **kw):
        return self.request("PUT", path, body, **kw)

    def post(self, path, body=None, **kw):
        return self.request("POST", path, body, **kw)

    def delete(self, path, **kw):
        return self.request("DELETE", path, **kw)

    def wait_ready(self, timeout_s: float = 60) -> dict:
        """Exits the program if the node hasn't answered GET / within timeout_s."""
        deadline = time.time() + timeout_s
        last = None
        while time.time() < deadline:
            try:
                r = self.get("/", timeout=3)
                if r.ok:
                    return r.body
                last = f"HTTP {r.status}"
            except Exception as exc:  # refused while the container boots
                last = repr(exc)
            time.sleep(1)
        raise SystemExit(f"Instance {self.label} at {self.url} not ready after "
                         f"{timeout_s}s (last error: {last}). Start it with `python run.py up`.")


def _parse(raw: bytes):
    text = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(text) if text else None
    except json.JSONDecodeError:
        return text


def doc_path(db: str, doc_id: str) -> str:
    """Leaves ':' unescaped so partitioned ids stay readable in the transcripts."""
    return f"/{db}/" + urllib.parse.quote(doc_id, safe=":")


def instances() -> tuple[Couch, Couch]:
    from .env import ensure_env
    ensure_env()
    env = load_env()
    a = Couch("A", f"http://127.0.0.1:{env.get('COUCH_A_PORT', '5984')}",
              _require(env, "COUCH_A_USER"), _require(env, "COUCH_A_PASSWORD"),
              env.get("COUCH_A_INTERNAL_URL", "http://couch-a:5984"))
    b = Couch("B", f"http://127.0.0.1:{env.get('COUCH_B_PORT', '5985')}",
              _require(env, "COUCH_B_USER"), _require(env, "COUCH_B_PASSWORD"),
              env.get("COUCH_B_INTERNAL_URL", "http://couch-b:5984"))
    return a, b


def wait_until(predicate, timeout_s: float = 60, interval_s: float = 0.5):
    """Returns (ok, last value, seconds waited)."""
    start = time.time()
    value = None
    while True:
        value = predicate()
        if value:
            return True, value, round(time.time() - start, 2)
        if time.time() - start >= timeout_s:
            return False, value, round(time.time() - start, 2)
        time.sleep(interval_s)


def all_docs(couch: "Couch", db: str) -> list[dict]:
    """Design documents are skipped."""
    r = couch.get(f"/{db}/_all_docs", params={"include_docs": True})
    return [row["doc"] for row in r.body["rows"] if not row["id"].startswith("_design/")]


def redact(obj: Any) -> Any:
    """Masks every "password" key at any depth, case-insensitive. Returns a copy."""
    if isinstance(obj, dict):
        return {k: ("***" if k.lower() == "password" else redact(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    return obj
