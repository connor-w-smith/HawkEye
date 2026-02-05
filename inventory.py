import uuid6
import bcrypt
import secrets
import hashlib
import smtplib

from email.mime.text import MIMEText
from datetime import datetime, timedelta
from db import get_connection
from search import *



###use for manual entry
#curl -X POST http://127.0.0.1:8000/manual-entry \
#  -H "Content-Type: application/json" \
#  -d '{
#    "finished_good_id": "***Put Real UUID here***",
#    "quantity": 5
#  }'


"""Function Declarations by DB Table"""

"""tblusercredentials functions"""

# def user_login_verification(username, password): Returns user_validated (boolean)
# def add_user_credentials(username, password, is_admin): Returns {"status":"success"}
# def update_user_password(username, password, new_password): Returns {"status":"success"}
# def delete_user_credentials(username): Returns {"status":"success"}
# def send_recovery_email(username, raw_token): Returns Boolean of success or fail to send
# def password_recovery(username): Returns token_hash
# def verify_token_password_reset(username, token): Returns password_hash
# def create_session(username):
# def validate_session(session_token):
# def delete_session(session_token):

"""tblfinishedgoods functions"""

# def add_finished_good(finished_good_name): Returns {"status":"success"}
# def delete_finished_good(finished_good_name): Returns {"status":"success"}
# def get_finished_good(finished_good_name): Returns finishedgoodid


"""TblProductionInventory Functions"""

# def add_inventory(finished_good_id, quantity): Returns {"status":"success"}
# def delete_inventory(finished_good_id, quantity_to_subtract): Returns {"status":"success"}
# def get_inventory(finished_good_id): Returns int current_stock


"""tblusercredentials functions"""

#verifies user login to webpage
#args: username, password, Returns: {"Status":"Success"}
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

#Adds new user to the login DB
#args: Username, password, is_admin, returns: success statement
def add_user_credentials(username, password, is_admin):

    #open connection to database
    conn = get_connection()
    #Disable autocommit
    conn.autocommit = False

    try:
        with (conn.cursor() as cur):

            #check if username already exists in the database
            cur.execute("""
                        SELECT 1
                        FROM tblusercredentials
                        WHERE username = %s""",(str(username),))

            #if a value is returned then the username already exists
            if cur.fetchone() is not None:
                raise ValueError(f"{username} already exists")

            #Hash Password
            password_bytes = password.encode('utf-8')
            password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
            hashed_password = password_hash.decode('utf-8')

            #insert new record into tblusercredentials
            cur.execute("""
                        INSERT INTO tblusercredentials 
                        (username, password, isadmin)
                        VALUES (%s, %s, %s)""",
                        (str(username), hashed_password, is_admin),)

            #If everything passed commit change
            conn.commit()


    except Exception as e:
        # Rollback in case of error to maintain data integrity
        conn.rollback()
        raise e

    finally:
        #close connection
        conn.close()

    return {"status":"success"}

"""def update_user_credentials(username, password, is_admin):"""
#Updates user password
#args: username, password, new_passsword returns success
def update_user_password(username, password, new_password):

    #Open connection to database
    conn = get_connection()
    #disable autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:

            cur.execute("""SELECT password
                        FROM tblusercredentials
                        WHERE username = %s""",
                        (str(username),))

            results = cur.fetchone()

            #Check if username exists in the DB
            if results is None:
                raise ValueError(f"{username} does not exist")

            #transfer password to usable variable
            stored_password = results[0]

            #verify current given password for security
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                #hash password
                password_bytes = new_password.encode('utf-8')
                password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                hashed_password = password_hash.decode('utf-8')

                #update password for user
                cur.execute("""UPDATE tblusercredentials
                        SET password = %s
                        WHERE username = %s""",
                        (hashed_password, str(username),))

                #commit changes
                conn.commit()

    except Exception as e:
        #rollback in case of data validity issues
        conn.rollback()
        raise e

    finally:
        #close connection
        conn.close()

    return {"status":"success"}



