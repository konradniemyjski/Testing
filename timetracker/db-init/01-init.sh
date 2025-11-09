
#!/bin/sh
set -e
echo ">>> Running 01-init.sh: creating useful extensions and defaults"
# Example: enable UUIDs (not required by your current schema)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL
echo ">>> 01-init.sh finished"
