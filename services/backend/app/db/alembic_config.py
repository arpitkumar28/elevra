"""Helpers for passing database URLs through Alembic configuration."""

def escape_alembic_config_value(value: str) -> str:
    """Escape ConfigParser markers while preserving the original database URL.

    Percent-encoded credentials are valid SQLAlchemy URLs, but Alembic
    Config.set_main_option uses ConfigParser interpolation and rejects bare
    percent signs. Doubling them here lets ConfigParser restore the URL when
    the option is read back.
    """
    return value.replace("%", "%%")
