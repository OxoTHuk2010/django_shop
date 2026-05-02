#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:?domain is required}"
LETSENCRYPT_PATH="${2:-./deploy/letsencrypt}"

LIVE_DIR="${LETSENCRYPT_PATH}/live/${DOMAIN}"

if [ -f "${LIVE_DIR}/fullchain.pem" ] && [ -f "${LIVE_DIR}/privkey.pem" ]; then
  echo "Certificate for ${DOMAIN} already exists"
  exit 0
fi

mkdir -p "${LIVE_DIR}"

openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout "${LIVE_DIR}/privkey.pem" \
  -out "${LIVE_DIR}/fullchain.pem" \
  -days 1 \
  -subj "/CN=${DOMAIN}"

echo "Dummy certificate generated for ${DOMAIN}"
