import psycopg2
from db import get_connection





"""Function Directory"""
# def get_finished_good_table():
# def get_production_inventory_table():
# def get_production_data_table():
# def get_production_data_table():



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





