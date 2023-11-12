import struct
import db
from dataclasses import dataclass

from typing import List

DB_FILE = 'fedbills.db'

def wipe():
    db.drop(DB_FILE)
    con, cur = db.connect(DB_FILE)
    cur.execute('CREATE TABLE IF NOT EXISTS bill_meta(title text, link text, parliament text)')
    cur.execute('CREATE TABLE IF NOT EXISTS bill(title text, link text, summary text, embedding blob)')
    con.commit()


def save_bill_meta(meta):
    con, cur = db.connect()
    cur.execute('INSERT INTO bill_meta(title, link, parliament) VALUES(?, ?, ?)',
                (meta.title, meta.link, meta.parliament)
                )
    con.commit()


def save_bill(bill):
    con, cur = db.connect()
    cur.execute('INSERT INTO bill(title, link, summary) VALUES(?, ?, ?)',
                (bill.title, bill.link, bill.summary)
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