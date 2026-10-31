"""First run writes .env from the template with random passwords.

To change passwords: python run.py wipe, delete .env, run again. Containers
created with the old .env keep the old admin passwords.
"""
from __future__ import annotations

import secrets
import string
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"
TEMPLATE = REPO_ROOT / ".env.example"
# no symbols: compose treats $ in .env as variable interpolation
PASSWORD_ALPHABET = string.ascii_letters + string.digits


def make_password(n: int = 20) -> str:
    return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(n))


def ensure_env(env_file: Path = ENV_FILE, template: Path = TEMPLATE) -> Path:
    """Does nothing if env_file already exists."""
    if env_file.exists():
        return env_file
    out = ["# Generated automatically by run.py. Git-ignored. Do not commit.", ""]
    for line in template.read_text(encoding="utf-8").splitlines():
        if line.startswith("COUCH_A_PASSWORD="):
            line = f"COUCH_A_PASSWORD={make_password()}"
        elif line.startswith("COUCH_B_PASSWORD="):
            line = f"COUCH_B_PASSWORD={make_password()}"
        out.append(line)
    env_file.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Created {env_file.name} with random passwords (Fauxton logins are listed in it).")
    return env_file
