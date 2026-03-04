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
import uuid6
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

#adds a new raw material
def add_raw_material(material_name: str, quantity: float, unit_of_measure: str):
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            #check if material already exists
            cur.execute("""
                SELECT 1
                FROM tblrawmaterials
                WHERE material_name = %s
            """, (str(material_name),))
            if cur.fetchone() is not None:
                raise ValueError(f"Raw material '{material_name}' already exists")

            #generate UUID
            new_id = uuid6.uuid7()

            #insert new raw material
            cur.execute("""
                INSERT INTO tblrawmaterials (materialid, material_name, quantity_in_stock, unit_of_measure, last_updated)
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
                FROM tblrawmaterials
                WHERE material_name = %s
            """, (str(material_name),))
            if cur.fetchone() is None:
                raise ValueError(f"Raw material '{material_name}' not found")

            #update material
            cur.execute("""
                UPDATE tblrawmaterials
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
                FROM tblrawmaterials
                WHERE material_name = %s
            """, (str(material_name),))
            if cur.fetchone() is None:
                raise ValueError(f"Raw material '{material_name}' not found")

            #delete material
            cur.execute("""
                DELETE FROM tblrawmaterials
                WHERE material_name = %s
            """, (str(material_name),))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

    return {"status": "success"}

####Recipe functions
def add_raw_recipe(finished_good_id: str, material_name: str, quantity_required: float):
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:

            #get finished good id from name
            cur.execute("""
                SELECT finishedgoodid
                FROM tblfinishedgoods
                WHERE finishedgoodname = %s
            """, (finished_good_id,))
            fg_row = cur.fetchone()

            if fg_row is None:
                raise ValueError(f"Finished good '{finished_good_id}' not found")

            finished_good_db_id = fg_row[0]

            #get material id
            cur.execute("""
                SELECT materialid
                FROM tblrawmaterials
                WHERE material_name = %s
            """, (material_name,))
            material_row = cur.fetchone()

            if material_row is None:
                raise ValueError(f"Raw material '{material_name}' not found")

            material_id = material_row[0]

            #prevent duplicate recipe entry
            cur.execute("""
                SELECT 1
                FROM tblrecipes
                WHERE finishedgoodid = %s AND materialid = %s
            """, (finished_good_db_id, material_id))

            if cur.fetchone() is not None:
                raise ValueError("Recipe entry already exists")

            #insert recipe row
            cur.execute("""
                INSERT INTO tblrecipes (recipeid, finishedgoodid, materialid, quantity_required)
                VALUES (gen_random_uuid(), %s, %s, %s)
            """, (finished_good_db_id, material_id, quantity_required))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    return {"status": "success"}

def delete_raw_recipe(finished_good_id: str, material_name: str):
    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:

            #get finished good id from name
            cur.execute("""
                SELECT finishedgoodid
                FROM tblfinishedgoods
                WHERE finishedgoodname = %s
            """, (finished_good_id,))
            fg_row = cur.fetchone()

            if fg_row is None:
                raise ValueError(f"Finished good '{finished_good_id}' not found")

            finished_good_db_id = fg_row[0]

            #get material id from name
            cur.execute("""
                SELECT materialid
                FROM tblrawmaterials
                WHERE material_name = %s
            """, (material_name,))
            material_row = cur.fetchone()

            if material_row is None:
                raise ValueError(f"Raw material '{material_name}' not found")

            material_id = material_row[0]

            #check recipe exists
            cur.execute("""
                SELECT 1
                FROM tblrecipes
                WHERE finishedgoodid = %s AND materialid = %s
            """, (finished_good_db_id, material_id))

            if cur.fetchone() is None:
                raise ValueError("Recipe entry not found")

            #delete it
            cur.execute("""
                DELETE FROM tblrecipes
                WHERE finishedgoodid = %s AND materialid = %s
            """, (finished_good_db_id, material_id))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    return {"status": "success"}

