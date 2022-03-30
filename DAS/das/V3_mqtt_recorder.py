import argparse
import os
import time
import sys
import socket
import mqtt_logger

parser = argparse.ArgumentParser(
    description="MQTT logger",
    add_help=True,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "topics",
    nargs="*",
    action="store",
    default=["#"],
    help="""MQTT topics""",
)

parser.add_argument(
    "--host",
    action="store",
    type=str,
    default="localhost",
    help="""Address of the MQTT broker""",
)

parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    default=False,
    help="""Verbose logging output""",
)

parser.add_argument(
    "-t",
    "--time",
    action="store",
    type=float,
    default=float("Inf"),
    help="""Length of time to record data (duration)""",
)

parser.add_argument(
    "-u",
    "--username",
    action="store",
    type=str,
    default=None,
    help="""Username for MQTT broker""",
)

parser.add_argument(
    "-p",
    "--password",
    action="store",
    type=str,
    default=None,
    help="""Password for MQTT broker""",
)

if __name__ == "__main__":
    CURRENT_FILEPATH = os.path.dirname(__file__)
    MQTT_LOG_FILEPATH = os.path.join(CURRENT_FILEPATH, "MQTT_log.db")

    # Read command line arguments
    args = parser.parse_args()

    # Logger can run forever or for a specific time
    try:
        # Make logger object and initiate logging
        main_recorder = mqtt_logger.Recorder(
            MQTT_LOG_FILEPATH,
            topics=args.topics,
            broker_address=args.host,
            verbose=args.verbose,
            username=args.username,
            password=args.password,
        )

        # Start the logger
        main_recorder.start()

        if args.time != float("Inf"):
            time.sleep(args.time)
        else:
            while True:
                pass

    except KeyboardInterrupt:
        pass

    except socket.timeout as e:
        print(f"{type(e)}: {e}")
        print(f"The IP address of the MQTT broker is probably wrong")

    except Exception as e:
        print(f"{type(e)}: {e}")

    finally:
        # Graceful exit that nicely quits the recorder to ensure the data is saved
        main_recorder.stop()
        sys.exit()
