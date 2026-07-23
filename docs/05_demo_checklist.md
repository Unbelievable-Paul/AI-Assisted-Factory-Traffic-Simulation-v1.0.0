# Demo Checklist

This checklist prepares Factory Network Visibility Lab v1.0.1 for a baseline demo.

This is not a traffic stress test.  
This is not a penetration testing activity.  
This is not a packet flooding test.

## 1. Receiver Server Checklist

On the receiver server, verify both receiver services:

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
sudo ss -tulpn | grep -E ':(445|1433|3389|10001|10274|10555|10888|102|502|4840|1883|8883|5672|5900|6514|8443|8080)'
```

Expected result:

```text
Factory cell receiver ports should be listening.
Extra receiver ports should be listening.
The web UI should be listening on TCP 8080.
```

## 2. Client VM Checklist

On the client VM, verify virtual namespaces:

```bash
ip netns list
```

Expected virtual devices:

```text
fe01
cell01
hmi01
edge01
maint01
```

Verify services:

```bash
systemctl status factory-virtual-hosts --no-pager
systemctl status factory-traffic-generator --no-pager
```

Expected result:

```text
active (running)
```

## 3. ARP Refresh

Before the demo, refresh ARP entries:

```bash
/opt/factory-lab/refresh_arp_virtual_hosts.sh
```

Then check the ARP table on the visibility platform or router.

Expected result:

```text
Virtual device IP and MAC pairs should appear after ARP refresh.
```

## 4. Receiver UI

Open:

```text
http://<receiver_server_ip>:8080
```

Expected UI fields:

```text
Received Events
Virtual Source IPs
NAT Source IPs
Tracked Flows
Observed Ports
Failed Port Binds
Aggregated Flow Records
Recent Timeline
Health JSON
```

## 5. Expected Traffic Types

The UI may display traffic related to:

```text
TCP 445 SMB-style File Sync
TCP 1433 MES SQL-style Traffic
TCP 3389 RDP-style Maintenance
TCP 102 Siemens S7
TCP 502 Modbus TCP
TCP 4840 OPC UA
TCP 1883 MQTT
TCP 8883 MQTT over TLS
TCP 5672 AMQP
TCP 5900 VNC-style Maintenance
TCP 6514 Syslog over TLS
TCP 8443 Vendor Web Console
UDP 53 DNS
UDP 123 NTP
UDP 514 Syslog
UDP 161 SNMP
UDP 47808 BACnet/IP
TCP 10001 Machine Heartbeat Channel
TCP 10274 Factory Cell Vendor Channel
TCP 10555 Quality Inspection Channel
TCP 10888 Maintenance Diagnostic Channel
```

## 6. Demo Explanation

Recommended explanation:

```text
This lab simulates multiple factory-style devices from a single client VM using Linux namespaces and macvlan interfaces.

Each virtual device has its own namespace, virtual source IP, virtual MAC address, role, and traffic profile.

The receiver server listens on common factory, ICS, IIoT, maintenance, infrastructure, and selected vendor-style ports.

Both receiver services write events to a shared JSONL log, and the unified UI displays the combined receiver-side view.

This is a baseline defensive visibility demo. It is not a traffic stress test.
```

## 7. Do Not Claim

Do not claim that this project provides:

```text
production readiness
high-rate traffic benchmarking
packet loss benchmarking
latency benchmarking
exploit simulation
vulnerability scanning
penetration testing
DoS or DDoS testing
```
