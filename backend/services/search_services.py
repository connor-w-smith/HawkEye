from ...db import get_connection



"""Finished Good Table Searches"""


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



"""Inventory Table Searches"""

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

"""ProductionData Table Searches"""
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
            # Format DB results as list of dicts for JSON serialization
            orders = [
                {"orderid": r[0], "partsproduced": r[1], "productionstartdate": r[2], "productionenddate": r[3]}
                for r in rows
            ]
            return orders
    finally:
        if conn:
            conn.close()

"""Raw Material Table Searches"""
#TODO: correct these when the logic is figured out (Static output in the interim)
def get_raw_material_recipe(finishedgoodid):
    output_data = [
        {'Raw Material ID': 1, 'Raw Material Name': 'Sheet Metal', 'Consumption Per Part Produced': 4},
        {'Raw Material ID': 2, 'Raw Material Name': 'Bolt', 'Consumption Per Part Produced': 8},
    ]
    return output_data

"""Active Production Table Searches"""
#TODO: correct when logic is figured out
def get_current_orders(finishedgoodid):
    # Temporary: show something for every finished_good
    all_orders = [
        {"FinishedGoodID": finishedgoodid, "OrderID": 1234, "SensorID": 1357, "PartsMade": 10},
        {"FinishedGoodID": finishedgoodid, "OrderID": 5678, "SensorID": 2468, "PartsMade": 250},
    ]
    return all_orders