#deletes user from tblusercredentials
#arg: username, returns: staus message
def delete_user_credentials(username):

    #open connection to database
    conn = get_connection()
    #disable autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT 1 FROM tblusercredentials
                        WHERE username = %s""",
                        (str(username),))

            #verify if user record was found
            if cur.fetchone() is None:
                raise ValueError(f"{username} does not exist")

            cur.execute("""DELETE FROM tblusercredentials 
                           WHERE username = %s""",
                           (str(username),))

    except Exception as e:
        #rollback in case of data validity issues
        conn.rollback()
        raise e

    finally:
        #close connection
        conn.close()

    return {"status":"success"}

#function sends the email with the recovery token to the user
#args: username(Email address), raw_token, Returns True(Sent) or False(Not Sent)
def send_recovery_email(username, raw_token):
    #creating variables for our email
    sender_email = "hawkeyeinventorysystems@gmail.com"
    app_password = "vduv utnk slzo idfr"

    #Create email to send
    subject = "Password Recovery Code"
    body = f"Hello,\n\nYour recovery code is {raw_token}\n\nThis token will expire in 15 minutes."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = username

    try:
        #connect to Gmail's SMTP server on port 587
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


#function to reset password if forgotten
#arg: username, returns: success message
def password_recovery(username):

    #open connection
    conn = get_connection()
    #disable autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            cur.execute(""" 
                        Select 1 
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

            cur.execute("""
                        UPDATE tblusercredentials
                        SET token = %s, tokenexpiration = %s
                        WHERE username = %s
                        """,(token_hash, token_expiration),str(username))

            #commit changes
            conn.commit()

            email_sent = send_recovery_email(username, raw_token)

            if email_sent:
                return token_hash

            else:
                return None

    except Exception as e:
        #roll back in case of error
        conn.rollback()
        raise e

    finally:
        #Close connection to allow update_user_password to connect to DB
        conn.close()




