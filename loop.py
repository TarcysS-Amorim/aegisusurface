# loop.py

import time
import json
from pathlib import Path
from datetime import datetime, UTC

from collectors.network import collect

INTERVAL_SECONDS = 60


def main():
    while True:
        snapshot = collect()

        ts = datetime.now(UTC)
        date_dir = ts.strftime("%Y-%m-%d")
        time_file = ts.strftime("%H-%M-%S.json")

        out_dir = Path("out/snapshots_v1/network") / date_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / time_file

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)

        print(f"[+] snapshot saved: {out_path}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
