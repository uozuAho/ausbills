import time
import traceback

from ausbills.parliament.federal import get_bills_metadata, get_bill

import staging2
import store
import llm_stuff


def main():
    # staging2.wipe()
    # load_staging2()

    # store.wipe()
    # load_bills()
    # generate_summary_embeddings(fake_emb=False, overwrite=False)
    print_similar_bills('war')


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


def generate_summary_embeddings(fake_emb=True, overwrite=False):
    """ Generate embeddings for bill summaries

        Parameters:
            fake_emb (bool): don't use real embeddings (that cost money)
            overwrite (bool): overwrite existing embeddings
    """
    embedder = llm_stuff.Embedder()
    # load all at once to prevent db locking
    # TODO: do in batches
    bills = list(store.load_bills())
    for i, bill in enumerate(bills):
        if store.has_embedding(bill.id) and not overwrite:
            print(f'skipping {i + 1} of {len(bills)}')
            continue
        text_to_embed = bill.summary or bill.title
        if not text_to_embed: continue
        emb = llm_stuff.Embedding.from_floats([1,2,3])
        if not fake_emb: emb = embedder.embed(text_to_embed)
        store.set_bill_summary_embedding(bill.id, emb)
        print(f'generated embedding {i + 1} of {len(bills)}')


def print_similar_bills(prompt):
    bills = store.load_similar_bills(prompt)
    for bill in bills:
        print(f'{bill.id}: {bill.title}')


if __name__ == '__main__':
    main()
