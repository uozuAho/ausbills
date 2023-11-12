import time

from ausbills.parliament.federal import get_bills_metadata, get_bill
import llm

import db


def main():
    # db.drop_and_build()
    # load_metadata()
    # load_bills()
    generate_summary_embeddings()


def load_metadata():
    con, cur = db.connect()
    print('loading metadata...')
    md = get_bills_metadata()
    print('saving to db...')
    for meta in md:
        cur.execute('INSERT INTO bill_meta(title, link, parliament) VALUES(?, ?, ?)', (meta.title, meta.link, meta.parliament))
    con.commit()


def load_bills():
    """ Currently loads bill summaries into the bill table """
    con, cur = db.connect()
    md = get_bills_metadata()
    for i, meta in enumerate(md[137:]):
        try:
            b = get_bill(meta)
            cur.execute('INSERT INTO bill(title, link, summary) VALUES(?, ?, ?)', (b.title, b.link, b.summary))
            con.commit()
            print(f'loaded {i + 137} of {len(md)}')
        except Exception as e:
            print(f'failed to load {i + 137} of {len(md)}: {e}')
        time.sleep(.5)


if __name__ == '__main__':
    main()