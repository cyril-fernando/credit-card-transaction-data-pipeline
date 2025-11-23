# Establish Runtime. Uses Python 3.11-slim to balance image size with library compatibility.
FROM python:3.11-slim

# System Dependencies. Installs Git required for dbt package management; cleans apt cache to minimize image footprint.
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Root Context. Defines the primary working directory for the application payload.
WORKDIR /opt/dagster/app

# Dependency Layer. Installs Python libraries. Ordered before source copy to leverage Docker layer caching for faster rebuilds.
COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Source Replication. Copies the full project repository. Relies on .dockerignore to exclude sensitive credentials and build artifacts.
COPY . .

# Instance Configuration. Configures DAGSTER_HOME and seeds the dagster.yaml settings file to enable persistent storage connections.
ENV DAGSTER_HOME=/opt/dagster/dagster_home
RUN mkdir -p $DAGSTER_HOME && cp dagster_project/dagster.yaml $DAGSTER_HOME/dagster.yaml

# Context Alignment. Shifts working directory to the Dagster project root to mirror local development paths and resolve imports correctly.
WORKDIR /opt/dagster/app/dagster_project

# Network Exposure. Exposes the standard Dagster webserver port for host mapping.
EXPOSE 3000

# Entrypoint Configuration. Grants execution permissions to the startup script.
# This script handles credential validation and dbt compilation before runtime.
RUN chmod +x /opt/dagster/app/scripts/start.sh

# Execution Entrypoint. Launches the startup script to initialize the pipeline environment.
CMD ["/opt/dagster/app/scripts/start.sh"]
