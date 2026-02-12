import psycopg2

DB_CONFIG = {
    "host": "44.194.16.99", #or "localhost"
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "pgpass"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)