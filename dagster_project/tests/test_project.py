# dagster_project/tests/test_project.py


def test_import_assets_module() -> None:
    """
    Smoke test: assets module imports without errors.
    """
    import credit_card_pipeline_dagster.assets as assets  # noqa: F401


def test_import_definitions_module() -> None:
    """
    Smoke test: definitions module imports and exposes defs.
    """
    from credit_card_pipeline_dagster.definitions import defs  # type: ignore[import]

    assert defs is not None
