#!/bin/bash
set -e

# 1. Credential Validation
# Ensures the Google Service Account key is present in the container environment.
# This prevents the pipeline from failing later during BigQuery authentication.
if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "ERROR: Google Cloud credentials not found at path: $GOOGLE_APPLICATION_CREDENTIALS"
    echo "Ensure the file is mapped correctly via Docker volume mounts."
    exit 1
fi

# 2. Dependency Installation
# Installs dbt project dependencies defined in packages.yml.
echo "Installing dbt dependencies..."
cd /opt/dagster/app/dbt_project
dbt deps > /dev/null

# 3. Manifest Compilation
# Compiles the dbt project to generate the 'manifest.json' artifact.
# Dagster requires this artifact to build the asset graph at runtime.
echo "Compiling dbt manifest..."
dbt compile

# 4. Execution
# Transfers control to the Dagster process.
# 'exec' ensures Dagster becomes PID 1, handling signal propagation correctly.
echo "Initializing Dagster webserver..."
cd /opt/dagster/app/dagster_project
exec dagster dev -h 0.0.0.0 -p 3000 -m credit_card_pipeline_dagster.definitions
