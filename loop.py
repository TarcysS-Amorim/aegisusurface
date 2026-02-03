# loop.py
#
# Continuous snapshot loop for AegisSurface
# Role:
# - call collector
# - persist schema-compliant snapshots
# - control timing
#
# No parsing, no features, no ML.

import time
import json
from pathlib import Path
from datetime import datetime, UTC

from collectors.network_linux import collect


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INTERVAL_SECONDS = 60
BASE_OUT_DIR = Path("out/snapshots_v2/network")


# ---------------------------------------------------------------------------
# Loop
# ---------------------------------------------------------------------------

def main():
    print("[*] AegisSurface loop started (Linux baseline v2)")
    print(f"[*] Interval: {INTERVAL_SECONDS}s")
    print(f"[*] Output: {BASE_OUT_DIR.resolve()}")

    while True:
        ts = datetime.now(UTC)

        try:
            snapshot = collect()
        except Exception as e:
            # Collector failure should not kill the loop
            print(f"[!] collector error: {e}")
            time.sleep(INTERVAL_SECONDS)
            continue

        date_dir = ts.strftime("%Y-%m-%d")
        time_file = ts.strftime("%H-%M-%S.json")

        out_dir = BASE_OUT_DIR / date_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / time_file

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
        except Exception as e:
            print(f"[!] failed to write snapshot: {e}")
        else:
            print(f"[+] snapshot saved: {out_path}")

        time.sleep(INTERVAL_SECONDS)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
