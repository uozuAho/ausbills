import struct
import db
from dataclasses import dataclass

from typing import List

import staging2

DB_FILE = 'fedbills.db'


@dataclass
class Bill:
    id: str
    title: str
    link: str
    summary: str | None = None
    status: str | None = None
    parliament: str | None = None
    house: str | None = None
    passed_house: bool = False
    passed_senate: bool = False
    sponsor: str | None = None

    @classmethod
    def from_dict(cls, d: dict):
        keys = cls.__annotations__.keys()
        kvs = {k: d[k] for k in keys if k in d}
        return Bill(**kvs)

    @staticmethod
    def from_staging(bill: staging2.Bill):
        return Bill.from_dict(bill.data)


def wipe():
    db.drop(DB_FILE)
    con, cur = db.connect(DB_FILE)
    cur.execute('CREATE TABLE IF NOT EXISTS bill('
                '_id integer primary key autoincrement, id text unique, title text, '
                'link text, summary text, status text, parliament text, house text, '
                'passed_house boolean, passed_senate boolean, '
                'sponsor text, embedding blob)')
    con.commit()


def save_bill(bill: Bill):
    con, cur = db.connect(DB_FILE)
    bill_dict = bill.__dict__
    fieldnames = ', '.join(bill_dict.keys())
    placeholders = ', '.join(['?'] * len(bill_dict))
    values = tuple(bill_dict.values())
    cur.execute(f'INSERT INTO bill({fieldnames}) VALUES({placeholders})', values)
    con.commit()


def load_bills():
    con, cur = db.connect()
    cur.execute('SELECT title, summary, embedding FROM bill')
    return cur.fetchall()


def save_bill_embedding(title, embedding: List[float]):
    con, cur = db.connect()
    cur.execute('UPDATE bill SET embedding = ? where title = ?',
                (emb_encode(embedding), title)
                )
    con.commit()


def emb_encode(values):
    return struct.pack("<" + "f" * len(values), *values)


def emb_decode(binary):
    return struct.unpack("<" + "f" * (len(binary) // 4), binary)
