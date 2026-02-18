from db import get_connection
from datetime import datetime, timedelta

import bcrypt
import secrets

"""User login/password reset functions"""

# verifies user login to webpage
# args: username, password, Returns: {"Status":"Success"}
def user_login_verification(username, password):
    # Open connection to database
    conn = get_connection()
    # disable autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:

            cur.execute("""SELECT password
                            FROM tblusercredentials
                            WHERE username = %s""",
                        (str(username),))

            results = cur.fetchone()

            # Check if username exists in the DB
            if results is None:
                raise ValueError(f"{username} does not exist")

            # transfer password to usable variable
            stored_password = results[0]

            # verify current given password for security
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                session_token = create_session(username)
                return {"token": session_token}

            else:
                raise ValueError("Password does not match")

    except Exception as e:
        raise e

    finally:
        conn.close()


"""User session functions"""

#create session token when user logs in
def create_session(username):
    conn = get_connection()
    conn.autocommit = False

    try:
        #creats session token and expiration
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=30)

        with conn.cursor() as cur:
            # Delete any existing sessions for this user (upsert pattern)
            cur.execute("""
                DELETE FROM tblsessions
                WHERE username = %s
            """, (username,))
            
            #inserts into tblsessions table in db
            cur.execute("""
                INSERT INTO tblsessions (session_token, username, expires_at)
                VALUES (%s, %s, %s)
            """, (session_token, username, expires_at))

            conn.commit()

        return session_token

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

#validate session(timeout) functions
def validate_session(session_token):
    conn = get_connection()

    try:
        #on connection check token row
        with conn.cursor() as cur:
            cur.execute("""
                SELECT username, expires_at
                FROM tblsessions
                WHERE session_token = %s
            """, (session_token,))

            row = cur.fetchone()

            #if no token session is invalid
            if row is None:
                raise ValueError("Invalid session")

            username, expires_at = row

            #if token is expired session will end
            if datetime.now() > expires_at:
                delete_session(session_token)
                raise ValueError("Session expired")

            return username

    finally:
        conn.close()

#delete session(logout) function
def delete_session(session_token):
    conn = get_connection()
    conn.autocommit = True

    try:
        #remove token from db when logout
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM tblsessions
                WHERE session_token = %s
            """, (session_token,))
    finally:
        conn.close()