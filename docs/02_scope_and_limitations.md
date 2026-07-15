# Scope and Limitations

## Purpose

This project is designed for defensive network visibility validation in an authorized lab environment.

The goal is to simulate benign factory-style communication patterns so that a monitoring platform can observe:

- virtual source devices
- virtual MAC addresses
- TCP and UDP service usage
- destination ports
- receiver-side logs
- basic flow aggregation
- normal traffic visibility

## Not a Stress Test Tool

This project is not designed for high-rate traffic generation.

It does not intentionally generate packet floods, SYN floods, UDP floods, malformed packets, exploit payloads, brute force attempts, or unauthorized scans.

## Not a Security Attack Tool

This project does not include exploit code.

This project does not attempt to bypass authentication, compromise systems, modify remote files, exfiltrate data, or disrupt services.

## Intended Use

Use this project only in a lab network where you have explicit authorization.

Recommended use cases:

- defensive visibility demo
- whitelist-learning validation
- benign factory traffic simulation
- receiver-side flow collection
- internal engineering education
- architecture proof of concept

## Out of Scope

The following are out of scope for v1.0:

- high PPS traffic stress testing
- packet flooding
- vulnerability scanning
- exploit simulation
- malware simulation
- unauthorized network discovery
- production deployment
- performance benchmarking
- packet loss benchmarking
- latency benchmarking

## Future Work

Possible future versions may add:

- configurable multi-VLAN lab mode
- controlled metrics collection
- TX/RX counters
- latency calculation
- loss-rate calculation
- Network_Visibility_Platform log parser
- CSV reporting

Those features should still remain within authorized defensive lab use only.
