# Importing the Flask class to create the Web app.
# Importing jsonify to return JSON to the browser
# Importing render_template to serve HTML files
from flask import Flask, jsonify, render_template, request

# Importing psycopg2 to connect Python to PostgresSQL
import psycopg2

# Importing extra helpers from psycopg2
import psycopg2.extras

# Importing inventory functions
from inventory import user_login_verification, password_recovery, reset_password_with_token

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


# Render reset password page (link from email)
@app.route("/reset-password")
def reset_password_page():
    token = request.args.get('token')
    email = request.args.get('email')
    return render_template('reset-password.html', token=token, email=email)

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


# API endpoint to confirm password reset using token
@app.route("/api/reset-password-confirm", methods=["POST"])
def api_reset_password_confirm():
    try:
        data = request.get_json()
        email = data.get('email')
        token = data.get('token')
        new_password = data.get('new_password')

        if not email or not token or not new_password:
            return jsonify({"status": "error", "message": "email, token and new_password are required"}), 400

        result = reset_password_with_token(email, token, new_password)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An error occurred"}), 500

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
        
        # Call password recovery to generate and store token; it returns the raw token
        raw_token = password_recovery(email)

        # Build reset link dynamically from the request host
        from urllib.parse import quote_plus
        base = request.host_url.rstrip('/')
        token_q = quote_plus(raw_token)
        email_q = quote_plus(email)
        reset_link = f"{base}/password-modal?token={token_q}&email={email_q}"

        # Send email using inventory helper
        from inventory import send_password_reset_email
        send_password_reset_email(email, reset_link)

        print(f"Password recovery initiated for {email}, reset link sent")
        return jsonify({"status": "ok", "message": "Password reset link sent to email"}), 200
            
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