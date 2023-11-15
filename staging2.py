from dataclasses import dataclass
import json
from ausbills.parliament.federal import BillFed, BillMetaFed
import db

DB_FILE = 'staging2.db'


@dataclass
class Bill:
    id: str
    data: dict
    error: str | None = None

    @staticmethod
    def from_meta(meta: BillMetaFed):
        return Bill(meta.id, meta.__dict__)

    @staticmethod
    def from_fed_bill(bill: BillFed):
        return Bill(bill.id, bill.__dict__)


def wipe():
    db.drop(DB_FILE)
    update_schema()


def update_schema():
    con, cur = db.connect(DB_FILE)
    with open('staging_schema.sql') as f:
        cur.executescript(f.read())
    con.commit()


def load_bill(id: str) -> Bill:
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT id, data, error FROM bill WHERE id=?', (id,))
    rows = cur.fetchall()
    if len(rows) == 0:
        return None
    if len(rows) > 1:
        raise Exception(f'expected 1 row for id={id}, got {len(rows)}')
    row = rows[0]
    return Bill(*row)


def save_bill(bill: Bill):
    con, cur = db.connect(DB_FILE)
    data_json = json.dumps(bill.data, indent=2)
    cur.execute('INSERT INTO bill(id, data, error) VALUES(?, ?, ?)',
                (bill.id, data_json, bill.error)
                )
    con.commit()


def delete_bill(id: str):
    con, cur = db.connect(DB_FILE)
    cur.execute('DELETE FROM bill WHERE id=?', (id,))
    con.commit()


def load_bills():
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT id, data, error FROM bill')
    rows = cur.fetchall()
    for row in rows:
        data = json.loads(row[1])
        yield Bill(row[0], data, row[2])


def has_short_summary(id):
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT count(*) from bill_summary_summary where bill_id = ?', (id,))
    return cur.fetchone()[0] > 0


def set_bill_short_summary(id, summary, error=None):
    con, cur = db.connect(DB_FILE)
    params = {'bill_id': id, 'summary': summary, 'error': error}
    cur.execute(
        'insert into bill_summary_summary (bill_id, summary, error) '
        'values (:bill_id, :summary, :error) '
        'on conflict (bill_id) do update set summary = :summary, error = :error',
        params)
    con.commit()
