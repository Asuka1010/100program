import neurokit2 as nk
import numpy as np
import json
import asyncio
from fastapi import FastAPI, WebSocket
from scipy.signal import correlate

app = FastAPI()

# Load ECG Data
data = nk.data("bio_resting_8min_200hz")
ecg_1 = data["S01"]["ECG"]  # ECG data for Person 1
ecg_2 = data["S03"]["ECG"]  # ECG data for Person 2

# Assume sampling rate of 200Hz (200 samples per second)
sampling_rate = 200
window_size = sampling_rate  # 1 second of data at a time

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket Connection Established!")

    for i in range(0, len(ecg_1) - window_size, window_size):
        # Extract 1-second ECG segments
        segment_1 = ecg_1[i:i + window_size]
        segment_2 = ecg_2[i:i + window_size]

        if len(segment_1) < window_size or len(segment_2) < window_size:
            break  # Stop when there is not enough data

        # Compute correlation for the current second
        correlation = correlate(segment_1, segment_2, mode='valid')
        max_correlation = float(np.max(correlation))  # Convert to standard float

        print(f"Time: {i//sampling_rate}s - Max Correlation: {max_correlation}")  # Debugging output

        # Ensure the JSON data structure matches what the frontend expects
        correlation_data = {
            "time": i // sampling_rate,  # Convert sample index to seconds
            "max_correlation": max_correlation
        }

        # Send data to the frontend
        await websocket.send_text(json.dumps(correlation_data))

        # Wait 1 second before sending the next update
        await asyncio.sleep(1)
