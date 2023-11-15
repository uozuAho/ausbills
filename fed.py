from collections import defaultdict
import textwrap
import time
import traceback

from ausbills.parliament.federal import get_bills_metadata, get_bill

import staging2
import store
import llm_stuff


def main():
    # grab source data
    # staging2.wipe()
    # load_staging2()

    # load the 'data warehouse'
    # store.wipe()
    # store.update_schema()
    # load_bills()
    # generate_summary_embeddings(fake_emb=False, overwrite=False)
    generate_short_summaries()

    # analyse stuff!
    # print_similar_bills('restrict individual rights')
    # print_similar_bills('socialist, social security, welfare')
    # cluster_bills(20)


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
    print(f'bills similar to "{prompt}":')
    for bill, score in store.load_similar_bills(prompt):
        print()
        print(f'{bill.id}: ({score:0.2f}): {bill.title}')
        pretty_print(bill.summary, indent=2)


def cluster_bills(num_clusters):
    embedder = llm_stuff.Embedder()
    bills = list(store.load_bill_summary_embeddings())
    embeddings = [b[1] for b in bills]
    labels = embedder.cluster(embeddings, num_clusters)
    clustered = defaultdict(list)  # label -> bill ids
    for label, bill in zip(labels, bills):
        clustered[label].append(bill[0])
    for key in clustered:
        print(f'cluster {key}:')
        for bill_id in clustered[key]:
            bill = store.load_bill(bill_id)
            print(f'  {bill_id}: {bill.title}')


def generate_short_summaries(overwrite=True, debug=True):
    """ Generate short summaries from existing summaries. Very slow! """
    # todo: do in batches of bills, and make parallel summarise calls
    # todo: store error messages and stack traces
    for bill in list(store.load_bills())[:5]:
        if len(bill.summary.split()) < 50: continue  # up to 50 words is fine
        if store.has_short_summary(bill.id) and not overwrite:
            print(f'skipping {bill.id}')
            continue

        if debug:
            print(f'generating short summary for {bill.id}, with current summary:')
            pretty_print(bill.summary, indent=2)
        short_summary = llm_stuff.summarise(bill.summary)
        store.set_bill_short_summary(bill.id, short_summary)
        print(f'summarised {bill.id}')


def pretty_print(text: str, indent=0, max_width=100):
    prefix = ' ' * indent
    print('\n'.join(prefix + line for line in textwrap.wrap(text, max_width)))

if __name__ == '__main__':
    main()
