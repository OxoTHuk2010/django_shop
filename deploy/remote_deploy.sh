#!/usr/bin/env bash
set -euo pipefail

SSH_TARGET="${DEPLOY_USER}@${DEPLOY_HOST}"
SSH_PORT="${DEPLOY_PORT:-22}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/myshop}"
DEPLOY_BUNDLE="${DEPLOY_BUNDLE:-myshop_bundle.tgz}"
SSH_OPTS="-o StrictHostKeyChecking=accept-new -o KexAlgorithms=curve25519-sha256"

ssh $SSH_OPTS -p "$SSH_PORT" "$SSH_TARGET" "mkdir -p '$DEPLOY_PATH'"
scp $SSH_OPTS -P "$SSH_PORT" "$DEPLOY_BUNDLE" "$SSH_TARGET:$DEPLOY_PATH/$DEPLOY_BUNDLE"

ssh $SSH_OPTS -p "$SSH_PORT" "$SSH_TARGET" bash <<EOF
set -euo pipefail
export DEPLOY_PATH='$DEPLOY_PATH'
export DEPLOY_BUNDLE='$DEPLOY_BUNDLE'

cd "$DEPLOY_PATH"
mkdir -p app
tar -xzf "$DEPLOY_BUNDLE" -C app
rm -f "$DEPLOY_BUNDLE"
cd app

sudo bash deploy/bootstrap_vm.sh

sudo docker compose -f docker-compose.yml down || true
sudo docker compose -f docker-compose.yml up -d --build

until sudo docker compose -f docker-compose.yml exec -T db pg_isready -U myshop; do
  sleep 2
done

sudo docker compose -f docker-compose.yml exec -T web python manage.py migrate --noinput
sudo docker compose -f docker-compose.yml exec -T web python manage.py collectstatic --noinput || true

for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -fsS --max-time 5 http://127.0.0.1:8000/ >/dev/null; then
    echo "DEPLOY_OK"
    exit 0
  fi
  sleep 2
done

echo "DEPLOY_FAILED: web endpoint is not reachable"
exit 1
EOF
