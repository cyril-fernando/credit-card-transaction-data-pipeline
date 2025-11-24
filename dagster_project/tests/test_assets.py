"""
Structural smoke tests for Dagster Definitions.

Goal:
- Confirm that the repository exposes assets, jobs, and schedules.
- Catch wiring regressions when assets or jobs are renamed or removed.
"""

from credit_card_pipeline_dagster.definitions import defs
from dagster import Definitions


def test_defs_is_definitions_instance() -> None:
    """
    Sanity: defs object is a Dagster Definitions instance.
    """
    assert isinstance(defs, Definitions)


def test_defs_exposes_assets() -> None:
    """
    Sanity: Definitions object has at least one asset registered.
    """
    asset_specs = list(defs.resolve_all_asset_specs())
    assert asset_specs, "No assets registered in Definitions"


def test_credit_card_pipeline_job_registered() -> None:
    """
    Sanity: Main credit card pipeline job is present in Definitions.
    """
    job = defs.get_job_def("credit_card_pipeline")
    assert job is not None, "credit_card_pipeline job not found in Definitions"
    assert job.name == "credit_card_pipeline"


def test_daily_schedule_registered() -> None:
    """
    Sanity: Daily pipeline schedule is present in Definitions.
    """
    schedule = defs.get_schedule_def("credit_card_pipeline_schedule")
    assert schedule is not None, "credit_card_pipeline_schedule not found in Definitions"
    assert schedule.name == "credit_card_pipeline_schedule"
