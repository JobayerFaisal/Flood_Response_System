import sqlite3
from datetime import datetime


class PersistentStore:

    def __init__(self, db_path="learning_memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mission_lifecycle (
            volunteer_id TEXT,
            mission_id TEXT,
            status TEXT,
            timestamp TEXT
        )
        """)

        self.conn.commit()

    def record_lifecycle(self, volunteer_id: str, mission_id: str, status: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO mission_lifecycle VALUES (?, ?, ?, ?)",
            (volunteer_id, mission_id, status, datetime.utcnow().isoformat())
        )
        self.conn.commit()


    def record_outcome(self, volunteer_id: str, outcome: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO volunteer_performance VALUES (?, ?, ?)",
            (volunteer_id, datetime.utcnow().isoformat(), outcome)
        )
        self.conn.commit()

    def get_history(self, volunteer_id: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT timestamp, outcome FROM volunteer_performance WHERE volunteer_id=?",
            (volunteer_id,)
        )
        return cursor.fetchall()
    
    def get_lifecycle_history(self, volunteer_id: str):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT mission_id, status, timestamp
            FROM mission_lifecycle
            WHERE volunteer_id = ?
            ORDER BY timestamp ASC
            """,
            (volunteer_id,)
        )
        return cursor.fetchall()