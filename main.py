import neurokit2 as nk
data = nk.data("bio_resting_8min_200hz")

data.keys()
#dict_keys(['S01', 'S02', 'S03', 'S04'])

data["S01"].head()
#nk.signal_plot(data["S01"]["ECG"])
#nk.signal_plot(data["S02"]["ECG"])
#nk.signal_plot(data["S03"]["ECG"])
#nk.signal_plot(data["S04"]["ECG"])

import numpy as np
from scipy.signal import correlate

ecg_1 = data["S01"]["ECG"][:1000]
ecg_2 = data["S03"]["ECG"][:1000]
correlation = correlate(ecg_1, ecg_2, mode='full')

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 4))
plt.plot(ecg_1, label='ECG 1')
plt.plot(ecg_2, label='ECG 2')
plt.legend()
plt.title('ECG Comparison')
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(ecg_1, label="ECG 1")  # Show first 1000 samples
plt.plot(ecg_2, label="ECG 2")
plt.title("ECG Comparison (First 1000 Samples)")
plt.xlabel("Sample Index")
plt.ylabel("ECG Signal")
plt.legend()
plt.show()

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
rng = np.random.default_rng()

# sig to ecg_1 sig = np.repeat([0., 1., 1., 0., 1., 0., 0., 1.], 128)
# sig_noise to ecg_2 sig_noise = sig + rng.standard_normal(len(sig))
corr = signal.correlate(ecg_2, np.ones(166), mode='same') / 166

clock = np.arange(83, len(ecg_1), 166)
fig, (ax_orig, ax_noise, ax_corr) = plt.subplots(3, 1, sharex=True)
ax_orig.plot(ecg_1)
ax_orig.plot(clock, ecg_1[clock], 'ro')
ax_orig.set_title('ECG_1')
ax_noise.plot(ecg_2)
ax_noise.set_title('ECG_2')
ax_corr.plot(corr)
ax_corr.plot(clock, corr[clock], 'ro')
ax_corr.axhline(0.5, ls=':')
ax_corr.set_title('Cross-correlated with rectangular pulse')
ax_orig.margins(0, 0.1)
fig.tight_layout()
plt.show()

import pandas as pd
# Extract indices where correlation is greater than 0
positive_indices = np.where(corr > 0)[0]  # Get indices where correlation is positive
positive_values = corr[positive_indices]  # Get corresponding correlation values

# Create a DataFrame to display as a table
df = pd.DataFrame({"Index": positive_indices, "Correlation": positive_values})

# Show the first few rows
print(df.head())  # Print a preview in the console