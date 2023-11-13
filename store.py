import json
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
    summary: str
    house: str
    passed_house: bool
    passed_senate: bool
    sponsor: str

    @staticmethod
    def from_staging(bill: staging2.Bill):
        b2 = bill.__dict__
        js = json.loads(bill.all_data)
        def j(key): return js[key] if key in js else None
        del(b2['all_data'])
        del(b2['error'])
        b2['house'] = j('house')
        b2['passed_house'] = bool(j('passed_house'))
        b2['passed_senate'] = bool(j('passed_senate'))
        b2['sponsor'] = j('sponsor')
        return Bill(**b2)


def wipe():
    db.drop(DB_FILE)
    con, cur = db.connect(DB_FILE)
    cur.execute('CREATE TABLE IF NOT EXISTS bill('
                'id text unique, title text, link text, summary text, house text, '
                'passed_house boolean, passed_senate boolean, sponsor text, embedding blob)')
    con.commit()


def save_bill(bill: Bill):
    con, cur = db.connect(DB_FILE)
    cur.execute('INSERT INTO bill(id, title, link, summary, house, passed_house, '
                'passed_senate, sponsor) VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                (bill.id, bill.title, bill.link, bill.summary, bill.house, bill.passed_house,
                 bill.passed_senate, bill.sponsor)
                )
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
