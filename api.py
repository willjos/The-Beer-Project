import psycopg2
import psycopg2.extras  # We'll need this to convert SQL responses into dictionaries
from flask import Flask, current_app, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)

CORS(app)

def get_db_connection(): # sets up a connection to my beer_data database in postgres
  try:
    conn = psycopg2.connect("dbname=beer_project user=willsimms host=localhost")
    return conn
  except:
    print("Error connecting to database.")

conn = get_db_connection() # connection made to database

def db_fetch(query, parameters=()): # executes a query and fetches all results from the DB
    if conn != None:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            try:
                cur.execute(query, parameters)
                fetch = cur.fetchall()
                return fetch
            except:
                return "Error executing query."
    else:
        return "No connection"

@app.route('/') #retrieves the website page
def index():
    return current_app.send_static_file("index.html")

@app.route('/beers') #endpoint that retrieves JSON of all beer info
def get_beers():
    query = """
        SELECT * FROM beer_data
        ORDER BY key;
    """
    fetch = db_fetch(query, parameters=())
    return fetch

@app.route('/beers/<int:key>') #endpoint that retrieves JSON of a single beer by its 'key' in the table.
def get_beer_by_key(key):
    query = """
        SELECT * FROM beer_data
        WHERE key = %s;
    """
    parameters = (key,)
    fetch = db_fetch(query, parameters)
    return fetch

@app.route('/search') #query parameter search endpoint that retrieves beers with all matches in their description in the table.
def search():
    def percentify(keywords):
        percentified_keywords = []
        for word in keywords:
            word = f'%{word}%'
            percentified_keywords.append(word)
        return percentified_keywords
    keywords = request.args.get('keywords').split(',')
    keywords_for_search = (percentify(keywords),)
    query = """
        SELECT * FROM beer_data 
        WHERE description ILIKE ANY (%s)
        ORDER BY key
        LIMIT 5;
    """ 
    fetch = db_fetch(query, keywords_for_search)
    if len(fetch) == 0:
        return '<h1> No beers found. </h1>' 
    return fetch

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)