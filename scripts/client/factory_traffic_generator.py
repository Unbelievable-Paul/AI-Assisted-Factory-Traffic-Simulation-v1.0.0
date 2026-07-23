#!/usr/bin/env python3

import collections
import json
import os
import random
import subprocess
import time
from datetime import datetime


# ============================================================
# Factory Traffic Generator - safer demo version
#
# Stability changes:
# 1. Do not send raw TCP demo payloads to Web UI port 8080.
# 2. Keep traffic low-rate and bounded.
# 3. Keep client-side logs bounded for long-running demos.
#
# Scope:
# This is benign demo traffic for authorized defensive lab validation.
# It is not a traffic stress test, exploit framework, or pentest tool.
# ============================================================

RECEIVER_SERVER_IP = os.getenv("RECEIVER_SERVER_IP", "<receiver_server_ip>")

LOG_DIR = os.getenv("CLIENT_LOG_DIR", "./runtime/factory-lab/logs")
LOG_FILE = os.path.join(LOG_DIR, "factory_traffic_generator.log")

MIN_INTERVAL_SECONDS = max(1, int(os.getenv("MIN_INTERVAL_SECONDS", "2")))
MAX_INTERVAL_SECONDS = max(MIN_INTERVAL_SECONDS, int(os.getenv("MAX_INTERVAL_SECONDS", "8")))

MAX_CLIENT_LOG_BYTES = int(os.getenv("MAX_CLIENT_LOG_BYTES", str(5 * 1024 * 1024)))
KEEP_CLIENT_LOG_LINES = int(os.getenv("KEEP_CLIENT_LOG_LINES", "1000"))

TCP_WEIGHT = int(os.getenv("TCP_WEIGHT", "80"))
UDP_WEIGHT = int(os.getenv("UDP_WEIGHT", "20"))


DEVICES = {
    "fe01": {
        "ip": "<virtual_device_ip_01>",
        "role": "Engineering Workstation",
        "tcp": [
            (445, "SMB File Sync"),
            (1433, "MES SQL Query"),
            (3389, "RDP Maintenance"),
            (10001, "Vendor Private Channel"),
            (10274, "Factory Cell Vendor Channel"),
            (10555, "Quality Inspection Channel"),
            (10888, "Maintenance Diagnostic Channel"),
        ],
        "udp": [
            (53, "DNS"),
            (123, "NTP Time Sync"),
            (514, "Syslog"),
        ],
    },

    "cell01": {
        "ip": "<virtual_device_ip_02>",
        "role": "Factory Cell Controller",
        "tcp": [
            (102, "Siemens S7 Communication"),
            (502, "Modbus TCP"),
            (4840, "OPC UA"),
            (1433, "MES SQL Upload"),
            # Do not use 8080 here. 8080 is reserved for the receiver Web UI.
            (10274, "Factory Cell Vendor Channel"),
        ],
        "udp": [
            (123, "NTP Time Sync"),
            (514, "Syslog"),
            (161, "SNMP"),
        ],
    },

    "hmi01": {
        "ip": "<virtual_device_ip_03>",
        "role": "HMI SCADA Station",
        "tcp": [
            (102, "Siemens S7 Monitoring"),
            (502, "Modbus TCP Monitoring"),
            (4840, "OPC UA Monitoring"),
            (8443, "SCADA Web Console"),
        ],
        "udp": [
            (514, "Syslog"),
            (161, "SNMP"),
            (47808, "BACnet IP"),
        ],
    },

    "edge01": {
        "ip": "<virtual_device_ip_04>",
        "role": "IIoT Edge Gateway",
        "tcp": [
            (1883, "MQTT Broker"),
            (8883, "MQTT over TLS"),
            (5672, "AMQP Message Queue"),
            (8443, "Edge Gateway Web Console"),
        ],
        "udp": [
            (53, "DNS"),
            (123, "NTP Time Sync"),
            (514, "Syslog"),
        ],
    },

    "maint01": {
        "ip": "<virtual_device_ip_05>",
        "role": "Maintenance Laptop",
        "tcp": [
            (3389, "RDP Maintenance"),
            (5900, "VNC Maintenance"),
            (8443, "Vendor Web Console"),
            (6514, "Syslog over TLS"),
        ],
        "udp": [
            (53, "DNS"),
            (123, "NTP Time Sync"),
            (161, "SNMP"),
        ],
    },
}


