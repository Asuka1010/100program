import asyncio
import json
import numpy as np
from fastapi import FastAPI, WebSocket
from scipy.signal import correlate
import neurokit2 as nk

app = FastAPI()

# Load ECG data
data = nk.data("bio_resting_8min_200hz")
ecg_1 = data["S01"]["ECG"][:2000]  # First 2000 samples
ecg_2 = data["S03"]["ECG"][:2000]

sampling_rate = 200  # ECG sampling rate
window_size = sampling_rate  # One-second window

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket Connected!")

    try:
        for i in range(0, len(ecg_1) - window_size, window_size):
            segment_1 = ecg_1[i:i + window_size]
            segment_2 = ecg_2[i:i + window_size]

            # Compute real-time correlation
            correlation_value = float(np.corrcoef(segment_1, segment_2)[0, 1])  # Normalized correlation (-1 to 1)

            # Simulated heart rate values (Replace with real sensor data)
            heart_rate_1 = ecg_1
            heart_rate_2 = ecg_2

            correlation_data = {
                "time": i // sampling_rate,
                "heart_rate_1": heart_rate_1,
                "heart_rate_2": heart_rate_2,
                "correlation": round((correlation_value + 1) / 2, 2)  # Normalize to range [0,1]
            }

            await websocket.send_text(json.dumps(correlation_data))
            await asyncio.sleep(1)  # Send data every second

    except Exception as e:
        print(f"❌ Error: {e}")
