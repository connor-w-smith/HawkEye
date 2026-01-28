from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import uuid

###use uvicorn to start FastAPI
#uvicorn manualEntry:app --reload

###code to open psql for database
#psql -h 98.92.53.251 -U postgres -d postgres

###use for manual entry
#curl -X POST http://127.0.0.1:8000/manual-entry \
#  -H "Content-Type: application/json" \
#  -d '{
#    "finished_good_id": "***Put Real UUID here***",
#    "quantity": 5
#  }'


#Create the FastAPI application
app = FastAPI()

#Database connection config
DB_CONFIG = {
    "host": "98.92.53.251",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "pgpass"
}

#Pydantic model that defines the expected JSON body
#FastAPI automatically validates incoming requests against this model
class ManualEntry(BaseModel):
    finished_good_id: uuid.UUID  #UUID of the finished good
    quantity: int                #Quantity to add manually

#Helper function to create a database connection
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

#POST endpoint for manual inventory entry
@app.post("/manual-entry")
def manual_entry(entry: ManualEntry):

    # Basic business rule validation
    if entry.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be positive"
        )

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
                raise HTTPException(
                    status_code=404,
                    detail="Finished good not found"
                )

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
                str(entry.finished_good_id),
                entry.quantity
            ))


        #Commit the transaction if everything succeeded
        conn.commit()

    except HTTPException:
        #Roll back database changes for known errors
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        print("DATABASE ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        #Always close the database connection
        conn.close()

    #Return success response
    return {"status": "manual entry recorded"}
