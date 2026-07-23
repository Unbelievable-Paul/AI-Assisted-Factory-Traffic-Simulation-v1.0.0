# Ports and Protocols

This project uses common factory, ICS, IIoT, infrastructure, and maintenance-style ports for benign traffic simulation.

The ports are intentionally documented clearly because they are part of the public technical model.

## TCP Ports

| Port | Protocol / Service | Simulated Purpose |
|---:|---|---|
| 445 | SMB-style File Sync | Recipe files, CSV logs, batch reports, configuration files |
| 1433 | MES SQL-style Traffic | Work orders, lot numbers, serial numbers, yield data |
| 3389 | RDP-style Maintenance | Remote maintenance and engineering access simulation |
| 102 | Siemens S7 | PLC and controller communication simulation |
| 502 | Modbus TCP | Register values, sensor values, equipment status |
| 4840 | OPC UA | Structured telemetry, alarm events, production state |
| 1883 | MQTT | IIoT telemetry and sensor event traffic |
| 8883 | MQTT over TLS | Encrypted IIoT telemetry simulation |
| 5672 | AMQP | Factory message queue simulation |
| 5900 | VNC-style Maintenance | Remote maintenance screen access simulation |
| 6514 | Syslog over TLS | Secure log transport simulation |
| 8443 | Vendor Web Console | HTTPS-style device management console simulation |
| 10001 | Machine Heartbeat Channel | Vendor-style machine heartbeat simulation |
| 10274 | Factory Cell Vendor Channel | Vendor-style factory cell communication simulation |
| 10555 | Quality Inspection Channel | Vendor-style quality inspection result simulation |
| 10888 | Maintenance Diagnostic Channel | Vendor-style maintenance diagnostics simulation |

## UDP Ports

| Port | Protocol / Service | Simulated Purpose |
|---:|---|---|
| 53 | DNS | Hostname lookup simulation |
| 123 | NTP | Time synchronization simulation |
| 514 | Syslog | System and process event logs |
| 161 | SNMP | Device health and monitoring |
| 47808 | BACnet/IP | Building automation and utility equipment simulation |

## Notes

These ports are used only for benign lab traffic generation.

The receiver intentionally does not listen on every TCP port from `10001` to `11000`.  
Only specific vendor demo ports are used to keep the long-running demo lightweight.

This project does not implement real industrial protocol logic. It only simulates structured traffic patterns for visibility and logging.
