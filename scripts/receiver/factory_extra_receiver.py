#!/usr/bin/env python3

import json
import os
import socket
import threading
from datetime import datetime


SERVER_IP = "0.0.0.0"
RECEIVER_DISPLAY_IP = os.getenv("RECEIVER_SERVER_IP", "<receiver_server_ip>")

EXTRA_BASE_DIR = os.getenv("EXTRA_RECEIVER_BASE_DIR", "./runtime/factory-extra-receiver")
LOG_DIR = os.path.join(EXTRA_BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "factory_extra_receiver.log")

RECEIVER_BASE_DIR = os.getenv("RECEIVER_BASE_DIR", "./runtime/factory-server")
SHARED_EVENT_LOG = os.getenv(
    "SHARED_EVENT_LOG",
    os.path.join(RECEIVER_BASE_DIR, "logs", "factory_cell_events.jsonl")
)


TCP_PORTS = {
    102: "Siemens S7 Communication",
    502: "Modbus TCP",
    4840: "OPC UA",
    1883: "MQTT Broker",
    8883: "MQTT over TLS",
    5672: "AMQP Message Queue",
    5900: "VNC Remote Maintenance",
    6514: "Syslog over TLS",
    8443: "Vendor Web Console",
}

UDP_PORTS = {
    53: "DNS",
    123: "NTP Time Sync",
    514: "Syslog",
    161: "SNMP",
    47808: "BACnet IP",
}


PORT_INFO = {
    102: ("ICS PLC", "Siemens S7 PLC communication."),
    502: ("ICS SCADA", "Modbus TCP traffic."),
    4840: ("ICS SCADA", "OPC UA traffic."),
    1883: ("IIoT", "MQTT broker traffic."),
    8883: ("IIoT", "MQTT over TLS traffic."),
    5672: ("IIoT Message Queue", "AMQP message queue traffic."),
    5900: ("Maintenance", "VNC remote maintenance traffic."),
    6514: ("Infrastructure", "Syslog over TLS traffic."),
    8443: ("Maintenance Web Console", "Vendor web console traffic."),
    53: ("Infrastructure", "DNS query traffic."),
    123: ("Infrastructure", "NTP time sync traffic."),
    514: ("Infrastructure", "Syslog traffic."),
    161: ("Infrastructure", "SNMP traffic."),
    47808: ("Building SCADA", "BACnet IP traffic."),
}


def now_string():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_line(message):
    os.makedirs(LOG_DIR, exist_ok=True)

    line = f"{now_string()} {message}"
    print(line, flush=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def safe_json_loads(text):
    try:
        return json.loads(text)
    except Exception:
        return {}


def write_shared_event(socket_src_ip, socket_src_port, dst_port, protocol, service_name, raw_payload):
    payload_text = raw_payload.decode("utf-8", errors="replace").strip()
    payload_json = safe_json_loads(payload_text)

    namespace = payload_json.get("namespace", "unknown")
    virtual_src_ip = payload_json.get("source_ip", socket_src_ip)
    role = payload_json.get("role", "unknown")
    message_type = payload_json.get("message_type", "unknown")

    group, description = PORT_INFO.get(
        dst_port,
        ("Extra Receiver", "Extra receiver traffic.")
    )

    event = {
        "time": now_string(),
        "socket_src_ip": socket_src_ip,
        "socket_src_port": socket_src_port,
        "virtual_src_ip": virtual_src_ip,
        "namespace": namespace,
        "role": role,
        "dst_ip": RECEIVER_DISPLAY_IP,
        "dst_port": dst_port,
        "protocol": protocol,
        "service": service_name,
        "group": group,
        "description": description,
        "message_type": message_type,
        "payload": payload_text[:800],
    }

    os.makedirs(os.path.dirname(SHARED_EVENT_LOG), exist_ok=True)

    with open(SHARED_EVENT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=True) + "\n")


def tcp_listener(port, service_name):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_IP, port))
        server_socket.listen(100)

        log_line(f"[TCP] Listening on {port} - {service_name}")

        while True:
            client_socket, client_address = server_socket.accept()
            source_ip, source_port = client_address

            try:
                client_socket.settimeout(3)

                try:
                    data = client_socket.recv(4096)
                except socket.timeout:
                    data = b""

                log_line(
                    f"[TCP] {source_ip}:{source_port} -> port {port} "
                    f"service={service_name} bytes={len(data)}"
                )

                write_shared_event(
                    socket_src_ip=source_ip,
                    socket_src_port=source_port,
                    dst_port=port,
                    protocol="TCP",
                    service_name=service_name,
                    raw_payload=data,
                )

                response = {
                    "ack": True,
                    "receiver": "factory-extra-receiver",
                    "service": service_name,
                    "port": port,
                    "protocol": "TCP",
                    "time": now_string(),
                }

                try:
                    client_socket.sendall(
                        (json.dumps(response, ensure_ascii=True) + "\n").encode("utf-8")
                    )
                except Exception:
                    pass

            except Exception as e:
                log_line(f"[TCP] Error on port {port}: {e}")

            finally:
                client_socket.close()

    except Exception as e:
        log_line(
            f"[TCP] Failed to listen on port {port} "
            f"service={service_name} error={e}"
        )


def udp_listener(port, service_name):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_IP, port))

        log_line(f"[UDP] Listening on {port} - {service_name}")

        while True:
            data, client_address = server_socket.recvfrom(4096)
            source_ip, source_port = client_address

            log_line(
                f"[UDP] {source_ip}:{source_port} -> port {port} "
                f"service={service_name} bytes={len(data)}"
            )

            write_shared_event(
                socket_src_ip=source_ip,
                socket_src_port=source_port,
                dst_port=port,
                protocol="UDP",
                service_name=service_name,
                raw_payload=data,
            )

            response = {
                "ack": True,
                "receiver": "factory-extra-receiver",
                "service": service_name,
                "port": port,
                "protocol": "UDP",
                "time": now_string(),
            }

            try:
                server_socket.sendto(
                    (json.dumps(response, ensure_ascii=True) + "\n").encode("utf-8"),
                    client_address
                )
            except Exception:
                pass

    except Exception as e:
        log_line(
            f"[UDP] Failed to listen on port {port} "
            f"service={service_name} error={e}"
        )


def main():
    log_line("============================================================")
    log_line("Factory Extra Receiver started")
    log_line("TCP ports: " + ", ".join(str(p) for p in TCP_PORTS.keys()))
    log_line("UDP ports: " + ", ".join(str(p) for p in UDP_PORTS.keys()))
    log_line("Shared event log: " + SHARED_EVENT_LOG)
    log_line("============================================================")

    for port, service_name in TCP_PORTS.items():
        threading.Thread(
            target=tcp_listener,
            args=(port, service_name),
            daemon=True,
        ).start()

    for port, service_name in UDP_PORTS.items():
        threading.Thread(
            target=udp_listener,
            args=(port, service_name),
            daemon=True,
        ).start()

    while True:
        threading.Event().wait(3600)


if __name__ == "__main__":
    main()
