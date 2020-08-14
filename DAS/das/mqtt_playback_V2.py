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
    'filepath', action='store', type=str,
    help="""Filepath of the csv log""")

parser.add_argument(
    '--host', action='store', type=str, default="localhost",
    help="""Address of the MQTT broker. If nothing is selected it will
    default to localhost.""")

parser.add_argument(
    '--speed', action='store', type=float, default=1,
    help="""Playback speed up. Default is 1x""")

parser.add_argument(
    '-v', '--verbose', action='store_true', default=False,
    help="""Verbose logging output"""
)
if __name__ == "__main__":
    CURRENT_FILEPATH = os.path.dirname(__file__)
    CSV_FILEPATH = os.path.join(CURRENT_FILEPATH, "csv_data")

    # Read command line arguments
    args = parser.parse_args()

    # Make logger object and initiate playback
    main_logger = logger.Playback(
        filepath=args.filepath,
        broker_address=args.host,
        verbose=args.verbose)
    main_logger.play(speed=args.speed)
