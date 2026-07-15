# Demo Checklist

This checklist prepares Factory Network Visibility Lab v1.0 for a baseline demo.

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
```
active (running)
```
Check listening ports:
```
sudo ss -tulpn | grep -E ':(445|1433|3389|10001|102|502|4840|1883|8883|5672|5900|6514|8443|8080)'
```
Expected result:
```
TCP receiver ports should be listening.
The web UI should be listening on TCP 8080.
```
## 2. Client VM Checklist

On the client VM, verify virtual namespaces:
```
ip netns list
```
Expected virtual devices:
```
fe01
cell01
hmi01
edge01
maint01
```
Verify services:
```
systemctl status factory-virtual-hosts --no-pager
systemctl status factory-traffic-generator --no-pager
```
Expected result:
```
active (running)
```
## 3. ARP Refresh

Before the demo, refresh ARP entries:
```
/opt/factory-lab/refresh_arp_virtual_hosts.sh
```
Then check the ARP table on the visibility platform or router.

Expected result:
```
Virtual device IP and MAC pairs should appear after ARP refresh.
```
## 4. Receiver UI

Open:
```
http://<receiver_server_ip>:8080
```
Expected UI fields:
```
Received Events
Virtual Source IPs
NAT Source IPs
Tracked Flows
Observed Ports
Failed Port Binds
Aggregated Flow Records
Recent Timeline
```
## 5. Expected Traffic Types

The UI may display traffic related to:
```
TCP 445      SMB-style File Sync
TCP 1433     MES SQL-style Traffic
TCP 3389     RDP-style Maintenance
TCP 102      Siemens S7
TCP 502      Modbus TCP
TCP 4840     OPC UA
TCP 1883     MQTT
TCP 8883     MQTT over TLS
TCP 5672     AMQP
TCP 5900     VNC-style Maintenance
TCP 6514     Syslog over TLS
TCP 8443     Vendor Web Console
UDP 53       DNS
UDP 123      NTP
UDP 514      Syslog
UDP 161      SNMP
UDP 47808    BACnet/IP
TCP 10001-11000 Vendor private range
```
## 6. Demo Explanation

Recommended explanation:
```
This v1.0 lab simulates multiple factory-style devices from a single client VM using Linux namespaces and macvlan interfaces.

Each virtual device has its own namespace, virtual source IP, virtual MAC address, role, and traffic profile.

The receiver server listens on common factory, ICS, IIoT, maintenance, and infrastructure ports. Both receiver services write events to a shared JSONL log, and the unified UI displays the combined receiver-side view.

This is a baseline defensive visibility demo. It is not a traffic stress test.
```
## 7. Do Not Claim

Do not claim that v1.0 provides:
```
production readiness
high-rate traffic benchmarking
packet loss benchmarking
latency benchmarking
exploit simulation
vulnerability scanning
penetration testing
DoS or DDoS testing
```
