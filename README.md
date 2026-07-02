# CloudOps Control Center

> A deliberately simple task app that is **built, deployed, monitored, and recovered like a real production service.**
> The application logic is thin on purpose — the point is the *operations*: Docker, Nginx, Azure VM, HTTPS, CI/CD, observability, and disaster recovery.

---

## 1. What it is

A small internal "control center" that a web operator would actually use:

| Feature | Priority | Ops keyword it demonstrates |
|---|---|---|
| Task CRUD + complete | P0 | baseline app |
| Service Health Check (HTTP) | P1 | monitoring, reliability, troubleshooting |
| SSL Certificate Expiry Checker | P1 | **SSL/TLS certificate management** |
| Incident Log | P2 | ITIL incident / problem management |
| Deployment History | P2 | change management, CI/CD, automation |

> P0–P1 alone justify the résumé line. P2 is "if time remains."

---

## 2. Architecture

```
Browser
  │  HTTPS
Cloudflare  ──────────────  DNS + SSL (edge) + WAF
  │
Azure VM ────────────────────────────────────────────
  │  :443
Nginx           reverse proxy, TLS termination
  │  proxy_pass
FastAPI         uvicorn/gunicorn  ──►  /metrics
  │
PostgreSQL
  ▲
  └─ Scheduler (APScheduler)
        └─ periodic HTTP + SSL checks  →  DB

Observability:
  Prometheus  ◄─ FastAPI /metrics + node_exporter
  Grafana     ◄─ Prometheus
  Alertmanager ─► Slack / Email
```

**Two distinct TLS concerns (important, and a good interview point):**
- Cloudflare / Nginx TLS = securing **this** service.
- SSL Expiry Checker feature = watching **external domains'** certificates the operator registers.

---

## 3. Data model

```
User               Task                Monitor              Check (health log)
----               ----                -------              ------------------
id                 id                  id                   id
email              title               name                 monitor_id (FK)
password_hash      description         url                  status_code
created_at         status             type (http|ssl)      response_ms
                   created_at         expected_status      ssl_expires_at
                   user_id (FK)       created_at           checked_at

Incident                       Deployment
--------                       ----------
id                             id
service_name                   commit_hash
issue                          status (success|failed|rolledback)
root_cause                     deployed_at
action                         rollback_available
status (open|resolved)
created_at
```

Phase 1 ships only `User` + `Task`. The rest arrive with their phases.

---

## 4. Tech stack

React · Cloudflare · Nginx · FastAPI · PostgreSQL · Docker Compose · Azure VM · GitHub Actions · Terraform · Prometheus · Grafana

---

## 5. Build phases (the commit history *is* the story)

| Phase | Goal | Done when |
|---|---|---|
| 1 | FastAPI + PostgreSQL + Docker Compose | Task CRUD works locally |
| 2 | Nginx reverse proxy | one `compose up`, 80 → FastAPI |
| 3 | Azure VM **manual** deploy | reachable on public IP |
| 4 | GitHub Actions CI/CD | push → test → build → deploy |
| 5 | Cloudflare (DNS + SSL + WAF) | domain over HTTPS |
| 6 | Health + SSL checker feature | status shown on dashboard |
| 7 | Prometheus + Grafana + Alertmanager | metrics dashboard + 1 alert |
| 8 | Terraform | VM / VNet / NSG reproducible as code |
| 9 | Incident / Deployment features | (spare time) ops story complete |

> Phase 3 is intentionally **manual** so the CI/CD in Phase 4 has a "pain → automation" story to tell.

---

## 6. Operational maturity (low cost, high signal)

1. **Runbook** in `docs/` — 3 failure scenarios with recovery steps.
2. **Deliberate incident → recovery** — e.g. break an Nginx upstream, capture the 502, log the incident, screenshot the Grafana alert.
3. **One Grafana dashboard** — uptime %, response-time p95, SSL days-remaining.

---

## 7. Repository layout

```
cloudops-control-center/
├─ backend/          FastAPI app (see backend/README.md)
├─ frontend/         React dashboard        (Phase 6)
├─ nginx/            reverse proxy config    (Phase 2)
├─ monitoring/       Prometheus/Grafana/Alertmanager (Phase 7)
├─ infra/            Terraform (VM/VNet/NSG) (Phase 8)
├─ .github/workflows/ CI/CD                  (Phase 4)
├─ docker-compose.yml       dev
├─ docker-compose.prod.yml  prod             (Phase 2+)
└─ README.md
```

---

## 8. Quick start (Phase 1)

```bash
cp .env.example .env          # adjust secrets if you like
docker compose up --build     # API on http://localhost:8000
# interactive docs:           http://localhost:8000/docs
```

---

## Résumé line

> Built and operated **CloudOps Control Center**, a containerized service dashboard (task management, HTTP/SSL health monitoring, incident logging, deployment history) on **Azure VM** with **Docker Compose, Nginx reverse proxy, PostgreSQL, and GitHub Actions CI/CD**. Provisioned infrastructure with **Terraform**, secured traffic via **Cloudflare DNS/SSL/WAF**, and implemented observability & alerting with **Prometheus, Grafana, and Alertmanager**.
