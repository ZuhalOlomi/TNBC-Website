from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import processor # Ensure your processor.py is updated to handle single-packet logic

app = Flask(__name__)
CORS(app)

SUBJECT_ID = "Subject_15"
DATA_DIR = "./dataset"  # Path to folder containing Subject_15

# --- HISTORICAL DATA ENDPOINT ---
@app.route('/api/patient-history', methods=['GET'])
def get_history():
    # Activity mapping verified from UTBIOME dataset
    # 0 = Squat, 3 = Extension, 6 = Gait
    activities = {"squat": 0, "extension": 3, "gait": 6}
    response = {}

    for name, folder_id in activities.items():
        rom, rms = processor.get_weekly_progress(SUBJECT_ID, folder_id, DATA_DIR)

        response[name] = {
            "rom": rom,
            "rms": rms,
            "completion": [int(np.random.randint(85, 100)) for _ in rom],
            "currentRom": rom[-1] if rom else 0,
            "romChange": f"{round(rom[-1] - rom[0], 1) if rom else 0}°"
        }

    return jsonify(response)

# --- NEW: REAL-TIME DATA ENDPOINT ---
@app.route('/api/live-data', methods=['POST'])
def receive_live_data():
    data = request.json  # Expected format: {"imu": [...], "emg": [...]}
    
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Convert incoming lists to numpy for processing
    imu_array = np.array(data.get('imu', []))
    emg_array = np.array(data.get('emg', []))

    # Calculate real-time metrics
    live_rom = processor.calculate_rom(imu_array)
    live_rms = processor.calculate_rms(emg_array)

    # In a full implementation, you'd save this to a 'LiveTrial' folder 
    # or Maria's SD card interface logic here.
    return jsonify({
        "status": "success",
        "current_rom": round(float(live_rom), 1),
        "current_rms": round(float(live_rms), 5)
    })

if __name__ == '__main__':
    # Setting host to '0.0.0.0' allows the ESP32 to connect to your PC's IP
    app.run(debug=True, port=5000, host='0.0.0.0')