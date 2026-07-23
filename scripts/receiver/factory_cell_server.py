#!/usr/bin/env python3

import collections
import html
import json
import os
import socket
import threading
from datetime import datetime
from flask import Flask, jsonify, redirect


# ============================================================
# Factory Cell Receiver Server - safer demo version
#
# Stability changes:
# 1. Do NOT listen on every TCP port from 10001 to 11000.
#    Only listen on the vendor ports used by the demo generator.
# 2. UI reads only the latest UI_MAX_LINES records.
# 3. Event log is automatically trimmed when it grows too large.
# 4. /health endpoint added for quick service checks.
#
# Scope:
# This is a benign defensive lab receiver for authorized demos.
# It is not a traffic stress test, exploit framework, or pentest tool.
# ============================================================

SERVER_IP = os.getenv("RECEIVER_SERVER_IP", "<receiver_server_ip>")
WEB_PORT = int(os.getenv("WEB_UI_PORT", "8080"))

BASE_DIR = os.getenv("RECEIVER_BASE_DIR", "./runtime/factory-server")
LOG_DIR = os.path.join(BASE_DIR, "logs")
EVENT_LOG = os.path.join(LOG_DIR, "factory_cell_events.jsonl")

UI_MAX_LINES = int(os.getenv("UI_MAX_LINES", "1000"))
TIMELINE_MAX_ROWS = int(os.getenv("TIMELINE_MAX_ROWS", "200"))
MAX_LOG_BYTES = int(os.getenv("MAX_LOG_BYTES", str(10 * 1024 * 1024)))
KEEP_LOG_LINES = int(os.getenv("KEEP_LOG_LINES", "1000"))

# Do not open the full 10001-11000 demo range.
# Only keep specific vendor ports used by the generator.
LISTEN_PORTS = [
    445,
    1433,
    3389,
    10001,
    10274,
    10555,
    10888,
]

app = Flask(__name__)

FAILED_BINDS = []
FAILED_BINDS_LOCK = threading.Lock()
EVENT_LOG_LOCK = threading.Lock()


DEVICE_MAP = {
    "fe01": {"ip": "<virtual_device_ip_01>", "mac": "<virtual_mac_01>", "role": "Engineering Workstation"},
    "cell01": {"ip": "<virtual_device_ip_02>", "mac": "<virtual_mac_02>", "role": "Factory Cell Controller"},
    "hmi01": {"ip": "<virtual_device_ip_03>", "mac": "<virtual_mac_03>", "role": "HMI SCADA Station"},
    "edge01": {"ip": "<virtual_device_ip_04>", "mac": "<virtual_mac_04>", "role": "IIoT Edge Gateway"},
    "maint01": {"ip": "<virtual_device_ip_05>", "mac": "<virtual_mac_05>", "role": "Maintenance Laptop"},
}


