to run:
run HW9.py

the only real issue is that you need to make sure to have a tmp.db file wherever you're running this from.
i just did: touch tmp.db and then everything ran fine.

things that i haven't yet accounted for:
- if you don't upload a file, you can still continue to the search page
- you can't upload multiple collections
- graceful error handling
- a link on the search page to reload and search again

