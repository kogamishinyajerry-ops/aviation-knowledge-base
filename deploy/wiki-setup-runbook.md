# Wiki.js Phase 8b Setup Runbook

> Phase 8b — Wiki.js portal local-dev setup. Live at `http://localhost:3000`.
> Source: `deploy/docker-compose.wiki.yml` + `deploy/.env.wiki`.
> Content: `wiki/` directory (60 pages auto-generated from `instances/` corpus).

---

## Status

```bash
docker ps --format "{{.Names}}: {{.Status}}" | grep akb
# akb-wiki: Up (healthy)
# akb-postgres: Up (healthy)
```

If not running:
```bash
cd ~/aviation-knowledge-base
docker compose -f deploy/docker-compose.wiki.yml --env-file deploy/.env.wiki up -d
```

Tear down (drops postgres data):
```bash
docker compose -f deploy/docker-compose.wiki.yml down -v
```

---

## Initial Admin Setup (one-time, ~2 min)

Wiki.js's first-run wizard requires manual web steps. Open `http://localhost:3000/`:

1. **Welcome screen** → click "Get Started"
2. **General** → Site URL: `http://localhost:3000` · Title: `Aviation Knowledge Base v0.1.0` · click Next
3. **Administrator Account**:
   - Email: any (e.g. `admin@local`)
   - Password: any (≥8 chars; this is local-dev only)
   - Confirm Password
   - Telemetry: optional (off recommended for local)
   - click Install
4. After install completes (~10s) → login screen → use the email/password above

---

## Load the corpus pages (3 paths, pick one)

The 60 pre-generated pages live at `wiki/` on the host and are mounted into the container at `/wiki-content`. Three ways to get them into Wiki.js:

### Path A — Disk Storage module (recommended, automated)

After admin login:

1. **Administration** (top-right cog) → **Storage**
2. Click **Disk** module → toggle **Active** → **Apply**
3. **Path on disk**: `/wiki-content` (already mounted RW from `wiki/`)
4. **Output Format**: Markdown
5. Click **Apply** → then **Sync** (top of module)
6. Wiki.js scans `/wiki-content` and creates pages from each `*.md` file
7. Refresh the home page — corpus pages appear

### Path B — Git Storage module (with GitHub push-back)

Use this if you want Wiki.js edits to push back to the GitHub repo's `wiki/` subdirectory (DEP-04 hard rule: scope = `wiki/` only).

1. Generate an SSH deploy key: `ssh-keygen -t ed25519 -f ~/.ssh/wiki-deploy -N ""`
2. Add public key to GitHub repo settings → Deploy keys → Allow write access
3. **Administration** → **Storage** → **Git** module → **Active**
4. Repository URL: `git@github.com:kogamishinyajerry-ops/aviation-knowledge-base.git`
5. Branch: `main` · Local path: `/wiki-content` · SSH key: paste private key contents
6. **Sync direction**: Bidirectional (Wiki.js edits push, repo updates pull)
7. **Path Prefix**: `wiki/` (DEP-04: never the full repo)
8. Apply + Sync

### Path C — Manual paste (each page individually)

Slowest but no module config. From admin home → **+ Create New Page** → paste markdown. Use only for spot-fixing.

---

## Verify

After Path A or B finishes sync:

- `http://localhost:3000/` → should show landing page with corpus stats (60 pages)
- `http://localhost:3000/entities` → 22 entity types
- `http://localhost:3000/entities/expert-note/canonical-example` → DEMO-04 worked example
- `http://localhost:3000/documents/far-25-1309` → FAR §25.1309 page with metadata + processed.md
- `http://localhost:3000/glossary` → 73 bilingual terms

Search bar (top): try `H-Darrieus` or `FADEC` — should hit the relevant pages.

---

## Regenerating pages from the corpus

When `instances/` or `docs/` changes (new entity, schema bump, etc.):

```bash
cd ~/aviation-knowledge-base
source .venv/bin/activate
python scripts/build_wiki_pages.py        # regenerates wiki/ from corpus
# Then in Wiki.js admin → Storage → Sync (re-pulls from disk)
```

The Disk Storage module idempotent-syncs: existing pages are updated, new files become new pages, deleted files become orphan pages (manually delete in admin).

---

## DEP-04 enforcement (Wiki.js Git scope = `wiki/` only)

**HARD RULE**: Wiki.js Git Storage module Path Prefix MUST be `wiki/` and the SSH deploy key MUST NOT have admin scope.

Violation modes (all forbidden):
- Setting Path Prefix to `""` or `/` (would let Wiki.js push pages anywhere)
- Using a personal access token instead of a deploy key (token has full repo write)
- Configuring Storage on `~/aviation-knowledge-base` host path (bypasses container isolation)

The current docker-compose mount (`../wiki:/wiki-content`) already enforces the scope structurally — Wiki.js only sees `wiki/`, can't reach `instances/` / `ontology/` / `scripts/`.

---

## Tear down + cleanup

```bash
docker compose -f deploy/docker-compose.wiki.yml down -v   # drop containers + postgres volume
docker volume prune -f
```

Re-run the admin wizard on next `up` (state is in postgres volume).
