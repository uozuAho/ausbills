from dataclasses import dataclass
import json
from ausbills.parliament.federal import BillFed, BillMetaFed
import db

DB_FILE = 'staging.db'


@dataclass
class Bill:
    id: str
    title: str
    link: str
    summary: str
    error: str
    all_data: str  # json blob of all bill data

    @staticmethod
    def from_meta(meta: BillMetaFed):
        all_data = json.dumps(meta.__dict__, indent=2)
        return Bill(meta.id, meta.title, meta.link, None, None, all_data=all_data)

    @staticmethod
    def from_fed_bill(bill: BillFed):
        return Bill(bill.id, bill.title, bill.link, bill.summary, error=None, all_data=bill.asJson())


def wipe():
    db.drop(DB_FILE)
    con, cur = db.connect(DB_FILE)
    cur.execute('CREATE TABLE IF NOT EXISTS bill(title text, link text, summary text, all_data json, error text)')
    con.commit()


def save_bill(bill: Bill):
    con, cur = db.connect(DB_FILE)
    cur.execute('INSERT INTO bill(title, link, summary, error, all_data) VALUES(?, ?, ?, ?, ?)',
                (bill.title, bill.link, bill.summary, bill.error, bill.all_data)
                )
    con.commit()


def load_bill(title: str) -> Bill:
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT title, link, summary, error, all_data FROM bill WHERE title=?', (title,))
    rows = cur.fetchall()
    if len(rows) == 0:
        return None
    if len(rows) > 1:
        raise Exception(f'expected 1 row for title={title}, got {len(rows)}')
    row = rows[0]
    all_data = json.loads(row[4])
    id = all_data['id'] if 'id' in all_data else None
    return Bill(id, *row)


def delete_bill(title: str):
    con, cur = db.connect(DB_FILE)
    cur.execute('DELETE FROM bill WHERE title=?', (title,))
    con.commit()


def load_bills():
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT title, link, summary, error, all_data FROM bill')
    rows = cur.fetchall()
    return [Bill(None, *row) for row in rows]
