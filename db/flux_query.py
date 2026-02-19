import time
import os
import importlib.util
from importlib.machinery import ModuleSpec
from datetime import datetime, timezone
import logging
import signal
import threading
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from db import get_connection


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
        
    except Exception:
        logger.exception('Error fetching active orders')
        return []

def get_influx_count_since(timestamp):
    """
    stupid function to get stupid count of stupid sensor hits from stupid influx since the given timestamp
    if stupid timestamp is None, gets count from stupid past 60 seconds
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

        query = f'from(bucket: "{INFLUX_BUCKET}") |> range({time_filter}) |> count()'
        # Provide org explicitly to the query API
        result = query_api.query(query=query, org=INFLUX_ORG)

        count = 0
        for table in result:
            for record in table.records:
                val = record.get_value()
                try:
                    count += int(val)
                except Exception:
                    # If value cannot be converted to int, attempt float then int
                    try:
                        count += int(float(val))
                    except Exception:
                        pass

        client.close()
        return count

    except Exception:
        logger.exception('Error querying InfluxDB')
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
        
    except Exception:
        logger.exception('Error updating production data for order %s', orderid)
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
        
    except Exception:
        logger.exception('Error updating active production for order %s', order_id)
        return False

def process_active_orders():
    """
    stupid function to call all the other stupid functions
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
        last_timestamp = order['last_processed_timestamp']
        current_count = order['current_count']
        
        logger.info('Order %s: %s/%s parts', order_id, current_count, target)
        
        # Check if order already at/past target and should be marked inactive
        if target is not None and current_count >= target:
            logger.info('Order %s already at target, marking inactive', order_id)
            current_time = datetime.now(timezone.utc)
            update_active_production(order_id, current_time, mark_inactive=True)
            continue
        
        #get new sensor hits since last check
        new_hits = get_influx_count_since(last_timestamp)
        
        #got any?
        if new_hits > 0:
            logger.info('Detected %d new sensor hit(s)', new_hits)
            
            #update production data with new count
            new_total = update_production_data(order_id, new_hits)
            
            if new_total is not None:
                logger.info('Updated total: %s/%s parts', new_total, target)
                
                # Update timestamp
                current_time = datetime.now(timezone.utc)
                
                # Check if target reached
                if target is not None and new_total >= target:
                    update_active_production(order_id, current_time, mark_inactive=True)
                else:
                    update_active_production(order_id, current_time, mark_inactive=False)
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