"""
===========================================
material_services.py
===========================================
Purpose:
Handles all business logic for raw-material-related operations.

This file should:
- Connect to the database if needed
- Perform calculations or lookups
- Return data for the API routes

Called by:
api/material_routes.py
"""

from db import get_connection
"""
# TODO: Implement DB connection logic if needed
def get_raw_material_recipe(finished_good_id: str):
    """'''
    Returns the raw materials required for a given finished good.
    Currently returns placeholder data; replace with DB queries.
    '''"""
    return [
        {'Raw Material ID': 1, 'Raw Material Name': 'Sheet Metal', 'Consumption Per Part Produced': 4},
        {'Raw Material ID': 2, 'Raw Material Name': 'Bolt', 'Consumption Per Part Produced': 8},
    ]
"""
#def add_raw_recipe(material_name):
    
#def delete_raw_recipe(material_name):


#adds a new raw material
def add_raw_material(material_name: str, quantity: float, unit_of_measure: str):
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            #check if material already exists
            cur.execute("""
                SELECT 1
                FROM tblrawmaterial
                WHERE material_name = %s
            """, (str(material_name),))
            if cur.fetchone() is not None:
                raise ValueError(f"Raw material '{material_name}' already exists")

            #generate UUID
            new_id = uuid6.uuid7()

            #insert new raw material
            cur.execute("""
                INSERT INTO tblrawmaterial (materialid, material_name, quantity_in_stock, unit_of_measure, last_updated)
                VALUES (%s, %s, %s, %s, NOW())
            """, (str(new_id), str(material_name), quantity, str(unit_of_measure)))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

    return {"status": "success"}


#updates raw material quantity and/or unit_of_measure
def update_raw_material(material_name: str, quantity: float = None, unit_of_measure: str = None):
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            #check material exists
            cur.execute("""
                SELECT 1
                FROM tblrawmaterial
                WHERE material_name = %s
            """, (str(material_name),))
            if cur.fetchone() is None:
                raise ValueError(f"Raw material '{material_name}' not found")

            #update material
            cur.execute("""
                UPDATE tblrawmaterial
                SET 
                    quantity_in_stock = COALESCE(%s, quantity_in_stock),
                    unit_of_measure = COALESCE(%s, unit_of_measure),
                    last_updated = NOW()
                WHERE material_name = %s
            """, (quantity, unit_of_measure, str(material_name)))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

    return {"status": "success"}



#deletes a raw material
def delete_raw_material(material_name: str):
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            #check material exists
            cur.execute("""
                SELECT 1
                FROM tblrawmaterial
                WHERE material_name = %s
            """, (str(material_name),))
            if cur.fetchone() is None:
                raise ValueError(f"Raw material '{material_name}' not found")

            #delete material
            cur.execute("""
                DELETE FROM tblrawmaterial
                WHERE material_name = %s
            """, (str(material_name),))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

    return {"status": "success"}
