# Troubleshooting

This guide covers common issues in Factory Network Visibility Lab v1.0.

All environment-specific values should be replaced with local lab values.

## 1. Receiver UI Does Not Open

Check the receiver service:

```bash
systemctl status factory-cell-server --no-pager
```
Check whether TCP 8080 is listening:
```
sudo ss -tulpn | grep ':8080'
```
Check logs:
```
journalctl -u factory-cell-server -n 80 --no-pager
```
Common causes:
```
receiver service is not running
firewall blocks TCP 8080
wrong receiver IP
Python dependency missing
port bind failed
```
## 2. Extra Receiver Traffic Does Not Appear in UI

Check the extra receiver service:
```
systemctl status factory-extra-receiver --no-pager
```
Check logs:
```
journalctl -u factory-extra-receiver -n 80 --no-pager
```
Check shared event log:
```
tail -f /home/<receiver_username>/factory-server/logs/factory_cell_events.jsonl
```
Common causes:
```
extra receiver is not running
shared event log path is wrong
sender is not generating traffic to extra receiver ports
destination port is not listening
UDP traffic was sent but no event was generated
```
## 3. Connection Refused

If a client test shows:
```
Connection refused
```
This usually means:
```
Routing is working, but no service is listening on that destination port.
```
Check receiver listening ports:
```
sudo ss -tulpn | grep -E ':(102|502|4840|1883|8883|5672|5900|6514|8443)'
```
## 4. Timeout

If a client test times out, possible causes include:
```
routing problem
firewall rule blocking traffic
wrong receiver IP
wrong gateway
namespace route missing
network visibility bridge not passing traffic
```
Check namespace route:
```
sudo ip netns exec fe01 ip route
```
Check gateway reachability:
```
sudo ip netns exec fe01 ping -c 2 <gateway_ip>
```
Check receiver reachability:
```
sudo ip netns exec fe01 ping -c 2 <receiver_server_ip>
```
## 5. ARP Table Does Not Show Virtual IP or MAC

ARP entries are temporary.

They may disappear after timeout.

Refresh ARP entries from the client VM:
```
/opt/factory-lab/refresh_arp_virtual_hosts.sh
```
Then check the ARP table again on the router or visibility platform.

## 6. Namespace Missing

Check namespaces:
```
ip netns list
```
If expected namespaces are missing, restart virtual hosts:
```
systemctl restart factory-virtual-hosts
ip netns list
```
## 7. Traffic Generator Not Sending

Check service status:
```
systemctl status factory-traffic-generator --no-pager
```
Check sender log:
```
tail -f /opt/factory-lab/logs/factory_traffic_generator.log
```
Common causes:
```
namespaces were not created
receiver IP is wrong
netcat is not installed
route is missing
receiver service is not listening
```
## 8. Port Bind Failed

Some ports require elevated privileges.

The receiver systemd service template includes:
```
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
```
These allow the service to bind to low-numbered ports such as TCP 445, TCP 102, UDP 53, and UDP 123.

If port binding still fails, check whether another process is already using the port:
```
sudo ss -tulpn | grep ':<port>'
```
## 9. Log File Becomes Too Large

The shared event log can grow during long runs.

Recommended action:
```
use log rotation
clear logs before demos
avoid long unattended runs
```
Example reset from UI:
```
Open the receiver UI and click Reset Records.
```
## 10. Public Repository Safety

Before publishing, verify that the repository does not contain:
```
real IP addresses
real MAC addresses
real hostnames
real usernames
passwords
private keys
company names
internal topology screenshots
production logs
```
