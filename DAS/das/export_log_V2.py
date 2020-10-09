from pathlib import Path
import argparse
import os
from das.utils import logger

parser = argparse.ArgumentParser(
    description="Convert MQTT logs to pretty CSVs",
    add_help=True,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "logfile",
    action="store",
    help="""Filepath for MQTT log created from MQTT_recorder (Should be a '.csv' file)""",
)

parser.add_argument(
    "-o",
    "--output",
    action="store",
    default=None,
    help="""Filepath for pretty output MQTT log. Accepts either '.csv' or '.xlsx' files""",
)

if __name__ == "__main__":
    CURRENT_FILEPATH = os.path.dirname(__file__)
    OUTPUT_FOLDER = os.path.join(CURRENT_FILEPATH, "csv_data_exported")

    try:
        # Read command line arguments
        args = parser.parse_args()

        # Create csv_folder_path folder if none exists
        Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

        # Remove '.csv' extension from input filepath
        LOG_NAME = os.path.basename(args.logfile)
        LOG_NAME = LOG_NAME.split(".")[0]

        # Generate file locations when -o is not selected
        OUTPUT_CSV_FILEPATH = os.path.join(OUTPUT_FOLDER, f"{LOG_NAME}.csv")
        OUTPUT_EXCEL_FILEPATH = os.path.join(OUTPUT_FOLDER, f"{LOG_NAME}.xlsx")

        # Create dataframe from input file
        df = logger.log_to_dataframe(args.logfile)

        # No output file has been selected (Export to default folder for both CSV and excel)
        if args.output is None:
            print("Excel saved at:", OUTPUT_EXCEL_FILEPATH)
            logger.make_nice_excel_with_many_topics(args.logfile, OUTPUT_EXCEL_FILEPATH)

            print("CSV saved at:  ", OUTPUT_CSV_FILEPATH)
            df.to_csv(OUTPUT_CSV_FILEPATH)

        # Output a CSV from log
        elif args.output.endswith(".csv"):
            print("CSV saved at:  ", args.output)
            df.to_csv(args.output)

        # Output a excel file from log
        elif args.output.endswith(".xlsx"):
            print("Excel saved at:", args.output)
            logger.make_nice_excel_with_many_topics(args.logfile, args.output)

        else:
            raise ValueError("Output filepath did not end in either '.csv' or '.xlsx'")
    except KeyboardInterrupt:
        pass

    except Exception as e:
        print(f"{type(e)}: {e}")
