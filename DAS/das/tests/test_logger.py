from das.utils import logger
import shutil
import os

CURRENT_FILEPATH = os.path.dirname(__file__)

# Sample logs are stored here to be used in tests
DATA_FOLDER = os.path.join(CURRENT_FILEPATH, "test_csv_data")
# Used to store the logs created by the tests
TEST_FOLDER = os.path.join(CURRENT_FILEPATH, "csv_data")


def test_Logger_make_csv_folder():
    main_logger = logger.Record(TEST_FOLDER)
    main_logger.stop()

    # Check that a directory called csv_data has been created and 0001_log.csv has been created
    assert os.path.exists(TEST_FOLDER)
    assert os.path.exists(os.path.join(TEST_FOLDER, "0001_log.csv"))

    # Clean up and remove test folder
    shutil.rmtree(TEST_FOLDER)

    # Check that the cleanup worked
    assert not os.path.exists(TEST_FOLDER)
    assert not os.path.exists(os.path.join(TEST_FOLDER, "0001_log.csv"))


def test_Playback_time_diff():

    main_logger = logger.Record(TEST_FOLDER)
    main_playback = logger.Playback(
        os.path.join(DATA_FOLDER, "test_log_1.csv"))

    main_playback.play(100)
    main_logger.stop()
