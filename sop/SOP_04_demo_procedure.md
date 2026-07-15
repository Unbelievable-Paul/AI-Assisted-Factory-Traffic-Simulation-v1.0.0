# SOP 04 - Demo Procedure

This procedure prepares the lab for a baseline visibility demo.

This is not a traffic stress test.

## 1. Confirm Receiver Services

On the receiver server:

```bash
systemctl status factory-cell-server --no-pager
systemctl status factory-extra-receiver --no-pager
```

## 2. Confirm Client Services

On the client VM:
```
systemctl status factory-virtual-hosts --no-pager
systemctl status factory-traffic-generator --no-pager
```

## 3. Refresh ARP Entries

On the client VM:
```
/opt/factory-lab/refresh_arp_virtual_hosts.sh
```
## 4. Open Unified Receiver UI

Open:
```
http://<receiver_server_ip>:8080
```

## 5. Show the Network Visibility Platform

Show:
```
ARP table
flow table
rule learning table
pass/drop logs if available
```

## 6. Explain the Model

Recommended explanation:
```
This v1.0 model simulates multiple factory devices from one client VM using Linux namespaces and macvlan interfaces. Each virtual device has its own virtual IP, MAC address, role, and traffic profile.

The receiver server listens on common factory, ICS, IIoT, maintenance, and infrastructure ports. Both receiver services write to a shared event log, and the unified UI displays all received events.

This model is designed for defensive visibility validation and demo purposes. It is not a traffic stress test.
```

## 7. Do Not Claim

### Do not claim:
```
high-scale performance testing
packet-loss benchmarking
latency benchmarking
production readiness
exploit simulation
security bypass testing
```
