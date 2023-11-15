import sqlite3
import db
from dataclasses import dataclass

from typing import Iterable, List

import staging2
import llm_stuff


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
    update_schema()


def update_schema():
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


def load_bill(id: str):
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('SELECT * from bill where id = ?', (id,))
    rows = cur.fetchall()
    if not rows: raise Exception(f'no bill with id {id}')
    if len(rows) > 1: raise Exception(f'multiple bills with id {id}')
    return Bill.from_dict(dict(rows[0]))


def load_bills() -> Iterable[Bill]:
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


def set_bill_summary_embedding(id, embedding: llm_stuff.Embedding):
    con, cur = db.connect(DB_FILE)
    params = {'bill_id': id, 'embedding': embedding.as_bytes()}
    cur.execute(
        'insert into bill_summary_embedding (bill_id, embedding) '
        'values (:bill_id, :embedding) '
        'on conflict (bill_id) do update set embedding = :embedding',
        params)
    con.commit()


def load_bill_summary_embeddings() -> Iterable[tuple[str, llm_stuff.Embedding]]:
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT bill_id, embedding from bill_summary_embedding')
    while row := cur.fetchone():
        bill_id, embedding = row
        if not embedding: continue
        embedding = llm_stuff.Embedding.from_bytes(embedding)
        yield bill_id, embedding


def load_similar_bills(prompt, num_bills=5) -> Iterable[tuple[Bill, float]]:
    """ Returns (bill id, score) """
    embedder = llm_stuff.Embedder()
    prompt_emb = embedder.embed(prompt)
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT bill_id, embedding from bill_summary_embedding')
    bill_scores = []
    while row := cur.fetchone():
        bill_id, embedding = row
        if not embedding: continue
        embedding = llm_stuff.Embedding.from_bytes(embedding)
        score = embedder.similarity(prompt_emb, embedding)
        bill_scores.append((bill_id, score))
    bill_scores.sort(key=lambda x: x[1], reverse=True)
    for bill in bill_scores[:num_bills]:
        id, score = bill
        yield load_bill(id), score


def has_short_summary(id):
    con, cur = db.connect(DB_FILE)
    cur.execute('SELECT count(*) from bill_summary_short where bill_id = ?', (id,))
    return cur.fetchone()[0] > 0


def set_bill_short_summary(id, summary):
    con, cur = db.connect(DB_FILE)
    params = {'bill_id': id, 'summary': summary}
    cur.execute(
        'insert into bill_summary_short (bill_id, summary) '
        'values (:bill_id, :summary) '
        'on conflict (bill_id) do update set summary = :summary',
        params)
    con.commit()
