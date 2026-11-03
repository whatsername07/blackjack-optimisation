import duckdb
import polars as pl
from typing import List, Dict, Any
import os

class DatabaseManager:
    """ Manages DuckDB connections, schema enforcement, and batch telemetry ingestion. """

    def __init__(self, db_path: str = "data/processed/blackjack_sim.db"):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Connect to duckDB (creates file if it does not exist)
        self.conn = duckdb.connect(db_path)
        self._initialise_schema()

    def _initialise_schema(self) -> None:
        """ Creates the needed relational tables if they do not exist. """
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS rounds (
                run_id UUID DEFAULT uuid(),
                round_id INTEGER,
                strategy_name VARCHAR,
                bet_amount DOUBLE,
                net_payout DOUBLE,
                cumulative_bankroll DOUBLE,
                -- Extended telemetry for SQL analytics
                player_total INTEGER,
                is_soft BOOLEAN,
                dealer_upcard INTEGER,
                true_count DOUBLE
            );
        """)

        self.conn.execute(""" 
            CREATE TABLE IF NOT EXISTS actions (
                round_id INTEGER,
                step_index INTEGER,
                action_taken VARCHAR,
                resulting_total INTEGER
            );
        """)

    def insert_rounds_batch(self, batch: List[Dict[str, Any]]) -> None:
        """
        High-speed bulk insertion of round telemetry.
        Converts the list of dictionaries to a Polars DataFrame for optimal DuckDB ingestion.
        """
        # If the batch is empty, there's nothing to insert
        if not batch:
            return

        # Convert the list of dictionaries to a Polars DataFrame
        df = pl.DataFrame(batch)

        # Use DuckDB's ability to ingest Polars DataFrames directly for efficient batch insertion
        self.conn.execute("""
            INSERT INTO rounds(
                round_id, strategy_name, bet_amount, net_payout, cumulative_bankroll
            )
            SELECT
                round_id, strategy_name, bet_amount, net_payout, cumulative_bankroll
            FROM df
        """)

    def query_to_df(self, query: str) -> pl.DataFrame:
        """ Executes a SQL query and returns the result as a Polars DataFrame. """
        return self.conn.execute(query).fetch_df().to_polars()

    def close(self) -> None:
        """ Closes the database connection safely. """
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()