# Admin Editor for Quartz — Implementation Plan

Bolt a browser-based admin editor onto the existing Quartz pipeline so posts
can be authored from any device. The public site remains a Quartz static
build; the editor writes `.md` files into the same `content/` tree Quartz
already consumes.

---

## 1. Target architecture

```
┌─────────────────┐    writes .md    ┌──────────────────┐
│  Admin app      │ ───────────────► │ shared content/  │
│  (Next.js +     │                  │   volume         │
│   TipTap +      │                  └────────┬─────────┘
│   NextAuth)     │                           │ watched
└─────────────────┘                           ▼
                                       ┌──────────────────┐
                                       │ Quartz container │
                                       │ npx quartz       │
                                       │   build --serve  │
                                       └──────────────────┘
```

Two services in one `docker-compose.yml`, sharing a bind mount of `./content`.

---

## 2. Prerequisite decision: where does this run?

The current deploy is **GitHub Pages** (workflow added in `9ebadfd`). Pages
serves static assets only and cannot host the admin container or watch a
shared volume. Pick one of:

| Option                                                | Public site                   | Admin app                           | Notes                                                                                                                                          |
| ----------------------------------------------------- | ----------------------------- | ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **A. Self-host both** (VPS, Fly.io, Railway, Hetzner) | Quartz `--serve` in container | Same host                           | Matches the diagram above. Simplest mental model. Requires a paid host + reverse proxy + TLS.                                                  |
| **B. Keep Pages, host admin only**                    | GitHub Pages                  | Separate host (Vercel/Fly)          | Admin writes `.md`, commits + pushes to repo, GH Actions rebuilds Pages. No shared volume — admin uses the GitHub API or `simple-git` instead. |
| **C. Local-only admin**                               | GitHub Pages                  | `localhost` via `docker compose up` | No public admin endpoint. Cheapest. Loses the "edit from any device" benefit.                                                                  |

**Recommendation:** **Option B** unless you specifically want to leave
GitHub Pages. It keeps the public site free + fast, and the editor just
becomes "a web UI that commits to your repo." The diagram changes — there's
no shared volume; the admin app talks to the GitHub API.

> Decision needed before implementation. The rest of this plan is written
> for **Option A** (shared volume), with notes for B where it diverges.

---

## 3. Open decisions

1. **Slug / path convention.** Quartz reads any `.md` under `content/`. Current
   layout is flat (`content/index.md`) plus one folder (`content/learning/`).
   Options:
   - Flat: `content/<slug>.md`
   - Dated: `content/posts/YYYY/MM/<slug>.md`
   - Topical folders chosen at save time
2. **Auth provider for NextAuth.** GitHub OAuth is lowest-friction
   (recommended). Google works too. Email/magic-link adds infra (SMTP).
3. **Editor scope.** MVP = create + edit + delete posts. Out of scope for v1:
   image uploads (needs a storage decision), drafts/scheduling, multi-author.
4. **Frontmatter shape.** Minimum: `title`, `date`, `tags`. Confirm whether
   Quartz needs anything else for your config (e.g. `aliases`, `draft`).

---

## 4. Implementation steps (Option A)

### 4.1 Repo layout

```
obsidian-notes/
├─ content/                 # existing — Quartz source
├─ quartz/ …                # existing
├─ Dockerfile               # existing — Quartz container
├─ admin/                   # NEW: Next.js admin app
│  ├─ app/
│  │  ├─ (auth)/…           # NextAuth routes
│  │  ├─ api/posts/route.ts # GET list, POST create
│  │  ├─ api/posts/[slug]/route.ts  # GET, PUT, DELETE
│  │  └─ editor/[[...slug]]/page.tsx
│  ├─ components/Editor.tsx # TipTap + tiptap-markdown
│  ├─ lib/fs.ts             # read/write under CONTENT_DIR
│  ├─ lib/auth.ts           # NextAuth config + email allowlist
│  ├─ Dockerfile
│  └─ package.json
└─ docker-compose.yml       # NEW
```

### 4.2 Admin app

- **Framework:** Next.js 15 (App Router).
- **Editor:** `@tiptap/react` + `@tiptap/starter-kit` + `tiptap-markdown`.
  Serializes directly to Markdown so what's saved matches what Quartz parses.
