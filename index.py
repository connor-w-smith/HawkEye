# Importing the Flask class to create the Web app.
# Importing jsonify to return JSON to the browser
# Importing render_template to serve HTML files
from flask import Flask, jsonify, render_template, request, make_response
import requests
#serve production server on flask
from waitress import serve

# Importing psycopg2 to connect Python to PostgresSQL
import psycopg2

# Importing extra helpers from psycopg2
import psycopg2.extras

# Importing inventory functions
from inventory import password_recovery, reset_password_with_token  
from db import get_connection

# Creating the Flask application
# __name__ will tell Flask where the file is
app = Flask(__name__)

BACKEND_URL = "http://127.0.0.1:8000"


#This route runs when someone visits the root URL
@app.route("/index")
def index():
    #send the HTML file to the browser
    return render_template("index.html")

#This route will send the user to the login page
@app.route("/")
def login():
    return render_template("login.html")

#This route will send the user to the password reset modal
@app.route("/password-modal")
def password_modal():
    return render_template("password-modal.html")

#This route will send the user to the page from the email link
@app.route("/reset-password")
def reset_password():
    token = request.args.get('token')
    email = request.args.get('email')
    return render_template("reset-password.html", token=token, email=email)

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

    resp = requests.get(
        f"{BACKEND_URL}/finishedgoods",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )

    return jsonify(resp.json()), resp.status_code


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

        # Send email using the working recovery email function
        from inventory import send_recovery_email
        send_recovery_email(email, raw_token)

        print(f"Password recovery initiated for {email}, reset link sent")
        return jsonify({"status": "success", "message": "Password reset link sent to your email"}), 200
            
    except ValueError as e:
        print(f"Password reset error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An error occurred"}), 500

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

@app.route("/api/search/finished-good-name")
def proxy_finished_good_name_search():
    name = request.args.get("finished_good_name")

    resp = requests.get(
        f"{BACKEND_URL}/finished-good-name-search",
        params={"finished_good_name": name},
        timeout=5
    )

    return jsonify(resp.json()), resp.status_code

@app.route("/api/search/finished-good-id")
def proxy_finished_good_id_search():
    finished_good_id = request.args.get("finished_good_id")

    resp = requests.get(
        f"{BACKEND_URL}/finished-good-id-search",
        params={"finished_good_id": finished_good_id},
        timeout=5
    )

    return jsonify(resp.json()), resp.status_code

#new updated search    
@app.route("/api/search/finished-goods")
def proxy_finished_goods_search():
    search = request.args.get("search")

    resp = requests.get(
        f"{BACKEND_URL}/finished-goods",
        params={"search": search},
        timeout=5
    )

    return jsonify(resp.json()), resp.status_code

#frontend product page endpoint
@app.route("/product/<finished_good_id>")
def product_page(finished_good_id):
    return render_template("product.html")

    
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000, debug=True)
    serve(app, host='0.0.0.0', port=5000)