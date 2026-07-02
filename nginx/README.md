# nginx — reverse proxy (Phase 2)

Fronts the FastAPI container. Clients hit Nginx on `:80`; Nginx proxies to `api:8000`
over the internal compose network. In the prod stack, `api` and `db` publish **no**
host ports — Nginx is the only public entry point.

TLS (`:443`) is intentionally deferred to **Phase 5** (Cloudflare + domain).

## Files
- `default.conf` — upstream + proxy config, plus a `/nginx-health` probe served by Nginx itself.
- `Dockerfile` — bakes `default.conf` into `nginx:1.27-alpine`.

## Run the production-style stack

```bash
# SECRET_KEY is required in prod (compose fails fast without it)
echo "SECRET_KEY=$(python -c 'import secrets;print(secrets.token_urlsafe(32))')" >> .env

docker compose -f docker-compose.prod.yml up --build -d

curl -i http://localhost/nginx-health     # proxy layer
curl -i http://localhost/health           # app via proxy
# Swagger UI:  http://localhost/docs
```

## Dev vs prod

| | `docker-compose.yml` (dev) | `docker-compose.prod.yml` |
|---|---|---|
| api port | published `8000:8000` | internal only (`expose`) |
| db port | published `5432:5432` | internal only |
| entry point | FastAPI directly | Nginx on `:80` |
| SECRET_KEY | defaulted | **required** |
| restart | – | `always` |
