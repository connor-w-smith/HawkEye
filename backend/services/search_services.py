import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

from db import get_connection



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

def get_orders_by_finishedgoodid(finishedgoodid, days):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pd.orderid,
                    pd.partsproduced,
                    TO_CHAR(ap.start_time, 'YYYY-MM-DD HH24:MI') AS productionstartdate,
                    TO_CHAR(ap.end_time, 'YYYY-MM-DD HH24:MI') AS productionenddate
                FROM tblproductiondata pd
                JOIN tblactiveproduction ap
                    ON pd.orderid = ap.orderid
                WHERE pd.finishedgoodid = %s
                AND ap.start_time >= NOW() - (%s * INTERVAL '1 day')
                ORDER BY ap.start_time DESC
            """, (finishedgoodid, days))

            rows = cursor.fetchall()

            orders = [
                {
                    "orderid": r[0],
                    "partsproduced": r[1],
                    "productionstartdate": r[2],
                    "productionenddate": r[3]
                }
                for r in rows
            ]

            return orders

    finally:
        conn.close()


"""Active Production Table Searches"""
#Pulls orders that are active and have a start time
def get_currently_packaging():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    pd.orderid, 
                    fg.finishedgoodname, 
                    pd.sensor_id, 
                    pd.partsproduced
                FROM tblproductiondata pd
                JOIN tblfinishedgoods fg ON pd.finishedgoodid = fg.finishedgoodid
                JOIN tblactiveproduction ap ON pd.orderid = ap.orderid
                WHERE ap.is_active = TRUE
            """)
            return cursor.fetchall()
    finally:
        conn.close()

#TODO: correct this function to sort by isactive
def get_current_finishedgood_orders(finishedgoodid):
    #open connection
    conn = get_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """SELECT 
                        pd.orderid, 
                        fg.finishedgoodname, 
                        pd.sensor_id, 
                        pd.partsproduced
                    FROM tblproductiondata pd
                    JOIN tblfinishedgoods fg ON pd.finishedgoodid = fg.finishedgoodid
                    JOIN tblactiveproduction ap ON pd.orderid = ap.orderid
                    WHERE fg.finishedgoodid = %s ;"""

            cursor.execute(query, (finishedgoodid,))
            results = cursor.fetchall()

            return results

    except Exception as e:
        raise e

    finally:
        conn.close()

"""Returns all completed orders with date filter (Defaults to 7 days)"""
def get_completed_orders(timeframe_days=7):
    #calculate start date for time frame
    start_date = datetime.now() - timedelta(days=timeframe_days)

    #Open connection
    conn = get_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """SELECT 
                        pd.orderid, 
                        pd.sensor_id,
                        fg.finishedgoodname, 
                        pd.partsproduced,
                        FROM tblproductiondata pd
                        JOIN tblfinishedgoods fg ON pd.finishedgoodid = fg.finishedgoodid
                        JOIN tblactiveproduction ap ON pd.orderid = ap.orderid
                        WHERE ap.is_active = false AND pd.productionenddate >= %s;
                    """
            cursor.execute(query, (start_date,))

            return cursor.fetchall()

    except Exception as e:
        raise e

    finally:
        conn.close()

def get_upcoming_orders():
    #open connection
    conn = get_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT 
                    ap.orderid,
                    fg.finishedgoodname,
                    ap.sensor_id,
                    ap.target_quantity
                FROM tblactiveproduction ap
                JOIN tblproductiondata pd 
                    ON ap.orderid = pd.orderid
                JOIN tblfinishedgoods fg 
                    ON pd.finishedgoodid = fg.finishedgoodid
                WHERE ap.is_active = TRUE 
                AND ap.start_time IS NULL;
            """

            cursor.execute(query)
            return cursor.fetchall()

    except Exception as e:
        raise e

    finally:
        conn.close()


def get_sensor_production_amounts():
    conn = get_connection()
    query = """
            SELECT 
                pd.sensor_id,
            -- Sum parts where the timestamp is within the last hour
            SUM(CASE 
                WHEN ap.last_processed_timestamp >= NOW() - INTERVAL '1 hour' THEN pd.partsproduced 
                ELSE 0 
            END):: INTEGER AS production_last_1h,
    
            -- Sum parts where the timestamp is within the last 24 hours
            SUM(CASE 
                WHEN ap.last_processed_timestamp >= NOW() - INTERVAL '24 hours' THEN pd.partsproduced 
                ELSE 0 
            END)::INTEGER AS production_last_24h
            FROM tblproductiondata pd
            JOIN tblactiveproduction ap ON pd.orderid = ap.orderid
            WHERE pd.sensor_id IS NOT NULL
                AND TRIM(LOWER(pd.sensor_id)) != 'n/a'  -- Removes spaces and handles 'N/A', 'n/a', ' n/a '
                AND pd.sensor_id != ''  
            GROUP BY pd.sensor_id;
        """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    except Exception as e:
        raise e

    finally:
        conn.close()


def get_finished_goods_with_quantities():
    """
    Returns all finished goods with their total parts produced from tblproductiondata.
    """
    conn = get_connection()
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    fg.finishedgoodid,
                    fg.finishedgoodname,
                    COALESCE(SUM(pd.partsproduced), 0) AS total_quantity
                FROM tblfinishedgoods fg
                LEFT JOIN tblproductiondata pd ON fg.finishedgoodid = pd.finishedgoodid
                GROUP BY fg.finishedgoodid, fg.finishedgoodname
                ORDER BY fg.finishedgoodname
            """)
            
            rows = cur.fetchall()
            
            return [
                {
                    "FinishedGoodID": r[0],
                    "FinishedGoodName": r[1],
                    "Quantity": int(r[2])
                }
                for r in rows
            ]
    
    finally:
        conn.close()
        
