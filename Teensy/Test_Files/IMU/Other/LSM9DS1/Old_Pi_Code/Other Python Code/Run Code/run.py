# ---------------------------------------------------------------------
# Last Modified:
#   30-12-2017
# Description:
#   This program is the test master. It decides which modules run append
#   and in what order.
# ---------------------------------------------------------------------

import subprocess
from time import sleep

p1 = subprocess.Popen(["python", "datav2a.py"])
print("\nStarting Data Recording v2a...")
sleep(1)

while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        p1.terminate()
        print("\n\nExecution Terminated.\n")
        break

p3 = subprocess.call('/home/pi/Documents/MHP_raspicam/Accelerometers/LSM9DS1/BumpTest_Code/Shell_Scripts/sendcsv.sh')
sleep(1)