- **Frontmatter UI:** plain form above the editor (title, date, tag chips).
  On save, prepend YAML frontmatter then the markdown body.
- **File ops:** Node `fs/promises` against `process.env.CONTENT_DIR`
  (`/content` inside the container, bind-mounted to host `./content`).
- **Slug generation:** kebab-case of title; collision check via `fs.access`.
- **API routes:**
  - `GET  /api/posts` — list `.md` files with parsed frontmatter
  - `POST /api/posts` — create new file
  - `GET  /api/posts/[slug]` — read raw markdown for editing
  - `PUT  /api/posts/[slug]` — overwrite
  - `DELETE /api/posts/[slug]` — remove file
- **Auth:**
  - `next-auth` with GitHub provider.
  - `ADMIN_EMAILS` env var = comma-separated allowlist; `signIn` callback
    rejects anyone not in it.
  - Middleware protects `/api/posts/*` and `/editor/*`.

### 4.3 Quartz container

Existing `Dockerfile` already runs `npx quartz build --serve`, which
watches `content/` and rebuilds on change. No changes required beyond
mounting the shared volume.

### 4.4 `docker-compose.yml` (sketch)

```yaml
services:
  quartz:
    build: .
    ports: ["8080:8080"]
    volumes:
      - ./content:/usr/src/app/content
  admin:
    build: ./admin
    ports: ["3000:3000"]
    environment:
      CONTENT_DIR: /content
      NEXTAUTH_URL: ${NEXTAUTH_URL}
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
      GITHUB_ID: ${GITHUB_ID}
      GITHUB_SECRET: ${GITHUB_SECRET}
      ADMIN_EMAILS: ${ADMIN_EMAILS}
    volumes:
      - ./content:/content
```

In production, front both with a reverse proxy (Caddy / Traefik) for TLS
and route `/admin` → admin:3000, `/` → quartz:8080.

### 4.5 Option B divergence (keep GitHub Pages)

If you go with B instead:

- Drop `docker-compose.yml` and the Quartz container.
- Replace `lib/fs.ts` with `lib/github.ts` using Octokit:
  `octokit.repos.createOrUpdateFileContents` to commit `.md` files.
- GitHub Actions (already present) rebuilds Pages on push.
- Host the admin app on Vercel/Fly — no shared volume needed.

---

## 5. Milestones

1. **M1 — Decide hosting model** (Option A vs B). Blocks everything else.
2. **M2 — Scaffold admin app** locally: Next.js + TipTap + a hardcoded
   write to `../content/test.md`. Confirms the editor → Quartz path end-to-end.
3. **M3 — Auth.** NextAuth + GitHub + email allowlist. Gate API routes.
4. **M4 — CRUD UI.** Post list, edit view, delete confirmation.
5. **M5 — Containerize.** `admin/Dockerfile`, `docker-compose.yml`, env file.
6. **M6 — Deploy.** Host setup, reverse proxy, TLS, DNS.
7. **M7 — Polish.** Slug collisions, validation, error toasts, mobile layout.

Out of scope for v1: image uploads, drafts, scheduled publishing,
multi-author, conflict resolution if you also edit `.md` files locally.

---

## 6. Risks / gotchas

- **Concurrent edits.** If you also edit `content/` via Obsidian locally and
  the admin app writes the same file, last-write-wins. Mitigation: pick one
  primary source while the admin app runs, or add a "last-modified" check.
- **TipTap markdown round-trip.** `tiptap-markdown` is lossy for some
  Obsidian-specific syntax (`[[wikilinks]]`, callouts, embeds). Verify
  against a sample of existing notes in M2 before committing to TipTap —
  CodeMirror with a raw-markdown view may be a safer default for an
  Obsidian-flavored vault.
- **Quartz watch mode in production.** `quartz build --serve` is the dev
  server. For production, run `quartz build` on file-change (e.g. via
  `chokidar-cli`) and serve the `public/` output with `nginx` or `caddy`.
- **Secrets.** `.env` must be gitignored. Never commit `NEXTAUTH_SECRET`,
  `GITHUB_SECRET`, or `ADMIN_EMAILS` to the repo.

---

## 7. Next action

