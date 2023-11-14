import time
import traceback

from ausbills.parliament.federal import get_bills_metadata, get_bill
import llm

import staging2
import store


def main():
    # staging2.wipe()
    # load_staging2()

    store.wipe()
    load_bills()

    # generate_summary_embeddings()
    # for b in get_similar_bills('climate change'):
    #     print(b)


def load_staging2(raise_on_error=False, reload_errors=False, limit=0):
    """ Load all bills from the web into the staging db

        Parameters:
            raise_on_error (bool): raise an exception if a bill fails to load
            reload_errors (bool): reload bills that had errors
            limit (int): limit the number of bills to load
    """
    md = get_bills_metadata()
    bills_to_load = md[:limit] if limit else md
    for i, meta in enumerate(bills_to_load):
        staged_bill = staging2.load_bill(meta.id)
        if staged_bill:
            if reload_errors and staged_bill.error:
                print(f'reloading {i} of {len(bills_to_load)}: {meta.id}')
                staging2.delete_bill(meta.id)
            else:
                print(f'skipping {i} of {len(bills_to_load)}: {meta.id}')
                continue
        try:
            bill = get_bill(meta)
            staging2.save_bill(staging2.Bill.from_fed_bill(bill))
            print(f'loaded {i + 1} of {len(bills_to_load)}')
        except Exception as e:
            bill = staging2.Bill.from_meta(meta)
            bill.error = str(e) + '\n' + traceback.format_exc()
            staging2.save_bill(bill)
            print(f'failed to load bill id={bill.id}: {e}')
            if raise_on_error: raise
        time.sleep(.5)


def load_bills():
    """ Load bills from staging into main db """
    for bill in staging2.load_bills():
        sbill = store.Bill.from_staging(bill)
        if not sbill.link.startswith('http'): continue
        store.save_bill(sbill)


def generate_summary_embeddings():
    model = llm.get_embedding_model('ada-002')
    bills = store.load_bills()
    for i, bill in enumerate(bills):
        title, summary, embedding = bill
        if embedding: continue    # don't regenerate
        if not summary: continue
        emb = model.embed(summary)
        store.save_bill_embedding(title, emb)
        print(f'generated embedding {i} of {len(bills)}')


def get_similar_bills(prompt):
    model = llm.get_embedding_model('ada-002')
    prompt_emb = model.embed(prompt)
    bills = store.load_bills()
    results = []
    for title, summary, embedding in bills:
        if not embedding: continue
        emb2 = store.emb_decode(embedding)
        results.append((title, summary, llm.cosine_similarity(prompt_emb, emb2)))
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:5]


if __name__ == '__main__':
    main()
