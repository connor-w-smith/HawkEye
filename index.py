# Importing the Flask class to create the Web app.
# Importing jsonify to return JSON to the browser
# Importing render_template to serve HTML files
from flask import Flask, jsonify, render_template, request, make_response
import requests
#serve production server on flask
from waitress import serve
# Importing inventory functions
from inventory import user_login_verification 
from db import get_connection
from search import get_finished_good_by_id, search_inventory_by_id


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
        ç
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

    
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000, debug=True)
    serve(app, host='0.0.0.0', port=5000)