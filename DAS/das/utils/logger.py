from pathlib import Path
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import pandas as pd
import json
import csv
import time
import os
import asyncio
import logging
import re

from pandas.core.frame import DataFrame

CsvConfig = {
    "delimiter": ",",
    "quotechar": "`",
    "quoting": csv.QUOTE_ALL,
    "skipinitialspace": True,
    "fieldnames": ["time_delta", "mqtt_topic", "message"],
}

# Set logging to output all info by default (with a space for clarity)
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class Recorder:
    """Record incoming MQTT messages on selected topics.

    Parameters
    ----------
    csv_folder_path : str
        Filepath of the folder where the logs are to be stored
    topics : List(str)
        A list containing the topic strings that are to be subscribed to
    broker_address : str
        The IP address that the MQTT broker lives on
    verbose : bool
        Specifies whether the incoming MQTT data and warnings are printed

    Attributes
    ----------
    TOPICS : List(str)
        List of topic names
    _recording : bool
        Whether the Recorder object is currently recording or not
    _VERBOSE : bool
        Specifies whether the incoming MQTT data and warnings are printed
    _START_TIME : `time`
        The current time used to produce time deltas
    _LOG_FILE : `File`
        Open log file object that can be written to
    _LOG_FILE_WRITER : `csv.DictWriter`
        Csv writter object that is used to write the data to the _LOG_FILE file
    _CLIENT : `paho.mqtt.client`
        MQTT client that connects to the broker and recives the messages
    """

    def __init__(
        self,
        csv_folder_path: str,
        topics: list = ["#"],
        broker_address: str = "localhost",
        verbose: bool = False,
    ) -> None:
        # The logger object can subscribe to many topics (if none are selected then it will subscribe to all)
        self.TOPICS = topics
        self._VERBOSE = verbose
        self._START_TIME = time.monotonic()

        # Create csv_folder_path folder if none exists
        Path(csv_folder_path).mkdir(parents=True, exist_ok=True)

        # Create the csv log and csv writter
        self._create_log_file(csv_folder_path)

        # Add headers for csv
        self._LOG_FILE_WRITER.writeheader()

        # Do not start logging when object is created (wait for start method)
        self._recording = False

        # Connect to MQTT broker
        self._CLIENT = mqtt.Client()
        self._CLIENT.on_connect = self._on_connect
        self._CLIENT.on_message = self._on_message
        self._CLIENT.connect(broker_address)
        self._CLIENT.loop_start()  # Threaded execution loop

    def _create_log_file(self, csv_folder_path: str) -> None:
        """Is used to open a log file and csv obj during the object init

        Parameters
        ----------
        csv_folder_path : str
            Filepath of the folder where the logs are to be stored
        """

        # Name the csv log file xxxx_log.csv where xxxx is a number
        previous_log_num = 0
        for filename in os.listdir(csv_folder_path):
            try:
                # Regular expression that extracts the decimal log number (group 1)
                current_log_num = int(re.search("(\d*)_log.csv", filename).group(1))
                if current_log_num > previous_log_num:
                    previous_log_num = current_log_num
            except AttributeError:
                if self._VERBOSE:
                    logging.warning(f"{filename} should not be in {csv_folder_path}")
            except Exception as e:
                logging.error(e)

        # Create the new log file and name it one more than the previous
        filename = f"{previous_log_num + 1}_log.csv"
        self._LOG_FILE = open(os.path.join(csv_folder_path, filename), "a")
        self._LOG_FILE_WRITER = csv.DictWriter(
            self._LOG_FILE,
            delimiter=CsvConfig["delimiter"],
            quotechar=CsvConfig["quotechar"],
            quoting=CsvConfig["quoting"],
            fieldnames=CsvConfig["fieldnames"],
        )

    def _on_connect(self, client, userdata, flags, rc) -> None:
        """Callback function for MQTT broker on connection."""

        if rc == 0:
            logging.info("Connection Successful!")
        else:
            raise ConnectionError(
                "Connection was unsuccessful, check that the broker IP is corrrect"
            )

        # Subscribe to all of the topics
        try:
            for topic in self.TOPICS:
                self._CLIENT.subscribe(topic)
                logging.info(f"Subscribed to: {topic}")
        except Exception as e:
            logging.error(e)

    def _on_message(self, client, userdata, msg) -> None:
        """Callback function for MQTT broker on message that logs the incoming MQTT message."""
        if self._recording:
            try:
                self.log(msg.topic, msg.payload.decode("utf-8"))
            except Exception as e:
                logging.error(e)

    def log(self, mqtt_topic: str, message: str) -> None:
        """Logs the time delta and message data to self._LOG_FILE in the csv format.

        Parameters
        ----------
        mqtt_topic : str
            Incoming topic to be recorded
        message : str
            Corresponding message to be recorded
        """
        time_delta = time.monotonic() - self._START_TIME

        # Write data to csv file
        try:
            self._LOG_FILE_WRITER.writerow(
                {
                    "time_delta": time_delta,
                    "mqtt_topic": mqtt_topic,
                    "message": message,
                }
            )
            if self._VERBOSE:
                logging.info(
                    f"{round(time_delta, 5): <10} | {mqtt_topic: <50} | {message}"
                )
        except Exception as e:
            logging.error(e)

    def start(self) -> None:
        self._recording = True
        logging.info(f"Logging started!")

    def stop(self) -> None:
        """Graceful exit for closing the file and stopping the MQTT client."""
        self._recording = False
        self._CLIENT.loop_stop()
        self._LOG_FILE.close()
        logging.info(f"Data saved in {self._LOG_FILE.name}")


