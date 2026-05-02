#!/usr/bin/env bash
set -euo pipefail

SSH_TARGET="${DEPLOY_USER}@${DEPLOY_HOST}"
SSH_PORT="${DEPLOY_PORT:-22}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/myshop}"
SSH_OPTS="-o StrictHostKeyChecking=accept-new -o KexAlgorithms=curve25519-sha256"

ssh $SSH_OPTS -p "$SSH_PORT" "$SSH_TARGET" "mkdir -p '$DEPLOY_PATH'"
scp $SSH_OPTS -P "$SSH_PORT" deploy/docker-compose.prod.yml "$SSH_TARGET:$DEPLOY_PATH/docker-compose.prod.yml"
scp $SSH_OPTS -P "$SSH_PORT" deploy/bootstrap_vm.sh "$SSH_TARGET:$DEPLOY_PATH/bootstrap_vm.sh"

ssh $SSH_OPTS -p "$SSH_PORT" "$SSH_TARGET" bash <<EOF
set -euo pipefail
export DEPLOY_PATH='$DEPLOY_PATH'
export GHCR_USER='${GHCR_USER}'
export GHCR_PAT='${GHCR_PAT}'
export IMAGE='ghcr.io/${GITHUB_REPOSITORY}:latest'
export SECRET_KEY='${DJANGO_SECRET_KEY}'
export DEBUG='${DJANGO_DEBUG}'
export DB_NAME='${DB_NAME}'
export DB_USER='${DB_USER}'
export DB_PASSWORD='${DB_PASSWORD}'
export DB_HOST='${DB_HOST}'
export DB_PORT='${DB_PORT}'

cd "$DEPLOY_PATH"

cat > .env <<ENV
IMAGE=
SECRET_KEY=
DEBUG=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
ENV

sed -i "s|^IMAGE=.*|IMAGE=$IMAGE|" .env
sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
sed -i "s|^DEBUG=.*|DEBUG=$DEBUG|" .env
sed -i "s|^DB_NAME=.*|DB_NAME=$DB_NAME|" .env
sed -i "s|^DB_USER=.*|DB_USER=$DB_USER|" .env
sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=$DB_PASSWORD|" .env
sed -i "s|^DB_HOST=.*|DB_HOST=$DB_HOST|" .env
sed -i "s|^DB_PORT=.*|DB_PORT=$DB_PORT|" .env

echo "$GHCR_PAT" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
bash bootstrap_vm.sh

docker compose -f docker-compose.prod.yml --env-file .env pull || true
docker compose -f docker-compose.prod.yml --env-file .env up -d

docker compose -f docker-compose.prod.yml --env-file .env exec -T web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml --env-file .env exec -T web python manage.py collectstatic --noinput
EOF
