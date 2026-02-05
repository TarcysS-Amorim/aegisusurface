# features/build_features_v1.py
#
# Feature builder v1 for AegisSurface
#
# Responsibility:
# - Load schema v1 snapshots
# - Build time-ordered, tabular features
# - Compute deltas between consecutive snapshots
#
# No ML. No scoring. No decisions.

import json
from pathlib import Path
from datetime import datetime

import pandas as pd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SNAPSHOT_ROOT = Path("out/snapshots_v2/network")
OUT_DIR = Path("out/features")
OUT_CSV = OUT_DIR / "network_features_v2.csv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_snapshots() -> list[dict]:
    """
    Load all snapshot JSON files recursively.
    """
    snapshots = []

    for path in sorted(SNAPSHOT_ROOT.rglob("*.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                snapshots.append(data)
        except Exception as e:
            print(f"[!] failed to load {path}: {e}")

    return snapshots


def extract_features(snapshot: dict) -> dict:
    """
    Extract numeric features from a single snapshot (schema v1).
    """
    ts = snapshot["snapshot"]["timestamp_utc"]

    net = snapshot["network"]

    listening = net["listening"]
    connections = net["connections"]

    return {
        "timestamp": ts,
        "listening_ports_total": listening["total_ports"],
        "loopback_ports": listening["loopback_ports"],
        "exposed_ports": listening["exposed_ports"],
        "sensitive_ports_count": len(listening["sensitive_ports"]),
        "established_external": connections["established_external"],
        "unique_external_ips": connections["unique_external_ips"],
    }


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def main():
    print("[*] Loading snapshots...")
    snapshots = load_snapshots()

    if not snapshots:
        raise RuntimeError("No snapshots found.")

    print(f"[+] Loaded {len(snapshots)} snapshots")

    rows = []
    for snap in snapshots:
        try:
            rows.append(extract_features(snap))
        except Exception as e:
            print(f"[!] failed to extract features: {e}")

    df = pd.DataFrame(rows)

    # Ensure temporal ordering
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    # -----------------------------------------------------------------------
    # Delta features (temporal change)
    # -----------------------------------------------------------------------

    numeric_cols = [
        "listening_ports_total",
        "loopback_ports",
        "exposed_ports",
        "sensitive_ports_count",
        "established_external",
        "unique_external_ips",
    ]

    for col in numeric_cols:
        df[f"delta_{col}"] = df[col].diff().fillna(0)

    # -----------------------------------------------------------------------
    # Persist
    # -----------------------------------------------------------------------

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    print(f"[✓] Feature table written to: {OUT_CSV}")
    print(f"[✓] Rows: {len(df)} | Columns: {len(df.columns)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