#verifies the token from the user for password recovery
#args: user name and token, returns: {"status":"success"}
def verify_token_password_reset(username, token):

    #open connection
    conn = get_connection()
    #disable autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT * FROM tblusercredentials
                        WHERE username = %s""",
                        (str(username),))

            row = cur.fetchone()

            if row is None:
                raise ValueError(f"{username} does not exist")

            """Add in the part to check the token and expiration here"""
            #checks token_hash abd expiration
            stored_token_hash = row[4]
            expiration_time = row[5]

            if stored_token_hash == token and datetime.now() < expiration_time:

                # create temp password to pass to the reset password function
                temp_password = "TempPassword123!"

                # hash password
                password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())

                cur.execute("""
                        UPDATE tblusercredentials
                        SET password = %s
                        WHERE username = %s""",
                        (password_hash, str(username),))

            # commit changes
            conn.commit()

        #close connection
        conn.close()

        return password_hash

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        #Ensure connection closed in case of error
        if conn and conn.is_connected():
            conn.close()

#create session token when user logs in
def create_session(username):
    conn = get_connection()
    conn.autocommit = False

    try:
        #creats session token and experiation
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


"""tblfinishedgoods functions"""

# Adds a new finished to tblfinishedgoods,
# arg:finishedgoodname, returns: finishedgoodid
def add_finished_good(finished_good_name):

    # Open a database connection
    conn = get_connection()
    # Disable autocommit so we can control transactions
    conn.autocommit = False

    try:
        # Create a cursor for executing SQL statements
        with conn.cursor() as cur:

            # Check if the FinishedGoodName exists
            cur.execute("""
                        SELECT 1
                        FROM tblfinishedgoods
                        WHERE finishedgoodname = %s
                    """, (str(finished_good_name),))

            #If A row is returned, the FinishedGoodName already exists in the table
            if cur.fetchone() is not None:
                raise ValueError(f"Finished Good '{finished_good_name}' Already Exists")

            #Generate a new UUIDv7
            new_id = uuid6.uuid7()

            #Insert new record, passing in both the UUID and FinishedGoodName
            cur.execute("""
                INSERT INTO tblfinishedgoods 
                    (finishedgoodid, finishedgoodname)
                Values (%s, %s)""",
                        (str(new_id), str(finished_good_name)))

        #If everything passed commit the change
        conn.commit()

    except Exception as e:
        #Rollback in case of error to maintain data integrity
        conn.rollback()
        raise e

    finally:
        conn.close()

    #Why status return and not a value or a boolean value
    return {"status":"success"}

#Deletes a finished good entry from tblfinishedgoods,
# arg:finishedgoodname, returns: success status
def delete_finished_good(finished_good_name): #Can add an id argument if needed

    #Open a Database connection
    conn = get_connection()
    #Disable autocommit
    conn.autocommit = False

    try:
        #Create a cursor for executing SQL statements
        with conn.cursor() as cur:

            # Check that the FinishedGoodName exists
            cur.execute("""
                    SELECT 1
                    FROM tblfinishedgoods
                    WHERE finishedgoodname = %s
                """, (str(finished_good_name),))

            # If no row is returned, the ID is invalid
            if cur.fetchone() is None:
                raise ValueError("Finished good not found")

            #Delete finished good name record
            cur.execute("""
                DELETE FROM tblfinishedgoods 
                WHERE finishedgoodname = %s
                """, (str(finished_good_name),))

        #Commit the transaction
        conn.commit()

    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        raise e

    finally:
        #close the connection
        conn.close()

    return {"status": "success"}

#Searches tblfinishedgoods for a finished good name
#arg: finishedgoodname returns: finishedgoodid
def get_finished_good(finished_good_name):

    #Open Database Connection
    conn = get_connection()
    #Disable Autocommit
    conn.autocommit = False

    try:
        #Create Cursor for executing SQL statements
        with conn.cursor() as cur:

            # Execute search query
            cur.execute("""
                    SELECT finishedgoodid 
                    FROM tblfinishedgoods 
                    WHERE finishedgoodname = %s
                """, (str(finished_good_name),))

            # Fetch the result
            result = cur.fetchone()

            # If result is None, the product was not found
            if result is None:
                return None

            # result is a tuple, e.g., (UUID('...'),)
            # Return the first element (the ID)
            return result[0]

    except Exception as e:
        # No rollback strictly needed for a SELECT, but good practice
        conn.rollback()
        print(f"Error searching for finished good: {e}")
        raise e

    finally:
        #close the connection
        conn.close()





"""TblProductionInventory Functions"""


#Adds inventory quantity to finished good, if no finishedgood record exists, adds part and quantity to table
#args: finishedgoodid, quantity, returns success statement
def add_inventory(finished_good_id, quantity):

    #Open a database connection
    conn = get_connection()
    #Disable autocommit so we can control transactions
    conn.autocommit = False

    try:
        #Create a cursor for executing SQL statements
        with conn.cursor() as cur:

            #Check that the FinishedGoodID exists
            cur.execute("""
                SELECT 1
                FROM tblfinishedgoods
                WHERE finishedgoodid = %s
            """, (str(finished_good_id),))

            #If no row is returned, the ID is invalid
            if cur.fetchone() is None:
                raise ValueError("Finished good not found")

            #Insert a new inventory record or update the existing one
            cur.execute("""
                INSERT INTO tblproductioninventory
                    (finishedgoodid, intavailableparts)
                VALUES (%s, %s)
                ON CONFLICT (finishedgoodid)
                DO UPDATE SET intavailableparts =
                    tblproductioninventory.intavailableparts
                    + EXCLUDED.intavailableparts
            """, (
                str(finished_good_id), quantity,))

        #Commit the transaction if everything succeeded
        conn.commit()

    except Exception as e:
        #Roll back database changes for known errors
        conn.rollback()
        raise e

    finally:
        #Always close the database connection
        conn.close()

    #Return success response
    return {"status": "success"}

#Deletes
def delete_inventory(finished_good_id, quantity_to_subtract):

    #open database connection
    conn = get_connection()
    #turn off autocommit
    conn.autocommit = False

    try:
        #create cursor to excute SQL commands
        with conn.cursor() as cur:

            # Check that the FinishedGoodID exists in tblfinishedgoods
            cur.execute("""
                    SELECT intavailableparts
                    FROM tblproductioninventory
                    WHERE finishedgoodid = %s
                """, (str(finished_good_id),))

            #Save record if found
            result = cur.fetchone()

            # If no row is returned, the ID is not in the inventory table
            if result is None:
                raise ValueError(f"Finished good not found in inventory table")

            current_stock = result[0]

            #check stock amount
            if current_stock < quantity_to_subtract:
                raise ValueError(f"Insufficient stock current available parts {current_stock}")

            #If product exists and inventory amount is greater than the amount to remove, delete stock value
            cur.execute("""
                UPDATE tblproductioninventory
                SET intavailableparts = intavailableparts - %s
                WHERE finishedgoodid = %s
                """, (quantity_to_subtract, str(finished_good_id),))

            #Commit the transaction
            conn.commit()

    except Exception as e:
        #rollback if any other errors happen
        conn.rollback()
        print(f"Transaction failed: {e}")
        raise e

    finally:
        #close connection
        conn.close()

    return {"status": "success"}

#searches the available inventory for a given finishedgoodid
#arg: finished_good_id, returns:inventory value if any
def get_inventory(finished_good_id):

    #open connection
    conn = get_connection()
    #turn off autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            #Query tblproductioninventory for available quantity
            cur.execute("""
                SELECT intavailableparts
                FROM tblproductioninventory
                WHERE finishedgoodid = %s
                """, (str(finished_good_id),))

            #records information from indicated row
            result = cur.fetchone()

            #check if finishedgoodid exists in table
            if result is None:
                raise ValueError(f"Finished good not found in inventory table")

            current_stock = result[0]

            #verify stock amount is valid
            if current_stock < 0:
                raise ValueError(f"Insufficient stock current available parts {current_stock}")

            return current_stock

    finally:
        #Close connection
        conn.close()







"""---anything beyond this is simply code for testing purposes---"""

"""def reset_test_database():
    #Clears all data from the tables to ensure a clean state for testing.
    conn = get_connection()
    # Disable autocommit to ensure atomic clearing
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            # List all tables you want to wipe
            # RESTART IDENTITY resets any SERIAL auto-increment counters to 1
            # CASCADE handles foreign key dependencies
            cur.execute(""""""
                TRUNCATE TABLE
                    tblusercredentials,
                    tblproductioninventory,
                    tblfinishedgoods
                RESTART IDENTITY CASCADE;
            """""")
            conn.commit()
            print("[INFO] Database reset successful.")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Database reset failed: {e}")
        raise e
    finally:
        conn.close()

