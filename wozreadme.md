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
- how to tell if a bill passed/will not pass?
  - DONE: add to ausbills lib. not currently reading status
  - **todo** reload staging with status
  - status:
    - Act = passed, now law
    - Not proceeding = will not pass
    - else: in progress
  - passed: in bill page: status = Act. will have an assent date & act number
  - will not pass: status = Not Proceeding. This means the bill in its current
    form will not be discussed further. It may be significantly reworked and
    reintroduced, but is not considered the same bill
    - See https://www.aph.gov.au/About_Parliament/House_of_Representatives/Powers_practice_and_procedure/Practice7/HTML/Chapter10/Bills%E2%80%94the_parliamentary_process
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
