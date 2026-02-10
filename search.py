from db import get_connection



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

#gets the inventory associated with a finishedgoodid
def get_production_inventory_by_finishedgoodid(finishedgoodid):
    #open connection
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            #db query
            cursor.execute("""SELECT fg.finishedgoodname, pi.intavailableparts FROM tblproductioninventory pi
                                JOIN tblfinishedgoods fg ON pi.finishedgoodid = fg.finishedgoodid
                                WHERE pi.finishedgoodid = %s""", (finishedgoodid,))

            result = cursor.fetchone()

            if not result:
                raise ValueError(f"No data found in production inventory table")

            return result

    #raise any DB errors
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        raise

    #close connection
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


def get_orders_by_finishedgoodid(finishedgoodid):
    #db connection
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""Select productionstartdate, productionenddate, orderid, partsproduced
                            FROM tblproductiondata where finishedgoodid = %s""",(finishedgoodid,))

            orders = cursor.fetchall()

            if not orders:
                raise ValueError(f"No data found for this product in production data table")

            else:
                return orders

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        raise

    finally:
        if conn:
            conn.close()


#TODO: correct these when the logic is figured out (Static output in the interim
def get_raw_material_recipe(finishedgoodid):

    output_data = {
        'Raw Material ID': [1,2],
        'Raw Material Name': ['Sheet Metal','Bolt'],
        'Consumption Per Part Produced': [4,8]
    }

    #Create table
    output_data = pd.DataFrame(output_data)

    return output_data


def get_current_orders(finishedgoodid):

    output_data = {
        'Order ID': [1234,5678],
        'Sensor ID': [1357,2468],
        'Parts Made': [10,250]
    }

    #create table
    output_data = pd.DataFrame(output_data)

    return output_data

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




