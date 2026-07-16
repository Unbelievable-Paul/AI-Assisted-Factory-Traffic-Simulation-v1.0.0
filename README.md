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

## Quick Start

This repository is a sanitized public reference version.

Before running the lab, replace all placeholder values such as:

```text
<receiver_server_ip>
<client_vm_ip>
<gateway_ip>
<visibility_platform_bridge_ip>
<pfsense_ip>
<receiver_username>
<client_username>
<parent_interface>
<virtual_device_ip_01>
<virtual_mac_01>
```
Install Python dependencies on the receiver server:
```
pip install -r requirements.txt
```
Common Linux tools required on the client VM include:
```
iproute2
netcat
ping
systemd
```
If scripts are copied from GitHub without executable permissions, either run them with `bash` or set executable permissions:

```bash
chmod +x scripts/client/*.sh
chmod +x scripts/tools/*.sh
```
Then follow the SOP files:
```
sop/SOP_01_receiver_server_setup.md
sop/SOP_02_client_generator_setup.md
sop/SOP_03_validation_steps.md
sop/SOP_04_demo_procedure.md
```
## Beginner-friendly AI Assistance Prompt

If you are completely new to Linux, networking, GitHub, systemd, Python, or virtual lab setup, you can download this repository as a `.zip` file and upload it to a large language model such as ChatGPT, Claude, Gemini, or another AI assistant.

You may ask the AI assistant to explain the project structure, summarize the purpose of each file, and guide you step by step through adapting the lab to your own authorized environment.

Example prompt:

```text
I am a beginner. I downloaded this GitHub repository as a zip file.

Please review the repository structure and explain what each folder and file does.

Then guide me step by step to set up this project in my own authorized lab environment.

Important:
- Do not assume any real IP address, hostname, username, or password.
- Ask me before replacing placeholders such as <receiver_server_ip>, <client_vm_ip>, <gateway_ip>, <visibility_platform_bridge_ip>, <pfsense_ip>, <receiver_username>, and <client_username>.
- Explain every command before asking me to run it.
- Keep the setup defensive and benign.
- Do not add traffic flooding, exploit logic, unauthorized scanning, brute force behavior, or offensive security features.
- Help me verify each step before moving to the next step.
```
## AI Assistance Disclaimer

AI-generated explanations and setup instructions are for reference only.

This repository is provided as a sanitized educational and lab reference. Users are responsible for reviewing, understanding, testing, and validating all commands, scripts, configurations, and modifications before running them.

Do not run this project on networks, systems, or environments where you do not have explicit authorization.

The authors and contributors are not responsible for any damage, data loss, service disruption, misconfiguration, legal issue, policy violation, or other consequence caused by using, modifying, deploying, or following AI-generated instructions based on this repository.

Use this project at your own risk.


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
```
## Terminology

In this repository, `Network Visibility Platform` means any software, hardware appliance, bridge, sensor, IDS/IPS, NDR, flow monitor, traffic monitoring system, or whitelist-learning platform that can observe, record, classify, or analyze network traffic.

A router or firewall may provide partial visibility through ARP tables, state tables, firewall logs, or traffic logs. However, in this architecture, the router/firewall/NAT role is documented separately from the Network Visibility Platform role.

This v1.0 lab used pfSense as an example router/firewall/NAT component. Other open-source firewall or routing platforms may be used if they provide equivalent routing, firewall, NAT, and logging functions.

## Receiver Services
```
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
```
## Example Virtual Devices
```
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
```
## What the Unified UI Displays
### The receiver UI displays:
```
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
```
## Sanitization Policy
### All environment-specific data must be replaced before publishing.
### Examples:
```
<receiver_server_ip>
<client_vm_ip>
<gateway_ip>
<visibility_platform_bridge_ip>
<pfsense_ip>
<your_hostname>
<your_username>
<your_password>
<your_company_domain>
<your_vm_id>
```
## Version

v1.0
Stable baseline demo model

## License
### See [LICENSE](MIT License).
