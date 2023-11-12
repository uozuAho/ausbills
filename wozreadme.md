# reading aus fed bills

Using Python 3.11 (llm install fails on 3.12)

# first time start
```py
. .venv/Scripts/activate
pip install -r requirements
llm keys set openai <enter your openai api key>
# modify then run:
python fed.py
# database utils
python db.py
```

# todo
- generate embeddings of summaries in bill table
- ask some questions
- ~60% of bills don't load. parsing html is probably broken

# notes
- stuff is broken in this library. see my changes. maybe PR?
