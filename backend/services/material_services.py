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

def add_raw_recipe(material_name):
    
def delete_raw_recipe(material_name):

def update_raw_recipe():

def add_raw_material():

def delete_raw_material():
"""