import asyncio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
from bleak import BleakClient

# Replace with your real Polar H10 address
POLAR_H10_ADDRESS = "F79FD746-804F-5E8F-FA33-28A9EC051003"
ECG_UUID = "fb005c51-02e7-f387-1cad-8acd2d8df0c8"

# Data storage
real_ecg_data = []
simulated_ecg_data = []
time_data = []

# Function to get real ECG data and simulate second device
async def ecg_callback(sender, data):
    real_value = int.from_bytes(data[:2], byteorder="little", signed=True)
    real_ecg_data.append(real_value)

    # Simulated second device (adding slight noise & delay)
    simulated_value = real_value + np.random.normal(0, 50)
    simulated_ecg_data.append(simulated_value)

    time_data.append(len(real_ecg_data))  # Use index as time

# Function to connect to Polar H10
async def connect_polar():
    async with BleakClient(POLAR_H10_ADDRESS) as client:
        print("Connected to Polar H10!")
        await client.start_notify(ECG_UUID, ecg_callback)
        await asyncio.sleep(30)  # Run for 30 seconds
        try:
            await client.stop_notify(ECG_UUID)
        except Exception as e:
            print(f"Error stopping notifications: {e}")
        print("Stopped ECG streaming.")

# Function to run asyncio inside matplotlib animation
def run_asyncio_in_background():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_polar())

import threading
threading.Thread(target=run_asyncio_in_background, daemon=True).start()

# Plot setup
fig, ax = plt.subplots()
ax.set_xlim(0, 300)
ax.set_ylim(-2000, 2000)
ax.set_title("Heart Rate Synchronization")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Heart Rate")

# Plot lines for both datasets
line1, = ax.plot([], [], label="Real Heart Rate", color="blue")
line2, = ax.plot([], [], label="Simulated Heart Rate", color="red")

# Annotation for high correlation effect
text = ax.text(0.5, 0.9, "", transform=ax.transAxes, ha="center", fontsize=12, color="green")

# Update function for live animation
def update(frame):
    if len(real_ecg_data) > 100 and len(simulated_ecg_data) > 100:
        # Get the last 100 data points
        segment_1 = np.array(real_ecg_data[-100:])
        segment_2 = np.array(simulated_ecg_data[-100:])
        time_segment = time_data[-100:]

        # Update the plot
        line1.set_data(time_segment, segment_1)
        line2.set_data(time_segment, segment_2)

        # Compute correlation
        correlation = np.corrcoef(segment_1, segment_2)[0, 1]
        ax.set_title(f"Heart Rate Synchronization (Correlation: {correlation:.2f})")

        # Show effect when correlation is high
        if correlation > 0.8:
            text.set_text("✨ High Synchronization ✨")
        else:
            text.set_text("")

    return line1, line2, text

# Run animation
ani = animation.FuncAnimation(fig, update, interval=1000, cache_frame_data=False)

# Show the plot
plt.legend()
plt.show()

import asyncio
from bleak import BleakClient, BleakScanner

async def find_characteristics():
    print("Scanning for devices...")
    devices = await BleakScanner.discover()

    for device in devices:
        if "Polar H10" in (device.name or ""):
            print(f"✅ Found Polar H10: {device.address}")
            async with BleakClient(device.address) as client:
                print("🔍 Listing available services and characteristics...")
                for service in client.services:
                    print(f"\n🔹 Service: {service.uuid}")
                    for char in service.characteristics:
                        print(f"   🟢 Characteristic: {char.uuid}")

await find_characteristics()
