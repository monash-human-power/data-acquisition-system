import sys
import argparse
import socket
import os
import mqtt_logger

parser = argparse.ArgumentParser(
    description="MQTT playback",
    add_help=True,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "--host",
    action="store",
    type=str,
    default="localhost",
    help="""Address of the MQTT broker.""",
)

parser.add_argument(
    "-s",
    "--speed",
    action="store",
    type=float,
    default=1,
    help="""Playback speed up""",
)

parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    default=False,
    help="""Verbose logging output""",
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
    # Read command line arguments
    args = parser.parse_args()

    CURRENT_FILEPATH = os.path.dirname(__file__)
    MQTT_LOG_FILEPATH = os.path.join(CURRENT_FILEPATH, "MQTT_log.db")

    try:
        # Make logger object and initiate playback
        main_playback = mqtt_logger.Playback(
            sqlite_database_path=MQTT_LOG_FILEPATH,
            broker_address=args.host,
            verbose=args.verbose,
            username=args.username,
            password=args.password,
        )

        main_playback.play(speed=args.speed)

    except KeyboardInterrupt:
        pass

    except socket.timeout as e:
        print(f"{type(e)}: {e}")
        print("The IP address of the MQTT broker is probably wrong")

    except Exception as e:
        print(f"{type(e)}: {e}")

    finally:
        # Graceful exit
        sys.exit()
