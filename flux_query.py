import time
from datetime import datetime, timezone
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from influx_details import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET
from db import get_connection

def get_active_orders():
    """
    Retrieves all active production orders from tblactiveproduction.
    Returns list of dicts with order info: orderid, target_quantity, last_processed_timestamp
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        #this uses aliases i think what is happening
        query = """
            SELECT ap.orderid, ap.target_quantity, ap.last_processed_timestamp, 
                   COALESCE(pd.partsproduced, 0) as current_count
            FROM tblactiveproduction ap
            JOIN tblproductiondata pd ON ap.orderid = pd.orderid
            WHERE ap.is_active = true
        """
        cur.execute(query)
        results = cur.fetchall()
        
        orders = []
        for row in results:
            orders.append({
                'orderid': row[0],
                'target_quantity': row[1],
                'last_processed_timestamp': row[2],
                'current_count': row[3]
            })
        
        cur.close()
        conn.close()
        return orders
        
    except Exception as e:
        print(f"Error fetching active orders: {e}")
        return []

def get_influx_count_since(timestamp):
    """
    stupid function to get stupid count of stupid sensor hits from stupid influx since the given timestamp
    if stupid timestamp is None, gets count from stupid past 60 seconds
    """
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        query_api = client.query_api()
        
        # If no timestamp, use last 60 seconds as default
        if timestamp is None:
            time_filter = "start: -60s"
        else:
            #weird influx crap with timestamps
            #i wish influx would blow up with a bomb
            #thanks copilot
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            time_filter = f'start: {timestamp.isoformat()}'
        
        query = f'from(bucket: "{INFLUX_BUCKET}") |> range({time_filter}) |> count()'
        result = query_api.query(query)
        
        count = 0
        for table in result:
            for record in table.records:
                count += record.get_value()
        
        client.close()
        return count
        
    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        return 0

def update_production_data(orderid, new_parts_count):
    """
    updates stupid partsproduced in stupid tblproductiondata by +='ing new_parts_count for orderid
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Increment partsproduced by new count
        cur.execute("""
            UPDATE tblproductiondata 
            SET partsproduced = COALESCE(partsproduced, 0) + %s 
            WHERE orderid = %s
            RETURNING partsproduced
        """, (new_parts_count, orderid))
        
        new_total = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        #this will return to process_active_orders() to check if we are at target production quantity or not
        return new_total
        
    except Exception as e:
        print(f"Error updating production data for order {orderid}: {e}")
        return None

def update_active_production(order_id, new_timestamp, mark_inactive=False):
    """
    Stupid function to ensure that stupid orders don't keep running forever after completion
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        if mark_inactive:
            cur.execute("""
                UPDATE tblactiveproduction 
                SET last_processed_timestamp = %s, is_active = false 
                WHERE orderid = %s
            """, (new_timestamp, order_id))
            print(f"✓ Order {order_id} marked as COMPLETE")
        else:
            cur.execute("""
                UPDATE tblactiveproduction 
                SET last_processed_timestamp = %s 
                WHERE orderid = %s
            """, (new_timestamp, order_id))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error updating active production for order {order_id}: {e}")
        return False

def process_active_orders():
    """
    stupid function to call all the other stupid functions
    """

    #are there active orders?
    active_orders = get_active_orders()
    
    if not active_orders:
        print("No active production orders found.")
        return
    
    #stupid orders have been checked stupidly
    print(f"\n{'='*60}")
    print(f"Processing {len(active_orders)} active order(s) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    #output if there were stupid orders
    

    for order in active_orders:
        order_id = order['orderid']
        target = order['target_quantity']
        last_timestamp = order['last_processed_timestamp']
        current_count = order['current_count']
        
        print(f"\nOrder {order_id}: {current_count}/{target} parts")
        
        #get new sensor hits since last check
        new_hits = get_influx_count_since(last_timestamp)
        
        #got any?
        if new_hits > 0:
            print(f"Detected {new_hits} new sensor hit(s)")
            
            #update production data with new count
            new_total = update_production_data(order_id, new_hits)
            
            if new_total is not None:
                print(f"Updated total: {new_total}/{target} parts")
                
                # Update timestamp
                current_time = datetime.now(timezone.utc)
                
                # Check if target reached
                if target is not None and new_total >= target:
                    update_active_production(order_id, current_time, mark_inactive=True)
                else:
                    update_active_production(order_id, current_time, mark_inactive=False)
                    print(f"Progress: {(new_total/target*100):.1f}% complete" if target else " Updated")
        #no hits
        else:
            print(f"No new parts detected")

if __name__ == "__main__":
    #stupid debug
    print("Starting HawkEye Production Monitor...")
    print("Monitoring active production orders for sensor data from InfluxDB\n")
    
    #stupid error checking
    while True:
        try:
            process_active_orders()
        except Exception as e:
            print(f"\nError in main loop: {e}")
        
        # Wait before next check
        time.sleep(10)  # Check every 10 seconds for more responsive updates