PORT_INFO = {
    445: ("SMB File Sync", "Factory Cell", "SMB style file transfer for recipe files, CSV logs, batch reports, and machine configuration files."),
    1433: ("MES SQL Query", "Factory Cell MES", "MES SQL traffic for work orders, lot numbers, serial numbers, yield data, and batch records."),
    3389: ("RDP Maintenance", "Maintenance", "RDP maintenance traffic for engineering access and remote troubleshooting."),
    10001: ("Machine Heartbeat Channel", "Vendor Private", "Machine heartbeat and online status traffic."),
    10274: ("Factory Cell Vendor Channel", "Vendor Private", "Factory cell private vendor channel used by simulated production equipment."),
    10555: ("Quality Inspection Channel", "Vendor Private", "Quality inspection and pass/fail result traffic."),
    10888: ("Maintenance Diagnostic Channel", "Vendor Private", "Diagnostic log and device self-test traffic."),
    102: ("Siemens S7 Communication", "ICS PLC", "Siemens S7 PLC communication for controller status, alarms, counters, and production data."),
    502: ("Modbus TCP", "ICS SCADA", "Modbus TCP traffic for registers, sensor values, equipment status, and process measurements."),
    4840: ("OPC UA", "ICS SCADA", "OPC UA traffic for telemetry, alarm events, production states, and structured machine data."),
    1883: ("MQTT Broker", "IIoT", "MQTT traffic for edge gateway telemetry, sensor data, and alarm events."),
    8883: ("MQTT over TLS", "IIoT", "Encrypted MQTT traffic for telemetry, machine events, and sensor data."),
    5672: ("AMQP Message Queue", "IIoT Message Queue", "AMQP traffic for middleware and factory event distribution."),
    5900: ("VNC Remote Maintenance", "Maintenance", "VNC remote maintenance traffic for viewing or operating equipment screens."),
    6514: ("Syslog over TLS", "Infrastructure", "Secure syslog traffic for system logs, alarms, and maintenance logs."),
    8443: ("Vendor Web Console", "Maintenance Web Console", "Vendor HTTPS web console or management interface."),
    53: ("DNS", "Infrastructure", "DNS query traffic for hostname resolution and service lookup."),
    123: ("NTP Time Sync", "Infrastructure", "NTP traffic for device time synchronization."),
    514: ("Syslog", "Infrastructure", "Syslog traffic for system events, process events, and alarm logs."),
    161: ("SNMP", "Infrastructure", "SNMP traffic for device health, interface status, and monitoring."),
    47808: ("BACnet IP", "Building SCADA", "BACnet IP traffic for building automation and utility equipment."),
}


def now_string():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def esc(value):
    return html.escape(str(value))


def describe_port(port):
    try:
        port_int = int(port)
    except Exception:
        return ("Unknown", "Unknown", "No description available.")
    return PORT_INFO.get(port_int, ("Unknown", "Unknown", "No description available."))


def safe_json_loads(text):
    try:
        return json.loads(text)
    except Exception:
        return {}


def trim_event_log_if_needed():
    if not os.path.exists(EVENT_LOG):
        return

    try:
        size = os.path.getsize(EVENT_LOG)
    except OSError:
        return

    if size <= MAX_LOG_BYTES:
        return

    try:
        with open(EVENT_LOG, "r", encoding="utf-8", errors="replace") as f:
            kept_lines = collections.deque(f, maxlen=KEEP_LOG_LINES) if KEEP_LOG_LINES > 0 else []

        tmp_path = EVENT_LOG + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as tmp:
            for line in kept_lines:
                tmp.write(line)

        os.replace(tmp_path, EVENT_LOG)
        print(f"[LOG] Trimmed {EVENT_LOG}. Previous size={size} bytes. Kept last {KEEP_LOG_LINES} lines.", flush=True)

    except Exception as e:
        print(f"[LOG] Failed to trim event log: {e}", flush=True)


def append_event(event):
    os.makedirs(LOG_DIR, exist_ok=True)
    line = json.dumps(event, ensure_ascii=True) + "\n"

    with EVENT_LOG_LOCK:
        with open(EVENT_LOG, "a", encoding="utf-8") as f:
            f.write(line)
        trim_event_log_if_needed()


def record_cell_event(socket_src_ip, socket_src_port, dst_port, protocol, raw_payload):
    payload_text = raw_payload.decode("utf-8", errors="replace").strip()
    payload_json = safe_json_loads(payload_text)

    namespace = payload_json.get("namespace", "unknown")
    virtual_src_ip = payload_json.get("source_ip", socket_src_ip)
    role = payload_json.get("role", "unknown")
    message_type = payload_json.get("message_type", "unknown")

    service, group, description = describe_port(dst_port)

    event = {
        "time": now_string(),
        "socket_src_ip": socket_src_ip,
        "socket_src_port": socket_src_port,
        "virtual_src_ip": virtual_src_ip,
        "namespace": namespace,
        "role": role,
        "dst_ip": SERVER_IP,
        "dst_port": dst_port,
        "protocol": protocol,
        "service": service,
        "group": group,
        "description": description,
        "message_type": message_type,
        "payload": payload_text[:800],
    }

    append_event(event)


