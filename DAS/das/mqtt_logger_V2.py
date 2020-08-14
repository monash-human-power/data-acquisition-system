import argparse
import os
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


if __name__ == "__main__":
    CURRENT_FILEPATH = os.path.dirname(__file__)
    CSV_FILEPATH = os.path.join(CURRENT_FILEPATH, "csv_data")

    # Read command line arguments
    args = parser.parse_args()

    # Make logger object and initiate logging
    logger.Logger(
        CSV_FILEPATH,
        topics=args.topics,
        broker_address=args.host,
        verbose=args.verbose)

    # So that the logger can run forever until interupted with CTR-C
    while True:
        pass
