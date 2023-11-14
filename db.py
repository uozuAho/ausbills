import sqlite3
import os

def connect(path):
    con = sqlite3.connect(path)
    cur = con.cursor()
    return con, cur

def drop(path):
    if os.path.exists(path):
        os.remove(path)

def print_schema():
    con, cur = connect()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    for table_name, sql in tables:
        print(f"Table: {table_name}\nSQL: {sql}\n")

def q(query):
    con, cur = connect()
    cur.execute(query)
    for rec in cur.fetchall():
        print(rec)

def cmd(sql):
    con, cur = connect()
    cur.execute(sql)
    con.commit()


if __name__ == '__main__':
    """ run interactively """
    con, cur = connect()
