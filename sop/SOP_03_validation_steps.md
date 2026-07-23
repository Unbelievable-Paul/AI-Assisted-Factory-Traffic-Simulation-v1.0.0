# SOP 03 - Validation Steps

This SOP validates that the receiver server, client virtual hosts, and benign traffic generator are working.

All values must be replaced with local lab values before use.

## 1. Receiver Server Validation

On the receiver server:

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

Open the web UI:

```text
http://<receiver_server_ip>:8080
```

Open the health endpoint:

```text
http://<receiver_server_ip>:8080/health
```

## 2. Client VM Validation

On the client VM:

```bash
ip netns list
```

Expected virtual hosts:

```text
fe01
cell01
hmi01
edge01
maint01
```

Check traffic generator:

```bash
systemctl status factory-traffic-generator --no-pager
```

Expected result:

```text
active (running)
```

## 3. ARP Refresh

Run the ARP refresh script before demos:

```bash
/opt/factory-lab/refresh_arp_virtual_hosts.sh
```

Then check the ARP table on the network visibility platform or router.

## 4. Shared Event Log

On the receiver server:

```bash
tail -f /home/<receiver_username>/factory-server/logs/factory_cell_events.jsonl
```

Expected records should include destination ports such as:

```text
445
1433
3389
102
502
4840
1883
5900
8443
47808
10001
10274
10555
10888
```

## 5. Unified UI

The UI should show:

```text
received event count
virtual source IP
NAT source IP
namespace
role
destination port
protocol
service
message type
recent timeline
```

## 6. Stability Validation

Confirm that the receiver is not opening the full vendor range:

```bash
systemctl status factory-cell-server --no-pager
```

Expected result:

```text
Tasks should remain low for the factory-cell-server service.
```

Also confirm that raw demo traffic is not being sent to Web UI port 8080:

```bash
grep -RIn "8080\|MES Web API" scripts/client/factory_traffic_generator.py
```

Expected result:

```text
No active traffic profile should send raw demo TCP payloads to 8080.
```
