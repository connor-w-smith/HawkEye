import time
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from influx_details import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET
from db import get_connection

#function to get number of records in the past minute from influxdb
def get_influx_count():
    #auth crap
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()

    #query db for how many records were added in the past minute
    query = f'from(bucket: "{INFLUX_BUCKET}") |> range(start: -60m) |> count()'
    result = query_api.query(query)

    #set count to 0 and increment for each record found
    count = 0
    for table in result:
        for record in table.records:
            count += record.get_value()
    
    client.close()
    
    #debugging
    #print(f"InfluxDB count in the past 60m: {count}")
    
    return count

def update_postgres(count, order_id):
    try:
        #connect to postgres
        conn = get_connection()
        cur = conn.cursor()

        #update partsproduced with sensor hits from influxdb
        cur.execute("UPDATE tblproductiondata SET partsproduced = %s WHERE orderid = %s", (count, order_id))
        conn.commit()
        cur.close()
        conn.close()

    except:
        print("Failed to connect to PostgreSQL Database")
        return False
    
if __name__ == "__main__":
    while True:
        try:
            current_hits = get_influx_count()
            print(f"Detected {current_hits} hits. Updating PostgreSQL...")
            update_postgres(current_hits, 9) #this will need to be changed to handle dynamic order IDs later.
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(60) #wait 60 seconds before next update

