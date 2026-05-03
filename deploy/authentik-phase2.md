# Authentik (SSO) — Deferred to Phase 2 (DEP-05)

> **AI 接力开发指南** — 本文不是部署手册，是一份**deferred-feature 规格说明**。任何接手 SSO 决策的工程师/AI，应先读本文，确认 promote-when 触发条件**全部**满足后才考虑启用 Authentik 块。在那之前，`docker-compose.yml.draft` 中的 `authentik:` 服务**整块**保持注释状态。

---

## Status: DEFERRED

⚠️ **Authentik service block is COMMENTED OUT in `deploy/docker-compose.yml.draft`. SSO is NOT enabled in v1.**

Why: RAGFlow OIDC integration is not production-ready as of 2026-05.

---

## Why deferred — the bug stack

Three independent issues block SSO unification across Wiki.js + RAGFlow:

### Issue 1: RAGFlow OIDC FR #3495 (still open)

Source: [https://github.com/infiniflow/ragflow/issues/3495](https://github.com/infiniflow/ragflow/issues/3495)

OIDC support in RAGFlow is a **feature request still pending upstream as of 2026-05**. There is no merged implementation that we can rely on. PRs have been proposed but none merged to a stable release.

### Issue 2: RAGFlow OIDC bug #12568 (Keycloak redirect loop)

Source: [https://github.com/infiniflow/ragflow/issues/12568](https://github.com/infiniflow/ragflow/issues/12568)

Even where partial OIDC code exists (since RAGFlow's Quart migration), users report a **redirect loop between RAGFlow and the IdP** — the login flow never issues the session cookie. Symptom: user clicks "Sign in with SSO" → redirected to Authentik/Keycloak → authenticates → bounced back to RAGFlow → bounced back to IdP → infinite loop. This is a hard-stop for any production SSO integration.

### Issue 3: One-sided readiness

- **Wiki.js side**: OIDC + Authentik integration is documented and works. See [Authentik Wiki.js integration guide](https://docs.goauthentik.io/integrations/services/wiki-js/). Wiki.js is **ready**.
- **RAGFlow side**: blocked by Issues 1 + 2 above.

Enabling Authentik for Wiki.js alone would fragment auth UX (users log in via SSO for Wiki.js but with separate local account for RAGFlow). Either both services SSO-enable together or neither does — that's the v1 design constraint.

---

## What's already in compose

The `authentik:` service block is **present but ENTIRELY commented out** in `deploy/docker-compose.yml.draft`:

```yaml
  # authentik:
  #   image: ghcr.io/goauthentik/server:2024.10
  #   restart: unless-stopped
  #   environment:
  #     AUTHENTIK_SECRET_KEY: ${AUTHENTIK_SECRET_KEY}
  #     AUTHENTIK_POSTGRESQL__HOST: postgres
  #     AUTHENTIK_POSTGRESQL__USER: ${AUTHENTIK_DB_USER}
  #     AUTHENTIK_POSTGRESQL__PASSWORD: ${AUTHENTIK_DB_PASS}
  #   ports:
  #     - "9000:9000"
  #   networks:
  #     - akb-net
```

The corresponding env vars in `deploy/.env.example` are placeholders:

```bash
AUTHENTIK_SECRET_KEY=<DEFERRED>
AUTHENTIK_DB_USER=<DEFERRED>
AUTHENTIK_DB_PASS=<DEFERRED>
```

This is a deliberate "ready-to-uncomment" stub. Do not delete; do not uncomment until trigger conditions are met.

---

## Promote when (the trigger condition)

Promote Authentik from DEFERRED to ENABLED when **ALL** of the following hold:

- [ ] **(a)** RAGFlow issue [#12568](https://github.com/infiniflow/ragflow/issues/12568) is **closed** in a tagged release ≥ v0.26.0 (or whichever release fixes the redirect loop).
- [ ] **(b)** RAGFlow FR [#3495](https://github.com/infiniflow/ragflow/issues/3495) is **merged** with documented Authentik-compatible OIDC config.
- [ ] **(c)** We have **≥2 confirmed user accounts** that demonstrably need cross-service navigation (i.e., users routinely move between Wiki.js and RAGFlow within the same session).
- [ ] **(d)** A new Phase plan covers: (i) Authentik bootstrap admin flow, (ii) Wiki.js OIDC config, (iii) RAGFlow OIDC config, (iv) Caddy SSO routing, (v) rollback plan.

If any of (a)–(d) is not satisfied, **stay on local accounts**. Cross-link this checklist from `.planning/ROADMAP_FUTURE.md` (06-03 deliverable) so the roadmap and this doc tell the same story.

---

## Workaround pattern (if SSO is needed before RAGFlow OIDC ships)

If business pressure requires SSO before upstream resolves the bug, there is a **workaround**: put RAGFlow behind Caddy `forward_auth` to Authentik.

**Sketch:**
- Caddy authenticates the user against Authentik via `forward_auth` directive.
- On success, Caddy proxies the request to RAGFlow with `X-User: <username>` headers.
- RAGFlow uses its **local-account login** with auto-provisioned accounts mapping to the SSO username.

**Pros:** unblocks SSO without waiting for RAGFlow OIDC.
**Cons (why this is a workaround, not a permanent design):**
- RAGFlow's local-account login still exists as a parallel auth path — must be locked down separately (e.g., bind RAGFlow's port only to the docker network, never to host).
- No OIDC token flow — group/role mapping must be re-implemented header-side.
- Disable when RAGFlow OIDC matures; do not let it become technical debt.

**Document this only as an option. Default v1 = no SSO.**

---

## Cross-references

| File | What it provides |
| --- | --- |
| `deploy/docker-compose.yml.draft` | Commented-out `authentik:` block + comment header citing #12568 |
| `deploy/.env.example` | `AUTHENTIK_*` env vars marked `<DEFERRED>` |
| `.planning/ROADMAP_FUTURE.md` | Promote-when rule mirrored (06-03 deliverable) |
| `.planning/research/STACK.md` | §"Auth / Reverse Proxy" — full rationale, Authentik vs Keycloak vs Authelia |
| `.planning/research/PITFALLS.md` | Pitfall context (RAGFlow OIDC immaturity is a recurring theme) |

---

## Open questions (for the future-phase planner)

- **Authentik upgrade path**: which Authentik release line do we pin? `2024.10` is in compose as a placeholder; reassess at promotion time.
- **Postgres co-tenancy**: Authentik wants its own Postgres; do we share the existing `postgres` service (different DB) or run a second Postgres? Shared is simpler; isolated is safer.
- **Session timeout**: aviation context may want shorter sessions than Authentik defaults.
- **Group → Wiki.js role mapping**: define the Authentik group structure that maps cleanly to Wiki.js's "admin / editor / reader" roles before promotion.
