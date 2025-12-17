# Agent Instructions

- Work from the repository root (`timetracker`) and keep new guidance files up to date when project conventions change.
- Prefer existing workflows: `npm --prefix frontend run build` is the standard frontend check; backend currently has no automated test suite beyond startup validation.
- When touching both backend and frontend, keep changes scoped to their respective folders and document any cross-service contracts in code comments or schemas.
- Keep documentation language consistent with the existing mix of Polish and English already present in the repo.
- App is suing podman for containerization and podman-compose for orchestration.
- Allways test at the end app localy. Use podman-compose to start the app and check if it works. If it doesn't, fix the issue and repeat the process. 