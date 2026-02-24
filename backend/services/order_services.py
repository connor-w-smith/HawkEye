from psycopg2.extras import RealDictCursor

from db import get_connection

def create_new_order(finishedgoodid: str, target_quantity: int, sensor_id: str | None = None):
    """
    Creates a new production order in tblproductiondata.
    The database trigger automatically creates a corresponding tracking row in tblactiveproduction.

    Args:
        finishedgoodid (str): UUID of the product to produce
        target_quantity (int): How many parts to produce
        sensor_id (str | None): Optional ID of the sensor assigned to this order. If provided, only this sensor will update this order.

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
            INSERT INTO tblproductiondata (finishedgoodid, partsproduced, target_quantity, sensor_id)
            VALUES (%s, 0, %s, %s)
            RETURNING orderid
            """

            cur.execute(query, (finishedgoodid, target_quantity, sensor_id))

            result = cur.fetchone()
            orderid = result["orderid"]

            conn.commit()

        return {
            "status": "success",
            "message": f"Production order created",
            "orderid": orderid,
            "target_quantity": target_quantity,
            "sensor_id": sensor_id
        }

    except Exception as e:
        conn.rollback()
        return {"status":"error", "message": str(e)}


    finally:
        conn.close()
