---
name: create-verification-skill
description: "Generate a project-local verification skill that drives a real app the way a user does — any language, framework, or platform. Use for 'make a verification skill for this repo', 'create a control skill for this repo', or when a project has no scripted way to prove UI/CLI/service behavior. This is a meta-skill: it BUILDS a project-specific E2E-driving harness, it does not itself drive an app."
---

# Create a verification skill

Every serious project needs a scripted way to drive the real app and prove behavior: launch it, exercise a feature the way a user would, and capture evidence. This skill generates that as a project-local skill (`.claude/skills/verify-<app>/` in that project's own repo) tailored to the repo. You write the generator's output for the next agent, not for a human: it will be read cold, mid-task, by an agent that has never seen the app.

**Framing:** this skill is a meta-skill {{AGENT_NAME}} invokes when it wants to *build* a project-specific E2E-driving harness — most likely for your main app, to close an E2E gate before every PR, or to give a bug-fix flow something concrete to run instead of narrating "should work now." It does not itself drive the app; the skill it generates does that. Once generated, `webapp-testing` (Playwright) is typically the harness the generated skill's Drive section calls into for a browser-facing app.

## 1. Interview the repo, not the user

Answer these from the codebase and only ask {{USER_NAME}} what you cannot observe:

- **Surface:** what does a user actually touch? A web UI, a CLI, a Django admin, an API, a mobile app? A repo can have several; pick the primary one and note the rest.
- **Run:** how does the app start locally? Prefer the repo's own documented dev command (package scripts, Makefile, README quickstart, `manage.py runserver`). Note ports, env vars, seed data, auth.
- **Drive:** how can an agent interact with it programmatically? Existing harnesses first — Playwright specs, existing test fixtures, curl-able endpoints, a debug port. Only then reach for `webapp-testing`'s generic Playwright recipe for a web UI, or a plain HTTP/`curl` recipe for a service, or a PTY/tmux harness for a CLI/TUI.
- **Observe:** what evidence can be captured? Screenshots, terminal transcripts, response bodies, logs, exit codes, DB state (e.g. IndexedDB state in the frontend, ORM state in the backend).
- **Isolate:** can two instances run side by side (ports, data dirs, profiles)? For example, whether a second checkout can run alongside the live repo without touching it. The generated skill should say explicitly whether concurrent verification runs are safe.

If the checkout doesn't build or start as-is, fix that first (or report it precisely) before generating; a skill written against a broken base teaches wrong steps. When an irrelevant missing asset blocks startup (a static dir the API never serves, a sample config), the generated skill may create it, clearly marked as verification scaffolding, and remove it in cleanup.

## 2. Generate the skill

Write `.claude/skills/verify-<app>/SKILL.md` with YAML frontmatter (`name: verify-<app>` and a `description` that names the app, the surface, and when to reach for it — without frontmatter the skill never registers) and these sections, each grounded in what the interview actually found (no placeholders left):

- **Launch:** the exact command that starts the app for verification, and how to tell it's ready (a log line, a port answering, a prompt). Include teardown. For a short-lived CLI there is no server to keep alive: launch means build once, then start each drive in its own isolated session.
- **Doctor:** one read-only check that answers "is this instance worth driving?" — process up, right version/build, port owned by us, auth valid. Run this first whenever anything looks off.
- **Drive:** the harness recipe with real selectors/commands from this repo, not examples. Prefer stable handles (ARIA labels, data attributes, route paths, Django URL names) over coordinates and tab order. For a web UI, this section typically hands off to `webapp-testing`.
- **Evidence:** what to capture for a proof and where it goes. State the proof standards: exercise the real user path, not internal setters or test-only endpoints; capture the action and the resulting state, not just the final screen; verify side effects (files written, rows inserted, Dexie tables updated, Slack messages sent) alongside what's visible; mocks only where a production boundary already isolates the external system. When the safe path is a dry-run or test mode, verify what it actually skips by observing (files, network, git refs) rather than trusting its name.
- **Cleanup:** how to tear down instances the run created. Never kill by process name; kill what you started. Cleanup removes instances and scratch state, never the evidence: proof artifacts survive the teardown, in a location the skill names.
- **Helpers:** any script the skill ships is executable and its invocation is shown in the skill body. A helper the reader has to reverse-engineer is not a helper.

## 3. Seed the feature map

Create `.claude/skills/verify-<app>/features/README.md` plus one file per user-facing feature you can identify (aim for the top 3-5 to start, from routes, commands, menus, or docs). Follow the shape in [`references/feature-map-example/`](references/feature-map-example/) (a generic "Notes app" example kept as-is from the upstream skill — adapt its structure, not its content, to the real app). Each file answers, from the user's point of view: what the feature is, how to reach it, how to drive it with the harness, and what observable end state proves it works. The four H2s are `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, and `Gotchas`. The map is the repo's maintained verification source; a proof that drives one convenient entry point is incomplete when the map lists others.

## 4. Prove the generated skill before handing it over

Run its own instructions end to end once: launch, doctor, drive ONE mapped feature (one is enough; the map exists so later runs can cover the rest), capture evidence, clean up. After cleanup, confirm the evidence still exists at the named location — a cleanup that eats the proof fails this step. Fix what fails, and run the generated cleanup after every failed iteration too, so broken attempts don't strand processes and ports. A generated skill that was never executed is a draft, not a deliverable.

## 5. Offer the maintenance loop

Point {{USER_NAME}} at `maintain-verification-skill` for keeping the map honest as the app changes.
