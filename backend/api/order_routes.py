

@router.get("/production-data/{finished_good_id}")
def read_order_history(finished_good_id: str):
    try:
        return get_orders_by_finishedgoodid(finished_good_id)
    except Exception:
        return []


@router.get("/production-data/current-orders/{finished_good_id}")
def read_current_order_table(finished_good_id: str):
    try:
        df = get_current_orders(finished_good_id)
        return {"current_orders": df.to_dict(orient="records")}
    except Exception:
        return {"current_orders": []}

#TODO: Break this apart and add DB portion to order_services file
def create_production_order(finishedgoodid: str, target_quantity: int):
    """
    Creates a new production order in tblproductiondata.
    The database trigger automatically creates a corresponding tracking row in tblactiveproduction.

    Args:
        finishedgoodid (str): UUID of the product to produce
        target_quantity (int): How many parts to produce

    Returns:
        dict: {"status": "success", "orderid": order_id_value}
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Insert new production order with partsproduced starting at 0
        # The trigger automatically creates the tblactiveproduction row
        cur.execute("""
            INSERT INTO tblproductiondata (finishedgoodid, partsproduced, target_quantity)
            VALUES (%s, 0, %s)
            RETURNING orderid
        """, (finishedgoodid, target_quantity))

        orderid = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": f"Production order created",
            "orderid": orderid,
            "target_quantity": target_quantity
        }

    except Exception as e:
        print(f"Error creating production order: {e}")
        raise Exception(f"Failed to create production order: {str(e)}")