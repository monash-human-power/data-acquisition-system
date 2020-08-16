import argparse
import os
import time
import sys
from das.utils import logger

parser = argparse.ArgumentParser(
    description='MQTT logger',
    add_help=True)

parser.add_argument(
    'topics', nargs='*', action='store', default=["#"],
    help="""Verbose logging output""")

parser.add_argument(
    '--host', action='store', type=str, default="localhost",
    help="""Address of the MQTT broker. If nothing is selected it will
    default to localhost.""")

parser.add_argument(
    '-v', '--verbose', action='store_true', default=False,
    help="""Verbose logging output""")

parser.add_argument(
    '-t', '--time', action='store', type=float,
    default=float('Inf'), help="""Length of time to record data
    (duration). If nothing is selected it will continuously record data.""")

if __name__ == "__main__":
    CURRENT_FILEPATH = os.path.dirname(__file__)
    CSV_FILEPATH = os.path.join(CURRENT_FILEPATH, "csv_data")

    # Read command line arguments
    args = parser.parse_args()

    # Make logger object and initiate logging
    main_recorder = logger.Record(
        CSV_FILEPATH,
        topics=args.topics,
        broker_address=args.host,
        verbose=args.verbose)

    # Logger can run forever or for a specific time
    if args.time != float('Inf'):
        time.sleep(args.time)
    else:
        while True:
            try:
                pass
            except KeyboardInterrupt:
                # Graceful exit
                print(f"\nData saved in {CSV_FILEPATH}")
                main_recorder.stop()
                sys.exit()

    main_recorder.stop()
