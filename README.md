# MyShop (Django + DRF)

E-commerce project based on technical specification: Django web, DRF API with JWT, PostgreSQL, Docker, tests, and GitHub Actions CI/CD.

## Quick Start

```bash
docker compose up --build
```

App URL: `http://localhost:8000/`  
Swagger/OpenAPI: `http://localhost:8000/api/docs/`

## Encoding Policy

All repository text files must be `UTF-8` without BOM:
- `*.py`, `*.html`, `*.css`, `*.js`, `*.md`, `*.yml`, `*.toml`

Check locally:

```bash
python scripts/verify_encoding.py
```

## CI/CD (GitHub Actions)

Workflow file: `.github/workflows/ci-cd.yml`

Stages:
1. `verify_encoding`
2. `lint`
3. `test` (PostgreSQL service)
4. `build` (push image to GHCR)
5. `deploy` (SSH deploy to VM)

### Required GitHub Secrets

- `DEPLOY_HOST` (set to `103.76.55.214`)
- `DEPLOY_PORT` (usually `22`)
- `DEPLOY_USER` (set to `oxothuk`)
- `DEPLOY_PATH` (for example `/opt/myshop`)
- `DEPLOY_SSH_KEY` (private key matching deployed public key)
- `GHCR_PAT` (token with `read:packages`)
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

## Deployment Notes

- VM bootstrap helper: `deploy/bootstrap_vm.sh`
- Remote deployment script used by workflow: `deploy/remote_deploy.sh`
- Current VM is expected to already accept key-based SSH for user `oxothuk`.
- Deploy script uses `StrictHostKeyChecking=accept-new` and `curve25519-sha256` KEX fallback.
