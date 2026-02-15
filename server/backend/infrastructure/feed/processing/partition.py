"""Partition management service for database partition operations."""

import re
from datetime import UTC, datetime, timedelta
from typing import Any

import sqlalchemy.exc
import structlog
from sqlalchemy import text

from backend.utils.date_utils import parse_iso_datetime

logger = structlog.get_logger()

SCHEMA_NAME = "content"
TABLE_NAME = "articles"
TABLE_PREFIX = "articles_"
PARTITION_FORMAT = "%Y_%m"


class Partition:
    """Service for managing database partitions."""

    def __init__(self, db: Any) -> None:
        """Initialize the partition service.

        Args:
            db: Database session.

        """
        self.db = db

    async def analyze_and_create_partitions(
        self, articles_data: list[dict[str, Any]]
    ) -> set[str]:
        """Analyze article dates and create all necessary partitions before processing.

        Args:
            articles_data: List of article data dictionaries to analyze.

        Returns:
            Set of partition names that were created.

        """
        try:
            partition_check_sql = text(
                """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = :schema
                  AND table_name = :table_name
                  AND table_type = 'PARTITIONED TABLE'
            )
            """
            )
            result = await self.db.execute(
                partition_check_sql,
                {"schema": SCHEMA_NAME, "table_name": TABLE_NAME},
            )
            is_partitioned = result.scalar()

            if not is_partitioned:
                logger.info(
                    "Articles table is not partitioned - skipping partition creation"
                )
                return set()

        except (sqlalchemy.exc.SQLAlchemyError, ValueError) as e:
            logger.warning(
                f"Could not check if articles table is partitioned: {e}"
            )
            return set()

        partitions_to_create = set()
        created_partitions = set()

        for article_data in articles_data:
            published_date = parse_iso_datetime(
                article_data.get("published_at")
            )
            if published_date:
                partition_month = published_date.strftime(PARTITION_FORMAT)
                partitions_to_create.add(partition_month)
            else:
                current_month = datetime.now(UTC).strftime(PARTITION_FORMAT)
                partitions_to_create.add(current_month)

        current_month = datetime.now(UTC).strftime(PARTITION_FORMAT)
        next_month = (
            (datetime.now(UTC) + timedelta(days=32))
            .replace(day=1)
            .strftime(PARTITION_FORMAT)
        )
        partitions_to_create.add(current_month)
        partitions_to_create.add(next_month)

        for partition_month in partitions_to_create:
            if not re.match(r"^\d{4}_\d{2}$", partition_month):
                logger.warning(
                    f"Skipping invalid partition format: {partition_month}"
                )
                continue

            try:
                table_name = f"{TABLE_PREFIX}{partition_month}"

                partition_exists_sql = text(
                    """
                    SELECT EXISTS (
                        SELECT 1 FROM pg_tables
                        WHERE schemaname = :schema_name
                          AND tablename = :table_name
                    )
                """
                )

                result = await self.db.execute(
                    partition_exists_sql,
                    {"schema_name": SCHEMA_NAME, "table_name": table_name},
                )
                exists = result.scalar()

                if not exists:
                    async with self.db.begin():
                        start_date = datetime.strptime(
                            partition_month + "-01", "%Y_%m-%d"
                        )
                        end_date = (start_date + timedelta(days=32)).replace(
                            day=1
                        )

                        full_partition_name = f"{SCHEMA_NAME}.{table_name}"
                        full_table_name = f"{SCHEMA_NAME}.{TABLE_NAME}"

                        partition_sql = text(
                            f"""
                            CREATE TABLE {full_partition_name}
                            PARTITION OF {full_table_name}
                            FOR VALUES FROM (:start_date)
                            TO (:end_date)
                        """
                        )

                        await self.db.execute(
                            partition_sql,
                            {
                                "start_date": start_date.isoformat(),
                                "end_date": end_date.isoformat(),
                            },
                        )

                        created_partitions.add(partition_month)
                        logger.info(
                            "Pre-created partition", table_name=table_name
                        )

            except (sqlalchemy.exc.SQLAlchemyError, ValueError, TypeError) as e:
                logger.exception(
                    "Failed to pre-create partition",
                    partition_month=partition_month,
                    error=str(e),
                )

        if created_partitions:
            logger.info(
                "Pre-created partitions",
                count=len(created_partitions),
                partitions=sorted(created_partitions),
            )

        return created_partitions
