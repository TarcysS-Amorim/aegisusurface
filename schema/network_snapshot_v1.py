# schema/network_snapshot_v1.py

SCHEMA_VERSION = "1.0"

def build_network_snapshot(
    *,
    timestamp_utc: str,
    hostname: str,
    ipv4: str,
    os_name: str,
    interval_seconds: int,
    listening_total: int,
    loopback_ports: int,
    exposed_ports: int,
    sensitive_ports: list[int],
    established_external: int,
    unique_external_ips: int
) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,

        "snapshot": {
            "timestamp_utc": timestamp_utc,
            "interval_seconds": interval_seconds
        },

        "host": {
            "hostname": hostname,
            "ipv4": ipv4,
            "os": os_name
        },

        "network": {
            "listening": {
                "total_ports": listening_total,
                "loopback_ports": loopback_ports,
                "exposed_ports": exposed_ports,
                "sensitive_ports": sensitive_ports
            },

            "connections": {
                "established_external": established_external,
                "unique_external_ips": unique_external_ips
            }
        }
    }
