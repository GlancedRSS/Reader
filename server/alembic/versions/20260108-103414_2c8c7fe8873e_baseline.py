"""baseline

Revision ID: 2c8c7fe8873e
Revises:
Create Date: 2026-01-08 10:34:14.392091+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "2c8c7fe8873e"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

from pathlib import Path  # noqa: E402


def upgrade() -> None:
    """Upgrade schema - run raw SQL files in order."""
    versions_dir = Path(__file__).parent
    alembic_dir = versions_dir.parent
    baseline_dir = alembic_dir / "baseline"

    sql_files = [
        "000_schemas.sql",
        "010_helpers.sql",
        "020_accounts.sql",
        "030_content.sql",
        "040_personalization.sql",
        "050_management.sql",
        "060_security.sql",
    ]

    for sql_file in sql_files:
        sql_path = baseline_dir / sql_file
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_path}")

        with open(sql_path, encoding="utf-8") as f:
            sql = f.read()

        op.execute(sa.text(sql))

        print(f"Executed {sql_file}")


def downgrade() -> None:
    """Downgrade schema - drop all schemas."""
    op.execute("DROP SCHEMA IF EXISTS management CASCADE")
    op.execute("DROP SCHEMA IF EXISTS personalization CASCADE")
    op.execute("DROP SCHEMA IF EXISTS content CASCADE")
    op.execute("DROP SCHEMA IF EXISTS accounts CASCADE")
    op.execute("DROP SCHEMA IF EXISTS extensions CASCADE")
