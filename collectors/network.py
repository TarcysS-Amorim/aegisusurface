# collectors/network_linux.py

import subprocess
import re
import platform
import socket
from datetime import datetime, UTC

from schema.network_snapshot_v1 import build_network_snapshot

SENSITIVE_PORTS = {135, 139, 445}
INTERVAL_SECONDS = 60


def run_ss():
    result = subprocess.run(
        ["ss", "-tulpen"],
        capture_output=True,
        text=True
    )
    return result.stdout.splitlines()


def parse_ss(lines):
    listening = []
    established = []

    for line in lines[1:]:  # pula header
        parts = re.split(r"\s+", line)
        if len(parts) < 5:
            continue

        state = parts[0]
        local = parts[4]
        peer = parts[5] if len(parts) > 5 else ""

        # normaliza local address
        if ":" in local:
            ip, port = local.rsplit(":", 1)
        else:
            continue

        try:
            port = int(port)
        except ValueError:
            continue

        if state == "LISTEN":
            listening.append((ip, port))
        elif state == "ESTAB":
            established.append(peer)

    return listening, established


def summarize(listening, established):
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
        if addr and not addr.startswith(("127.", "::1")):
            external_ips.add(addr.split(":")[0])

    return {
        "listening_ports_total": len(listening),
        "loopback_listening_ports": len(loopback_ports),
        "exposed_listening_ports": len(exposed_ports),
        "sensitive_ports_open": sorted(set(sensitive_open)),
        "established_external_conns": len(established),
        "unique_external_ips": len(external_ips),
    }


def collect():
    lines = run_ss()
    listening, established = parse_ss(lines)
    summary = summarize(listening, established)

    snapshot = build_network_snapshot(
        timestamp_utc=datetime.now(UTC).isoformat(),
        hostname=platform.node(),
        ipv4=socket.gethostbyname(socket.gethostname()),
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


if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2))
