import time
from dagster import sensor, RunRequest, SensorEvaluationContext, SkipReason
from pathlib import Path
from dagster import (
    Definitions,
    ScheduleDefinition,
    AssetSelection,
    define_asset_job,
    EnvVar,
)
from dagster_dbt import DbtCliResource
from .assets import fraud_detection_dbt_assets, dbt_project

# Point to your dbt profiles directory
DBT_PROFILES_DIR = Path.home() / ".dbt"

# Define a job for running all dbt assets
fraud_detection_job = define_asset_job(
    name="fraud_detection_refresh",
    selection=AssetSelection.all(),
    description="Runs all fraud detection dbt models and tests",
)

# Schedule: Daily refresh at 2am Singapore time
daily_fraud_refresh = ScheduleDefinition(
    name="daily_fraud_refresh",
    job=fraud_detection_job,
    cron_schedule="0 2 * * *",  # 2am daily
    execution_timezone="Asia/Singapore",
    description="Automatically refreshes fraud risk scores daily at 2am",
)

# Schedule: Weekly full refresh on Sundays at 3am
weekly_full_refresh = ScheduleDefinition(
    name="weekly_full_refresh",
    job=fraud_detection_job,
    cron_schedule="0 3 * * 0",  # 3am on Sundays
    execution_timezone="Asia/Singapore",
    description="Weekly full rebuild of all models",
)

# Sensor: Check for data freshness every 5 minutes
@sensor(
    name="fraud_detection_sensor",
    job=fraud_detection_job,
    minimum_interval_seconds=300,  # Check every 5 minutes
)




def fraud_data_freshness_sensor(context: SensorEvaluationContext):
    """
    Sensor that checks if raw data needs refresh.
    In production, this would check GCS bucket or BigQuery table timestamp.
    For demo, we'll use a simple time-based trigger.
    """
    # Get last run timestamp from cursor
    last_run = float(context.cursor) if context.cursor else 0
    current_time = time.time()  # ← FIXED: Use Python's time module
    
    # Calculate hours since last run
    hours_since_last_run = (current_time - last_run) / 3600
    
    if hours_since_last_run > 6:
        # Update cursor with current time
        context.update_cursor(str(current_time))
        
        # Trigger the job
        return RunRequest(
            run_key=f"sensor_run_{int(current_time)}",
            tags={"source": "sensor", "trigger": "freshness_check"}
        )
    
    # Skip if run recently
    return SkipReason(f"Last run was {hours_since_last_run:.1f} hours ago (threshold: 6 hours)")



# Definitions - register everything
defs = Definitions(
    assets=[fraud_detection_dbt_assets],
    jobs=[fraud_detection_job],
    schedules=[daily_fraud_refresh, weekly_full_refresh],
    sensors=[fraud_data_freshness_sensor],  
    resources={
        "dbt": DbtCliResource(
            project_dir=dbt_project,
            profiles_dir=DBT_PROFILES_DIR
        )
    }
)

