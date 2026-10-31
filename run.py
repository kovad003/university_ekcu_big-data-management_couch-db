#!/usr/bin/env python3
"""One entry point for the whole project. No manual setup needed.

  python run.py            everything: .env, containers, setup, fresh data, experiments A-D
  python run.py up         create .env if needed, start A and B, setup, seed
  python run.py A          experiment A: CRUD + Mango          (also B, C, D)
  python run.py reset      back to the starting state (demo data re-seeded)
  python run.py status     container state and versions
  python run.py down       stop the containers (data is kept)
  python run.py wipe       remove containers AND their data volumes (asks first)
  python run.py test       offline reference tests (needs: pip install -r requirements-dev.txt)
  python run.py manifest   write MANIFEST.sha256; `manifest --check` verifies it

Options:
  --step     pause before every step (recording); single experiments pause by
             default when run in a real terminal
  --auto     never pause
  --timing   with C or the full run: include the optional timing experiment
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
from lib.env import ensure_env  # noqa: E402

EXPERIMENTS = {"A": "10_crud_mango.py", "B": "20_replication_conflict.py",
               "C": "30_partitioned_queries.py", "D": "40_atomicity.py"}


def sh(*cmd, check=True):
    print(f"$ {' '.join(cmd)}")
    code = subprocess.call(list(cmd), cwd=ROOT)
    if check and code != 0:
        sys.exit(code)
    return code


def py(script, *args):
    """Uses the same interpreter as run.py, so an active .venv is respected."""
    return sh(sys.executable, str(SCRIPTS / script), *args, check=False)


def docker_ok():
    if os.environ.get("SKIP_DOCKER"):  # for testing without docker
        return False
    if not shutil.which("docker"):
        sys.exit("Docker is not installed. See README section 4 (Fedora: Docker CE).")
    r = subprocess.run(["docker", "info"], capture_output=True, text=True)
    if r.returncode != 0:
        msg = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "unknown error"
        hint = ""
        if "permission denied" in r.stderr.lower():
            hint = "\nFix: sudo usermod -aG docker $USER, then log out and back in."
        elif "connect" in r.stderr.lower():
            hint = "\nFix: sudo systemctl enable --now docker"
        sys.exit(f"Docker is installed but not usable: {msg}{hint}")
    return True


def up(mode):
    ensure_env()
    if docker_ok():
        sh("docker", "compose", "up", "-d")
    if py("01_setup.py", mode) != 0:
        sys.exit("Setup failed; see the output above.")


def reset():
    if py("90_reset.py", "--yes", "--no-seed") != 0:
        sys.exit("Reset failed.")
    if py("02_seed.py", "--auto") != 0:
        sys.exit("Seeding failed.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", nargs="?", default="all",
                   choices=["all", "up", "A", "B", "C", "D", "a", "b", "c", "d",
                            "reset", "status", "down", "wipe", "test", "manifest"])
    p.add_argument("--step", action="store_true")
    p.add_argument("--auto", action="store_true")
    p.add_argument("--timing", action="store_true")
    p.add_argument("--check", action="store_true", help="with manifest: verify instead of write")
    a = p.parse_args()
    cmd = a.command.upper() if len(a.command) == 1 else a.command
    mode = "--step" if a.step else "--auto" if a.auto else ""
    mode_args = [mode] if mode else []

    if cmd == "all":
        up("--auto")
        reset()
        failed = []
        for key, script in EXPERIMENTS.items():
            extra = ["--timing"] if (key == "C" and a.timing) else []
            if py(script, *(mode_args or ["--auto"]), *extra) != 0:
                failed.append(key)
        print("\nAll experiments passed. Evidence is in evidence/." if not failed
              else f"\nFailed experiments: {', '.join(failed)}. See their output above.")
        sys.exit(1 if failed else 0)

    if cmd == "up":
        up("--auto")
        reset()
        print("\nReady. Next: python run.py A   (or B, C, D)")
    elif cmd in EXPERIMENTS:
        ensure_env()
        if cmd == "B":  # b refuses leftovers from an earlier run
            print("Experiment B starts from a fresh state: resetting first.")
            reset()
        extra = ["--timing"] if (cmd == "C" and a.timing) else []
        sys.exit(py(EXPERIMENTS[cmd], *mode_args, *extra))
    elif cmd == "reset":
        reset()
    elif cmd == "status":
        if docker_ok():
            sh("docker", "compose", "ps", check=False)
        py("01_setup.py", "--auto")
    elif cmd == "down":
        if docker_ok():
            sh("docker", "compose", "stop")
    elif cmd == "test":
        try:
            import pytest  # noqa: F401
        except ImportError:
            sys.exit("pytest is not installed: python -m pip install -r requirements-dev.txt")
        sys.exit(sh(sys.executable, "-m", "pytest", "-q", check=False))
    elif cmd == "manifest":
        sys.exit(py("make_manifest.py", *(["--check"] if a.check else [])))
    elif cmd == "wipe":
        if input("This DELETES both containers and ALL their data. Type 'wipe': ").strip() == "wipe":
            if docker_ok():
                sh("docker", "compose", "down", "-v")
        else:
            print("Aborted.")


if __name__ == "__main__":
    main()
