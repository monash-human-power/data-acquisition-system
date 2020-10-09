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
    "input_log",
    action="store",
    help="""Filepath for outputted MQTT log. Accepts either .csv or .xlsx""",
)

parser.add_argument(
    "-o",
    "--output",
    action="store",
    default=None,
    help="""Filepath for outputted MQTT log. Accepts either .csv or .xlsx""",
)

parser.add_argument(
    "-v", "--verbose", action="store_true", default=False, help="""Verbose output""",
)

if __name__ == "__main__":
    CURRENT_FILEPATH = os.path.dirname(__file__)
    OUTPUT_FOLDER = os.path.join(CURRENT_FILEPATH, "csv_data_exported")

    try:
        #  Remove later
        # args.input_log = "/Users/blake/Sync/Projects/MHP_2020/data-acquisition-system/DAS/das/csv_data/136_log.csv"

        # Read command line arguments
        args = parser.parse_args()

        # Create csv_folder_path folder if none exists
        Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

        LOG_NAME = os.path.basename(args.input_log).split(".")[
            0
        ]  # Remove '.csv' extension
        OUTPUT_CSV_FILEPATH = os.path.join(OUTPUT_FOLDER, f"{LOG_NAME}.csv")
        OUTPUT_EXCEL_FILEPATH = os.path.join(OUTPUT_FOLDER, f"{LOG_NAME}.xlsx")

        # Create dataframe from input file
        df = logger.log_to_dataframe(args.input_log)

        # No output file has been selected (Export to default folder for both CSV and excel)
        if args.output is None:
            print("Excel saved at:", OUTPUT_EXCEL_FILEPATH)
            logger.make_nice_excel_with_many_topics(
                args.input_log, OUTPUT_EXCEL_FILEPATH
            )

            print("CSV saved at:  ", OUTPUT_CSV_FILEPATH)
            df.to_csv(OUTPUT_CSV_FILEPATH)

        # Output a CSV from log
        elif args.output.endswith(".csv"):
            print("CSV saved at:  ", args.output)
            df.to_csv(args.output)

        # Output a excel file from log
        elif args.output.endswith(".xlsx"):
            print("Excel saved at:", args.output)
            logger.make_nice_excel_with_many_topics(args.input_log, args.output)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print(f"{type(e)}: {e}")
