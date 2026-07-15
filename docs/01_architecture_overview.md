# Architecture Overview

## Project Purpose

Factory Network Visibility Lab v1.0 is a baseline defensive visibility lab.

It simulates multiple benign factory-style devices from one client VM and sends structured low-rate traffic to a receiver server.

This project is designed for:

- defensive network visibility validation
- whitelist-learning demonstration
- receiver-side event visualization
- lab education
- architecture proof of concept

This project is not a traffic stress test, packet flooding tool, penetration testing tool, or exploit framework.

## High-level Architecture

```text
Client Traffic Generator VM
        |
        |  Linux namespaces + macvlan
        |
        v
Virtual Factory Devices
        |
        v
Network Visibility / Bridge Device
        |
        v
Router / Firewall / NAT
        |
        v
Receiver Server
        |
        v
Unified Web UI
```

## Main Components

### 1. Client Traffic Generator VM

The client VM creates multiple virtual factory devices.

Each virtual device has:

- a namespace name
- a virtual source IP
- a virtual MAC address
- a device role
- a traffic profile

Example device roles:

```text
Engineering Workstation
Factory Cell Controller
HMI / SCADA Station
IIoT Edge Gateway
Maintenance Laptop
```

### 2. Receiver Server

The receiver server runs two receiver services.

```text
factory-cell-server.service
factory-extra-receiver.service
```

Both services write received events into a shared JSONL event log.

The unified UI reads from the shared event log and displays all received traffic.

### 3. Unified UI

The UI displays:

- received event count
- virtual source IP
- NAT source IP
- namespace
- device role
- destination port
- protocol
- service name
- traffic group
- message type
- recent timeline
- aggregated flow records

## Sanitized Topology

All environment-specific values must be replaced with placeholders.

```text
Client VM: <client_vm_ip>
Receiver Server: <receiver_server_ip>
Gateway: <gateway_ip>
Network Visibility Device: <Network_Visibility_Platform_bridge_ip>
Router / Firewall / NAT: <pfsense_ip>
```

## v1.0 Scope

v1.0 is a stable baseline demo model.

It does not include:

- multi-VLAN scaling
- high-rate traffic testing
- packet-loss benchmarking
- latency benchmarking
- offensive security testing
- exploit simulation

Those features may be considered in future controlled defensive lab versions.
