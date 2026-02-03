# collectors/network_linux.py
#
# Linux network collector for AegisSurface
# Sensor: ss (iproute2)
# Contract: schema/network_snapshot_v1.py (v1.0)
#
# Responsibilities:
# - Observe sockets (LISTEN / ESTAB)
# - Summarize exposure and connections
# - Emit schema-compliant snapshot
#
# No decisions. No ML. No actions.

import subprocess
import re
import platform
from datetime import datetime, UTC

from schema.network_snapshot_v1 import build_network_snapshot


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INTERVAL_SECONDS = 60

# Historically sensitive ports (exposure signal, not vulnerability claim)
SENSITIVE_PORTS = {135, 139, 445}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_primary_ipv4() -> str:
    """
    Get the primary IPv4 address used for outbound traffic.
    Robust against multiple interfaces, VPNs, Wi-Fi, etc.
    """
    result = subprocess.run(
        ["ip", "-4", "route", "get", "1.1.1.1"],
        capture_output=True,
        text=True,
        check=False,
    )

    match = re.search(r"src (\S+)", result.stdout)
    return match.group(1) if match else "0.0.0.0"


# ---------------------------------------------------------------------------
# Low-level sensor
# ---------------------------------------------------------------------------

def _run_ss() -> list[str]:
    """
    Run `ss -tulpen` and return raw output lines.
    """
    result = subprocess.run(
        ["ss", "-tulpen"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.splitlines()


def _parse_ss(lines: list[str]):
    """
    Parse ss output.

    Returns:
        listening: list[(ip, port)]
        established: list[str]  # peer addresses
    """
    listening = []
    established = []

    # Skip header
    for line in lines[1:]:
        parts = re.split(r"\s+", line.strip())
        if len(parts) < 6:
            continue

        state = parts[0]
        local = parts[4]
        peer = parts[5]

        if ":" not in local:
            continue

        ip, port = local.rsplit(":", 1)

        try:
            port = int(port)
        except ValueError:
            continue

        if state == "LISTEN":
            listening.append((ip, port))
        elif state == "ESTAB":
            established.append(peer)

    return listening, established


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def _summarize(listening, established) -> dict:
    loopback_ports = []
    exposed_ports = []
    sensitive_open = []

    for ip, port in listening:
        if ip in ("127.0.0.1", "::1"):
            loopback_ports.append(port)
        else:
            exposed_ports.append(port)
            if port in SENSITIVE_PORTS:
                sensitive_open.append(port)

    external_ips = set()
    for addr in established:
        if not addr.startswith(("127.", "::1")):
            external_ips.add(addr.split(":")[0])

    return {
        "listening_ports_total": len(listening),
        "loopback_listening_ports": len(loopback_ports),
        "exposed_listening_ports": len(exposed_ports),
        "sensitive_ports_open": sorted(set(sensitive_open)),
        "established_external_conns": len(established),
        "unique_external_ips": len(external_ips),
    }


# ---------------------------------------------------------------------------
# Public collector API
# ---------------------------------------------------------------------------

def collect() -> dict:
    """
    Collect a single Linux network snapshot (schema v1.0).
    """
    lines = _run_ss()
    listening, established = _parse_ss(lines)
    summary = _summarize(listening, established)

    snapshot = build_network_snapshot(
        timestamp_utc=datetime.now(UTC).isoformat(),
        hostname=platform.node(),
        ipv4=get_primary_ipv4(),
        os_name=platform.platform(),
        interval_seconds=INTERVAL_SECONDS,
        listening_total=summary["listening_ports_total"],
        loopback_ports=summary["loopback_listening_ports"],
        exposed_ports=summary["exposed_listening_ports"],
        sensitive_ports=summary["sensitive_ports_open"],
        established_external=summary["established_external_conns"],
        unique_external_ips=summary["unique_external_ips"],
    )

    return snapshot


# ---------------------------------------------------------------------------
# Manual test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2))
