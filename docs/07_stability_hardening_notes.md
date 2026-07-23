# Stability Hardening Notes

This note documents the v1.0.1 stability hardening changes for the factory network visibility lab.

## Summary

The receiver and generator were adjusted for safer long-running demo behavior.

## Receiver server

File:

```text
scripts/receiver/factory_cell_server.py
```

Changes:

- The receiver no longer listens on the full TCP range `10001-11000`.
- The receiver now listens only on the vendor ports used by the demo:
  - `10001`
  - `10274`
  - `10555`
  - `10888`
- The receiver still listens on:
  - `445`
  - `1433`
  - `3389`
  - `8080` for the Web UI
- A `/health` endpoint was added.
- The UI reads only the latest demo records.
- The JSONL event log is automatically trimmed when it grows too large.

Reason:

Opening the full `10001-11000` range can create around 1000 listener threads/tasks. For a small demo, only the specific simulated vendor ports are needed.

## Traffic generator

File:

```text
scripts/client/factory_traffic_generator.py
```

Changes:

- Raw demo traffic is no longer sent to TCP `8080`.
- TCP `8080` is reserved for the receiver Web UI.
- The former MES Web API demo traffic is mapped to a vendor/factory channel instead.
- Client-side logs are bounded.
- The default interval remains low-rate and benign.

## Operational reminder

For long-running demos, consider also limiting systemd journal retention on the demo VM.

Example values:

```text
SystemMaxUse=100M
RuntimeMaxUse=50M
MaxRetentionSec=1day
```

## Scope reminder

This project is for authorized defensive lab validation and receiver-side visualization.

It is not:

- a traffic stress test
- a packet flooding tool
- a penetration testing tool
- an exploit framework
- a DoS or DDoS tool
