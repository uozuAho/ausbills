import sqlite3

con = sqlite3.connect("fedbills.db")
cur = con.cursor()

def print_schema(cur):
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    for table_name, sql in tables:
        print(f"Table: {table_name}\nSQL: {sql}\n")

def q(query):
    cur.execute(query)
    for rec in cur.fetchall():
        print(rec)

# print_schema(cur)
# vals = {'title': 'test'}
# cur.execute('insert into bill_meta(title) values(:title)', vals)
# con.commit()
# bills = cur.execute('select * from bill').fetchall()
# for bill in bills:
#     print(bill)