MESSAGE_TYPES = [
    "heartbeat",
    "production_record",
    "alarm_event",
    "sensor_snapshot",
    "batch_status",
    "quality_summary",
    "maintenance_log",
    "machine_state_update",
]


def now_string():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def trim_client_log_if_needed():
    if not os.path.exists(LOG_FILE):
        return

    try:
        size = os.path.getsize(LOG_FILE)
    except OSError:
        return

    if size <= MAX_CLIENT_LOG_BYTES:
        return

    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            kept_lines = collections.deque(f, maxlen=KEEP_CLIENT_LOG_LINES) if KEEP_CLIENT_LOG_LINES > 0 else []

        tmp_path = LOG_FILE + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as tmp:
            for line in kept_lines:
                tmp.write(line)

        os.replace(tmp_path, LOG_FILE)

    except Exception as e:
        print(f"[LOG] Failed to trim client log: {e}", flush=True)


def log_line(message):
    os.makedirs(LOG_DIR, exist_ok=True)
    line = f"{now_string()} {message}"
    print(line, flush=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    trim_client_log_if_needed()


def build_payload(namespace, device, protocol, port, service):
    return {
        "timestamp": now_string(),
        "namespace": namespace,
        "source_ip": device["ip"],
        "role": device["role"],
        "destination_ip": RECEIVER_SERVER_IP,
        "destination_port": port,
        "protocol": protocol,
        "service": service,
        "message_type": random.choice(MESSAGE_TYPES),
    }


def send_flow(namespace, device, protocol, port, service):
    payload = build_payload(namespace, device, protocol, port, service)
    raw_payload = (json.dumps(payload, ensure_ascii=True) + "\n").encode("utf-8")

    if protocol == "TCP":
        cmd = [
            "ip", "netns", "exec", namespace,
            "nc", "-w", "3", RECEIVER_SERVER_IP, str(port),
        ]
        timeout = 6
    else:
        cmd = [
            "ip", "netns", "exec", namespace,
            "nc", "-u", "-w", "1", RECEIVER_SERVER_IP, str(port),
        ]
        timeout = 4

    try:
        result = subprocess.run(
            cmd,
            input=raw_payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )

        if result.returncode == 0:
            log_line(
                f"SENT {protocol} {device['ip']} -> {RECEIVER_SERVER_IP}:{port} "
                f"namespace={namespace} role={device['role']} service={service}"
            )
        else:
            error_text = result.stderr.decode(errors="replace").strip()
            log_line(
                f"FAILED {protocol} {device['ip']} -> {RECEIVER_SERVER_IP}:{port} "
                f"namespace={namespace} role={device['role']} service={service} error={error_text}"
            )

    except Exception as e:
        log_line(
            f"ERROR {protocol} {device['ip']} -> {RECEIVER_SERVER_IP}:{port} "
            f"namespace={namespace} role={device['role']} service={service} exception={e}"
        )


def main():
    log_line("============================================================")
    log_line("Factory Traffic Generator started")
    log_line("Mode: low-rate benign lab traffic")
    log_line("This is not a traffic stress test")
    log_line(f"Destination receiver: {RECEIVER_SERVER_IP}")
    log_line("Virtual hosts: " + ", ".join(DEVICES.keys()))
    log_line(f"Interval range: {MIN_INTERVAL_SECONDS}-{MAX_INTERVAL_SECONDS} seconds")
    log_line("Web UI port 8080 is reserved and is not used for raw demo traffic.")
    log_line("============================================================")

    while True:
        namespace = random.choice(list(DEVICES.keys()))
        device = DEVICES[namespace]

        protocol = random.choices(
            population=["TCP", "UDP"],
            weights=[TCP_WEIGHT, UDP_WEIGHT],
            k=1,
        )[0]

        if protocol == "TCP":
            port, service = random.choice(device["tcp"])
        else:
            port, service = random.choice(device["udp"])

        send_flow(namespace, device, protocol, port, service)

        sleep_time = random.randint(MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS)
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
