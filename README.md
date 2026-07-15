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
