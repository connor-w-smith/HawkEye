import uuid6
from  db import get_connection


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



"TblProductionInventory Functions"
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
    return {"status": "entry recorded"}

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

    return {"status": "entry recorded"}

#returns the available inventory for a given finishedgoodid
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




"""
# --- TEMPORARY MAIN FOR TESTING ---
#set back db call before commenting this out
if __name__ == "__main__":
    test_product = "HawkEye Pro Widget"

    try:
        # 1. Setup: Add Product
        print("--- Testing Product Management ---")
        pid = add_finished_good(test_product)
        print(f"[SUCCESS] Product added: {pid}")

        # 2. Test: Add Inventory (Initial & Update)
        print("\n--- Testing Add Inventory ---")
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
"""