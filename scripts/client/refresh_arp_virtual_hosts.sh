#!/usr/bin/env bash
set -euo pipefail

GATEWAY_IP="${GATEWAY_IP:-<gateway_ip>}"
VISIBILITY_BRIDGE_IP="${VISIBILITY_BRIDGE_IP:-<netkeeper_bridge_ip>}"

TARGETS=(
  "${GATEWAY_IP}"
  "${VISIBILITY_BRIDGE_IP}"
)

HOSTS=(
  "fe01"
  "cell01"
  "hmi01"
  "edge01"
  "maint01"
)

echo "============================================================"
echo "[INFO] Refreshing ARP entries for virtual factory hosts"
echo "[INFO] Gateway target: ${GATEWAY_IP}"
echo "[INFO] Visibility bridge target: ${VISIBILITY_BRIDGE_IP}"
echo "============================================================"

for TARGET in "${TARGETS[@]}"; do
  echo "[INFO] Refreshing ARP entries for target ${TARGET}"

  for NS in "${HOSTS[@]}"; do
    echo "[INFO] ${NS} -> ${TARGET}"
    sudo ip netns exec "${NS}" ping -c 2 -W 1 "${TARGET}" >/dev/null 2>&1 || true
  done
done

echo "============================================================"
echo "[DONE] ARP refresh completed"
echo "============================================================"
