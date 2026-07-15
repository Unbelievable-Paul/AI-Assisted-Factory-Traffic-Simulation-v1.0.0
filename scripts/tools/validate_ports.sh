#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo "[INFO] Factory Network Visibility Lab v1.0"
echo "[INFO] Port documentation validation"
echo "============================================================"

REQUIRED_PORTS=(
  "445"
  "1433"
  "3389"
  "102"
  "502"
  "4840"
  "1883"
  "8883"
  "5672"
  "5900"
  "6514"
  "8443"
  "53"
  "123"
  "514"
  "161"
  "47808"
  "10001"
  "11000"
)

FAILED=0

for port in "${REQUIRED_PORTS[@]}"; do
  if grep -RIn --exclude-dir=.git "$port" README.md docs sop scripts systemd >/dev/null 2>&1; then
    echo "[PASS] Port/reference found: $port"
  else
    echo "[WARN] Port/reference missing: $port"
    FAILED=1
  fi
done

echo "============================================================"

if [ "$FAILED" -eq 1 ]; then
  echo "[WARN] Some expected port references were not found."
  echo "[ACTION] Review documentation and scripts."
  exit 1
fi

echo "[PASS] Port documentation validation passed."
echo "============================================================"