def tcp_listener(port):
    service, _group, _description = describe_port(port)

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(50)

        print(f"[TCP] Listening on {port} - {service}", flush=True)

        while True:
            client_socket, client_address = server_socket.accept()
            socket_src_ip, socket_src_port = client_address

            try:
                client_socket.settimeout(2)

                try:
                    data = client_socket.recv(4096)
                except socket.timeout:
                    data = b""

                record_cell_event(
                    socket_src_ip=socket_src_ip,
                    socket_src_port=socket_src_port,
                    dst_port=port,
                    protocol="TCP",
                    raw_payload=data,
                )

                response = {
                    "ack": True,
                    "receiver": "factory-cell-server",
                    "server": SERVER_IP,
                    "port": port,
                    "service": service,
                    "time": now_string(),
                }

                try:
                    client_socket.sendall((json.dumps(response, ensure_ascii=True) + "\n").encode("utf-8"))
                except Exception:
                    pass

            except Exception as e:
                print(f"[TCP] Error on port {port}: {e}", flush=True)

            finally:
                try:
                    client_socket.close()
                except Exception:
                    pass

    except Exception as e:
        msg = f"Failed to bind TCP {port} service={service} error={e}"
        print("[ERROR] " + msg, flush=True)

        with FAILED_BINDS_LOCK:
            FAILED_BINDS.append(msg)


def load_events_from_file(max_lines=UI_MAX_LINES):
    if not os.path.exists(EVENT_LOG):
        return []

    try:
        with open(EVENT_LOG, "r", encoding="utf-8", errors="replace") as f:
            lines = collections.deque(f, maxlen=max_lines)
    except Exception as e:
        print(f"[UI] Failed to read event log: {e}", flush=True)
        return []

    events = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue

    return events


def build_aggregated(events):
    aggregated = {}

    for event in events:
        virtual_src_ip = event.get("virtual_src_ip", event.get("socket_src_ip", "unknown"))
        nat_src_ip = event.get("socket_src_ip", "unknown")
        namespace = event.get("namespace", "unknown")
        role = event.get("role", "unknown")
        protocol = event.get("protocol", "unknown")
        dst_port = event.get("dst_port", "unknown")

        key = f"{virtual_src_ip}|{namespace}|{role}|{protocol}|{dst_port}"

        if key not in aggregated:
            aggregated[key] = {
                "count": 0,
                "first_seen": event.get("time", ""),
                "last_seen": event.get("time", ""),
                "virtual_src_ip": virtual_src_ip,
                "nat_src_ip": nat_src_ip,
                "namespace": namespace,
                "role": role,
                "dst_ip": event.get("dst_ip", SERVER_IP),
                "dst_port": dst_port,
                "protocol": protocol,
                "service": event.get("service", "unknown"),
                "group": event.get("group", "unknown"),
                "description": event.get("description", ""),
                "last_message_type": event.get("message_type", "unknown"),
                "last_payload": event.get("payload", ""),
            }

        aggregated[key]["count"] += 1
        aggregated[key]["last_seen"] = event.get("time", "")
        aggregated[key]["nat_src_ip"] = nat_src_ip
        aggregated[key]["last_message_type"] = event.get("message_type", "unknown")
        aggregated[key]["last_payload"] = event.get("payload", "")

    items = list(aggregated.values())
    items.sort(key=lambda x: x.get("last_seen", ""), reverse=True)

    timeline = list(events)
    timeline.sort(key=lambda x: x.get("time", ""), reverse=True)

    return items, timeline


