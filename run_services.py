"""Kyzentra AI - All Services Launcher (Python)

Usage:
    python run_services.py
"""

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

SERVICES = [
    {"name": "Frontend", "port": 3000, "arg": "frontend"},
    {"name": "Backend",  "port": 8000, "arg": "backend"},
    {"name": "Kie",      "port": 8001, "arg": "kie"},
    {"name": "Kie-2",    "port": 8002, "arg": "kie-2"},
]

def main():
    bat_path = ROOT_DIR / "run_services.bat"
    if not bat_path.exists():
        print(f"[!] Error: {bat_path} not found.")
        sys.exit(1)

    print("=" * 66)
    print("             Kyzentra AI - Starting All Services")
    print("=" * 66)
    print()

    for s in SERVICES:
        print(f"  -> Spawning {s['name']:<10} on http://localhost:{s['port']}")
        cmd = f'cmd.exe /k call "{bat_path}" {s["arg"]}'
        subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            cwd=str(ROOT_DIR)
        )

    print()
    print("=" * 66)
    print("All 4 services launched in separate terminal windows.")
    print("=" * 66)

if __name__ == "__main__":
    main()
