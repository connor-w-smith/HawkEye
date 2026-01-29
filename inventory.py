from db import get_connection

###use for manual entry
#curl -X POST http://127.0.0.1:8000/manual-entry \
#  -H "Content-Type: application/json" \
#  -d '{
#    "finished_good_id": "***Put Real UUID here***",
#    "quantity": 5
#  }'

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
