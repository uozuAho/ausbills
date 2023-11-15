# reading aus fed bills

Using Python 3.11 (llm install fails on 3.12)

# first time start
```py
. .venv/Scripts/activate
pip install -r requirements
llm keys set openai <enter your openai api key>
export OPENAI_API_KEY=<your openai api key>
# modify then run:
python fed.py
```

# why?
- understand what the federal parliament (legislative) is doing, and has done, at a glance
- I'd also like to know about executive and state level, but starting small

# todo
- summarise long summaries
- load bill memorandums, embed, summarise
    - does this give better summaries than bill summaries/shortened summaries?
- clustering: try again once you've embedded bill memorandums
- load bills from previous parliaments
- show number of bills passed over time
    - who gets more done while in parliament?
    - do libs/labor cause different bills to be passed/rejected?
- data quality
    - loading 11 bad records in current parliament bills list. why?

# maybe
- fuzzy search by everything: sponsor, party, date, government
- search by fields + similarity, eg: bills that didn't pass, cluster...?

# notes
- stuff is broken in this library. see my changes. maybe PR?
- several bill titles don't parse correctly from the bills list. don't really
  care, bill link is important
- 1 bill doesn't have a summary on the website
- ignore bills with bad links, there's only 2, these possibly don't have links
  on the bill list page
- clustering: results not very good when just using summary embeddings. Takes
  work to understand clusters, bills seem to end up in wrong clusters
