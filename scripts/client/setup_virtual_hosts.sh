#!/usr/bin/env bash
set -euo pipefail

PARENT_IF="${PARENT_IF:-<parent_interface>}"
GATEWAY="${GATEWAY:-<gateway_ip>}"

HOSTS=(
  "fe01 <virtual_device_ip_01>/24 <virtual_mac_01> engineering_workstation"
  "cell01 <virtual_device_ip_02>/24 <virtual_mac_02> factory_cell_controller"
  "hmi01 <virtual_device_ip_03>/24 <virtual_mac_03> hmi_scada_station"
  "edge01 <virtual_device_ip_04>/24 <virtual_mac_04> iiot_edge_gateway"
  "maint01 <virtual_device_ip_05>/24 <virtual_mac_05> maintenance_laptop"
)

echo "============================================================"
echo "[INFO] Setting up virtual factory hosts"
echo "[INFO] Parent interface: ${PARENT_IF}"
echo "[INFO] Gateway: ${GATEWAY}"
echo "============================================================"

for entry in "${HOSTS[@]}"; do
  read -r NS IPADDR MAC ROLE <<< "$entry"

  echo "[INFO] Creating namespace ${NS}"
  sudo ip netns del "${NS}" 2>/dev/null || true
  sudo ip link del "${NS}-mv" 2>/dev/null || true

  sudo ip netns add "${NS}"

  sudo ip link add "${NS}-mv" \
    link "${PARENT_IF}" \
    address "${MAC}" \
    type macvlan mode bridge

  sudo ip link set "${NS}-mv" netns "${NS}"

  sudo ip netns exec "${NS}" ip link set lo up
  sudo ip netns exec "${NS}" ip link set "${NS}-mv" name eth0
  sudo ip netns exec "${NS}" ip addr add "${IPADDR}" dev eth0
  sudo ip netns exec "${NS}" ip link set eth0 up
  sudo ip netns exec "${NS}" ip route add default via "${GATEWAY}"

  echo "[INFO] ${NS} role=${ROLE} ip=${IPADDR} mac=${MAC}"
done

echo "============================================================"
echo "[DONE] Virtual factory hosts created"
echo "============================================================"
