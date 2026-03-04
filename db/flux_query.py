import sys
import time
import os
import importlib.util
from importlib.machinery import ModuleSpec
from datetime import datetime, timezone
import logging
import signal
import threading

# Add parent directory to path so imports work from any working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from db import get_connection
from backend.services.material_services import consume_raw_materials_for_production


def _load_influx_details():
    """Load Influx connection constants from influx_details.py.
    Tries normal import first, then falls back to loading the file from the parent directory.
    """
    try:
        # Try regular import (works when project root is on PYTHONPATH)
        from influx_details import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET
        return INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET
    except Exception:
        # Fallback: load influx_details.py relative to this file (parent directory)
        here = os.path.dirname(__file__)
        candidate = os.path.abspath(os.path.join(here, '..', 'influx_details.py'))
        if os.path.exists(candidate):
            spec = importlib.util.spec_from_file_location('influx_details', candidate)
            if spec is None or not isinstance(spec, ModuleSpec):
                raise ImportError(f"Could not create module spec from {candidate}")
            if spec.loader is None or not hasattr(spec.loader, 'exec_module'):
                raise ImportError(f"Module spec for {candidate} has no loader")
            module = importlib.util.module_from_spec(spec)
            # type: ignore[attr-defined]
            spec.loader.exec_module(module)
            return module.INFLUX_URL, module.INFLUX_TOKEN, module.INFLUX_ORG, module.INFLUX_BUCKET
        raise


# Load Influx configuration values
INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET = _load_influx_details()


# Runtime configuration via environment (useful for systemd)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
_level = getattr(logging, LOG_LEVEL, logging.INFO)
logging.basicConfig(level=_level, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger('flux_query')

POLL_INTERVAL = int(os.getenv('HAWKEYE_POLL_INTERVAL', os.getenv('POLL_INTERVAL', '10')))
RUN_ONCE = os.getenv('HAWKEYE_RUN_ONCE', os.getenv('RUN_ONCE', 'false')).lower() in ('1', 'true', 'yes')

# Event used to detect shutdown signals
_stop_event = threading.Event()


def _handle_signal(signum, frame):
    logger.info('Received signal %s, initiating shutdown', signum)
    _stop_event.set()


# register signals for graceful shutdown
signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)

def get_active_orders():
    """
    Retrieves all active production orders from tblactiveproduction.
    Returns list of dicts with order info: orderid, target_quantity, start_time, end_time, last_processed_timestamp, sensor_id
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        #this uses aliases i think what is happening
        query = """
            SELECT ap.orderid,
                ap.target_quantity,
                ap.start_time,
                ap.end_time,
                ap.last_processed_timestamp,
                pd.finishedgoodid,
                COALESCE(pd.partsproduced, 0) as current_count,
                COALESCE(pd.sensor_id, '') as sensor_id
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
                'start_time': row[2],
                'end_time': row[3],
                'last_processed_timestamp': row[4],
                'finished_good_id': row[5],
                'current_count': row[6],
                'sensor_id': row[7]

            })
        
        cur.close()
        conn.close()
        return orders
        
    except Exception:
        logger.exception('Error fetching active orders')
        return []

