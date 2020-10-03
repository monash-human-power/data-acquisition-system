import argparse
import os
import time
import sys
from das.utils import logger

parser = argparse.ArgumentParser(
    description="Convert MQTT logs to pretty CSVs",
    add_help=True,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "filepaths",
    nargs="*",
    action="store",
    default=[],
    help="""filepaths of MQTT logs that are to be converted to pretty CSVs""",
)

parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    default=False,
    help="""Verbose logging output""",
)

if __name__ == "__main__":
    CURRENT_FILEPATH = os.path.dirname(__file__)
    CSV_FILEPATH = os.path.join(CURRENT_FILEPATH, "csv_data")

    # Read command line arguments
    args = parser.parse_args()

    # Make logger object and initiate logging
    print("yes")
    print(args.filepaths)

    if args.filepaths != []:
        print("yoooo")
    # if args.filepaths is None:
    #     print("yay")
    # FIX

    # # Start the logger
    # main_recorder.start()

    # # Logger can run forever or for a specific time
    # try:
    #     if args.time != float("Inf"):
    #         time.sleep(args.time)
    #     else:
    #         while True:
    #             pass

    # except (KeyboardInterrupt, Exception):
    #     pass

    # finally:
    #     # Graceful exit that nicely quits the recorder to ensure the data is saved
    #     main_recorder.stop()
    #     sys.exit()
