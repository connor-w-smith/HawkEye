import psycopg2
import uuid

DB_CONFIG = {
    "host": "98.92.53.251",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "pgpass"
}

#Hard-coded list of finished goods
FINISHED_GOODS = [
    ("Widget A", "1597bddb-8b44-4bab-a8a9-eeb20b626175"),
    ("Widget B", "36d567ae-267d-49be-bbb6-a1a0c40a11f4"),
    ("Control Module", "b9f7078c-efcc-4954-8a22-7e8815bb227e"),
    ("Sensor Housing", "603911ce-6757-4b82-92fb-f85eccb0a5a4"),
    ("Power Supply Unit", "75ab283e-8559-4183-b285-10f5331e8407"),
    ("Motor Assembly", "38b223f7-28a3-4a33-9fd5-352ae497f863"),
    ("Circuit Board Assembly", "933dbdb3-e032-4313-b871-0a4f923ad30f"),
    ("Final Product Assembly", "f35f580c-2191-4e18-a5fc-9be4ba5912d3"),
]

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def show_menu():
    print("\n=== Manual Inventory Entry ===")
    for i, (name, _) in enumerate(FINISHED_GOODS, start=1):
        print(f"{i}. {name}")
    print("0. Exit")

def main():
    while True:
        show_menu()

        try:
            choice = int(input("\nSelect item number: "))
        except ValueError:
            print("Invalid input. Enter a number.")
            continue

        if choice == 0:
            print("Exiting.")
            break

        if choice < 1 or choice > len(FINISHED_GOODS):
            print("Invalid selection.")
            continue

        try:
            quantity = int(input("Enter quantity to add: "))
            if quantity <= 0:
                raise ValueError
        except ValueError:
            print("Quantity must be a positive integer.")
            continue

        finished_good_name, finished_good_id = FINISHED_GOODS[choice - 1]

        conn = get_connection()
        conn.autocommit = False

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO tblproductioninventory
                        (finishedgoodid, intavailableparts)
                    VALUES (%s, %s)
                    ON CONFLICT (finishedgoodid)
                    DO UPDATE SET intavailableparts =
                        tblproductioninventory.intavailableparts
                        + EXCLUDED.intavailableparts
                """, (finished_good_id, quantity))

            conn.commit()
            print(f"Added {quantity} units to {finished_good_name}")

        except Exception as e:
            conn.rollback()
            print("Database error:", e)

        finally:
            conn.close()

if __name__ == "__main__":
    main()
