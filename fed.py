import time

from ausbills.parliament.federal import get_bills_metadata, get_bill
import llm

import store


def main():
    # store.wipe()
    # load_metadata()
    # load_bills()
    # generate_summary_embeddings()
    for b in get_similar_bills('climate change'):
        print(b)


def load_metadata():
    print('loading metadata...')
    md = get_bills_metadata()
    print('saving to db...')
    for meta in md:
        store.save_bill_meta(meta)


def load_bills():
    md = get_bills_metadata()
    for i, meta in enumerate(md):
        try:
            b = get_bill(meta)
            store.save_bill(b)
            print(f'loaded {i} of {len(md)}')
        except Exception as e:
            print(f'failed to load {i} of {len(md)}: {e}')
        time.sleep(.5)


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