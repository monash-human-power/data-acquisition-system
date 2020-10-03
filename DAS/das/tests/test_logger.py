from das.utils import logger
import shutil
import os
import time
import unittest
import csv
import pandas as pd

CsvConfig = {
    "delimiter": ",",
    "quotechar": "`",
    "quoting": csv.QUOTE_ALL,
    "skipinitialspace": True,
    "fieldnames": ["time_delta", "mqtt_topic", "message"],
}

CURRENT_FILEPATH = os.path.dirname(__file__)

# Used to store the logs created by the tests
TEST_FOLDER = os.path.join(CURRENT_FILEPATH, "csv_data")

# Sample MQTT broker to run tests on
MQTT_BROKER = "broker.hivemq.com"


class LoggerBaseTestTearDown(unittest.TestCase):
    def tearDown(self):
        # Clean up and remove test folder
        shutil.rmtree(TEST_FOLDER)

        # Check that the cleanup worked
        assert not os.path.exists(TEST_FOLDER)


class TestSingleRecorder(LoggerBaseTestTearDown):
    def setUp(self):
        # Start and stop logger immediately
        recorder_1 = logger.Recorder(
            csv_folder_path=TEST_FOLDER, topics=["sensor/#"], broker_address=MQTT_BROKER
        )
        recorder_1.start()
        recorder_1.stop()

    def test_make_csv_folder(self):
        # Check that a directory called csv_data has been created and 1_log.csv has been created
        assert os.path.exists(TEST_FOLDER)
        assert os.path.exists(os.path.join(TEST_FOLDER, "1_log.csv"))


class TestMultipleRecorders(LoggerBaseTestTearDown):
    def setUp(self):

        self.log_to_topic = {
            "1_log.csv": "sensor",
            "2_log.csv": "test",
            "3_log.csv": "data",
        }

        # Start logger 1 for sensor/#
        recorder_1 = logger.Recorder(
            csv_folder_path=TEST_FOLDER,
            topics=[f"{self.log_to_topic['1_log.csv']}/#"],
            broker_address=MQTT_BROKER,
        )

        # Start logger 2 for test/#
        recorder_2 = logger.Recorder(
            csv_folder_path=TEST_FOLDER,
            topics=[f"{self.log_to_topic['2_log.csv']}/#"],
            broker_address=MQTT_BROKER,
        )

        # Start logger 3 for data/#
        recorder_3 = logger.Recorder(
            csv_folder_path=TEST_FOLDER,
            topics=[f"{self.log_to_topic['3_log.csv']}/#"],
            broker_address=MQTT_BROKER,
        )

        # Start all recorders
        recorder_1.start()
        recorder_2.start()
        recorder_3.start()

        # Wait for a short amount of time
        time.sleep(5)

        # Pause the recorders at different times
        recorder_3.stop()
        recorder_1.stop()
        recorder_2.stop()

    def test_number_of_logs(self):
        # Check that a directory called csv_data has been created
        assert os.path.exists(TEST_FOLDER)

        # Check that there are 3 logs in the test folder
        assert len(os.listdir(TEST_FOLDER)) == 3

    def test_correct_output_logs(self):
        # Ensure that each log file is correctly formatted
        for filepath in os.listdir(TEST_FOLDER):
            log_file = open(os.path.join(TEST_FOLDER, filepath), "r")
            csv_reader = csv.DictReader(
                log_file,
                delimiter=CsvConfig["delimiter"],
                quotechar=CsvConfig["quotechar"],
                quoting=CsvConfig["quoting"],
                skipinitialspace=CsvConfig["skipinitialspace"],
            )

            for row in csv_reader:
                # Assert that the rows contain data and are not null
                assert row["time_delta"]

                # The correct log should contain the correct data
                assert row["mqtt_topic"].startswith(self.log_to_topic[filepath])

                # Assert that the message is a string
                assert isinstance(row["message"], str)

            log_file.close()


class TestPlayback(LoggerBaseTestTearDown):
    def setUp(self):
        main_recorder = logger.Recorder(
            csv_folder_path=TEST_FOLDER, topics=["sensor/#"], broker_address=MQTT_BROKER
        )

        # Wait for a short amount of time
        main_recorder.start()
        time.sleep(5)
        main_recorder.stop()

    def test_accurate_playback(self):
        main_recorder = logger.Recorder(TEST_FOLDER)
        main_playback = logger.Playback(os.path.join(TEST_FOLDER, "1_log.csv"))

        main_recorder.start()
        main_playback.play(speed=10)
        main_recorder.stop()

        log_file1 = os.path.join(TEST_FOLDER, "1_log.csv")
        original_df = pd.read_csv(
            log_file1,
            quotechar=CsvConfig["quotechar"],
            quoting=CsvConfig["quoting"],
            skipinitialspace=CsvConfig["skipinitialspace"],
        )

        log_file2 = os.path.join(TEST_FOLDER, "2_log.csv")
        playback_df = pd.read_csv(
            log_file2,
            quotechar=CsvConfig["quotechar"],
            quoting=CsvConfig["quoting"],
            skipinitialspace=CsvConfig["skipinitialspace"],
        )

        assert playback_df["message"].equals(original_df["message"])
