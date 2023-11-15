from collections import defaultdict
import queue
import random
import textwrap
import threading
import time
import traceback

from ausbills.parliament.federal import get_bills_metadata, get_bill

import staging2
import store
import llm_stuff


def main():
    # grab source data
    # staging2.wipe()
    # staging2.update_schema()
    # load_staging2()

    # load the 'data warehouse'
    # store.wipe()
    # store.update_schema()
    # load_bills()
    # generate_summary_embeddings(fake_emb=False, overwrite=False)

    # generate_short_summaries(fake=True, overwrite=True, limit=0, num_workers=20)
    generate_short_summaries(fake=False, overwrite=True, limit=0, num_workers=5)

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


def generate_short_summaries(
        fake=True,
        overwrite=True,
        limit=20,
        num_workers=5):
    """ Generate short summaries from existing summaries. Very slow!

        Parameters:
            fake (bool): use a fake summariser (for testing)
            overwrite (bool): overwrite existing short summaries
            limit (int): limit the number of bills to summarise
            num_workers (int): number of workers to use
    """
    def summarise_fake(text):
        time.sleep(1 + random.random() * 5)
        if random.random() < .1:
            raise Exception('fake error')
        return "Fake text!"

    bill_queue = queue.Queue()

    # todo: load bills in batches
    bills = list(store.load_bills())
    if limit: bills = bills[:limit]
    for bill in bills:
        if not bill.summary or len(bill.summary.split()) < 50:
            print(f'skipping already short: {bill.id}')
            continue
        if staging2.has_short_summary(bill.id) and not overwrite:
            print(f'skipping existing: {bill.id}')
            continue
        bill_queue.put(bill)

    print(f'summarising {bill_queue.qsize()} bills with {num_workers} workers...')
    terminate_requested = False

    def worker():
        nonlocal terminate_requested
        while True:
            try:
                if terminate_requested: break
                bill = bill_queue.get_nowait()
                summary = ''
                print(f'generating short summary for {bill.id}')
                if fake:
                    summary = summarise_fake(bill.summary)
                else:
                    summary = llm_stuff.summarise(bill.summary)
                staging2.set_bill_short_summary(bill.id, summary)
                print(f'summarised {bill.id}')
                bill_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                print(f"Error processing bill {bill.id}: {e}")
                stack_trace = traceback.format_exc()
                staging2.set_bill_short_summary(bill.id, summary, error=f'{e}\n{stack_trace}')
                bill_queue.task_done()

    threads = []
    for _ in range(num_workers):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    try:
        while True:
            for t in threads:
                t.join(timeout=0.3)
            if not any(t.is_alive() for t in threads):
                break
    except KeyboardInterrupt:
        print("Interrupted by user. Waiting for threads to finish current jobs...")
        # let's gracefully exit
        terminate_requested = True


def pretty_print(text: str, indent=0, max_width=100):
    prefix = ' ' * indent
    print('\n'.join(prefix + line for line in textwrap.wrap(text, max_width)))


if __name__ == '__main__':
    main()