class Playback:
    """Playback MQTT messages from log files in realtime or faster.

    Parameters
    ----------
    filepath : str
        Filepath of the log file for playback
    broker_address : str
        The IP address that the MQTT broker lives on
    verbose : bool
        Specifies whether the outgoing MQTT data and warnings are printed

    Attributes
    ----------
    _VERBOSE: bool
        Specifies whether the incoming MQTT data and warnings are printed
    _BROKER_ADDRESS: bool
        The IP address of the MQTT broker
    _log_data: list(dict)
        A list of all of the rows in the log file stored in dict format
    """

    def __init__(
        self, filepath: str, broker_address: str = "localhost", verbose: bool = False
    ) -> None:
        self._VERBOSE = verbose
        self._BROKER_ADDRESS = broker_address

        # Read in data from log file and save each row in _log_data list
        log_file = open(filepath, "r")
        csv_reader = csv.DictReader(
            log_file,
            delimiter=CsvConfig["delimiter"],
            quotechar=CsvConfig["quotechar"],
            quoting=CsvConfig["quoting"],
            skipinitialspace=CsvConfig["skipinitialspace"],
        )

        self._log_data = []
        for row in csv_reader:
            # Convert time delta to float
            row["time_delta"] = float(row["time_delta"])
            self._log_data.append(row)

    def play(self, speed: float = 1) -> None:
        """Play the logged data at a certain speed using an async function.

        Parameters
        ----------
        speed : float
            Speed multiplier to determine how fast to send out the data. A higher value means faster.
        """

        logging.info(f"⚡ Playback initiated at {speed}x speed ⚡")

        # Run the event loop to issue out all of the MQTT publishes
        asyncio.run(self._publish(speed))

    async def _publish(self, speed) -> None:
        """Async function that collects all the necessary publish functions and gathers them to then be run by the
        event loop.

        Parameters
        ----------
        speed : float
            Speed multiplier to determine how fast to send out the data. A higher value means faster.
        """

        async def _publish_aux(row):
            scaled_sleep = row["time_delta"] / speed
            await asyncio.sleep(scaled_sleep)

            if self._VERBOSE:
                logging.info(
                    f"{round(row['time_delta'], 5): <10} | {round(scaled_sleep, 5): <10} | {row['mqtt_topic']: <50} | {row['message']}"
                )

            try:
                publish.single(
                    row["mqtt_topic"], row["message"], hostname=self._BROKER_ADDRESS
                )
            except Exception as e:
                logging.error(e)

        publish_queue = []
        for row in self._log_data:
            publish_queue.append(_publish_aux(row))

        # Load all async operation at the start using gather
        await asyncio.gather(*publish_queue, return_exceptions=True)


def log_to_dataframe(input_filepath: str) -> DataFrame:
    """ Converts a log file to a pandas dataframe, flattening the nested data.

        Parameters
        ----------
        input_filepath : str
            filepath of the log to be converted to a dataframe

        Returns
        ----------
        DataFrame
            A pandas dataframe containing all of the logged values
    """

    array_of_dicts = []
    with open(input_filepath, mode="r") as csv_file:
        csv_reader = csv.DictReader(
            csv_file,
            delimiter=CsvConfig["delimiter"],
            quotechar=CsvConfig["quotechar"],
            quoting=CsvConfig["quoting"],
            fieldnames=CsvConfig["fieldnames"],
        )

        # First row is filled with crappy headers so not included
        row_num = 0
        finished = False
        while not finished:
            try:
                row = next(csv_reader, None)
            except Exception as e:
                logging.error(f"{type(e)}:{e} @ csv row {row_num}")

            if row is None:
                finished = True

            if row_num != 0 and not finished:
                array_of_dicts.append(
                    {
                        "time_delta": row["time_delta"],
                        "MQTT_topic": row["mqtt_topic"],
                        **_flatten(row["message"]),  # COPY THING
                    }
                )

            row_num += 1

    df = pd.DataFrame.from_dict(array_of_dicts)

    # convert the time_delta to numbers (weird parsing bug)
    df["time_delta"] = pd.to_numeric(df["time_delta"])

    return df


