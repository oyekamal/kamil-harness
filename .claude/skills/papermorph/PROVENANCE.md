# Provenance

- Upstream: https://github.com/DozenTwelve/Papermorph, path `.claude/skills/papermorph/`, commit `c8d058f` ("feat: merge volume controls and math chapters 16-20").
- License: MIT, Copyright (c) 2026 TedKaczynski (upstream `LICENSE`, copied here unchanged as `LICENSE`).
- Vendored into this harness. Every upstream file is byte-identical to the commit above.
- Local additions only: this file, `LICENSE` (copied from the repo root), and the section at the end of `SKILL.md` ("Running locally"). Upstream instructions above them are unchanged.
- Not vendored: upstream `site/` (example books, ~144 MB of MP3s) and `site/lib/bookshelf.*` (the multi-book shelf on papermorph.diamonddoge.org). A book needs neither: each book carries its own engine copy from `assets/engine/`, and its own cover + contents page from `assets/templates/book.html`. Live examples: https://papermorph.diamonddoge.org
- To re-sync: clone upstream, `diff -r <clone>/.claude/skills/papermorph <this folder>`; only the files listed above should differ.
