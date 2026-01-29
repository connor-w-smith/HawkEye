import psycopg2

DB_CONFIG = {
    "host": "98.92.53.251",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "pgpass"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)