#for product page yarrrrr
def get_active_order_for_finishedgood(finishedgoodid):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    pd.orderid,
                    fg.finishedgoodname,
                    ap.sensor_id,
                    pd.partsproduced,
                    ap.target_quantity
                FROM tblproductiondata pd
                JOIN tblfinishedgoods fg ON pd.finishedgoodid = fg.finishedgoodid
                JOIN tblactiveproduction ap ON pd.orderid = ap.orderid
                WHERE fg.finishedgoodid = %s
                  AND ap.is_active = TRUE
            """, (finishedgoodid,))
            return cursor.fetchall()
    finally:
        conn.close()

def get_completed_orders(days: int):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    ap.orderid,
                    ap.sensor_id,
                    fg.finishedgoodname,
                    ap.target_quantity AS planproduction
                FROM tblactiveproduction ap
                JOIN tblproductiondata pd ON ap.orderid = pd.orderid
                JOIN tblfinishedgoods fg ON pd.finishedgoodid = fg.finishedgoodid
                WHERE ap.is_active = FALSE
                  AND ap.end_time >= NOW() - (%s * INTERVAL '1 day')
                ORDER BY ap.end_time DESC;
            """, (days,))
            return cursor.fetchall()
    finally:
        conn.close()

"""Sensor Page Search Functions"""
def get_active_order_for_sensor(sensorid):
    conn = get_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT 
                    ap.orderid,
                    fg.finishedgoodname,
                    ap.sensor_id,
                    pd.partsproduced,
                    ap.target_quantity
                FROM tblactiveproduction ap
                JOIN tblproductiondata pd 
                    ON ap.orderid = pd.orderid
                JOIN tblfinishedgoods fg 
                    ON pd.finishedgoodid = fg.finishedgoodid
                WHERE ap.sensorid = %s
                AND ap.is_active = TRUE;
            """

            cursor.execute(query, (sensorid,))
            results = cursor.fetchall()

            return results

    except Exception as e:
        raise e

    finally:
        conn.close()

def get_completed_orders_sensor(sensorid):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """ SELECT
                            ap.orderid,
                            pd.partsproduced,
                            pd.productionstartdate,
                            pd.productionenddate,
                            FROM tblactiveproduction ap
                            JOIN tblproductiondata pd 
                                ON ap.orderid = pd.orderid
                            WHERE ap.sensorid = %s 
                            AND ap.is_active = FALSE 
                            AND pd.productionstartdate IS NOT NULL; """

            cur.execute(query, (sensorid,))
            results = cur.fetchall()

            return results

    except Exception as e:
        raise e

    finally:
        conn.close()

def get_upcoming_orders_sensor(sensorid):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """ SELECT
                               ap.orderid,
                               fg.finishedgoodname,
                               pd.target_quantity,
                               FROM tblactiveproduction ap
                               JOIN tblproductiondata pd 
                                   ON ap.orderid = pd.orderid
                               JOIN tblfinishedgoods fg 
                                   ON pd.finishedgoodid = fg.finishedgoodid
                               WHERE ap.sensorid = %s 
                               AND ap.is_active = FALSE 
                               AND pd.productionstartdate IS NULL; """

            cur.execute(query, (sensorid,))
            results = cur.fetchall()

            return results

    except Exception as e:
        raise e