@app.route("/health")
def health():
    try:
        event_log_size = os.path.getsize(EVENT_LOG) if os.path.exists(EVENT_LOG) else 0
    except OSError:
        event_log_size = -1

    with FAILED_BINDS_LOCK:
        failed_binds = list(FAILED_BINDS)

    return jsonify(
        {
            "status": "ok" if not failed_binds else "degraded",
            "server_ip": SERVER_IP,
            "web_port": WEB_PORT,
            "listen_ports": LISTEN_PORTS,
            "failed_bind_count": len(failed_binds),
            "failed_binds": failed_binds,
            "event_log": EVENT_LOG,
            "event_log_size_bytes": event_log_size,
            "ui_max_lines": UI_MAX_LINES,
            "max_log_bytes": MAX_LOG_BYTES,
            "keep_log_lines": KEEP_LOG_LINES,
            "time": now_string(),
        }
    )


@app.route("/")
def index():
    events = load_events_from_file()
    aggregated, timeline = build_aggregated(events)

    with FAILED_BINDS_LOCK:
        failed_binds = list(FAILED_BINDS)

    unique_virtual_ips = sorted({item["virtual_src_ip"] for item in aggregated})
    unique_nat_ips = sorted({item["nat_src_ip"] for item in aggregated})
    unique_ports = sorted({str(item["dst_port"]) for item in aggregated})

    try:
        log_size = os.path.getsize(EVENT_LOG) if os.path.exists(EVENT_LOG) else 0
    except OSError:
        log_size = -1

    arch = """
Traffic Generator VM: <client_vm_hostname>
Main IP: <client_vm_ip>
Bridge: <client_bridge_name>

  fe01     <virtual_device_ip_01>   <virtual_mac_01>   Engineering Workstation
  cell01   <virtual_device_ip_02>   <virtual_mac_02>   Factory Cell Controller
  hmi01    <virtual_device_ip_03>   <virtual_mac_03>   HMI SCADA Station
  edge01   <virtual_device_ip_04>   <virtual_mac_04>   IIoT Edge Gateway
  maint01  <virtual_device_ip_05>   <virtual_mac_05>   Maintenance Laptop

        |
        v

Network Visibility Platform Bridge
Bridge IP: <visibility_platform_bridge_ip>

        |
        v

Router / Firewall / NAT
LAN: <router_lan_ip>
WAN: <router_wan_ip>

        |
        v

Receiver Server
IP: <receiver_server_ip>

Services:
  factory-cell-server.service:
    TCP 445, 1433, 3389, 10001, 10274, 10555, 10888, Web UI 8080

  factory-extra-receiver.service:
    TCP 102, 502, 4840, 1883, 8883, 5672, 5900, 6514, 8443
    UDP 53, 123, 514, 161, 47808
"""

    page = []
    page.append("""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Factory Traffic Simulation UI</title>
<meta http-equiv="refresh" content="5">
<style>
body { font-family: Arial, Helvetica, sans-serif; background: #f4f6f8; color: #111827; margin: 0; padding: 0; }
.header { padding: 24px 28px 10px 28px; }
h1 { font-size: 34px; margin: 0 0 8px 0; }
.subtitle { color: #4b5563; font-size: 15px; }
.cards { display: flex; flex-wrap: wrap; gap: 14px; padding: 12px 28px; }
.card { background: white; border-radius: 12px; padding: 16px 22px; min-width: 180px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.card-title { font-size: 15px; }
.card-value { font-size: 32px; color: #2563eb; font-weight: bold; margin-top: 4px; }
.section { background: white; margin: 18px 28px; border-radius: 12px; padding: 18px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.table-wrap { overflow-x: auto; max-height: 430px; border: 1px solid #e5e7eb; border-radius: 10px; }
table { width: 100%; border-collapse: collapse; min-width: 1300px; }
th { position: sticky; top: 0; background: #1f2937; color: white; text-align: left; padding: 10px; z-index: 1; }
td { padding: 10px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }
tr:nth-child(even) { background: #f9fafb; }
.badge { display: inline-block; padding: 3px 8px; border-radius: 999px; background: #dbeafe; color: #1d4ed8; font-size: 12px; font-weight: bold; }
.button { display: inline-block; background: #dc2626; color: white; padding: 12px 18px; border-radius: 10px; text-decoration: none; font-weight: bold; }
.health-button { display: inline-block; background: #2563eb; color: white; padding: 12px 18px; border-radius: 10px; text-decoration: none; font-weight: bold; margin-left: 8px; }
.diagram { font-family: monospace; white-space: pre; background: #111827; color: #e5e7eb; padding: 16px; border-radius: 10px; overflow-x: auto; line-height: 1.45; }
.payload { font-family: monospace; white-space: pre-wrap; max-width: 520px; }
.note { color: #4b5563; line-height: 1.6; }
.warn { color: #92400e; background: #fef3c7; padding: 10px; border-radius: 8px; }
</style>
</head>
<body>
""")

    page.append(f"""
<div class="header">
    <h1>Factory Traffic Simulation UI</h1>
    <div class="subtitle">
        Receiver: {esc(SERVER_IP)} |
        Web UI: :{WEB_PORT} |
        Auto refresh: 5 seconds |
        UI reads latest {UI_MAX_LINES} records only |
        Shared log: {esc(EVENT_LOG)}
    </div>
</div>
""")

    page.append(f"""
<div class="cards">
    <div class="card"><div class="card-title">Loaded Events</div><div class="card-value">{len(events)}</div></div>
    <div class="card"><div class="card-title">Virtual Source IPs</div><div class="card-value">{len(unique_virtual_ips)}</div></div>
    <div class="card"><div class="card-title">NAT Source IPs</div><div class="card-value">{len(unique_nat_ips)}</div></div>
    <div class="card"><div class="card-title">Tracked Flows</div><div class="card-value">{len(aggregated)}</div></div>
    <div class="card"><div class="card-title">Observed Ports</div><div class="card-value">{len(unique_ports)}</div></div>
    <div class="card"><div class="card-title">Failed Port Binds</div><div class="card-value">{len(failed_binds)}</div></div>
    <div class="card"><div class="card-title">Event Log Size</div><div class="card-value">{esc(log_size)}</div></div>
</div>
""")

    page.append("""
<div class="section">
    <a class="button" href="/reset">Reset Records</a>
    <a class="health-button" href="/health">Health JSON</a>
    <p class="note">
        The UI reads only the latest demo records from the shared JSONL event log.
        Old demo data is automatically trimmed when the log grows too large.
        The Web UI runs on 8080, so the traffic generator should not send raw TCP payloads to 8080.
        If a router or NAT exists between the generator and receiver, NAT Source IP may show the router or firewall address.
        Virtual Source IP is parsed from the payload sent by the namespace traffic generator.
    </p>
</div>
""")

    if failed_binds:
        page.append("""
<div class="section">
    <div class="warn">
        Some TCP ports failed to bind. Check the Failed Port Binds section below and run:
        sudo ss -tulpn
    </div>
</div>
""")

    page.append(f"""
<div class="section">
    <h2>Architecture Overview</h2>
    <div class="diagram">{esc(arch)}</div>
</div>
""")

    page.append("""
<div class="section">
    <h2>Virtual Factory Devices</h2>
    <div class="table-wrap">
    <table>
        <thead><tr><th>Namespace</th><th>Virtual IP</th><th>MAC Address</th><th>Role</th></tr></thead>
        <tbody>
""")

    for ns, dev in DEVICE_MAP.items():
        page.append(f"""
            <tr>
                <td><span class="badge">{esc(ns)}</span></td>
                <td>{esc(dev["ip"])}</td>
                <td>{esc(dev["mac"])}</td>
                <td>{esc(dev["role"])}</td>
            </tr>
""")

    page.append("""
        </tbody>
    </table>
    </div>
</div>
""")

    page.append("""
<div class="section">
    <h2>Aggregated Flow Records</h2>
    <div class="table-wrap">
    <table>
        <thead>
            <tr>
                <th>Count</th><th>Virtual Source IP</th><th>NAT Source IP</th><th>Namespace</th><th>Role</th>
                <th>Destination Port</th><th>Protocol</th><th>Service</th><th>Group</th><th>Last Message Type</th><th>Last Seen</th><th>Last Payload</th>
            </tr>
        </thead>
        <tbody>
""")

    for item in aggregated:
        page.append(f"""
            <tr>
                <td>{esc(item["count"])}</td>
                <td>{esc(item["virtual_src_ip"])}</td>
                <td>{esc(item["nat_src_ip"])}</td>
                <td>{esc(item["namespace"])}</td>
                <td>{esc(item["role"])}</td>
                <td>{esc(item["dst_port"])}</td>
                <td>{esc(item["protocol"])}</td>
                <td>{esc(item["service"])}</td>
                <td>{esc(item["group"])}</td>
                <td>{esc(item["last_message_type"])}</td>
                <td>{esc(item["last_seen"])}</td>
                <td class="payload">{esc(item["last_payload"])}</td>
            </tr>
""")

    page.append("""
        </tbody>
    </table>
    </div>
</div>
""")

    page.append("""
<div class="section">
    <h2>Recent Timeline</h2>
    <div class="table-wrap">
    <table>
        <thead>
            <tr>
                <th>Time</th><th>Virtual Source IP</th><th>NAT Source IP</th><th>Namespace</th><th>Role</th>
                <th>Destination Port</th><th>Protocol</th><th>Service</th><th>Message Type</th><th>Description</th>
            </tr>
        </thead>
        <tbody>
""")

    for event in timeline[:TIMELINE_MAX_ROWS]:
        page.append(f"""
            <tr>
                <td>{esc(event.get("time", ""))}</td>
                <td>{esc(event.get("virtual_src_ip", ""))}</td>
                <td>{esc(event.get("socket_src_ip", ""))}</td>
                <td>{esc(event.get("namespace", ""))}</td>
                <td>{esc(event.get("role", ""))}</td>
                <td>{esc(event.get("dst_port", ""))}</td>
                <td>{esc(event.get("protocol", ""))}</td>
                <td>{esc(event.get("service", ""))}</td>
                <td>{esc(event.get("message_type", ""))}</td>
                <td>{esc(event.get("description", ""))}</td>
            </tr>
""")

    page.append("""
        </tbody>
    </table>
    </div>
</div>
""")

    if failed_binds:
        page.append("""
<div class="section">
    <h2>Failed Port Binds</h2>
    <div class="table-wrap">
    <table>
        <thead><tr><th>Error</th></tr></thead>
        <tbody>
""")
        for err in failed_binds:
            page.append(f"<tr><td>{esc(err)}</td></tr>")
        page.append("""
        </tbody>
    </table>
    </div>
</div>
""")

    page.append("""
</body>
</html>
""")

    return "".join(page)


