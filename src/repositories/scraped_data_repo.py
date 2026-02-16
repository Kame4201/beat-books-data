"""
Repository for handling scraped data operations.

This repository handles:
1. Tracking scraped data metadata
2. Dynamic table creation for scraped data
3. Idempotent upserts of scraped data
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect, Inspector
from typing import List

from src.entities.scraped_data import ScrapedData
from src.repositories.base_repo import BaseRepository
from src.dtos.scraped_data_dto import ScrapedDataMetadataCreate


class ScrapedDataRepository(BaseRepository[ScrapedData]):
    """
    Repository for scraped data operations.

    Extends BaseRepository for metadata tracking and adds methods
    for dynamic table creation and data insertion.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=ScrapedData)

    def create_metadata_table_if_not_exists(self) -> None:
        """
        Create the scraped_data_metadata table if it doesn't exist.

        This table tracks what URLs have been scraped and when.
        """
        bind = self.session.bind
        assert bind is not None, "Session is not bound to an engine"
        inspector = inspect(bind)
        if not isinstance(inspector, Inspector):
            raise RuntimeError("Expected an Inspector instance")
        if not inspector.has_table("scraped_data_metadata"):
            ScrapedData.metadata.create_all(bind)

    def track_scraped_data(self, metadata: ScrapedDataMetadataCreate) -> ScrapedData:
        """
        Record metadata about scraped data.

        Args:
            metadata: DTO containing scraped data metadata

        Returns:
            Created ScrapedData entity
        """
        entity = ScrapedData(
            source_url=metadata.source_url,
            table_id=metadata.table_id,
            table_name=metadata.table_name,
            scraped_at=metadata.scraped_at,
            season=metadata.season,
            entity_type=metadata.entity_type,
            table_type=metadata.table_type,
            rows_scraped=metadata.rows_scraped,
            source_type=metadata.source_type,
        )
        return self.create(entity, commit=True)

    def clean_identifier(self, name: str) -> str:
        """
        Clean a string to be used as a SQL identifier.

        Args:
            name: String to clean

        Returns:
            Cleaned identifier (alphanumeric and underscores only)
        """
        return "".join(c if c.isalnum() or c == "_" else "_" for c in str(name).lower())

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        bind = self.session.bind
        assert bind is not None, "Session is not bound to an engine"
        inspector = inspect(bind)
        assert isinstance(inspector, Inspector)
        return inspector.has_table(table_name)

    def create_dynamic_table(self, table_name: str, df: pd.DataFrame) -> None:
        """
        Dynamically create a database table based on DataFrame structure.

        Args:
            table_name: Name for the database table (will be cleaned)
            df: DataFrame to base table structure on

        Raises:
            Exception: If table creation fails
        """
        clean_table_name = self.clean_identifier(table_name)

        # Check if table already exists
        if self.table_exists(clean_table_name):
            return  # Table already exists, skip creation

        # Build column definitions
        columns = ["id SERIAL PRIMARY KEY"]

        for col in df.columns:
            clean_col = self.clean_identifier(col)

            # Determine data type based on pandas dtype
            dtype = df[col].dtype
            if pd.api.types.is_integer_dtype(dtype):
                sql_type = "INTEGER"
            elif pd.api.types.is_float_dtype(dtype):
                sql_type = "FLOAT"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                sql_type = "TIMESTAMP"
            else:
                sql_type = "TEXT"

            columns.append(f"{clean_col} {sql_type}")

        # Create table
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {clean_table_name} (
            {', '.join(columns)}
        )
        """

        try:
            self.session.execute(text(create_sql))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Could not create table {clean_table_name}: {e}")

    def delete_by_source_url(self, table_name: str, source_url: str) -> int:
        """
        Delete rows from a table by source URL (for idempotent upserts).

        Args:
            table_name: Name of the table
            source_url: Source URL to delete

        Returns:
            Number of rows deleted
        """
        clean_table_name = self.clean_identifier(table_name)

        # Check if table has source_url column
        bind = self.session.bind
        assert bind is not None, "Session is not bound to an engine"
        inspector = inspect(bind)
        assert isinstance(inspector, Inspector)
        if not inspector.has_table(clean_table_name):
            return 0
        columns = [col["name"] for col in inspector.get_columns(clean_table_name)]
        if "source_url" not in columns:
            return 0

        try:
            delete_sql = text(f"DELETE FROM {clean_table_name} WHERE source_url = :url")
            result = self.session.execute(delete_sql, {"url": source_url})
            self.session.commit()
            return result.rowcount
        except Exception as e:
            self.session.rollback()
            print(f"Warning: Could not delete from {clean_table_name}: {e}")
            return 0

    @staticmethod
    def _convert_value(val):
        """Convert a pandas/numpy value to a native Python type for DB insertion."""
        # Check for NaN/None
        try:
            if val is None:
                return None
            is_na = pd.isna(val)
            if isinstance(is_na, (bool, np.bool_)) and is_na:
                return None
        except (ValueError, TypeError):
            pass

        if isinstance(val, (np.integer,)):
            return int(val)
        if isinstance(val, (np.floating,)):
            f = float(val)
            return None if pd.isna(f) else f
        if isinstance(val, (np.bool_,)):
            return bool(val)
        if isinstance(val, pd.Timestamp):
            return val.to_pydatetime()
        if isinstance(val, (str, int, float, bool)):
            return val
        return str(val)

    def insert_dataframe_rows(self, table_name: str, df: pd.DataFrame) -> int:
        """
        Insert DataFrame rows into database table.

        Args:
            table_name: Target table name
            df: DataFrame to insert

        Returns:
            Number of rows inserted

        Raises:
            Exception: If insertion fails
        """
        clean_table_name = self.clean_identifier(table_name)
        rows_inserted = 0

        for _, row in df.iterrows():
            # Clean column names and prepare values
            clean_cols = []
            values = []
            placeholders = []

            for idx, (col, val) in enumerate(row.items()):
                clean_col = self.clean_identifier(col)
                clean_cols.append(clean_col)
                placeholders.append(f":val{idx}")

                # Convert value to a native Python type
                converted = self._convert_value(val)
                values.append(converted)

            # Build and execute insert statement
            insert_sql = text(f"""
                INSERT INTO {clean_table_name} ({', '.join(clean_cols)})
                VALUES ({', '.join(placeholders)})
            """)

            params = {f"val{idx}": val for idx, val in enumerate(values)}

            try:
                self.session.execute(insert_sql, params)
                rows_inserted += 1
            except Exception as e:
                self.session.rollback()
                print(f"Warning: Could not insert row into {clean_table_name}: {e}")
                continue

        self.session.commit()
        return rows_inserted

    def upsert_dataframe(self, table_name: str, df: pd.DataFrame) -> int:
        """
        Insert or update DataFrame rows into database table.

        Uses a delete-then-insert strategy for idempotent runs:
        1. Delete existing rows with same source_url
        2. Insert new rows

        Args:
            table_name: Target table name
            df: DataFrame to upsert

        Returns:
            Number of rows inserted
        """
        # Delete existing rows from same source_url(s)
        if "source_url" in df.columns:
            source_urls = df["source_url"].unique()
            for source_url in source_urls:
                self.delete_by_source_url(table_name, source_url)

        # Insert new rows
        return self.insert_dataframe_rows(table_name, df)

    def get_scraped_metadata_by_url(self, source_url: str) -> List[ScrapedData]:
        """
        Get all scraped data metadata for a specific URL.

        Args:
            source_url: URL to search for

        Returns:
            List of ScrapedData entities
        """
        from sqlalchemy import select

        stmt = select(ScrapedData).where(ScrapedData.source_url == source_url)
        return list(self.session.execute(stmt).scalars().all())

    def get_all_scraped_metadata(self, limit: int = 100) -> List[ScrapedData]:
        """
        Get all scraped data metadata records.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of ScrapedData entities
        """
        return self.list(limit=limit)
