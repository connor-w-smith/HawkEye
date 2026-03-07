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
        return {"status": "error", "message": str(e)}


    finally:
        conn.close()

def delete_order(orderid: str):
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = "SELECT 1 FROM tblproductiondata WHERE orderid = %s"

            cur.execute(query, (orderid,))
            result = cur.fetchone()

            if result is None:
                return {"status": "error", "message": "Order not found"}

            cur.execute("DELETE FROM tblproductiondata WHERE orderid = %s", (orderid,))

            cur.execute("DELETE FROM tblactiveproduction WHERE orderid = %s", (orderid,))

        conn.commit()

        return {
            "status": "success",
        }

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}

    finally:
        conn.close()

def edit_order(orderid: str, finishedgoodid: str, target_quantity: int, sensor_id: str | None):
    """
    Updates an existing production order.
    finishedgoodid is ignored for tblactiveproduction because that column doesn't exist there.
    """
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Update tblproductiondata (has finishedgoodid)
            cur.execute("""
                UPDATE tblproductiondata
                SET target_quantity = %s,
                    sensor_id = %s
                WHERE orderid = %s
            """, (target_quantity, sensor_id, orderid))

            # Update tblactiveproduction (no finishedgoodid column)
            cur.execute("""
                UPDATE tblactiveproduction
                SET target_quantity = %s,
                    sensor_id = %s
                WHERE orderid = %s
            """, (target_quantity, sensor_id, orderid))

            conn.commit()

            return {"status": "success"}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}

    finally:
        conn.close()
"""

    # Lines below were added by Chase to be more verbose on output for failed order creation
    NOT READY TO BE DEPLOYED YET. (check line 72 in order_routes.py for detail)
    
    except psycopg2.IntegrityError as e:
        conn.rollback()
        error_msg = str(e)
        if 'unique_active_sensor_id' in error_msg:
            return {"status": "error", "detail": f"Sensor '{sensor_id}' already has an active production order. Complete or cancel the existing order before creating a new one."}
        return {"status": "error", "detail": f"Database constraint violation: {error_msg}"}
    
    except Exception as e:
        conn.rollback()
        return {"status": "error", "detail": str(e)}

    finally:
        conn.close()
"""