from dotenv import load_dotenv
from log_2_excel import DataLogger

import os







if __name__ == "__main__":

        # Load env variables
    load_dotenv()
    mqtt_log_file = os.getenv("MQTT_LOG_FILE")
    excel_log_file = os.getenv("EXCEL_LOG_FILE")

    DATALOGGER = DataLogger(
        db_file=mqtt_log_file,
        xl_file=excel_log_file
        )
    
    for f in os.listdir(mqtt_log_file):
        
        name, ext = os.path.splitext(f)
        if ext == ".db":
            time = name[8:]
            xl_ext = excel_log_file + "runfile" + time + ".xlsx"
            db_ext = mqtt_log_file + f

            DATALOGGER.convertXL(db_ext, xl_ext)