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
```
active (running)
```
Check listening ports:
```
sudo ss -tulpn | grep -E ':(445|1433|3389|10001|102|502|4840|1883|8883|5672|5900|6514|8443|8080)'
```
Open the web UI:
```
http://<receiver_server_ip>:8080
```
## 2. Client VM Validation

On the client VM:
```
ip netns list
```
Expected virtual hosts:
```
fe01
cell01
hmi01
edge01
maint01
```
Check traffic generator:
```
systemctl status factory-traffic-generator --no-pager
```
Expected result:
```
active (running)
```
## 3. ARP Refresh

Run the ARP refresh script before demos:
```
/opt/factory-lab/refresh_arp_virtual_hosts.sh
```
Then check the ARP table on the network visibility platform or router.

## 4. Shared Event Log

On the receiver server:
```
tail -f /home/<receiver_username>/factory-server/logs/factory_cell_events.jsonl
```
Expected records should include destination ports such as:
```
445
1433
3389
502
4840
1883
5900
8443
47808
10001-11000
```

## 5. Unified UI

The UI should show:
```
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
