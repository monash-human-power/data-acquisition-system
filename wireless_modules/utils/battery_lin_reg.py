"""
A quick script to calibrate the battery ADC for the WMs.
Power the WM from a bench power supply with a bunch of different voltages,
put the measured and true values below, run the script,
and then use the slope and intercept in the WM code.

Results from below input:
Slope: 		0.7106689209693502
Intercept:	0.9267915203537527
R^2: 		0.9847840762003852
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

true_voltages = np.array(
    [
        3.00,
        3.10,
        3.20,
        3.30,
        3.40,
        3.50,
        3.60,
        3.70,
        3.80,
        3.90,
        4.00,
        4.10,
        4.20,
    ]
)
read_voltages = np.array(
    [
        3.02,
        3.12,
        3.25,
        3.33,
        3.44,
        3.55,
        3.69,
        3.83,
        3.97,
        4.15,
        4.33,
        4.50,
        4.72,
    ]
)

result = linregress(read_voltages, true_voltages)
print(f"Slope:\t\t{result.slope}")
print(f"Intercept:\t{result.intercept}")
print(f"R^2:\t\t{result.rvalue ** 2}")

plt.plot(read_voltages, true_voltages, label="Raw values")
plt.plot(
    read_voltages, read_voltages * result.slope + result.intercept, label="Modelled"
)
plt.grid(which="both")
plt.legend()
plt.xlabel("Measured voltage")
plt.ylabel("True voltage")
plt.show()