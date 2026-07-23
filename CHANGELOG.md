# Changelog

## v1.0.1

Stability hardening patch for long-running demo behavior.

### Changed

- Limited `factory-cell-server.service` vendor listener ports.
- Replaced the full `10001-11000` listener range with specific demo vendor ports:
  - `10001`
  - `10274`
  - `10555`
  - `10888`
- Reserved TCP `8080` for the receiver Web UI.
- Removed raw TCP demo payload traffic to TCP `8080` from the client traffic generator.
- Added bounded receiver-side JSONL event log retention.
- Added bounded client-side generator log retention.
- Reduced UI event loading to the latest demo records only.

### Added

- Receiver `/health` endpoint.
- Stability hardening documentation:
  - `docs/07_stability_hardening_notes.md`

### Notes

This remains a low-rate, benign, defensive visibility lab demo.

It is not a traffic stress test tool.

It is not a penetration testing tool.

It is not a packet flooding tool.

## v1.0.0

Initial stable baseline demo model.

### Added

- Receiver server model
- Unified receiver UI
- Shared JSONL event log
- Factory cell receiver service
- Extra receiver service
- Client virtual host model
- Linux namespace and macvlan based simulated devices
- Benign factory-style traffic profiles
- Validation SOP
- Demo SOP
- Sanitization policy
- Scope and limitations document

### Notes

This version is a baseline visibility demo.

It is not a traffic stress test tool.

It is not a penetration testing tool.

It is not a packet flooding tool.
