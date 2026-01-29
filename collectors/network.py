# collectors/network.py

import subprocess
import re
import platform
import socket
from datetime import datetime, UTC

from schema.network_snapshot_v1 import build_network_snapshot

SENSITIVE_PORTS = {135, 139, 445}
INTERVAL_SECONDS = 60


def run_netstat():
    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True,
        text=True,
        shell=True
    )
    return result.stdout.splitlines()


def parse_netstat(lines):
    listening = []
    established = []

    for line in lines:
        if line.startswith("  TCP") or line.startswith("  UDP"):
            parts = re.split(r"\s+", line.strip())
            if len(parts) < 4:
                continue

            proto = parts[0]
            local = parts[1]
            remote = parts[2]
            state = parts[3] if proto == "TCP" else "UDP"

            if state == "LISTENING":
                listening.append(local)
            elif state == "ESTABLISHED":
                established.append(remote)

    return listening, established


def summarize(listening, established):
    exposed_ports = []
    loopback_ports = []
    sensitive_open = []

    for addr in listening:
        try:
            ip, port = addr.rsplit(":", 1)
            port = int(port)
        except ValueError:
            continue

        if ip.startswith("127.") or ip in ("[::1]", "::1"):
            loopback_ports.append(port)
        else:
            exposed_ports.append(port)
            if port in SENSITIVE_PORTS:
                sensitive_open.append(port)

    external_ips = set()
    for addr in established:
        if not addr.startswith(("127.", "[::1]", "::1")):
            external_ips.add(addr.split(":")[0])

    return {
        "listening_ports_total": len(listening),
        "loopback_listening_ports": len(loopback_ports),
        "exposed_listening_ports": len(exposed_ports),
        "sensitive_ports_open": sorted(set(sensitive_open)),
        "established_external_conns": len(established),
        "unique_external_ips": len(external_ips)
    }


def collect():
    lines = run_netstat()
    listening, established = parse_netstat(lines)
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
        unique_external_ips=summary["unique_external_ips"]
    )

    return snapshot


if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2))
