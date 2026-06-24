"""
=============================================
Migration: Add is_default column to bots table
=============================================

This migration adds the is_default column to track which bot is the default.

Usage:
    python migrations/add_default_bot_column.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.db.sqlite.models import get_engine


def migrate():
    """Run the migration"""
    engine = get_engine()

    # Check if column already exists
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(bots)"))
        columns = [row[1] for row in result]

        if "is_default" in columns:
            print("Column 'is_default' already exists in bots table. Migration skipped.")
            return

    # Add column
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE bots ADD COLUMN is_default BOOLEAN DEFAULT 0"))
        conn.commit()
        print("Column 'is_default' added to bots table successfully.")


if __name__ == "__main__":
    migrate()
