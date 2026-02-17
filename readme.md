 /$$   /$$                         /$$       /$$$$$$$$                    
| $$  | $$                        | $$      | $$_____/                    
| $$  | $$  /$$$$$$  /$$  /$$  /$$| $$   /$$| $$       /$$   /$$  /$$$$$$ 
| $$$$$$$$ |____  $$| $$ | $$ | $$| $$  /$$/| $$$$$   | $$  | $$ /$$__  $$
| $$__  $$  /$$$$$$$| $$ | $$ | $$| $$$$$$/ | $$__/   | $$  | $$| $$$$$$$$
| $$  | $$ /$$__  $$| $$ | $$ | $$| $$_  $$ | $$      | $$  | $$| $$_____/
| $$  | $$|  $$$$$$$|  $$$$$/$$$$/| $$ \  $$| $$$$$$$$|  $$$$$$$|  $$$$$$$
|__/  |__/ \_______/ \_____/\___/ |__/  \__/|________/ \____  $$ \_______/
                                                       /$$  | $$          
                                                      |  $$$$$$/          
                                                       \______/           

            -----------Inventory systems-----------

Running the Application
~~~~ UPDATED ~~~~
TLDR//
in terminal:
-1. uvicorn backend.main:app --reload
-2. python3 index.py
-3. url once started - http://127.0.0.1:5000

This project runs using two servers at the same time:
-A FastAPI backend for database and API logic
-A Flask frontend for the web interface

Both servers must be running for the application to work.

Requirements:
Python 3.10+
PostgreSQL running and accessible

Required Python packages installed (fastapi, uvicorn, flask, waitress, psycopg2, requests, etc.)

Starting the Backend (FastAPI):
The backend must be started first.

Command:
uvicorn backend.main:app --reload

Expected Output:
Uvicorn running on http://127.0.0.1:8000


This starts the API server on port 8000.
Do not close this terminal.

Starting the Frontend (Flask):
Open a new terminal window.

Command:
python3 index.py

Expected Output:
Serving on http://0.0.0.0:5000


This starts the web server on port 5000.
Do not close this terminal.

Accessing the Application
Open a web browser and go to:
http://127.0.0.1:5000

This will load the login page.


!Important Notes!
Both servers must be running at the same time
If the backend is not running, login and search will fail
“Connection refused” errors mean FastAPI is not running
Use database accounts with properly hashed passwords