# TODO: Add playback
# TODO: Add nicer saving and filtering
# TODO: Do propper error checking
# TODO: Check that it exits nicely

import argparse
import os
import logger

parser = argparse.ArgumentParser(
    description='MQTT wireless logger',
    add_help=True)

parser.add_argument(
    '--host', action='store', type=str, default="localhost",
    help="""Address of the MQTT broker. If nothing is selected it will
    default to localhost.""")

if __name__ == "__main__":
    CURRENT_FILEPATH = os.path.dirname(__file__)
    CSV_FILEPATH = os.path.join(CURRENT_FILEPATH, "csv_data")

    # x = logger.Playback(os.path.join(CSV_FILEPATH, "0022_log.csv"))
    args = parser.parse_args()
    x = logger.Playback(os.path.join(
        CSV_FILEPATH, "0031_log.csv"), broker_address=args.host)
    x.play()
