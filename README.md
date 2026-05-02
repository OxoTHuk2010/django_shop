# MyShop (Django + DRF)

E-commerce project based on technical specification: Django web, DRF API with JWT, PostgreSQL, Docker, tests, and GitHub Actions CI/CD.

## Quick Start

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

App URL: `http://localhost:8000/`  
Swagger/OpenAPI: `http://localhost:8000/api/docs/`

Demo catalog data from the provided Hop-and-Barley pages is seeded automatically by migration
`products.0002_seed_hop_and_barley_products` on a clean database.

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
3. `test` (PostgreSQL service, coverage gate `>=70%`)
4. `deploy` (self-hosted runner on VM, local docker compose rebuild)

## Local Debug -> Prod Flow

Before pushing to `main`, run local debug stack on this PC:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T web python manage.py migrate --noinput
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T web pytest -q
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T web pytest --cov=. --cov-report=term-missing
```

Stop local debug stack:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

Production deploy is done only by GitHub pipeline using `docker-compose.yml` with `prod` profile (Nginx on port 80).

## API JWT Flow

1. Obtain pair:
   - `POST /api/token/`
   - body: `{"username":"<user>","password":"<password>"}`
2. Refresh access:
   - `POST /api/token/refresh/`
   - body: `{"refresh":"<refresh_token>"}`
3. Use access token:
   - `Authorization: Bearer <access_token>`

## Main Routes

- Web:
  - `/` catalog
  - `/product/<slug>/` product detail
  - `/cart/` cart
  - `/checkout/` checkout
  - `/account/` user account
- API:
  - `/api/products/`
  - `/api/orders/`
  - `/api/cart/`
  - `/api/products/<product_id>/reviews/`
  - `/api/docs/`, `/api/schema/`

### Required GitHub Secrets

- No SSH secrets required for deploy when using self-hosted runner.
- Runner labels expected by workflow: `self-hosted`, `Linux`, `X64`.

## Deployment Notes

- VM bootstrap helper: `deploy/bootstrap_vm.sh`
- Workflow runs deploy job directly on VM runner and executes `docker compose up -d --build`.
- `deploy/remote_deploy.sh` is kept as fallback/manual SSH deploy option.

## Acceptance Checklist

- [x] Django templates render migrated pages from Hop-and-Barley style.
- [x] REST API implemented for products/orders/cart/reviews/users register.
- [x] JWT auth endpoints enabled and covered by tests.
- [x] OpenAPI docs available at `/api/docs/`.
- [x] PostgreSQL + Docker setup for local and production.
- [x] GitHub Actions pipeline includes encoding/lint/test/deploy.
- [x] Encoding policy enforced (`UTF-8` without BOM).
