import time
import traceback

from ausbills.parliament.federal import get_bills_metadata, get_bill
import llm

import staging2
import store


def main():
    # staging2.wipe()
    # load_staging2()

    # store.wipe()
    # load_bills()
    # generate_summary_embeddings(fake_emb=False, overwrite=False)
    pass

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
    embedder = Embedder()
    # load all at once to prevent db locking
    # TODO: do in batches
    bills = list(store.load_bills())
    for i, bill in enumerate(bills):
        if store.has_embedding(bill.id) and not overwrite:
            print(f'skipping {i + 1} of {len(bills)}')
            continue
        text_to_embed = bill.summary or bill.title
        if not text_to_embed: continue
        emb = [1,2,3]
        if not fake_emb: emb = embedder.embed(text_to_embed)
        store.set_bill_summary_embedding(bill.id, emb)
        print(f'generated embedding {i + 1} of {len(bills)}')


class Embedder:
    def __init__(self, model_name='ada-002'):
        self.model = llm.get_embedding_model(model_name)

    def embed(self, text):
        def embed_single(text):
            return self.model.embed(text)
        # retry in case of rate limiting
        return self._retry(embed_single, text)

    def similarity(self, emb1, emb2):
        return llm.cosine_similarity(emb1, emb2)

    def _retry(self, func, *args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f'failed to {func.__name__}: {e}')
                time.sleep(2**i)
        raise Exception('failed to execute function')


# def get_similar_bills(prompt):
#     embedder = Embedder()
#     prompt_emb = embedder.embed(prompt)
#     bills = store.load_similar_bills(prompt_emb)
#     results = []
#     for bill bills:
#         if not embedding: continue
#         emb2 = store.emb_decode(embedding)
#         results.append((title, summary, embedder.similarity(prompt_emb, emb2)))
#     results.sort(key=lambda x: x[2], reverse=True)
#     return results[:5]


if __name__ == '__main__':
    main()
