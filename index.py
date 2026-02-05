# Importing the Flask class to create the Web app.
# Importing jsonify to return JSON to the browser
# Importing render_template to serve HTML files
from flask import Flask, jsonify, render_template, request

# Importing psycopg2 to connect Python to PostgresSQL
import psycopg2

# Importing extra helpers from psycopg2
import psycopg2.extras

# Importing inventory functions
from inventory import user_login_verification, password_recovery 

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
@app.route("/index")
def index():
    #send the HTML file to the browser
    return render_template("index.html")

#This route will send the user to the password reset modal
@app.route("/password-modal")
def password_modal():
    return render_template("password-modal.html")

#This route will send the user to the login page
@app.route("/")
def login():
    return render_template("login.html")

#API endpoint for user login verification
@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required"}), 400
        
        # Call the login verification function from inventory.py
        user_validated = user_login_verification(username, password)
        
        if user_validated:
            return jsonify({"status": "success", "message": "Login successful"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
            
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": "An error occurred during login"}), 500

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

#API endpoint for password reset request
@app.route("/api/request-password-reset", methods=["POST"])
def api_request_password_reset():
    try:
        data = request.get_json()
        email = data.get("email")
        
        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400
        
        # Call password recovery function from inventory.py
        token_hash = password_recovery(email)
        print(f"Password recovery initiated for {email}, token: {token_hash}")
        
        return jsonify({"status": "ok", "message": "Password reset token generated"}), 200
            
    except ValueError as e:
        print(f"Password reset error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An error occurred"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)