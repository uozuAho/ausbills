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
- loading meta: 11 bad records. why?
- loading bills: ~60% of bills don't load. parsing html is probably broken
- load bill memorandums, embed, any better?
    - ask more specific questions
    - try RAG?
- load all bills? possibly just getting last few years
- try clustering?

# notes
- stuff is broken in this library. see my changes. maybe PR?
