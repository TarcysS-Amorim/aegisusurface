# features/build_features_v1.py

import json
from pathlib import Path
from datetime import datetime
import pandas as pd


SNAPSHOT_ROOT = Path("out/snapshots/network")


def load_snapshots() -> list[dict]:
    """
    Carrega todos os snapshots JSON em ordem temporal.
    """
    snapshots = []

    for day_dir in sorted(SNAPSHOT_ROOT.glob("*")):
        if not day_dir.is_dir():
            continue

        for file in sorted(day_dir.glob("*.json")):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                snapshots.append(data)

    return snapshots


def extract_row(snapshot: dict) -> dict:
    """
    Extrai uma linha numérica a partir de um snapshot v1.0
    """
    ts = snapshot["snapshot"]["timestamp_utc"]

    net = snapshot["network"]
    listening = net["listening"]
    connections = net["connections"]

    return {
        "timestamp": datetime.fromisoformat(ts),

        # Superfície
        "listening_total": listening["total_ports"],
        "loopback_ports": listening["loopback_ports"],
        "exposed_ports": listening["exposed_ports"],
        "sensitive_ports_count": len(listening["sensitive_ports"]),

        # Comportamento
        "established_external": connections["established_external"],
        "unique_external_ips": connections["unique_external_ips"],
    }


def build_dataframe(snapshots: list[dict]) -> pd.DataFrame:
    """
    Constrói DataFrame temporal a partir dos snapshots
    """
    rows = [extract_row(s) for s in snapshots]
    df = pd.DataFrame(rows)

    df = df.sort_values("timestamp").reset_index(drop=True)

    return df


def add_deltas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona features de variação temporal (delta)
    """
    delta_cols = [
        "exposed_ports",
        "established_external",
        "unique_external_ips",
        "sensitive_ports_count",
    ]

    for col in delta_cols:
        df[f"delta_{col}"] = df[col].diff().fillna(0)

    return df


def main():
    snapshots = load_snapshots()
    if not snapshots:
        raise RuntimeError("Nenhum snapshot encontrado.")

    df = build_dataframe(snapshots)
    df = add_deltas(df)

    out_dir = Path("out/features")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "network_features_v1.csv"
    df.to_csv(out_path, index=False)

    print(f"[+] Feature table criada: {out_path}")
    print(df.tail())


if __name__ == "__main__":
    main()
