from flask import Flask, jsonify, render_template, request, make_response
import requests

# serve production server on flask
from waitress import serve
'''
In terminal run: uvicorn main:app --reload

In another terminal run: python3 index.py

web app will be available at: http://127.0.0.1:5000/

'''

app = Flask(__name__)

BACKEND_URL = "http://127.0.0.1:8000"

# -------------------- Pages --------------------

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/search")
def search_page():
    return render_template("search.html")

@app.route("/password-modal")
def password_modal():
    return render_template("password-modal.html")

@app.route("/reset-password")
def reset_password_page():
    return render_template(
        "reset-password.html",
        token=request.args.get("token"),
        email=request.args.get("email")
    )

# -------------------- Auth API (Proxy to FastAPI) --------------------

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()

    resp = requests.post(
        f"{BACKEND_URL}/login",
        json=data
    )

    if resp.status_code != 200:
        return jsonify(resp.json()), resp.status_code

    session_token = resp.json()["session_token"]

    response = make_response(jsonify({"status": "success"}))
    response.set_cookie("session_token", session_token, httponly=True)
    return response


@app.route("/api/logout", methods=["POST"])
def api_logout():
    token = request.cookies.get("session_token")

    if token:
        requests.post(
            f"{BACKEND_URL}/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

    response = make_response(jsonify({"status": "logged out"}))
    response.delete_cookie("session_token")
    return response


@app.route("/api/request-password-reset", methods=["POST"])
def api_request_password_reset():
    resp = requests.post(
        f"{BACKEND_URL}/request-password-reset",
        json=request.get_json()
    )
    return jsonify(resp.json()), resp.status_code


@app.route("/api/reset-password-confirm", methods=["POST"])
def api_reset_password_confirm():
    resp = requests.post(
        f"{BACKEND_URL}/reset-password",
        json=request.get_json()
    )
    return jsonify(resp.json()), resp.status_code

# -------------------- Data API (Proxy to FastAPI) --------------------

@app.route("/api/finishedgoods")
def finished_goods():
    token = request.cookies.get("session_token")

    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    resp = requests.get(
        f"{BACKEND_URL}/finishedgoods",
        headers={"Authorization": f"Bearer {token}"}
    )

    return jsonify(resp.json()), resp.status_code


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
    serve(app, host="0.0.0.0", port=5000)