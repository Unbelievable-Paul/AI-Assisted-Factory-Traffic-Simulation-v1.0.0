# SOP 02 - Client Traffic Generator Setup

This SOP describes the client VM setup for Factory Network Visibility Lab v1.0.

The client VM creates multiple virtual factory devices using Linux namespaces and macvlan interfaces.

## Purpose

The client VM generates low-rate benign factory-style traffic.

This is not a traffic stress test.

This is not a packet flooding tool.

This is not a penetration testing tool.

## Virtual Device Model

Each virtual device has:

- namespace name
- virtual source IP
- virtual MAC address
- role
- traffic profile

Example roles:

```text
fe01     Engineering Workstation
cell01   Factory Cell Controller
hmi01    HMI / SCADA Station
edge01   IIoT Edge Gateway
maint01  Maintenance Laptop
```

## Main Scripts

The client VM uses these scripts:

```text
setup_virtual_hosts.sh
cleanup_virtual_hosts.sh
refresh_arp_virtual_hosts.sh
factory_traffic_generator.py
```

## Script Purpose

### setup_virtual_hosts.sh

Creates Linux network namespaces and macvlan interfaces.

### cleanup_virtual_hosts.sh

Removes the virtual namespaces.

### refresh_arp_virtual_hosts.sh

Sends a small number of ICMP packets from each namespace to refresh ARP entries on the router or visibility device.

### factory_traffic_generator.py

Generates benign low-rate TCP and UDP traffic from each virtual device to the receiver server.

## Validation

Check namespaces:

```bash
ip netns list
```

Expected example result:

```text
fe01
cell01
hmi01
edge01
maint01
```

Check traffic generator service:

```bash
systemctl status factory-traffic-generator --no-pager
```

Expected result:

```text
active (running)
```

## ARP Refresh Before Demo

Run:

```bash
/opt/factory-lab/refresh_arp_virtual_hosts.sh
```

This helps the router or visibility platform display virtual IP and MAC mappings before a demo.

## Notes

Do not publish real IP addresses, hostnames, usernames, passwords, MAC addresses from a production environment, or company-specific topology details.
