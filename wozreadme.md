# reading aus fed bills

Using Python 3.11 (llm install fails on 3.12)

# first time start
```py
. .venv/Scripts/activate
pip install -r requirements
llm keys set openai <enter your openai api key>
# modify then run:
python fed.py
# interactive database utils
python -i db.py
```

# todo
- staging
    - dedupe by id instead of title
        - DONE: rebuild using json
        - DONE: reload staging, as many bills may have been skipped
    - note: several titles don't parse correctly from the bills list. don't really care, bill link is important
    - note: 1 bill doesn't have a summary on the website
    - note: ignore records with bad links, there's only 1
- loading meta: 11 bad records. why?
- load bill memorandums, embed, any better?
    - ask more specific questions
    - try RAG?
- load bills from previous parliaments
- try clustering?

# notes
- stuff is broken in this library. see my changes. maybe PR?