Answer the three open decisions in §3 (hosting model, slug convention,
auth provider). Once those are picked, M2 (scaffold + prove the round-trip
on one test post) is ~half a day of work.

##### -----------

##### -----------

##### -----------

##### -----------

##### -----------

##### -----------

##### -----------

# Multi-Project Blog CMS — Implementation Plan

A custom CMS where a **superadmin** manages projects and viewer accounts,
**admins** author blogs inside projects via a TipTap editor, and **viewers**
read blogs in projects they've been granted access to. Wikilinks
(`[[Other Note]]`) resolve only to blogs within the _same_ project.

> Supersedes the earlier "Admin Editor for Quartz" sketch. The new scope —
> multi-tenancy, per-project authentication, revokable viewer credentials —
> doesn't fit Quartz's static-build model. See §1.1.

---

## 1. What changed and why

### 1.1 Quartz dropped from the stack

The previous plan layered an admin editor over Quartz. With the new
requirements:

- **Auth-gated content** can't be statically built. Quartz outputs a single
  set of HTML files for everyone; we need a server that decides "does _this
  user_ have access to _this project_?" on every request.
- **Multiple isolated projects**, each with their own users, content tree,
  and wikilink namespace. Quartz assumes one global content tree.
- **Per-project wikilink resolution** — `[[Note]]` in Project A must not see
  Project B's notes. Quartz resolves links globally across `content/`.

The cleanest path is to drop Quartz and build the public viewer as part of
the same Next.js app. We can carry forward Quartz's visual conventions
(graph view, link popovers, callout styles) as Next.js components if you
want them, but the engine goes.

### 1.2 New requirements at a glance

| Capability                                | Owner                 | Notes                                             |
| ----------------------------------------- | --------------------- | ------------------------------------------------- |
| Create / delete projects                  | superadmin            | (also admin? — see §7)                            |
| Create / edit / delete blogs in a project | admin (or superadmin) | TipTap headless editor, stored as markdown        |
| Create viewer accounts                    | superadmin            | Email + initial password, scoped to a project     |
| Grant / revoke project access             | superadmin            | Per-(user, project) membership row                |
| Wikilinks scoped to project               | system                | `[[Title]]` in Project A → only Project A's blogs |

---

## 2. Architecture

```
                      ┌──────────────────────────┐
                      │   Next.js app            │
                      │                          │
   superadmin ───────►│   /admin/*               │
   admin       ──────►│   /projects/:slug/edit/* │
   viewer      ──────►│   /projects/:slug/*      │
                      │                          │
                      └────────────┬─────────────┘
                                   │
                                   ▼
                      ┌──────────────────────┐
                      │   Postgres           │
                      │  (blogs.body stores  │
                      │   markdown text)     │
                      └──────────────────────┘
```

Single Next.js app, single Postgres database. No shared volume, no separate
public viewer container. Drastically simpler infra than the previous plan.

---

## 3. Data model (Prisma sketch)

```prisma
model User {
  id              String       @id @default(cuid())
  email           String       @unique
  hashedPassword  String
  role            UserRole     // SUPERADMIN | ADMIN | VIEWER
  mustChangePassword Boolean   @default(true)
  memberships     Membership[]
  authoredBlogs   Blog[]       @relation("BlogAuthor")
  createdAt       DateTime     @default(now())
}

enum UserRole { SUPERADMIN ADMIN VIEWER }

model Project {
  id          String       @id @default(cuid())
  slug        String       @unique
  name        String
  description String?
  blogs       Blog[]
  members     Membership[]
  createdAt   DateTime     @default(now())
}

model Membership {
  user        User       @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId      String
  project     Project    @relation(fields: [projectId], references: [id], onDelete: Cascade)
  projectId   String
  role        MemberRole // EDITOR | VIEWER
  createdAt   DateTime   @default(now())

  @@id([userId, projectId])
}

enum MemberRole { EDITOR VIEWER }

model Blog {
  id          String   @id @default(cuid())
  project     Project  @relation(fields: [projectId], references: [id], onDelete: Cascade)
  projectId   String
  slug        String   // unique within a project
  title       String
  body        String   // markdown text
  frontmatter Json?
  author      User     @relation("BlogAuthor", fields: [authorId], references: [id])
  authorId    String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@unique([projectId, slug])
}
```

