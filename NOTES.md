# Fork notes

- **GHCR publish failed** (`installation not allowed to Create organization package`): new `ambrosekuo` registry namespace needs explicit `packages: write` on workflow jobs; upstream didn't because their org had permissive token defaults + existing package.
- **Fix:** add `permissions: { contents: write, packages: write }` to jobs — no manual PAT needed.
