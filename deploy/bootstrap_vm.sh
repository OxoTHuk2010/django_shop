#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

if ! docker compose version >/dev/null 2>&1; then
  apt-get update
  apt-get install -y docker-compose-plugin
fi

if ! command -v openssl >/dev/null 2>&1; then
  apt-get update
  apt-get install -y openssl
fi

systemctl enable docker
systemctl start docker
