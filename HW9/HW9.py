from flask import Flask, redirect,request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from pybtex.database.input import bibtex

app = Flask(__name__)
app.debug = True
#connection to mysql server
app.config['SQALCHEMY_DATABASE_URI'] = 'sqlite:////tmp.test.db' 
db = SQLAlchemy(app) #database name is  db

class Article(db.Model): 
    id = db.Column(db.Integer, primary_key=True, unique=True)
    adsurl = db.Column(db.String(80))
    adsnote = db.Column(db.String(80))
    keywords = db.Column(db.String(200))
    title = db.Column(db.String(50))
    year = db.Column(db.Integer)
    authors = db.Column(db.String(200))

    def __init__(self, adsurl, adsnote, keywords, title, year,authors):
        self.adsurl = adsurl
        self.adsnote = adsnote
        self.keywords = keywords
        self.title = title
        self.year = year
        self.authors = authors

def make_db(bib_filepath):
    """
    parse collection
    takes in the filepath to the bibtex collection
    creates a database using SQLAlchemy
    """
    parser = bibtex.Parser()
    #bib_data = parser.parse_file('/Users/matar/Documents/Courses/python-seminar/Homeworks/homework9_data/homework_9_refs.bib')
    bib_data = parser.parse_file(bib_filepath)

    # make database - each instance of class is a row in the table Article 
    db.create_all()
    for key in bib_data.entries.keys():
        entry = bib_data.entries[key]
        if entry.type == 'article':
            #fieldnames = bib_data.entries[entry].fields.keys()
            adsurl = entry.fields['adsurl']
            adsnote = entry.fields['adsnote']
            title = entry.fields['title']
            year = entry.fields['year']
            try:
                keywords = entry.fields['keywords']
            except:
                keywords = ""
            try:
                authors = entry.fields['author'].replace('{',"").replace('}',"")
            except:
                authors = ""
            article = Article(adsurl, adsnote, keywords, title, year,authors) 
            #create instance of Article, writing to database

            db.session.add(article)
            try:
                db.session.commit()
            except:
                pass

def format_results(querylist):
    """ 
    makes html string to display query results - should have used template
    hardcoded, and ugly
    """
    astring = "<p><h1> Query Results </h1></p>"
    articles =""
    fieldnames = ['adsurl','adsnote','journal','title','year']
    for article in querylist:
        details = "<p> <b>" + article.title + "</b> </p> <p>" + article.authors + "</p> <p>" + str(article.year) + "</p> <p> keywords: " + article.keywords + "</p> <p>" + article.adsnote + "</p> <p>" + article.adsurl + "</p> <hr>"
        articles = articles+details
    return astring+articles
        


@app.route('/', methods = ['GET','POST'])
def index():
    """
    page to upload collection. NOTE: can only upload 1 collection (overwrites previous ones). it also lets you to continue when you haven't actually uploaded. need to fix.
    """
    if request.method == 'GET':
        return '''
        <form action = "" method = "POST" enctype=multipart/form-data>
        <p> Please upload a collection: <br>
        <input type = "file" name = "collection" />
        </p>
        <input type = submit value = Upload>
        </form>'''
    else:
        bfile = request.files["collection"]
        filepath = 'tmp.db'
        bfile.save(filepath)
        make_db('tmp.db')
        return redirect('/search')

@app.route('/search', methods = ["GET", "POST"])
def search():
    """
    performs search on query.
    slow for large queries.
    need to add button to reload search page for new search.
    """
    if request.method == 'GET':
        return '''
        <form action = "search" method = "POST">
        <p> What is your query? </p>
        <p> Note that queries must be formatted as sql queries </p> 
        <p> for example : keywords LIKE "% MAGELLANIC%"</p>
        <input type = "text" name = "querystring" />
        </p>
        <input type = "submit" value = Search>
        </form>
        '''
    else:
        querystring = request.form["querystring"]
        return format_results(Article.query.filter(querystring).all())

if __name__ == "__main__":
    app.run()

