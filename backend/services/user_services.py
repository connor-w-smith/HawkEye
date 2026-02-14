import hashlib
import secrets
import smtplib
import urllib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

import bcrypt

from db import get_connection


# function sends the email with the recovery token to the user
# args: username(Email address), raw_token, Returns True(Sent) or False(Not Sent)
def send_recovery_email(username, raw_token):
    # creating variables for our email
    sender_email = "h.einventorysystems@gmail.com"
    app_password = "jtco shcy myej oesr"

    # Create the password reset link
    base_url = "http://127.0.0.1:5000"  # Update this to your production URL when deploying
    reset_link = f"{base_url}/reset-password?token={urllib.parse.quote(raw_token)}&email={urllib.parse.quote(username)}"

    # Create email to send with HTML
    subject = "Password Recovery Link"

    # Plain text version
    text_body = f"""Hello,

Click the link below to reset your password:

{reset_link}

This link will expire in 15 minutes.

If you did not request a password reset, please ignore this email."""

    # HTML version with clickable link
    html_body = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password Here</a></p>
            <p>This link will expire in 15 minutes.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
        </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = username

    # Attach both plain text and HTML versions
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    msg.attach(part1)
    msg.attach(part2)

    try:
        # connect to Gmail's SMTP server on port 587
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False

#function to reset password if forgotten
#arg: username (email), returns: raw_token (for sending in email)
def password_recovery(username):

    #open connection
    conn = get_connection()
    #disable autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            cur.execute(""" 
                        SELECT 1 
                        FROM tblusercredentials
                        WHERE username = %s""", (str(username),))

            #verify that the user exists
            if cur.fetchone() is None:
                raise ValueError(f"{username} does not exist")

            #create a token
            raw_token = secrets.token_urlsafe(32)

            #hash the token before saving
            token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
            #set token expiration
            token_expiration = datetime.now() + timedelta(minutes=15)

            # UPDATE user's token and expiration (not INSERT)
            cur.execute("""
                        UPDATE tblusercredentials
                        SET token = %s, tokenexpiration = %s
                        WHERE username = %s""",(token_hash, token_expiration, username),)
            #commit changes
            conn.commit()

            # Return raw token so the calling function can send the email
            return raw_token

    except Exception as e:
        #roll back in case of error
        conn.rollback()
        raise e

    finally:
        #Close connection
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
    
def get_user_credentials_table():
    # db connection
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT username, isadmin
                            FROM tblusercredentials""")

            rows = cursor.fetchall()

            if not rows:
                raise ValueError(f"No data found in user credentials table")

            else:
                return rows

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        raise

    finally:
        if conn:
            conn.close()