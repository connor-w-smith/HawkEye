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

from backend.models import AddUserRequest
# Importing inventory functions
from db import get_connection




# Creating the Flask application
# __name__ will tell Flask where the file is
app = Flask(__name__)

BACKEND_URL = "http://127.0.0.1:8000"

# in Flask dev server, using requests
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_all(path):
    import requests
    # Forward everything to FastAPI
    resp = requests.request(
        method=request.method,
        url=f"http://127.0.0.1:8000/{path}",
        headers={key: value for key, value in request.headers},
        params=request.args,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )
    return (resp.content, resp.status_code, resp.headers.items())
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
    data = request.get_json()
    print(f"DEBUG - Data being sent to FastAPI: {data}")

    # Send the data to FastAPI
    # Note: We use /auth/reset-password because that's where the 404 is happening
    response = requests.post(
        f"{BACKEND_URL}/users/reset-password",
        json=data,
        timeout=5
    )

    if response.status_code == 404:
        return jsonify({"status": "error", "message": "Backend route not found"}), 404

    return jsonify(response.json()), response.status_code
    

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



#API endpoint for password reset request
@app.route("/api/request-password-reset", methods=["POST"])
def api_request_password_reset():
    try:
        data = request.get_json()
        email = data.get("email")
        
        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400
        
        response = requests.post(f"{BACKEND_URL}/users/request-password-reset",
            json=data,
            timeout=5
        )
        if response.status_code == 404:
            return jsonify({"status": "error", "message": "Backend Route Not Found (404)"}), 404
        if response.status_code == 200:
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

@app.route("/start-order")
def start_order_page():
    return render_template("start-order.html")

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

@app.route("/api/create-production-order", methods=["POST"])
def proxy_create_production_order():
    data = request.get_json()
    
    resp = requests.post(
        f"{BACKEND_URL}/create-production-order",
        json=data,
        timeout=5
    )
    
    return jsonify(resp.json()), resp.status_code

# Specific route for a single finished good
@app.route("/api/finished-goods/<finished_good_id>")
def read_finished_good(finished_good_id):
    try:
        finished_good = get_finished_good_by_id(finished_good_id)
        if not finished_good:
            return jsonify({"error": "Finished good not found"}), 404

        # Make sure it's a dict
        if isinstance(finished_good, list):
            finished_good = finished_good[0]

        inventory_list = search_inventory_by_id(finished_good_id)
        inventory_count = inventory_list[0]["AvailableInventory"] if inventory_list else 0

        return jsonify({
            "finished_good": {
                "FinishedGoodID": finished_good["FinishedGoodID"],
                "FinishedGoodName": finished_good["FinishedGoodName"]
            },
            "inventory": {"AvailableInventory": inventory_count}
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 404


#Generic finished goods search/list route
@app.route("/api/finished-goods")
def finished_goods():
    token = request.cookies.get("session_token")
    search_query = request.args.get("search")
    try:
        resp = requests.get(
            f"{BACKEND_URL}/finished-goods",
            params={"search": search_query},
            headers={"Authorization": f"Bearer {token}"} if token else {},
            timeout=5
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 503

    

# Frontend product page
@app.route("/product/<finished_good_id>")
def product_page(finished_good_id):
    print(f"Serving product page for ID: {finished_good_id}")  # Debug log
    return render_template(
        "product.html",
        finished_good_id=finished_good_id
    )

@app.route("/api/production-data/<finished_good_id>")
def proxy_production_data(finished_good_id):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/production-data/{finished_good_id}",
            timeout=5
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 503

@app.route("/api/inventory/raw-materials/<finished_good_id>")
def proxy_raw_materials(finished_good_id):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/inventory/raw-materials/{finished_good_id}",
            timeout=5
        )
        return jsonify(resp.json()), resp.status_code
    except Exception:
        return jsonify({"raw_materials": []}), 200
        
@app.route("/api/production-data/current-orders/<finished_good_id>")
def proxy_current_orders(finished_good_id):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/production-data/current-orders/{finished_good_id}",
            timeout=5
        )
        return jsonify(resp.json()), resp.status_code
    except Exception:
        return jsonify({"current_orders": []}), 200

# Users management route
@app.route("/users")
def users_page():
    return render_template("users.html")


# API endpoint to get all users
@app.route("/api/users", methods=["GET"])
def api_get_users():
    try:
        results = get_users()

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#
# API endpoint to add a new user
@app.route("/api/users", methods=["POST"])
def api_add_user():
    try:
        data = request.get_json()

        users_data = AddUserRequest(
            username = data.get("username"),
            password = data.get("password"),
            is_admin = data.get("is_admin", False)
        )

        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required"}), 400

        result = add_user(users_data)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "An error occurred"}), 500

# API endpoint to delete a user
@app.route("/api/users/<username>", methods=["DELETE"])
def api_delete_user(username):
    try:
        result= delete_user(username)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "An error occurred"}), 500

    
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000, debug=True)
    serve(app, host='0.0.0.0', port=5000)