@app.route("/reset")
def reset():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with EVENT_LOG_LOCK:
            open(EVENT_LOG, "w", encoding="utf-8").close()
    except Exception as e:
        print(f"[UI] Failed to clear event log: {e}", flush=True)

    return redirect("/")


def main():
    os.makedirs(LOG_DIR, exist_ok=True)

    print("============================================================", flush=True)
    print("Factory Traffic Simulation UI starting", flush=True)
    print("Server IP: " + SERVER_IP, flush=True)
    print("Web UI: http://0.0.0.0:" + str(WEB_PORT), flush=True)
    print("Health: http://0.0.0.0:" + str(WEB_PORT) + "/health", flush=True)
    print("Shared event log: " + EVENT_LOG, flush=True)
    print("UI max records: " + str(UI_MAX_LINES), flush=True)
    print("Max log bytes: " + str(MAX_LOG_BYTES), flush=True)
    print("Keep log lines: " + str(KEEP_LOG_LINES), flush=True)
    print("Listening TCP ports: " + ", ".join(str(p) for p in LISTEN_PORTS), flush=True)
    print("============================================================", flush=True)

    for port in LISTEN_PORTS:
        thread = threading.Thread(target=tcp_listener, args=(port,), daemon=True, name=f"tcp-listener-{port}")
        thread.start()

    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, threaded=True)


if __name__ == "__main__":
    main()
