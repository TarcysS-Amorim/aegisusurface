import pandas as pd
import numpy as np

# ------------------------------------------------------------------
# Load scored dataset
# ------------------------------------------------------------------

df = pd.read_csv("out/features/network_features_v2_scored.csv")

# ------------------------------------------------------------------
# Normalize reconstruction error
# ------------------------------------------------------------------

ae = df["reconstruction_error"]
df["ae_norm"] = (ae - ae.mean()) / ae.std()

# ------------------------------------------------------------------
# Statistical z-scores (selected features)
# ------------------------------------------------------------------

STAT_COLS = [
    "exposed_ports",
    "established_external",
    "unique_external_ips",
    "sensitive_ports_count",
]

z_scores = []
for col in STAT_COLS:
    z = (df[col] - df[col].mean()) / df[col].std()
    z_scores.append(z.abs())

df["stat_score"] = pd.concat(z_scores, axis=1).mean(axis=1)

# ------------------------------------------------------------------
# Hybrid risk score
# ------------------------------------------------------------------

W_AE = 0.6
W_STAT = 0.4

df["risk_score"] = W_AE * df["ae_norm"].abs() + W_STAT * df["stat_score"]

# ------------------------------------------------------------------
# Rank
# ------------------------------------------------------------------

df = df.sort_values("risk_score", ascending=False)
OUT = "out/features/network_features_v2_ranked.csv"
df.to_csv(OUT, index=False)

print(f"[✓] Ranked risk table written to: {OUT}")
print(df[["timestamp", "risk_score"]].head(10))
