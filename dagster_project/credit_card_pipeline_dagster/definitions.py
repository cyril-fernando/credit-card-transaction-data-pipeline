"""
Dagster definitions for credit card fraud detection pipeline.

Registers assets, jobs, schedules, and resources. This is the entry point
that Dagster loads when running 'dagster dev'.
"""
from dagster import AssetSelection, Definitions, ScheduleDefinition, define_asset_job
from dagster_dbt import DbtCliResource

from .assets import credit_card_dbt_assets, dbt_project, raw_transactions_table

# ============================================================================
# JOBS - Group assets into executable units
# ============================================================================

# Job that materializes all assets (Python ingestion + dbt transformations)
credit_card_pipeline = define_asset_job(
    name="credit_card_pipeline",
    selection=AssetSelection.all(),
)


# ============================================================================
# SCHEDULES - Automate job execution
# ============================================================================

# Run complete pipeline daily at 2am Singapore time
daily_pipeline_schedule = ScheduleDefinition(
    job=credit_card_pipeline,
    cron_schedule="0 2 * * *",
    execution_timezone="Asia/Singapore",
)


# ============================================================================
# RESOURCES - External system connections
# ============================================================================

# dbt CLI resource for executing dbt commands
resources = {
    "dbt": DbtCliResource(project_dir=dbt_project),
}


# ============================================================================
# DEFINITIONS - Register everything with Dagster
# ============================================================================

defs = Definitions(
    assets=[raw_transactions_table, credit_card_dbt_assets],
    jobs=[credit_card_pipeline],
    schedules=[daily_pipeline_schedule],
    resources=resources,
)
