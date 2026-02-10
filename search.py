from db import get_connection



"""Function Directory"""

# def search_finished_by_name(finished_name: str): Returns output{FinishedGoodID, FinishedGoodName}
# def search_finished_by_id(finished_id: str): Returns output{FinishedGoodID, FinishedGoodName}
# def search_inventory_by_id(finished_id: str): Returns output{{FinishedGoodID, FinishedGoodName, AvailableInventory}
# def search_inventory_by_name(finished_name: str): Returns output{{FinishedGoodID, FinishedGoodName, AvailableInventory}

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