**Role model (two layers):**

- `User.role` (global): what you can do at the _system_ level.
  - `SUPERADMIN` bypasses every check.
  - `ADMIN` can create projects; auto-granted `EDITOR` Membership on
    anything they create.
  - `VIEWER` can do nothing without a Membership row.
- `Membership.role` (per-project): what you can do _inside one project_.
  - `EDITOR`: read + write blogs.
  - `VIEWER`: read only.

**Revocation = `DELETE FROM Membership WHERE userId=? AND projectId=?`**.
Cascade-deleting a User also drops all their Memberships.

---

## 4. Routes / surfaces

```
/signin                                    email + password
/signout
/change-password                           forced on first sign-in

/admin                                     superadmin home
/admin/projects                            list / create / delete projects
/admin/projects/:slug/members              grant / revoke (any role)
/admin/users                               list all users
/admin/users/new                           create user + set initial password

/projects                                  projects current user can access
/projects/:slug                            blog index for one project (viewer-readable)
/projects/:slug/:blogSlug                  rendered blog
/projects/:slug/edit                       editor home (EDITOR or SUPERADMIN)
/projects/:slug/edit/new                   new blog
/projects/:slug/edit/:blogSlug             edit existing blog (TipTap)

/api/projects                              CRUD — SUPERADMIN
/api/projects/:id/members                  grant / revoke — SUPERADMIN
/api/projects/:id/blogs                    CRUD — EDITOR of that project
/api/users                                 CRUD — SUPERADMIN
```

**Access middleware** — one helper, `requireAccess(req, { projectId, role })`,
called by every mutation handler. Centralizing this prevents the classic
"forgot to check perms on one route" bug.

---

## 5. Editor & wikilinks

### 5.1 TipTap setup

- `@tiptap/react` + `@tiptap/starter-kit`
- `tiptap-markdown` for canonical markdown storage (`getMarkdown()` /
  `setContent()`)
- Custom `WikiLink` node: highlight `[[Title]]` while editing, offer an
  autocomplete dropdown populated from the current project's blog list

### 5.2 Wikilink resolution (read side)

A small remark plugin invoked when rendering a blog:

1. Parse `[[Title]]` and `[[slug|Display Text]]`.
2. Batch-resolve against the current project:
   `SELECT slug, title FROM Blog WHERE projectId=? AND (slug IN (...) OR title ILIKE ANY(...))`
3. On hit: emit `<a href="/projects/:projectSlug/:blogSlug">`.
4. On miss: emit `<span class="broken-link">` (so the reader sees the dead
   link, and the editor can surface a "broken links" badge).

Resolution happens at render time on the server, so renaming a blog updates
inbound links automatically (when matched by slug).

### 5.3 Save flow

```
TipTap state ──getMarkdown()──► markdown body
                                       │
                                       ├─ frontmatter form (title, tags, date)
                                       ▼
                          POST /api/projects/:id/blogs (or PUT)
                                       │
                                       ▼
                          INSERT / UPDATE Blog row
```

---

## 6. Auth model

- **Provider:** NextAuth with the `Credentials` provider (email + password).
  Passwords hashed with `bcrypt` (cost ≥ 12).
- **Initial password flow:** when a superadmin creates a user, they type a
  temporary password. The user's `mustChangePassword` flag is `true`;
  middleware redirects them to `/change-password` until cleared.
- **Session:** JWT, 7-day expiry. `session.user` carries `role` and an array
  of accessible `projectId`s — refreshed at sign-in and on membership change.
- **Bootstrap:** a one-shot seed script reads `SUPERADMIN_EMAIL` /
  `SUPERADMIN_PASSWORD` from env and creates the first `SUPERADMIN`. All
  subsequent user creation goes through the UI.
- **Hardening:** force HTTPS in production, rate-limit `/api/auth/*`, set
  secure cookies. CSRF protected by NextAuth defaults.

---

## 7. Open decisions

1. **Quartz, drop or keep?** Plan assumes **drop**. Confirm — if you want
   Quartz's graph view / popover UX, we'd port those features into the new
   app rather than keep the engine.
2. **Viewer credential model.** Plan assumes **per-user accounts** (email +
   password). Alternative: one shared password per project (Notion-style
   "anyone with the link + password"). Per-user is the only way to revoke
   individuals without breaking everyone else.
