import uuid6

from db import get_connection

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
        #create cursor to execute SQL commands
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