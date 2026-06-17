"""Create private working files from examples if they do not exist."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COPIES = [
    ("00_user_profile/personal_info.example.yaml", "00_user_profile/personal_info.yaml"),
    ("00_user_profile/experience_bank.example.yaml", "00_user_profile/experience_bank.yaml"),
    ("00_user_profile/truth_rules.example.md", "00_user_profile/truth_rules.md"),
    ("06_tracker/applied_jobs_master.example.csv", "06_tracker/applied_jobs_master.csv"),
    ("config.example.yaml", "config.yaml"),
]


def main() -> int:
    for source_name, target_name in COPIES:
        source = ROOT / source_name
        target = ROOT / target_name
        if target.exists():
            print(f"Keeping existing {target_name}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        print(f"Created {target_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
