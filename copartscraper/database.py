import sqlite3
from typing import List, Tuple
from .models import LotData, CarCondition

class CopartDatabase:
    def __init__(self, db_path: str = "CarsDatabase.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        """Create the LotData table if it does not exist."""
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS LotData (
                image_id TEXT,
                lot_url TEXT,
                id INTEGER PRIMARY KEY,
                name TEXT,
                odometer TEXT,
                conditions TEXT,
                auction TEXT,
                start_date TEXT,
                last_check TEXT,
                current_bid TEXT,
                buy_now TEXT
            )
        """)
        self.conn.commit()

    def fetch_all_ids(self) -> List[int]:
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM LotData")
        return [row[0] for row in cur.fetchall()]

    def fetch_lot(self, lot_id: int) -> LotData | None:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT image_id, lot_url, id, name, odometer, conditions,
                auction, start_date, current_bid, buy_now
            FROM LotData
            WHERE id = ?
            """,
            (lot_id,),
        )
        row = cur.fetchone()
        return self._row_to_lot(row) if row else None

    def delete_lot(self, lot_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM LotData WHERE id = ?", (lot_id,))
        self.conn.commit()

    def insert_lot(self, lot: LotData) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO LotData (
                image_id, lot_url, id, name, odometer,
                conditions, auction, start_date,
                last_check, current_bid, buy_now
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lot.image_id,
                lot.lot_url,
                lot.id,
                lot.name,
                lot.odometer,
                str(lot.conditions),
                lot.auction,
                lot.start_date,
                lot.last_check,
                lot.current_bid,
                lot.buy_now,
            ),
        )
        self.conn.commit()

    def _row_to_lot(self, row: tuple) -> LotData:
        return LotData(
            image_id=row[0],
            lot_url=row[1],
            id=row[2],
            name=row[3],
            odometer=row[4],
            conditions=CarCondition.from_str(row[5]),
            auction=row[6],
            start_date=row[7],
            last_check=None,
            current_bid=row[8],
            buy_now=row[9],
        )

    def close(self):
        self.conn.close()