3. **Who can create projects** — only `SUPERADMIN`, or any `ADMIN`? Plan
   currently allows `ADMIN`, who becomes auto-EDITOR on creation.
4. **Who can invite viewers to a project** — only `SUPERADMIN`, or also the
   project's `EDITOR`s? Plan currently restricts to `SUPERADMIN`.
5. **What is a "blog"?** A long-form post (one big doc, TOC, footnotes) or a
   note (short, lots of cross-links, Obsidian-style)? Changes editor
   features and default UI.
6. **Wikilink syntax.** `[[Title]]` (Obsidian), `[[slug]]`, both? Plan supports
   both — slug match wins, title match is fallback.
7. **Existing content.** Migrate the current `content/index.md` +
   `content/learning/` into a "Personal Notes" project on first boot, or
   start clean?
8. **Hosting.** Fly.io / Railway / Render / self-hosted VPS. All work; Fly.io
   is the cheapest path with managed Postgres + a single-region app.

---

## 8. Milestones

1. **M1 — Decisions confirmed.** Answer §7. Blocks coding.
2. **M2 — Scaffold.** `create-next-app` + Prisma + Postgres (Docker compose
   for local dev), schema migrations, seed superadmin.
3. **M3 — Auth.** NextAuth credentials provider, sign-in / change-password
   flow, role middleware.
4. **M4 — Superadmin UI.** Project CRUD, user CRUD, membership grant/revoke.
5. **M5 — Editor.** TipTap + frontmatter form + `POST/PUT /api/blogs`. Prove
   the markdown round-trip on a real blog.
6. **M6 — Wikilinks.** Remark plugin (read side) + TipTap autocomplete
   (write side), both scoped to the current project.
7. **M7 — Viewer side.** Project list, blog list, rendered blog with
   wikilink resolution + access gating.
8. **M8 — Containerize.** Dockerfile (Next.js standalone output), compose
   pinning Postgres + the app, `.env.example`.
9. **M9 — Deploy.** Provision host + managed Postgres, TLS, custom domain.
10. **M10 — Polish.** Search within project, broken-link badge in editor,
    soft-delete for projects, simple audit log of who changed what.

**Out of scope for v1:** image uploads, drafts / scheduled publishing,
comments, project-level themes, full-text search, 2FA, public (no-login)
projects, importing existing Obsidian vaults wholesale.

---

## 9. Risks / gotchas

- **TipTap ↔ Markdown round-trip.** `tiptap-markdown` is lossy for some
  Obsidian-flavored syntax (callouts, footnotes, dataview, embeds). Verify
  against real content in M5 _before_ committing. CodeMirror + a markdown
  preview is the fallback if TipTap's serializer breaks too much.
- **Wikilink renames.** Linking by title means renames silently break inbound
  links. Mitigation: prefer slug-based resolution; show a "broken links
  detected" badge in the editor.
- **Privilege escalation.** A viewer must never reach
  `POST /api/projects/:id/blogs`. Centralize the access check in
  `requireAccess()` and call it from every mutation handler. Easy to forget
  on one new route otherwise — write tests for the negative cases.
- **N+1 on wikilink resolution.** A blog with 50 wikilinks shouldn't issue
  50 SQL queries. Batch-fetch all referenced slugs in one
  `WHERE projectId = ? AND slug IN (…)`.
- **Cascading deletes.** Deleting a project drops every blog and membership
  for that project. Surface a strong "type the project name to confirm"
  dialog in the UI.
- **Password handling.** Use `bcrypt` (cost ≥ 12). Never log plaintext.
  Rate-limit sign-in. Force HTTPS in production. Consider lockout after N
  failed attempts.
- **Session-cache staleness.** If `session.user.projectIds` is cached in the
  JWT, a viewer who's just had their access revoked still has a valid token
  until expiry. Mitigation: re-check Membership on every request (cheap with
  an index) rather than trust the JWT for authorization.

---

## 10. Next action

Answer §7. Once those are settled, M2–M3 (scaffold + auth shell) is ~1 day
of work, and M5 (editor + markdown round-trip on a real blog) is the
earliest demoable milestone — ~3–4 days from a clean start.

##### -----------
