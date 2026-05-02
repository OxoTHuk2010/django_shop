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
4. `deploy` (self-hosted runner on VM, local docker compose rebuild)

### Required GitHub Secrets

- No SSH secrets required for deploy when using self-hosted runner.
- Runner labels expected by workflow: `self-hosted`, `Linux`, `X64`.

## Deployment Notes

- VM bootstrap helper: `deploy/bootstrap_vm.sh`
- Workflow runs deploy job directly on VM runner and executes `docker compose up -d --build`.
- `deploy/remote_deploy.sh` is kept as fallback/manual SSH deploy option.
