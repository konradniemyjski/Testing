
# Worklog Compose Setup

Struktura:
.
├── docker-compose.yml
├── db-init/
│   ├── 01-init.sh
│   └── 02-schema.sql
├── backend/                               # FastAPI backend (Python)
└── frontend/                              # Nuxt 3 frontend (Vue)

Uruchomienie (podman/doker):
  podman-compose up --build
  # lub
  docker compose up --build

Uwaga:
- Skrypty w db-init/ odpalą się tylko przy pierwszym starcie bazy (gdy pgdata jest puste).
- Jeżeli masz własny skrypt .sh z repo, skopiuj go do db-init/ i upewnij się, że ma chmod +x.
- Backend korzysta z Python + FastAPI i oczekuje zmiennej środowiskowej `DATABASE_URL` wskazującej na Postgresa.
