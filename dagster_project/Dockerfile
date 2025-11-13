FROM python:3.13-slim

WORKDIR /opt/dagster/app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*


COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY dbt_project /opt/dagster/dbt_project
COPY dagster_project /opt/dagster/dagster_project

ENV DAGSTER_HOME=/opt/dagster/dagster_home
RUN mkdir -p $DAGSTER_HOME

WORKDIR /opt/dagster/dagster_project

EXPOSE 3000

# Create an entrypoint script that runs dbt build before starting Dagste
CMD ["sh", "-c", "cd /opt/dagster/dbt_project && dbt build --profiles-dir /opt/dagster/.dbt && cd /opt/dagster/dagster_project && dagster dev -h 0.0.0.0 -p 3000"]
