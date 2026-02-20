from psycopg2.extras import RealDictCursor

from db import get_connection

def create_new_order(finishedgoodid: str, target_quantity: int):
    """
    Creates a new production order in tblproductiondata.
    The database trigger automatically creates a corresponding tracking row in tblactiveproduction.

    Args:
        finishedgoodid (str): UUID of the product to produce
        target_quantity (int): How many parts to produce

    Returns:
        dict: {"status": "success", "orderid": order_id_value}
    """
    #create connection
    conn = get_connection()

    #Turn off auto commit
    conn.autocommit = False

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            query = """
            INSERT INTO tblproductiondata (finishedgoodid, partsproduced, target_quantity)
            VALUES (%s, 0, %s)
            RETURNING orderid
            """

            cur.execute(query, (finishedgoodid, target_quantity))

            result = cur.fetchone()
            orderid = result["orderid"]

            conn.commit()

        return {
            "status": "success",
            "message": f"Production order created",
            "orderid": orderid,
            "target_quantity": target_quantity
        }

    except Exception as e:
        conn.rollback()
        return {"status":"error", "message": str(e)}


    finally:
        conn.close()
