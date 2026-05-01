# MyShop (Django + DRF)

E-commerce project based on technical specification: Django web, DRF API with JWT, PostgreSQL, Docker, tests, and CI/CD skeleton.

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

## Project Structure

- `config/`: settings, urls, wsgi/asgi
- `products/`: catalog domain and product pages
- `orders/`: cart and checkout flow
- `users/`: auth/account views
- `reviews/`: product reviews
- `api/`: DRF API resources
- `templates/`: Django templates adapted from Hop-and-Barley layout
- `static/`: static assets (css/js/img)
- `tests/`: test suite
- `.gitlab-ci.yml`: CI/CD pipeline skeleton

## Routes (Web)

- `/`, `/products/`: catalog with search/filter/sort
- `/product/<slug>/`: product page
- `/cart/`: session cart
- `/checkout/`: checkout (auth required)
- `/account/register/`, `/account/login/`, `/account/logout/`, `/account/`, `/account/forgot-password/`
- `/guides-recipes/`
- `/shop-admin/products/`, `/shop-admin/add/` (custom static admin-like pages)

## Routes (API)

- `POST /api/users/register/`
- `POST /api/token/` and `POST /api/token/refresh/`
- `GET /api/products/`, `GET /api/products/<id>/`
- `GET|POST|PATCH|DELETE /api/cart/`
- `GET|POST /api/products/<id>/reviews/`
- `GET|POST|PUT|PATCH|DELETE /api/orders/` and `/api/orders/<id>/`
- `POST /api/orders/<id>/cancel/`

## JWT Usage Example

1. Get tokens:

```bash
curl -X POST http://localhost:8000/api/token/ -H "Content-Type: application/json" -d '{"username":"demo","password":"demo12345"}'
```

2. Use access token:

```bash
curl http://localhost:8000/api/orders/ -H "Authorization: Bearer <access_token>"
```

## Quality Checks

```bash
python scripts/verify_encoding.py
flake8 .
mypy .
pytest
```

## CI/CD Overview (GitLab)

Pipeline stages:
1. `verify_encoding` — UTF-8 guard
2. `lint` — flake8 + mypy
3. `test` — migrate + pytest (PostgreSQL service)
4. `build` — Docker image build and push (main branch)
5. `deploy` — manual deploy skeleton with VM variables placeholders

Required CI variables (placeholders):
- `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD`, `CI_REGISTRY`
- `DEPLOY_SSH_HOST`, `DEPLOY_SSH_PORT`, `DEPLOY_SSH_USER`, `DEPLOY_SSH_KEY`
- `DEPLOY_APP_DIR`, `DEPLOY_ENV_FILE_CONTENT`
- app secrets (`SECRET_KEY`, DB creds)

## TЗ -> Implementation Matrix

Must-have:
- Catalog + product page: implemented
- Cart + stock validation: implemented
- Checkout with transaction: implemented
- Account/auth (session): implemented
- Admin management: Django admin + custom admin-like pages implemented
- REST API + JWT + OpenAPI: implemented
- PostgreSQL + Docker Compose: implemented
- Tests + lint hooks: implemented (baseline)

Bonus:
- GraphQL: not implemented
- Coverage >= 80%: not yet
- Advanced deployment automation: skeleton only (VM details pending)

## Acceptance Checklist

- [x] All web pages render via Django templates
- [x] API and Swagger are available
- [x] UTF-8 encoding guard exists and enforced in CI
- [x] CI pipeline skeleton created
- [x] Basic business tests added
- [ ] VM-specific deploy script (next step after VM details)