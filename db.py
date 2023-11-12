import sqlite3
import os

DATABASE = 'fedbills.db'

def connect():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    return con, cur

def drop_and_build():
    os.remove(DATABASE)
    con, cur = connect()
    cur.execute('CREATE TABLE IF NOT EXISTS bill_meta(title text, link text, parliament text)')
    cur.execute('CREATE TABLE IF NOT EXISTS bill(title text, link text, summary text)')
    con.commit()

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