
# Worklog Compose Setup

Struktura:
.
├── docker-compose.yml
├── db-init/
│   ├── 01-init.sh
│   └── 02-schema.sql
├── worklog-backend-auth-put-delete/       # wklej tutaj kod backendu z Dockerfile
└── worklog-frontend-logout-register/      # wklej tutaj kod frontendu z Dockerfile

Uruchomienie (podman/doker):
  podman-compose up --build
  # lub
  docker compose up --build

Uwaga:
- Skrypty w db-init/ odpalą się tylko przy pierwszym starcie bazy (gdy pgdata jest puste).
- Jeżeli masz własny skrypt .sh z repo, skopiuj go do db-init/ i upewnij się, że ma chmod +x.
- Backend wymaga dependency do Postgresa w pom.xml (org.postgresql:postgresql).