def get_finished_good_for_order(order_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT finishedgoodid
                FROM tblproductiondata
                WHERE orderid = %s
            """, (order_id,))

            row = cur.fetchone()

            if row:
                return row[0]

            return None

    finally:
        conn.close()

def get_influx_count_since(timestamp, sensor_id=None):
    """
    Get count of sensor hits from InfluxDB since the given timestamp, along with first and last hit timestamps.
    If sensor_id is provided, filters hits to only that sensor (using the 'location' tag).
    If timestamp is None, gets count from past 60 seconds.
    Returns a dict with keys: 'count', 'first_timestamp', 'last_timestamp'
    """
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        query_api = client.query_api()

        # If no timestamp, use last 60 seconds as default (duration literal)
        if timestamp is None:
            time_filter = "start: -60s"
        else:
            # Ensure timestamp is timezone-aware and convert to UTC RFC3339 with trailing Z
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            ts_utc = timestamp.astimezone(timezone.utc)
            # Format like 2026-02-18T12:34:56Z which Flux accepts
            time_str = ts_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            time_filter = f"start: {time_str}"

        # If sensor_id is provided, filter by the 'location' tag in InfluxDB
        sensor_filter = ""
        if sensor_id:
            sensor_filter = f'|> filter(fn: (r) => r.location == "{sensor_id}")'

        # Query to get count
        count_query = f'''
from(bucket: "{INFLUX_BUCKET}") 
  |> range({time_filter}) 
  {sensor_filter} 
  |> count()
'''
        result = query_api.query(query=count_query, org=INFLUX_ORG)
        count = 0
        for table in result:
            for record in table.records:
                try:
                    count += int(record.get_value())
                except Exception:
                    pass
        
        logger.info(f"Count query result: {count}")
        
        # Query to get min time (first hit)
        first_time_query = f'''
from(bucket: "{INFLUX_BUCKET}") 
  |> range({time_filter}) 
  {sensor_filter} 
  |> min(column: "_time")
'''
        result = query_api.query(query=first_time_query, org=INFLUX_ORG)
        first_timestamp = None
        for table in result:
            for record in table.records:
                try:
                    first_timestamp = record.get_time()
                    logger.info(f"First timestamp: {first_timestamp}")
                except Exception as e:
                    logger.warning(f"Could not parse first_time: {e}")
        
        # Query to get max time (last hit)
        last_time_query = f'''
from(bucket: "{INFLUX_BUCKET}") 
  |> range({time_filter}) 
  {sensor_filter} 
  |> max(column: "_time")
'''
        result = query_api.query(query=last_time_query, org=INFLUX_ORG)
        last_timestamp = None
        for table in result:
            for record in table.records:
                try:
                    last_timestamp = record.get_time()
                    logger.info(f"Last timestamp: {last_timestamp}")
                except Exception as e:
                    logger.warning(f"Could not parse last_time: {e}")
        
        client.close()
        return {
            'count': count,
            'first_timestamp': first_timestamp,
            'last_timestamp': last_timestamp
        }

    except Exception:
        logger.exception('Error querying InfluxDB for sensor_id=%s', sensor_id)
        return {
            'count': 0,
            'first_timestamp': None,
            'last_timestamp': None
        }

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
        
    except Exception:
        logger.exception('Error updating production data for order %s', orderid)
        return None

def update_active_production(order_id, start_time=None, end_time=None, mark_inactive=False):
    """
    Update timestamps for a production order.
    - start_time: timestamp of first sensor hit (set once, preserved)
    - end_time: timestamp of last sensor hit (only set when order completes)
    - last_processed_timestamp: updated with each check to end_time (used for incremental queries and hour/24-hour analytics)
    - mark_inactive: if True, sets is_active to false
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        if mark_inactive:
            cur.execute("""
                UPDATE tblactiveproduction 
                SET start_time = COALESCE(%s, start_time), 
                    end_time = %s,
                    last_processed_timestamp = %s,
                    is_active = false 
                WHERE orderid = %s
            """, (start_time, end_time, end_time, order_id))
            print(f"✓ Order {order_id} marked as COMPLETE")
        else:
            # During normal operation, only update start_time (if not set) and last_processed_timestamp
            cur.execute("""
                UPDATE tblactiveproduction 
                SET start_time = COALESCE(%s, start_time), 
                    last_processed_timestamp = %s
                WHERE orderid = %s
            """, (start_time, end_time, order_id))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception:
        logger.exception('Error updating active production for order %s', order_id)
        return False

def process_active_orders():
    """
    Process all active production orders by fetching sensor data from InfluxDB
    and updating timestamps and counts in the database.
    """

    #are there active orders?
    active_orders = get_active_orders()
    
    if not active_orders:
        logger.debug('No active production orders found.')
        return
    
    #stupid orders have been checked stupidly
    logger.info('\n%s', '=' * 60)
    logger.info('Processing %d active order(s) at %s', len(active_orders), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info('%s', '=' * 60)
    #output if there were stupid orders
    

    for order in active_orders:
        order_id = order['orderid']
        target = order['target_quantity']
        start_time = order['start_time']
        last_processed_timestamp = order['last_processed_timestamp']  # Use this as query reference point
        current_count = order['current_count']
        sensor_id = order.get('sensor_id', '')
        
        logger.info('Order %s (Sensor %s): %s/%s parts', order_id, sensor_id or 'unassigned', current_count, target)
        
        # Check if order already at/past target and should be marked inactive
        if target is not None and current_count >= target:
            logger.info('Order %s already at target, marking inactive', order_id)
            update_active_production(order_id, mark_inactive=True)
            continue
        
        #get new sensor hits since last check (filtered by sensor_id if assigned)
        hit_data = get_influx_count_since(last_processed_timestamp, sensor_id=sensor_id)
        new_hits = hit_data['count']
        first_timestamp = hit_data['first_timestamp']
        last_timestamp = hit_data['last_timestamp']
        
        #got any?
        if new_hits > 0:
            logger.info('Detected %d new sensor hit(s)', new_hits)
            
            #update production data with new count
            new_total = update_production_data(order_id, new_hits)
            if new_total is not None:
                finished_good_id = order['finished_good_id']

                consume_raw_materials_for_production(
                    finished_good_id,
                    new_hits
                )
                logger.info('Updated total: %s/%s parts', new_total, target)
                
                # Update timestamps if we got valid ones
                if first_timestamp and last_timestamp:
                    # Set start_time if it's not already set
                    if not start_time:
                        start_time = first_timestamp
                    
                    # Check if target reached
                    if target is not None and new_total >= target:
                        update_active_production(order_id, start_time=start_time, end_time=last_timestamp, mark_inactive=True)
                    else:
                        # Just update last_processed_timestamp (don't set end_time yet)
                        update_active_production(order_id, start_time=start_time, end_time=last_timestamp, mark_inactive=False)
                        if target:
                            logger.info('Progress: %.1f%% complete', (new_total / target * 100))
                        else:
                            logger.info('Updated')
        #no hits
        else:
            logger.debug('No new parts detected')

def _run_loop():
    logger.info('Starting HawkEye Production Monitor...')
    logger.info('Monitoring active production orders for sensor data from InfluxDB')

    try:
        while not _stop_event.is_set():
            try:
                process_active_orders()
            except Exception:
                logger.exception('Error in processing loop')

            # If configured to run once, break after a single iteration
            if RUN_ONCE:
                break

            # Wait with stop_event so we can exit early on signal
            _stop_event.wait(POLL_INTERVAL)
    finally:
        logger.info('Shutting down HawkEye Production Monitor')


if __name__ == "__main__":
    _run_loop()