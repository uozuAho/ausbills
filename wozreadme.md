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

# why?
- understand what the federal parliament (legislative) is doing, and has done, at a glance
- I'd also like to know about executive and state level, but starting small

# todo
- embedding: use title if no summary, or skip if title is garbage
- cluster
    - by sponsor?
    - by area? kmeans? how many areas are there?
- load bills from previous parliaments
- show number of bills passed over time
- do libs/labor cause different bills to be passed/rejected?
- load bill memorandums, embed, any better?
    - ask more specific questions
    - try RAG?
- data quality
    - loading 11 bad records in current parliament bills list. why?
- try clustering?

# notes
- stuff is broken in this library. see my changes. maybe PR?
- several bill titles don't parse correctly from the bills list. don't really
  care, bill link is important
- 1 bill doesn't have a summary on the website
- ignore bills with bad links, there's only 2, these possibly don't have links
  on the bill list page
