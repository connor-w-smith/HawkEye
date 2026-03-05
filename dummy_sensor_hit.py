import sys
import time
from datetime import datetime, timezone
from db import get_connection

def send_sensor_hit(sensor_id, hits=1):
    """
    Simulate a sensor hit by incrementing partsproduced for the active order with the given sensor_id.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Find the active order for this sensor
            cur.execute('''
                SELECT ap.orderid FROM tblactiveproduction ap
                JOIN tblproductiondata pd ON ap.orderid = pd.orderid
                WHERE ap.is_active = true AND pd.sensor_id = %s
                ORDER BY ap.orderid ASC LIMIT 1
            ''', (sensor_id,))
            row = cur.fetchone()
            if not row:
                print(f"No active order found for sensor {sensor_id}")
                return
            orderid = row[0]
            # Increment partsproduced
            cur.execute('''
                UPDATE tblproductiondata SET partsproduced = COALESCE(partsproduced, 0) + %s WHERE orderid = %s
            ''', (hits, orderid))
            conn.commit()
            print(f"Sent {hits} sensor hit(s) to order {orderid} (sensor {sensor_id})")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dummy_sensor_hit.py <sensor_id> [hits]")
        sys.exit(1)
    sensor_id = sys.argv[1]
    hits = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    send_sensor_hit(sensor_id, hits)
