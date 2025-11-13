from pathlib import Path
from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets, DbtProject

# Point to your dbt project
DBT_PROJECT_PATH = Path(__file__).joinpath("..", "..", "..", "dbt_project").resolve()
dbt_project = DbtProject(project_dir=DBT_PROJECT_PATH)

@dbt_assets(manifest=dbt_project.manifest_path)
def fraud_detection_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """
    Exposes all dbt models as Dagster assets.
    Each model (stg_raw_transactions, int_transaction_features, fraud_risk_scores)
    becomes an individual asset that can be orchestrated.
    """
    yield from dbt.cli(["build"], context=context).stream()