# --- TEMPORARY MAIN FOR TESTING ---
#set back db call before commenting this out
if __name__ == "__main__":
    # RESET EVERYTHING FIRST
    print("--- Resetting Database Environment ---")
    reset_test_database()
    
    test_product = "Pokemon Cards"

    try:
        # 1. Setup: Add Product
        print("--- Testing Product Management ---")
        pid = add_finished_good(test_product)
        print(f"[SUCCESS] Product added: {pid}")

        # 2. Test: Add Inventory (Initial & Update)
        print("\n--- Testing Add Inventory ---")
        pid = get_finished_good(test_product)
        add_inventory(pid, 50)
        stock_1 = get_inventory(pid)
        print(f"Initial stock (expected 50): {stock_1}")

        add_inventory(pid, 25)
        stock_2 = get_inventory(pid)
        print(f"Updated stock (expected 75): {stock_2}")

        # 3. Test: Delete/Subtract Inventory
        print("\n--- Testing Subtract Inventory ---")
        delete_inventory(pid, 20)
        stock_3 = get_inventory(pid)
        print(f"Stock after subtracting 20 (expected 55): {stock_3}")

        # 4. Test: Over-subtraction (Should fail)
        print("\n--- Testing Insufficient Stock Error ---")
        try:
            delete_inventory(pid, 100)
        except ValueError as e:
            print(f"[EXPECTED ERROR] {e}")

        # 5. Cleanup: Delete Product
        print("\n--- Testing Cleanup ---")
        # Because of ON DELETE CASCADE in your SQL,
        # deleting the product also clears the inventory table!
        delete_finished_good(test_product)

        final_search = get_finished_good(test_product)
        print(f"Final product check (expected None): {final_search}")

    except Exception as error:
        print(f"Test failed: {error}")

# --- Testing User Credentials ---
    print("\n--- Testing User Management ---")
    try:
        # 1. Add User
        print("Adding test user...")
        add_user_credentials("test_admin3@gmail.com", "AdminPass123!", True)

        # 2. Verify Login
        print("Verifying login...")
        login = user_login_verification("test_admin3@gmail.com", "AdminPass123!")
        print(f"Login result: {login}")

        # 3. Password Recovery
        print("Running password recovery...")
        recovery = password_recovery("test_admin3@gmail.com")
        print(f"Recovery status: {recovery}")

        # 5. Cleanup User
        delete_user_credentials("test_admin@gmail.com")
        print("Test user deleted.")

    except Exception as e:
        print(f"User test failed: {e}")

# --- Testing Search & Inventory Joins ---
    print("\n--- Testing Search Functions ---")
    try:
        # 1. Setup a product for searching
        search_target = "Holographic Charizard"
        add_finished_good(search_target)
        target_id = get_finished_good(search_target)
        add_inventory(target_id, 10)

        # 2. Test: search_finished_by_name (Case-Insensitive check)
        print("Testing: search_finished_by_name('holographic')...")
        name_results = search_finished_by_name("holographic")
        print(f"Results found: {len(name_results)}")
        for item in name_results:
             print(f" - Found Item: {item['FinishedGoodName']} (ID: {item['FinishedGoodID']})")

        # 3. Test: search_inventory_by_name (The INNER JOIN check)
        print("\nTesting: search_inventory_by_name('Charizard')...")
        inv_results = search_inventory_by_name("Charizard")
        if inv_results:
            print(f"Inventory Join Success: {inv_results[0]['FinishedGoodName']} has {inv_results[0]['AvailableInventory']} in stock.")
        else:
            print("[FAILURE] No inventory join results found.")

        # 4. Test: search_inventory_by_id (Integer/UUID casting check)
        print(f"\nTesting: search_inventory_by_id for ID {target_id}...")
        id_inv_results = search_inventory_by_id(str(target_id))
        print(f"ID Search Results: {id_inv_results}")

        # Cleanup search target
        delete_finished_good(search_target)

    except Exception as e:
        print(f"Search test failed: {e}")
"""