def get_raw_materials_for_finished_good(finished_good_id: str):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    rm.materialid,
                    rm.material_name,
                    rm.unit_of_measure,
                    r.quantity_required,
                    rm.quantity_in_stock
                FROM tblrecipes r
                JOIN tblrawmaterials rm
                    ON r.materialid = rm.materialid
                WHERE r.finishedgoodid = %s
            """, (finished_good_id,))

            rows = cur.fetchall()

            #convert to structured response
            result = [
                {
                    "material_id": row[0],
                    "material_name": row[1],
                    "unit_of_measure": row[2],
                    "quantity_required_per_unit": row[3],
                    "quantity_available": row[4]
                }
                for row in rows
            ]

            return result

    finally:
        conn.close()

#for raw materials table
def get_all_raw_materials():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    materialid,
                    material_name,
                    quantity_in_stock,
                    unit_of_measure,
                    last_updated
                FROM tblrawmaterials
                ORDER BY material_name
            """)

            rows = cur.fetchall()

            return [
                {
                    "material_id": r[0],
                    "material_name": r[1],
                    "quantity_in_stock": r[2],
                    "unit_of_measure": r[3],
                    "last_updated": r[4]
                }
                for r in rows
            ]

    finally:
        conn.close()

#for recipes table
def get_all_recipes():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    fg.finishedgoodname,
                    rm.material_name,
                    r.quantity_required
                FROM tblrecipes r
                JOIN tblfinishedgoods fg
                    ON r.finishedgoodid = fg.finishedgoodid
                JOIN tblrawmaterials rm
                    ON r.materialid = rm.materialid
                ORDER BY fg.finishedgoodname, rm.material_name
            """)

            rows = cur.fetchall()

            return [
                {
                    "finished_good": r[0],
                    "raw_material": r[1],
                    "quantity_required": r[2]
                }
                for r in rows
            ]

    finally:
        conn.close()
    
def consume_raw_materials_for_production(finished_good_id: str, produced_quantity: int):
    """
    Subtracts raw materials based on recipe when finished goods are produced.
    """

    conn = get_connection()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:

            # Get recipe rows
            cur.execute("""
                SELECT materialid, quantity_required
                FROM tblrecipes
                WHERE finishedgoodid = %s
            """, (finished_good_id,))

            recipe_rows = cur.fetchall()

            if not recipe_rows:
                raise ValueError("No recipe found for finished good")

            for material_id, qty_required in recipe_rows:

                total_material_used = qty_required * produced_quantity

                # subtract inventory
                cur.execute("""
                    UPDATE tblrawmaterials
                    SET quantity_in_stock = quantity_in_stock - %s,
                        last_updated = NOW()
                    WHERE materialid = %s
                """, (total_material_used, material_id))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

    return {"status": "success"}

def calculate_max_production(finished_good_id: str):
    """
    Returns the maximum number of finished goods that can be produced
    based on current raw material inventory and recipe requirements.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT 
                    rm.material_name,
                    rm.quantity_in_stock,
                    r.quantity_required
                FROM tblrecipes r
                JOIN tblrawmaterials rm
                    ON r.materialid = rm.materialid
                WHERE r.finishedgoodid = %s
            """, (finished_good_id,))

            rows = cur.fetchall()

            if not rows:
                raise ValueError("No recipe found for finished good")

            material_limits = []
            limiting_material = None
            max_units = None

            for material_name, quantity_in_stock, quantity_required in rows:

                possible_units = quantity_in_stock // quantity_required

                material_limits.append({
                    "material_name": material_name,
                    "quantity_in_stock": quantity_in_stock,
                    "quantity_required_per_unit": quantity_required,
                    "max_possible_units": int(possible_units)
                })

                if max_units is None or possible_units < max_units:
                    max_units = possible_units
                    limiting_material = material_name

            return {
                "max_producible_units": int(max_units),
                "limiting_material": limiting_material,
                "materials": material_limits
            }

    finally:
        conn.close()