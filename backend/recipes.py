"""
============================================================
MOCK RECIPE DEFINITIONS (Bill of Materials)
============================================================

Each finished good may require multiple raw materials.
Each entry represents the quantity required to produce ONE unit.

Structure:
FinishedGoodName
    RawMaterialName : quantity_required


------------------------------------------------------------
HawkEye Pro Widget
finishedgoodid: 019c1582-9c0a-7a84-939f-1411d7f9088d
------------------------------------------------------------
Sensor Chip        : 2
Microcontroller    : 1
Plastic Housing    : 1


------------------------------------------------------------
Widget A
finishedgoodid: 1597bddb-8b44-4bab-a8a9-eeb20b626175
------------------------------------------------------------
Steel Gear         : 2
Ball Bearings      : 4


------------------------------------------------------------
Widget B
finishedgoodid: 36d567ae-267d-49be-bbb6-a1a0c40a11f4
------------------------------------------------------------
Steel Gear         : 1
Aluminum Plate     : 1


------------------------------------------------------------
Motor Assembly
finishedgoodid: 38b223f7-28a3-4a33-9fd5-352ae497f863
------------------------------------------------------------
Copper Wire        : 8
Ball Bearings      : 2
Electric Motor Core: 1


------------------------------------------------------------
Sensor Housing
finishedgoodid: 603911ce-6757-4b82-92fb-f85eccb0a5a4
------------------------------------------------------------
Plastic Housing    : 1
Sensor Chip        : 1


------------------------------------------------------------
Power Supply Unit
finishedgoodid: 75ab283e-8559-4183-b285-10f5331e8407
------------------------------------------------------------
Power Transformer  : 1
Voltage Regulator  : 1
Copper Wire        : 4


------------------------------------------------------------
Circuit Board Assembly
finishedgoodid: 933dbdb3-e032-4313-b871-0a4f923ad30f
------------------------------------------------------------
Microcontroller    : 1
Sensor Chip        : 1
Copper Wire        : 2


------------------------------------------------------------
Control Module
finishedgoodid: b9f7078c-efcc-4954-8a22-7e8815bb227e
------------------------------------------------------------
Microcontroller    : 1
Voltage Regulator  : 1
Plastic Housing    : 1


------------------------------------------------------------
Gear Assembly
finishedgoodid: 7d741889-8fc7-49d4-a26c-e2a13499f71f
------------------------------------------------------------
Steel Gear         : 2
Ball Bearings      : 3
Aluminum Plate     : 1


------------------------------------------------------------
Final Product Assembly
finishedgoodid: f35f580c-2191-4e18-a5fc-9be4ba5912d3
------------------------------------------------------------
Circuit Board Assembly : 1
Motor Assembly         : 1
Sensor Housing         : 1
Power Supply Unit      : 1


------------------------------------------------------------
Widget C
finishedgoodid: c8c6cf6f-b703-4baa-bb97-e596d5e52ad3
------------------------------------------------------------
Aluminum Plate     : 1
Copper Wire        : 3
Sensor Chip        : 1

============================================================
NOTES
============================================================

• Each row in tblrecipes represents ONE raw material used by a finished good.
• Recipes act like a Bill of Materials (BOM).
• When a finished good is produced, the backend should:

    1. Look up all rows in tblrecipes where finishedgoodid matches.
    2. Multiply quantity_required by quantity produced.
    3. Subtract those amounts from tblrawmaterials.quantity_in_stock.

Example:

Producing 5 Motor Assemblies requires:
    Electric Motor Core : 1 x 5 = 5
    Copper Wire         : 8 x 5 = 40
    Ball Bearings       : 2 x 5 = 10

Those amounts should be deducted from raw material inventory.

============================================================
"""