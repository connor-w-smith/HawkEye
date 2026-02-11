from db import get_connection
import psycopg2



"""Function Directory"""

# def search_finished_by_name(finished_name: str): Returns output{FinishedGoodID, FinishedGoodName}
# def search_finished_by_id(finished_id: str): Returns output{FinishedGoodID, FinishedGoodName}
# def search_inventory_by_id(finished_id: str): Returns output{{FinishedGoodID, FinishedGoodName, AvailableInventory}
# def search_inventory_by_name(finished_name: str): Returns output{{FinishedGoodID, FinishedGoodName, AvailableInventory}
# def get_finished_good_table():
# def get_production_inventory_table():
# def get_production_inventory_by_finishedgoodid(finishedgoodid):
# def get_production_data_table():
# def get_orders_by_finishedgoodid(finishedgoodid):

#TODO: correct these functions as the functions get working
# def get_current_orders(finishedgoodid):
# def get_current_orders(finishedgoodid):

# def get_user_credentials_table():
def search_finished_goods_fuzzy(search: str):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            if search == "":
                cur.execute("""
                    SELECT FinishedGoodID, FinishedGoodName
                    FROM tblFinishedGoods
                    ORDER BY FinishedGoodName
                """)
            else:
                like_pattern = f"%{search}%"

                cur.execute("""
                    SELECT FinishedGoodID, FinishedGoodName
                    FROM tblFinishedGoods
                    WHERE
                        CAST(FinishedGoodID AS TEXT) ILIKE %s
                        OR FinishedGoodName ILIKE %s
                    ORDER BY FinishedGoodName
                """, (like_pattern, like_pattern))

            rows = cur.fetchall()

            return [
                {
                    "FinishedGoodID": r[0],
                    "FinishedGoodName": r[1]
                }
                for r in rows
            ]

    finally:
        conn.close()

'''
#searches tblfinishedgoods using finishedgoodname
def search_finished_by_name(finished_name: str):
    #open db connection
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            #ILIKE is for case-insensitive and % is for wildcards
            query = ("""SELECT finishedgoodid, finishedgoodname
                     FROM tblfinishedgoods 
                     WHERE finishedgoodname ILIKE %s""")

            #format the search for wildcards
            like_pattern = f"%{finished_name}%"

            cursor.execute(query, (like_pattern,))

            #fetchall to get all matching results
            results = cursor.fetchall()

            #converting tuples to list of dictionary objects
            output = []
            for row in results:
                output.append({
                    "FinishedGoodID": row[0],
                    "FinishedGoodName": row[1]
                })

            return output

    except Exception as e:
        raise e

    finally:
        #ensure connection is closed
        conn.close()

#searches tblfinishedgoods by finishedgoodid
def search_finished_by_id(finished_id: str):
    #open db connection
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            #ILIKE is for case-insensitive and % is for wildcards
            query = ("""SELECT finishedgoodid, finishedgoodname 
                     FROM tblfinishedgoods 
                     WHERE finishedgoodid = %s""")

            cursor.execute(query, (finished_id,))

            #fetchall to get all matching results
            results = cursor.fetchall()

            #converting tuples to list of dictionary objects
            output = []
            for row in results:
                output.append({
                    "FinishedGoodID": row[0],
                    "FinishedGoodName": row[1]
                })

            return output

    except Exception as e:
        raise e

    finally:
        #ensure connection is closed
        conn.close()


def search_inventory_by_id(finished_id: str):
    #open db connection
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            #ILIKE is for case-insensitive and % is for wildcards
            query = ("""SELECT pi.finishedgoodid,fg.finishedgoodname, pi.intavailableparts 
                     FROM tblproductioninventory pi
                     INNER JOIN tblfinishedgoods fg on pi.finishedgoodid = fg.finishedgoodid
                     WHERE pi.finishedgoodid = %s""")


            cursor.execute(query, (finished_id,))

            #fetchall to get all matching results
            results = cursor.fetchall()

            #converting tuples to list of dictionary objects
            output = []

            for row in results:
                output.append({
                    "FinishedGoodID": row[0],
                    "FinishedGoodName": row[1],
                    "AvailableInventory": row[2]
                })

            return output

    except Exception as e:
        raise e

    finally:
        #ensure connection is closed
        conn.close()
'''

