# Sanitization Policy

This repository is intended to be public.

Before committing any file, remove or replace environment-specific information.

## Replace These Values

| Real Value Type | Public Placeholder |
|---|---|
| Receiver server IP | `<receiver_server_ip>` |
| Client VM IP | `<client_vm_ip>` |
| Gateway IP | `<gateway_ip>` |
| NetKeeper bridge IP | `<netkeeper_bridge_ip>` |
| pfSense IP | `<pfsense_ip>` |
| Hostname | `<your_hostname>` |
| Username | `<your_username>` |
| Password | `<your_password>` |
| SSH username | `<ssh_username>` |
| Company domain | `<your_company_domain>` |
| Proxmox node name | `<your_proxmox_node>` |
| VM ID | `<your_vm_id>` |
| Real MAC address | `<your_mac_address>` |

## Do Not Commit

Do not commit:

- real passwords
- real usernames
- real hostnames
- real company domains
- real internal IP addresses
- SSH private keys
- VPN information
- screenshots containing sensitive information
- production network diagrams
- company-specific configuration files

## Acceptable Public Information

It is acceptable to document:

- TCP and UDP ports
- protocol names
- generic service roles
- generic architecture
- sanitized topology
- placeholder-based commands
- lab-only setup instructions

## Recommended Validation

Before publishing the repository, manually review every file and make sure real environment data is replaced with placeholders.
