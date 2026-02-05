# Importing the Flask class to create the Web app.
# Importing jsonify to return JSON to the browser
# Importing render_template to serve HTML files
from flask import Flask, jsonify, render_template, request
import requests

#serve production server on flask
from waitress import serve

# Importing psycopg2 to connect Python to PostgresSQL
import psycopg2

# Importing extra helpers from psycopg2
import psycopg2.extras

# Importing inventory functions
from inventory import user_login_verification 
from db import get_connection

# Creating the Flask application
# __name__ will tell Flask where the file is
app = Flask(__name__)

BACKEND_URL = "http://127.0.0.1:8000"
############################ LEGACY CODE ############################

# Function to create a new database connection
'''
def get_connection():
    return psycopg2.connect(
        host="98.92.53.251",
        database="postgres",
        user="postgres",
        password="pgpass",
        port=5432
    )
'''
    
########################### END LEGACY CODE ###########################

#This route runs when someone visits the root URL
@app.route("/index")
def index():
    #send the HTML file to the browser
    return render_template("index.html")

#This route will send the user to the login page
@app.route("/")
def login():
    return render_template("login.html")

#login endpoint to sned data to backend
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()

    try:
        resp = requests.post(
            f"{BACKEND_URL}/login",
            json={
                "username": data.get("username"),
                "password": data.get("password")
            },
            timeout=5
        )

        if resp.status_code != 200:
            return jsonify(resp.json()), 401

        result = resp.json()

        response = make_response(jsonify({"status": "success"}))
        response.set_cookie(
            "session_token",
            result["session_token"],
            httponly=True,
            samesite="Lax"
        )
        return response

    except requests.RequestException:
        return jsonify({"error": "Backend unavailable"}), 503

#checks session token before asking backend for data
@app.route("/api/finishedgoods")
def finished_goods():
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
def get_finished_goods():
    conn = get_connection() #function imported from db.py

    resp = requests.get(
        f"{BACKEND_URL}/finishedgoods",
        headers={"Authorization": f"Bearer {token}"}
    )

    return jsonify(resp.json()), resp.status_code

#deletes token once user is logged out
@app.route("/api/logout", methods=["POST"])
def logout():
    token = request.cookies.get("session_token")
    if token:
        requests.post(
            f"{BACKEND_URL}/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

    response = make_response(jsonify({"status": "logged out"}))
    response.delete_cookie("session_token")
    return response

@app.route("/search")
def search_page():
    return render_template("search.html")

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000, debug=True)
    serve(app, host='0.0.0.0', port=5000)