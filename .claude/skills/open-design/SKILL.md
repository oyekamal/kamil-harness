---
name: open-design
description: Run OpenDesign (nexu-io/open-design, the open-source Claude Design alternative) locally in Docker with Claude Code as the runtime, and drive it headlessly to produce web prototypes, decks, documents, images, and HyperFrames from a text brief. Use for "open design", "opendesign", "make a prototype/landing page/deck with open-design", or when a design artifact needs its 164 bundled design skills + design systems. Tested 2026-09-07 (v0.21.1).
---

# OpenDesign

**Requires:** Docker and a Claude Code login to mount into the container.

Self-hosted design agent. Container `open-design` on `http://127.0.0.1:7456`, Claude Code mounted from the host as the agent runtime. Everything lives in `deploy/`.

## Commands

```bash
deploy/od.sh up                      # build (first time) + start; prints URL + login
deploy/od.sh run "<brief>"           # headless Playwright: submit brief, wait, save outputs to deploy/out/
deploy/od.sh down                    # stop container (data volume persists)
```

Browser login: user `open-design`, password = `OD_API_TOKEN` in `deploy/.env` (also in `deploy/.token`). API: `Authorization: Bearer <token>`. Files: `GET /api/projects/<id>/files` and `/files/<name>`.

## Expectations

- One Prototype brief ≈ 8–9 min on the default Claude Code model (skill read → build → self-critique). Tell {{USER_NAME}} up front.
- HTML export works. PDF/PPTX export returns 501 in Docker (desktop runtime only) — render the HTML with Playwright yourself if a PDF is needed.
- Default artifact type is Prototype; switch in the UI, or extend `od_run.py` to click "Slide deck" / "Document" / "Image" before Run.
- Copy anything worth keeping out of `deploy/out/` into `vault/experiments/open-design/`.

## Gotchas (already handled by od.sh, don't re-debug)

- Container uid is 1001; host `~/.claude/.credentials.json` is 0600 uid 1000 → `od.sh up` copies creds into `deploy/claude-home/` (644) and mounts that, not the whole `~/.claude`. This also keeps {{AGENT_NAME}}'s host hooks out of the container. Re-run `up` if Claude auth expires (creds are a snapshot).
- `docker-compose.linux.yml` mounts `~/.local/bin` + `~/.local/share/claude` + host glibc; needs image `open-design-local` (Dockerfile.local adds libc6-compat).
- Brief box is a Lexical editor (`data-testid=home-hero-input`): `keyboard.insert_text`, not `locator.type`.
- Onboarding page appears on a fresh browser profile; `od_run.py` clicks Local Agent → Continue automatically.

Upstream repo for updates/skills catalog: https://github.com/nexu-io/open-design
