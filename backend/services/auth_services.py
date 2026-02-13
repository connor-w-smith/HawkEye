from ...db import get_connection
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

import os
import urllib.parse
import smtplib
import hashlib
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


# Adds new user to the login DB
# args: Username, password, is_admin, returns: success statement
def add_user_credentials(username, password, is_admin):
    # open connection to database
    conn = get_connection()
    # Disable autocommit
    conn.autocommit = False

    try:
        with (conn.cursor() as cur):

            # check if username already exists in the database
            cur.execute("""
                        SELECT 1
                        FROM tblusercredentials
                        WHERE username = %s""", (str(username),))

            # if a value is returned then the username already exists
            if cur.fetchone() is not None:
                raise ValueError(f"{username} already exists")

            # Hash Password
            password_bytes = password.encode('utf-8')
            password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
            hashed_password = password_hash.decode('utf-8')

            # insert new record into tblusercredentials
            cur.execute("""
                        INSERT INTO tblusercredentials 
                        (username, password, isadmin)
                        VALUES (%s, %s, %s)""",
                        (str(username), hashed_password, is_admin), )

            # If everything passed commit change
            conn.commit()


    except Exception as e:
        # Rollback in case of error to maintain data integrity
        conn.rollback()
        raise e

    finally:
        # close connection
        conn.close()

    return {"status": "success"}


"""def update_user_credentials(username, password, is_admin):"""


# Updates user password
# args: username, password, new_password returns success
def update_user_password(username, password, new_password):
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
                # hash password
                password_bytes = new_password.encode('utf-8')
                password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                hashed_password = password_hash.decode('utf-8')

                # update password for user
                cur.execute("""UPDATE tblusercredentials
                        SET password = %s
                        WHERE username = %s""",
                            (hashed_password, str(username),))

                # commit changes
                conn.commit()

                return {"status": "success"}

    except Exception as e:
        # rollback in case of data validity issues
        conn.rollback()
        raise e

    finally:
        # close connection
        conn.close()


# deletes user from tblusercredentials
# arg: username, returns: staus message
def delete_user_credentials(username):
    # open connection to database
    conn = get_connection()
    # disable autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT 1 FROM tblusercredentials
                        WHERE username = %s""",
                        (str(username),))

            # verify if user record was found
            if cur.fetchone() is None:
                raise ValueError(f"{username} does not exist")

            cur.execute("""DELETE FROM tblusercredentials 
                           WHERE username = %s""",
                        (str(username),))

            # commit the deletion to the database
            conn.commit()

    except Exception as e:
        # rollback in case of data validity issues
        conn.rollback()
        raise e

    finally:
        # close connection
        conn.close()

    return {"status": "success"}


# function to reset password if forgotten - uses email
# arg: email (username), returns: success message
def password_recovery_email(email):
    # open connection
    conn = get_connection()
    # disable autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            cur.execute(""" 
                        SELECT 1 
                        FROM tblusercredentials
                        WHERE username = %s""", (str(email),))

            # verify that the user exists
            if cur.fetchone() is None:
                raise ValueError(f"{email} does not exist")

            # create a token
            raw_token = secrets.token_urlsafe(32)

            # hash the token before saving
            token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
            # set token expiration
            token_expiration = datetime.now() + timedelta(minutes=15)

            cur.execute("""
                        UPDATE tblusercredentials
                        SET token = %s, tokenexpiration = %s
                        WHERE username = %s""", (token_hash, token_expiration, email), )
            # commit changes
            conn.commit()

        # Send email with reset token using BASE_URL (fallback)
        base = os.environ.get('BASE_URL', 'http://localhost:5000')
        token_q = urllib.parse.quote_plus(raw_token)
        email_q = urllib.parse.quote_plus(email)
        reset_link = f"{base.rstrip('/')}/password-modal?token={token_q}&email={email_q}"
        send_password_reset_email(email, reset_link)

    except Exception as e:
        # roll back in case of error
        conn.rollback()
        raise e

    finally:
        # Close connection
        conn.close()

    return {"status": "success", "message": "Password reset link sent to email"}


def send_password_reset_email(email, reset_link):
    """Send password reset email using a fully constructed reset_link"""
    # Email configuration (update with your email settings)
    sender_email = "hawkeyeinventorysystems@gmail.com"
    sender_password = "mhlw dmkq vvvq jjiq"

    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset Request"
        message["From"] = sender_email
        message["To"] = email

        text = f"""Hello,\n\nYou requested a password reset. Click the link below to reset your password.\n\n{reset_link}\n\nThis link will expire in 15 minutes.\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nHawkEye Inventory System"""

        html = f"""<html><body><p>Hello,</p><p>You requested a password reset. Click the link below to reset your password.</p><p><a href=\"{reset_link}\">Reset Password</a></p><p>This link will expire in 15 minutes.</p><p>If you did not request this, please ignore this email.</p><p>Best regards,<br>HawkEye Inventory System</p></body></html>"""

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())
        server.quit()

        print(f"Password reset email sent to {email}")

    except Exception as e:
        print(f"Error sending email: {e}")
        raise e


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