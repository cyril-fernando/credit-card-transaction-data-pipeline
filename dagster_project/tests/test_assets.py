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
    asset_specs = list(defs.get_all_asset_specs())
    assert asset_specs, "No assets registered in Definitions"


def test_credit_card_pipeline_job_registered() -> None:
    """
    Sanity: Main credit card pipeline job is present in Definitions.
    """
    job_names = {job_def.name for job_def in defs.get_all_job_defs()}

    expected_job_name = "credit_card_pipeline"
    assert expected_job_name in job_names, f"{expected_job_name} not found in Definitions"


def test_daily_schedule_registered() -> None:
    """
    Sanity: Daily pipeline schedule is present in Definitions.
    """
    schedule_names = {schedule_def.name for schedule_def in defs.get_all_schedule_defs()}

    expected_schedule_name = "daily_pipeline_schedule"
    assert (
        expected_schedule_name in schedule_names
    ), f"{expected_schedule_name} not found in Definitions"
