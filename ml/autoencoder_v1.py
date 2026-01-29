import pandas as pd

df = pd.read_csv("out/features/network_features_v1.csv")

print(df.describe())

cols = [
    "exposed_ports",
    "established_external",
    "unique_external_ips",
    "sensitive_ports_count",
]

print("\nMédias:")
print(df[cols].mean())

print("\nDesvios padrão:")
print(df[cols].std())

print("\nDeltas (média ~0 é o esperado):")
print(df[[f"delta_{c}" for c in cols]].mean())
