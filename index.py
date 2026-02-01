# Importing the Flask class to create the Web app.
# Importing jsonify to return JSON to the browser
# Importing render_template to serve HTML files
from flask import Flask, jsonify, render_template

# Importing psycopg2 to connect Python to PostgresSQL
import psycopg2

# Importing extra helpers from psycopg2
import psycopg2.extras 

# Creating the Flask application
# __name__ will tell Flask where the file is
app = Flask(__name__)

# Function to create a new database connection
def get_connection():
    return psycopg2.connect(
        host="98.92.53.251",
        database="postgres",
        user="postgres",
        password="pgpass",
        port=5432
    )

#This route runs when someone visits the root URL
@app.route("/")
def index():
    #send the HTML file to the browser
    return render_template("index.html")

#Route to the API endpoint that returns JSON data
@app.route("/api/finishedgoods")
def get_finished_goods():
    conn = get_connection()

    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    #SQL query with PostgresSQL
    cur.execute("""
        SELECT finishedgoodid, finishedgoodname FROM 
        tblfinishedgoods ORDER BY finishedgoodname;""")
    
    goods = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(goods)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)