def search_inventory_by_name(finished_name: str):
    #open db connection
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            #ILIKE is for case-insensitive and % is for wildcards
            query = ("""SELECT fg.finishedgoodid, fg.finishedgoodname, pi.intavailableparts 
                     FROM tblfinishedgoods fg
                     INNER JOIN tblproductioninventory pi on fg.finishedgoodid = pi.finishedgoodid
                     WHERE fg.finishedgoodname ILIKE %s""")

            #format the search for wildcards
            like_pattern = f"%{finished_name}%"

            cursor.execute(query, (like_pattern,))

            #fetchall to get all matching results
            results = cursor.fetchall()

            #converting tuples to list of dictionary objects
            output = []
            for row in results:
                output.append({
                    "FinishedGoodID": row[0],
                    "FinishedGoodName": row[1],
                    "AvailableInventory": row[2]
                })

            return output

    except Exception as e:
        raise e

    finally:
        #ensure connection is closed
        conn.close()

def get_finished_good_by_id(finished_good_id: str):
    results = search_finished_by_id(finished_good_id)
    if not results:
        return None
    return results[0] 

#returns all columns from tblfinishedgoods
def get_finished_good_table():

    # connect to db
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            #db query
            cursor.execute("""SELECT finishedgoodid, finishedgoodname
                            FROM tblfinishedgoods""")

            #store found rows to be passed
            rows = cursor.fetchall()

            if not rows:
                raise ValueError(f"No data found in finished good table")

            else:
                return rows

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        raise

    finally:
        if conn:
            #close connection
            conn.close()

#Available Inventory by Part
def get_production_inventory_table():
    #open connection
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            #db query
            cursor.execute("""SELECT finishedgoodid, intavailableparts 
                            FROM tblproductioninventory""")

            rows = cursor.fetchall()

            if not rows:
                raise ValueError(f"No data found in production inventory table")

            else:
                return rows

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        raise

    finally:
        if conn:
            conn.close()

def get_orders_by_finishedgoodid(finishedgoodid):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT orderid, partsproduced, productionstartdate, productionenddate
                FROM tblproductiondata
                WHERE finishedgoodid = %s
            """, (finishedgoodid,))
            rows = cursor.fetchall()
            if not rows:
                # Return fake data for testing
                return [
                    {"orderid": 101, "partsproduced": 50, "productionstartdate": "2026-01-01", "productionenddate": "2026-01-02"},
                    {"orderid": 102, "partsproduced": 75, "productionstartdate": "2026-01-03", "productionenddate": "2026-01-04"},
                ]
            orders = [
                {"orderid": r[0], "partsproduced": r[1], "productionstartdate": r[2], "productionenddate": r[3]}
                for r in rows
            ]
            return orders
    finally:
        if conn:
            conn.close()



def get_production_data_table():
    #open db connection
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT orderid, partsproduced, productionstarttime, productionendtime, 
                            productionstartdate, productionenddate FROM tblproductiondata""")

            rows = cursor.fetchall()

            if not rows:
                raise ValueError(f"No data found in production data table")

            else:
                return rows

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        raise

    finally:
        if conn:
            conn.close()


def get_production_inventory_by_finishedgoodid(finishedgoodid):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT fg.finishedgoodname, pi.intavailableparts
                FROM tblproductioninventory pi
                JOIN tblfinishedgoods fg ON pi.finishedgoodid = fg.finishedgoodid
                WHERE pi.finishedgoodid = %s
            """, (finishedgoodid,))
            result = cursor.fetchone()
            if not result:
                return {"FinishedGoodName": "", "AvailableInventory": 0}

            return {"FinishedGoodName": result[0], "AvailableInventory": result[1]}
    finally:
        if conn:
            conn.close()



#TODO: correct these when the logic is figured out (Static output in the interim
def get_raw_material_recipe(finishedgoodid):
    output_data = [
        {'Raw Material ID': 1, 'Raw Material Name': 'Sheet Metal', 'Consumption Per Part Produced': 4},
        {'Raw Material ID': 2, 'Raw Material Name': 'Bolt', 'Consumption Per Part Produced': 8},
    ]
    return output_data



def get_current_orders(finishedgoodid):
    # Temporary: show something for every finished_good
    all_orders = [
        {"FinishedGoodID": finishedgoodid, "OrderID": 1234, "SensorID": 1357, "PartsMade": 10},
        {"FinishedGoodID": finishedgoodid, "OrderID": 5678, "SensorID": 2468, "PartsMade": 250},
    ]
    return all_orders



def get_user_credentials_table():
    # db connection
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT userid, username, password, isadmin
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






