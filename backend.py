import asyncio
import threading
import numpy as np
from flask import Flask
from flask_socketio import SocketIO
from bleak import BleakClient, BleakScanner

# Flask サーバー設定
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # CORS 有効化

# Bluetooth UUID（Heart Rate Measurement UUID）
HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# 心拍データ保存用
real_hr_data = []
simulated_hr_data = []

# **Polar H10 をスキャンする関数**
async def find_polar_h10():
    print("🔍 Searching for Polar H10 devices...")
    devices = await BleakScanner.discover()

    for device in devices:
        if device.name and "Polar H10" in device.name:  # 名前に "Polar H10" を含むデバイスを探す
            print(f"✅ Found Polar H10: {device.address}")
            return device.address

    print("❌ No Polar H10 found. Make sure it's turned on and worn.")
    return None

# **心拍データを取得 & WebSocket 送信**
async def hr_callback(sender, data):
    """Polar H10 から心拍データを取得し、WebSocket で送信"""
    flags = data[0]
    hr_value = data[1] if (flags & 0x01) == 0 else int.from_bytes(data[1:3], byteorder="little", signed=False)

    print(f"📡 Heart Rate: {hr_value} bpm")

    # 擬似的な2人目の心拍データ（少しノイズを加える）
    simulated_value = hr_value + np.random.normal(0, 2)

    # データを保存
    real_hr_data.append(hr_value)
    simulated_hr_data.append(simulated_value)

    # 過去30秒分のデータのみ保持
    if len(real_hr_data) > 30:
        real_hr_data.pop(0)
        simulated_hr_data.pop(0)

    # 相関係数を計算
    correlation = np.corrcoef(real_hr_data, simulated_hr_data)[0, 1] if len(real_hr_data) > 5 else 0

    # フロントエンドへデータ送信
    socketio.emit("heart_rate", {
        "real_heart_rate": hr_value,
        "simulated_heart_rate": simulated_value,
        "correlation": round(correlation, 2)
    })

# **Polar H10 に接続**
async def connect_polar():
    polar_address = await find_polar_h10()  # スキャンしてデバイスアドレスを取得
    if not polar_address:
        return  # Polar H10 が見つからなかったら終了

    async with BleakClient(polar_address) as client:
        print("✅ Connected to Polar H10!")

        try:
            await client.start_notify(HEART_RATE_UUID, hr_callback)
            await asyncio.sleep(600)  # 10分間データを取得
        except Exception as e:
            print(f"❌ Error starting notifications: {e}")

        try:
            if client.is_connected:
                await client.stop_notify(HEART_RATE_UUID)
                print("✅ Stopped Heart Rate streaming.")
        except Exception as e:
            print(f"⚠️ Warning: Could not stop notifications: {e}")

# **非同期処理をバックグラウンドで実行**
def run_asyncio():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_polar())

# **バックグラウンドスレッドで Polar H10 の接続を開始**
threading.Thread(target=run_asyncio, daemon=True).start()

# **Flask サーバーを起動**
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
