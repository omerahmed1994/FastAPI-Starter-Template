"""Backward-compatible re-exports for database utilities.

The new canonical module is `app.core.database`. This file exists so
older imports like `from app.core.db import engine` continue to work.
"""

from app.core.database import engine, init_db  # noqa: F401

