#!/usr/bin/env bash
set -euo pipefail

HOSTS=(
  "fe01"
  "cell01"
  "hmi01"
  "edge01"
  "maint01"
)

echo "============================================================"
echo "[INFO] Cleaning up virtual factory hosts"
echo "============================================================"

for NS in "${HOSTS[@]}"; do
  echo "[INFO] Removing namespace ${NS}"
  sudo ip netns del "${NS}" 2>/dev/null || true
done

echo "============================================================"
echo "[DONE] Virtual factory hosts removed"
echo "============================================================"
