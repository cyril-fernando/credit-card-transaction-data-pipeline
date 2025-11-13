from pathlib import Path
from dagster import Definitions
from dagster_dbt import DbtCliResource
from .assets import fraud_detection_dbt_assets, dbt_project

# Point to your dbt profiles directory
DBT_PROFILES_DIR = Path.home() / ".dbt"

defs = Definitions(
    assets=[fraud_detection_dbt_assets],
    resources={
        "dbt": DbtCliResource(
            project_dir=dbt_project,
            profiles_dir=DBT_PROFILES_DIR
        )
    }
)
