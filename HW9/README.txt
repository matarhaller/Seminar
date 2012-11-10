to run:
run HW9.py

you need to make sure to have a tmp.db file wherever you're running this from.


things that i haven't yet accounted for:
- if you don't upload a file, you can still continue to the search page
- you can't upload multiple collections
- graceful error handling

in order to make it work with mulitple collections, i think i need to have make_db not create a db each time
instead, it should add the existing bibtex entries to the database (with instances of Article)
one of the fields of the the Article class should be the collection name (and then you can keep track of collections and search by it)...
