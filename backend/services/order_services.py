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

            material_quantity_query = """
                WITH CurrentOrderRequirement AS (   
                    SELECT materialid, quantity_required
                    FROM tblrecipes
                    WHERE finishedgoodid = %s
                ),
                TotalActiveDemand AS (
                    SELECT tr.materialid, SUM(pd.target_quantity * tr.quantity_required) AS planned_qty
                    FROM tblproductiondata pd
                    JOIN tblrecipes tr ON pd.finishedgoodid = tr.finishedgoodid
                    JOIN tblactiveproduction ap ON pd.orderid = ap.orderid
                    WHERE ap.end_time IS NULL
                    GROUP BY tr.materialid
                )
                SELECT 
                    rm.materialid,
                    rm.material_name,
                    -- (Quantity for THIS order) + (Total already reserved)
                    ((cor.quantity_required * %s) + COALESCE(gad.planned_qty, 0)) AS total_required,
                    rm.quantity_in_stock
                FROM CurrentOrderRequirement cor
                JOIN tblrawmaterials rm ON cor.materialid = rm.materialid
                LEFT JOIN TotalActiveDemand gad ON cor.materialid = gad.materialid
            """

            cur.execute(material_quantity_query, (finishedgoodid, target_quantity))
            requirements = cur.fetchall()

            shortages = []
            for item in requirements:
                if item['total_required'] > item['quantity_in_stock']:
                    shortages.append({
                        "material_name": item['material_name'],
                        "required": item['total_required'],
                        "available": item['quantity_in_stock'],
                        "short_by": item['total_required'] - item['quantity_in_stock']
                    })

            if shortages:
                conn.rollback()
                return{
                    "status": "error",
                    "message": "Insufficient raw materials including planned orders.",
                    "shortages": shortages
                }


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


def edit_completed_order(orderid: str, partsproduced: int, start_time: str, end_time: str):
    """
    Updates a completed production order:
    - partsproduced (tblproductiondata)
    - start_time, end_time (tblactiveproduction)
    
    start_time and end_time should be ISO strings (e.g., '2026-03-07T10:00')
    """
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Update parts produced
            cur.execute("""
                UPDATE tblproductiondata
                SET partsproduced = %s
                WHERE orderid = %s
            """, (partsproduced, orderid))

            # Update start_time / end_time
            cur.execute("""
                UPDATE tblactiveproduction
                SET start_time = %s,
                    end_time = %s
                WHERE orderid = %s
            """, (start_time, end_time, orderid))

            conn.commit()
            return {"status": "success"}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}

    finally:
        conn.close()

def create_completed_order(finishedgoodid: str, partsproduced: int, start_time: str, end_time: str):
    """
    Creates a completed production order.
    Inserts a new row in tblproductiondata and tblactiveproduction with
    partsproduced, start_time, and end_time.

    Args:
        finishedgoodid (str): UUID of the finished good
        partsproduced (int): Number of parts produced
        start_time (str): ISO string start time
        end_time (str): ISO string end time

    Returns:
        dict: {"status": "success", "orderid": ...} or {"status": "error", "message": ...}
    """
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Insert into tblproductiondata
            cur.execute("""
                INSERT INTO tblproductiondata (finishedgoodid, partsproduced, target_quantity, sensor_id)
                VALUES (%s, %s, %s, NULL)
                RETURNING orderid
            """, (finishedgoodid, partsproduced, partsproduced))  # target_quantity = partsproduced for completed orders

            result = cur.fetchone()
            orderid = result["orderid"]

            # Insert corresponding row in tblactiveproduction
            cur.execute("""
                INSERT INTO tblactiveproduction (orderid, start_time, end_time)
                VALUES (%s, %s, %s)
            """, (orderid, start_time, end_time))

        conn.commit()
        return {
            "status": "success",
            "message": "Completed order created",
            "orderid": orderid,
            "partsproduced": partsproduced,
            "start_time": start_time,
            "end_time": end_time
        }

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