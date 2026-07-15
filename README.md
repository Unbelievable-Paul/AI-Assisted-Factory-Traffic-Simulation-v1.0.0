# Factory Network Visibility Lab v1.0

This repository contains an AI-assisted factory network traffic visibility lab developed with ChatGPT.

The project simulates benign factory-style network flows from multiple virtual devices to a receiver server and displays received events in a unified web UI.

## Important Scope Statement

This project is **not** a traffic stress testing tool.

This project is **not** a penetration testing tool.

This project is **not** a packet flooding tool.

This project is **not** designed to bypass, attack, or exploit any system.

The purpose of this project is to generate low-rate, benign, structured lab traffic for defensive network visibility validation, whitelist-learning demonstrations, and receiver-side event visualization.

Use this project only in an authorized lab environment.

## AI-assisted Development Notice

This project was developed as an AI-assisted engineering workflow using ChatGPT.

It is not affiliated with, endorsed by, or sponsored by OpenAI.

## v1.0 Overview

The v1.0 model contains two major components:

1. Receiver Server

   The receiver server listens on multiple factory-style TCP and UDP ports and provides a unified web UI.

2. Client Traffic Generator

   The client VM creates multiple virtual factory devices using Linux network namespaces and macvlan interfaces. Each virtual device has a unique virtual IP, MAC address, role, and traffic profile.

## High-level Architecture

```text
Virtual Factory Devices
inside Client VM
        |
        v
Network Visibility / Bridge Device
        |
        v
Router / Firewall / NAT
        |
        v
Receiver Server with Unified UI

## Receiver Services

factory-cell-server.service
  TCP 445
  TCP 1433
  TCP 3389
  TCP 10001-11000
  Web UI 8080

factory-extra-receiver.service
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

## Example Virtual Devices

fe01
  Role: Engineering Workstation

cell01
  Role: Factory Cell Controller

hmi01
  Role: HMI / SCADA Station

edge01
  Role: IIoT Edge Gateway

maint01
  Role: Maintenance Laptop

## What the Unified UI Displays
# The receiver UI displays:

Received event count
Virtual source IP
NAT source IP
Namespace
Device role
Destination port
Protocol
Service name
Traffic group
Message type
Recent timeline
Aggregated flow records

## Sanitization Policy
# All environment-specific data must be replaced before publishing.
# Examples:

<receiver_server_ip>
<client_vm_ip>
<gateway_ip>
<netkeeper_bridge_ip>
<pfsense_ip>
<your_hostname>
<your_username>
<your_password>
<your_company_domain>
<your_vm_id>

## Version

v1.0
Stable baseline demo model

## License
# See /LICENSE.
