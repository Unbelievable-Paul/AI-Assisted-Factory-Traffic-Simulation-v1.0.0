#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo "[INFO] Factory Network Visibility Lab v1.0"
echo "[INFO] Sanitization validation"
echo "============================================================"

FAILED=0

echo "[INFO] Checking for private key material..."

PRIVATE_KEY_PATTERNS=(
  "BEGIN OPENSSH PRIVATE KEY"
  "BEGIN RSA PRIVATE KEY"
  "BEGIN EC PRIVATE KEY"
  "BEGIN DSA PRIVATE KEY"
  "BEGIN PRIVATE KEY"
)

for pattern in "${PRIVATE_KEY_PATTERNS[@]}"; do
  if grep -RIn --exclude-dir=.git --exclude="validate_sanitization.sh" "$pattern" .; then
    echo "[FAIL] Found private key pattern: $pattern"
    FAILED=1
  fi
done

echo "[INFO] Checking for likely IPv4 addresses..."

if grep -RInE --exclude-dir=.git --exclude="validate_sanitization.sh" '(^|[^0-9])([0-9]{1,3}\.){3}[0-9]{1,3}([^0-9]|$)' .; then
  echo "[WARN] Found IPv4-looking values."
  echo "[WARN] Review each match. Replace real environment IP addresses with placeholders."
  FAILED=1
fi

echo "[INFO] Checking for likely MAC addresses..."

if grep -RInE --exclude-dir=.git --exclude="validate_sanitization.sh" '([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}' .; then
  echo "[WARN] Found MAC-looking values."
  echo "[WARN] Review each match. Replace real environment MAC addresses with placeholders."
  FAILED=1
fi

echo "[INFO] Checking for common secret assignment patterns..."

SECRET_ASSIGNMENT_PATTERNS=(
  "password[[:space:]]*="
  "passwd[[:space:]]*="
  "secret[[:space:]]*="
  "token[[:space:]]*="
  "api_key[[:space:]]*="
  "apikey[[:space:]]*="
  "access_key[[:space:]]*="
)

for pattern in "${SECRET_ASSIGNMENT_PATTERNS[@]}"; do
  if grep -RInEi --exclude-dir=.git --exclude="validate_sanitization.sh" "$pattern" .; then
    echo "[FAIL] Found possible secret assignment pattern: $pattern"
    FAILED=1
  fi
done

echo "============================================================"

if [ "$FAILED" -eq 1 ]; then
  echo "[FAIL] Sanitization validation found items that need review."
  echo "[ACTION] Replace real values with placeholders before publishing."
  exit 1
fi

echo "[PASS] Sanitization validation passed."
echo "============================================================"
