# SOP 01 - Receiver Server Setup

This SOP describes the receiver server setup for Factory Network Visibility Lab v1.0.

All environment-specific values must be replaced with placeholders before publishing.

## Purpose

The receiver server listens on factory-style TCP and UDP ports and displays received events in a unified web UI.

This is for benign defensive visibility validation only.

This is not a traffic stress test.

## Receiver Services

The receiver server runs two services:

```text
factory-cell-server.service
factory-extra-receiver.service
```

## Service 1: Factory Cell Server

The factory cell server listens on:

```text
TCP 445
TCP 1433
TCP 3389
TCP 10001-11000
TCP 8080 for Web UI
```

Purpose:

```text
SMB-style file sync
MES SQL-style traffic
RDP-style maintenance traffic
Vendor private machine channels
Unified receiver web UI
```

## Service 2: Factory Extra Receiver

The extra receiver listens on:

```text
TCP 102
TCP 502
TCP 4840
TCP 1883
TCP 8883
TCP 5672
TCP 5900
TCP 6514
TCP 8443

UDP 53
UDP 123
UDP 514
UDP 161
UDP 47808
```

Purpose:

```text
ICS / PLC traffic
SCADA traffic
IIoT traffic
maintenance traffic
infrastructure traffic
building automation traffic
```

## Shared Event Log

Both services write events to:

```text
/home/<receiver_username>/factory-server/logs/factory_cell_events.jsonl
```

In the public repository, replace real usernames with:

```text
<receiver_username>
```

## Web UI

Open the UI with:

```text
http://<receiver_server_ip>:8080
```

## Validation

Check service status:

```bash
systemctl status factory-cell-server --no-pager
systemctl status factory-extra-receiver --no-pager
```

Expected result:

```text
active (running)
```

Check listening ports:

```bash
sudo ss -tulpn | grep -E ':(445|1433|3389|10001|102|502|4840|1883|8883|5672|5900|6514|8443|8080)'
```

## Notes

Do not publish real receiver IP addresses, hostnames, usernames, passwords, or internal paths that reveal company-specific infrastructure.
