from dataclasses import dataclass
import json
from ausbills.parliament.federal import BillFed, BillMetaFed
import db
import staging

DB_FILE = 'staging2.db'


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

    @staticmethod
    def from_old(bill: staging.Bill):
        j = json.loads(bill.all_data)
        bill.id = j['id']
        return Bill(**bill.__dict__)


def wipe():
    db.drop(DB_FILE)
    con, cur = db.connect(DB_FILE)
    cur.execute('CREATE TABLE IF NOT EXISTS bill(id text, title text, link text, summary text, all_data json, error text)')
    con.commit()


def load_bill(id: str) -> Bill:
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT id, title, link, summary, error, all_data FROM bill WHERE id=?', (id,))
    rows = cur.fetchall()
    if len(rows) == 0:
        return None
    if len(rows) > 1:
        raise Exception(f'expected 1 row for id={id}, got {len(rows)}')
    row = rows[0]
    return Bill(*row)


def save_bill(bill: Bill):
    con, cur = db.connect(DB_FILE)
    cur.execute('INSERT INTO bill(id, title, link, summary, error, all_data) VALUES(?, ?, ?, ?, ?, ?)',
                (bill.id, bill.title, bill.link, bill.summary, bill.error, bill.all_data)
                )
    con.commit()


def delete_bill(id: str):
    con, cur = db.connect(DB_FILE)
    cur.execute('DELETE FROM bill WHERE id=?', (id,))
    con.commit()


def load_bills():
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT id, title, link, summary, error, all_data FROM bill')
    rows = cur.fetchall()
    return [Bill(*row) for row in rows]
