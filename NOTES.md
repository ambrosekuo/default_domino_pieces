# Fork notes

For docker image itself when running, 
pip install domino
domino platform run-compose --github-token

Need to do this for mac:
- Set `platform: linux/amd64` on Domino services in `docker-compose.yaml` (Apple Silicon has no arm64 image manifests).
- Add `AIRFLOW_UID=50000` to `.env` so Airflow volume mounts don't hit macOS permission warnings.



- **GHCR publish failed** (`installation not allowed to Create organization package`): new `ambrosekuo` registry namespace needs explicit `packages: write` on workflow jobs; upstream didn't because their org had permissive token defaults + existing package.
- **Fix:** add `permissions: { contents: write, packages: write }` to jobs — no manual PAT needed.


