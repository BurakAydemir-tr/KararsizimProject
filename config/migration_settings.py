"""Explicit management settings: --settings=config.migration_settings."""
from .settings import *  # noqa: F403
from .environment import database

DATABASES = {"default": database("DATABASE_MIGRATION_URL")}