def _flatten(message_string: str) -> dict:
    """ Flattens a dict so that it goes from deeply nested to one level deep. Works BEST with 
        the MHP MQTT JSON data structure.

        Parameters
        ----------
        message_string : str
            Takes a single JSON line from the raw log file

        Returns
        ----------
        Dict
            A dictionary containing the flattened data only a single level deep

    """

    # If there is not JSON it will error out and return the message string
    try:
        message_json = json.loads(message_string)
        prefix_key = "data"
        return _flatten_aux(prefix_key, message_json)

    except json.decoder.JSONDecodeError:
        return {"message": message_string}


def _flatten_aux(last_key: str, message_json: dict or str) -> dict:
    """ The auxiliary recursive function for _flatten which does all of the hard work flattening the dict.

        Parameters
        ----------
        last_key : str
            The last key from the dict above. Is used as the name of each item in the flattened dict.
        message_json : dict or str
            Depending on how deep the recursion has been it will either be a dict or a string

        Returns
        ----------
        Dict
            A dictionary containing the flattened data only a single level deep (once finished)
    """

    # In the case of an empty list return an empty list
    if message_json == {}:
        return {}

    # In the case of a string or number record the value with the last key
    elif (
        isinstance(message_json, int)
        or isinstance(message_json, float)
        or isinstance(message_json, str)
    ):
        return {last_key: message_json}

    # In the case of a list parse each index individually
    elif isinstance(message_json, list):
        flat_dict = {}
        for item in message_json:
            flat_dict.update(_flatten_aux(last_key, item))

        return flat_dict

    # In the case of a "type" "value" pair set the key to the type (MHP structure)
    elif (
        isinstance(message_json, dict)
        and len(message_json.keys()) == 2
        and "type" in message_json.keys()
        and "value" in message_json.keys()
    ):
        return _flatten_aux(f"{last_key}_{message_json['type']}", message_json["value"])

    # In the case of a nested dict (most general)
    else:
        flat_dict = {}
        for key in message_json.keys():
            next_key = f"{last_key}_{key}"
            next_json = message_json[key]

            flat_dict.update(_flatten_aux(next_key, next_json))

        return flat_dict


def topic_filter(df: DataFrame, topic: str) -> DataFrame:
    """ Filters a dataframe created from a log according to its MQTT topic

        Parameters
        ----------
        df : DataFrame
            A dataframe created by log_to_dataframe
        topic : str
            Specifies the MQTT topic that the df is filtered against

        Returns
        ----------
        DataFrame
            It is simply the input dataframe with only the input topic stored 
    """

    # Create a filtered for a specific topic
    filter = df["MQTT_topic"] == topic
    filtered_df = df.loc[filter]

    # Remove NaN cols to make more compact (aka drop)
    filtered_df = filtered_df.dropna(axis=1)

    return filtered_df


def multi_sheet_excel(input_filepath: str, output_filepath: str) -> None:
    """ Converts an input log to an excel file with multiply sheets and saves it at the output filepath

        Parameters
        ----------
        input_filepath : str
            Input log filepath (log file created by the MQTT_recorder)
        output_filepath : str
            Specifies where the excel file will be outputted to
    """

    df = log_to_dataframe(input_filepath)

    # Find all unique topics
    topics = []
    for topic in df["MQTT_topic"]:
        if topic not in topics:
            topics.append(topic)

    # Make a DataFrame for each topic
    dfs = []
    for topic in topics:
        topic_tuple = (topic_filter(df, topic), topic)
        dfs.append(topic_tuple)

    # Merge all dataframes into excel sheets
    Excelwriter = pd.ExcelWriter(output_filepath, engine="openpyxl")

    for (df, topic) in dfs:
        # Excel cannot except / in the sheet names so we replace with -
        excel_safe_topic = topic.lstrip("/")  # remove starting / for nicer page names
        excel_safe_topic = excel_safe_topic.replace("/", "-")
        df.to_excel(Excelwriter, sheet_name=excel_safe_topic, index=True)

    Excelwriter.save()
