import sqlite3
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
    with open('store_schema.sql') as f:
        cur.executescript(f.read())
    con.commit()


def save_bill(bill: Bill):
    con, cur = db.connect(DB_FILE)
    bill_dict = bill.__dict__
    fieldnames = ', '.join(bill_dict.keys())
    placeholders = ', '.join(['?'] * len(bill_dict))
    values = tuple(bill_dict.values())
    cur.execute(f'INSERT INTO bill({fieldnames}) VALUES({placeholders})', values)
    con.commit()


def load_bills() -> List[Bill]:
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('SELECT * from bill')
    while row := cur.fetchone():
        yield Bill.from_dict(dict(row))


def has_embedding(id):
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT count(*) from bill_summary_embedding where bill_id = ?', (id,))
    return cur.fetchone()[0] > 0


def set_bill_summary_embedding(id, embedding: List[float]):
    con, cur = db.connect(DB_FILE)
    emb_bytes = emb_encode(embedding)
    params = {'bill_id': id, 'embedding': emb_bytes}
    cur.execute(
        'insert into bill_summary_embedding (bill_id, embedding) '
        'values (:bill_id, :embedding) '
        'on conflict (bill_id) do update set embedding = :embedding',
        params)
    con.commit()


# def load_similar_bills()
#     embedder = Embedder()
#     prompt_emb = embedder.embed(prompt)
#     bills = store.load_similar_bills(prompt_emb)
#     results = []
#     for bill bills:
#         if not embedding: continue
#         emb2 = store.emb_decode(embedding)
#         results.append((title, summary, embedder.similarity(prompt_emb, emb2)))
#     results.sort(key=lambda x: x[2], reverse=True)
#     return results[:5]


def emb_encode(values):
    return struct.pack("<" + "f" * len(values), *values)


def emb_decode(binary):
    return struct.unpack("<" + "f" * (len(binary) // 4), binary)
