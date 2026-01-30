import uuid6
from db import get_connection


###use for manual entry
#curl -X POST http://127.0.0.1:8000/manual-entry \
#  -H "Content-Type: application/json" \
#  -d '{
#    "finished_good_id": "***Put Real UUID here***",
#    "quantity": 5
#  }'


"""tblfinishedgoods functions"""

# Adds a new finished to tblfinishedgoods, arg:finishedgoodname
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
    return new_id

#Deletes a finished good entry from tblfinishedgoods, arg:finishedgoodname
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

    #If return needed add here

#Searches tblfinishedgoods for a finished good name,arg: finishedgoodname returns: finishedgoodid
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
            """, (str(entry.finished_good_id),))


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
                str(entry.finished_good_id), quantity))

        #Commit the transaction if everything succeeded
        conn.commit()

    except HTTPException:
        #Roll back database changes for known errors
        conn.rollback()
        raise

    finally:
        #Always close the database connection
        conn.close()

    #Return success response
    return {"status": "entry recorded"}

"""
# --- TEMPORARY MAIN FOR TESTING ---
#set back db call before commenting this out
if __name__ == "__main__":
    test_product = "HawkEye Pro Widget"

    # 1. Add it
    new_id = add_finished_good(test_product)
    print(f"Added {test_product} with ID: {new_id}")

    # 2. Search for it
    found_id = get_finished_good(test_product)
    print(f"Found ID via search: {found_id}")

    # 3. Delete it
    delete_finished_good(test_product)

    # 4. Verify it's gone
    final_check = get_finished_good(test_product)
    print(f"Search after delete (should be None): {final_check}")
"""