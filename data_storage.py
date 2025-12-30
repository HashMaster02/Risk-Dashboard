import sqlite3
import threading
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

DB_PATH = "investment_data.db"

class DatabaseManager:
    """Thread-safe database manager for investment data"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
        try:
            yield self._local.connection
        except Exception as e:
            self._local.connection.rollback()
            raise e

    def _init_db(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    atr REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_timestamp
                ON investment_data(symbol, timestamp DESC)
            """)
            conn.commit()

    def insert_data(self, symbol: str, price: float, atr: float) -> bool:
        """Insert new investment data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO investment_data (symbol, price, atr)
                    VALUES (?, ?, ?)
                """, (symbol, price, atr))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False

    def get_latest_data_per_symbol(self) -> List[Dict]:
        """Get the most recent data for each symbol"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    WITH ranked_data AS (
                        SELECT
                            symbol,
                            price,
                            atr,
                            timestamp,
                            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY timestamp DESC) as rn
                        FROM investment_data
                    )
                    SELECT symbol, price, atr, timestamp
                    FROM ranked_data
                    WHERE rn = 1
                    ORDER BY timestamp DESC
                """)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def get_all_data(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all data with optional limit"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT symbol, price, atr, timestamp FROM investment_data ORDER BY timestamp DESC"
                if limit:
                    query += f" LIMIT {limit}"
                cursor.execute(query)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching all data: {e}")
            return []

# Singleton instance
db_manager = DatabaseManager()
