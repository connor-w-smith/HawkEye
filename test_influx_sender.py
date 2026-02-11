import time
import random
from datetime import datetime
from typing import cast
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
from influx_details import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET

def send_sensor_data(count: int = 1, interval: float = 1.0):
    """
    Sends test sensor data to InfluxDB at specified interval using line protocol.
    
    Args:
        count: Number of data points to send per interval
        interval: Seconds between each send (default 1 second)
    """
    data_point_count = 0
    client = None
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        print(f"Connecting to InfluxDB at {INFLUX_URL}")
        print(f"Writing to bucket: {INFLUX_BUCKET}")
        print(f"Sending {count} point(s) every {interval} second(s)")
        print("Press Ctrl+C to stop\n")
        
        while True:
            # Create line protocol strings
            lines = []
            for i in range(count):
                sensor_id = random.randint(1, 5)
                line = f"sensor_hit,sensor_id=sensor_{sensor_id} count=1"
                lines.append(line)
            
            # Send to InfluxDB
            write_api.write(bucket=INFLUX_BUCKET, write_precision=cast(WritePrecision, WritePrecision.S), record="\n".join(lines))
            
            data_point_count += count
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] Sent {count} point(s) | Total: {data_point_count}")
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print(f"\n\nStopped. Total points sent: {data_point_count}")
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
    except Exception as e:
        print(f"Error: {e}")
        if client is not None:
            try:
                client.close()
            except Exception:
                pass

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    count = 1
    interval = 1.0
    
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print(f"Invalid count: {sys.argv[1]}. Using default (1)")
    
    if len(sys.argv) > 2:
        try:
            interval = float(sys.argv[2])
        except ValueError:
            print(f"Invalid interval: {sys.argv[2]}. Using default (1.0)")
    
    print("="*60)
    print("HawkEye InfluxDB Test Data Sender")
    print("="*60)
    
    send_sensor_data(count=count, interval=interval)
