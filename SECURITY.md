# Security Policy
Do not expose this UI directly to the public Internet.
## AI-generated Guidance

Users may use AI assistants to help understand or adapt this repository.

However, AI-generated guidance may be incomplete, incorrect, unsafe for a specific environment, or unsuitable for a particular network design.

Users are solely responsible for reviewing and validating all AI-generated commands, scripts, and configuration changes before applying them.
## Web UI Exposure

The receiver UI is intended for trusted lab networks only.

Do not expose the Flask web UI directly to the public Internet.

If remote access is required, place it behind a VPN, firewall rule, SSH tunnel, or other access control mechanism.

## Authorized Use Only

This project is intended only for authorized defensive lab environments.

Do not use this project on networks, systems, or environments where you do not have explicit permission.

## Not an Offensive Tool

This project does not include exploit code, brute force logic, malware behavior, packet flooding, vulnerability scanning, or unauthorized access functionality.

## Reporting Security Issues

If you find a security issue in this repository, please open a private issue or contact the repository owner.

Do not include sensitive environment data, private IP addresses, credentials, or internal company information in public issues.

## Sensitive Data

Do not commit:

- credentials
- SSH private keys
- API keys
- VPN configuration
- company hostnames
- internal IP addresses
- real usernames
- production logs
- sensitive screenshots
