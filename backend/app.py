from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
from pathlib import Path
import processor  # Make sure processor.py exists and is importable

app = Flask(__name__)
CORS(app)

# ===============================
# CONFIG
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = str(BASE_DIR / "data")
SUBJECT_ID = "Subject_2" # changing this as needed to test out
# ===============================
# HISTORICAL DATA ENDPOINT
# ===============================
@app.route('/api/patient-history', methods=['GET'])
def get_history():
    print("\n🔥 /api/patient-history endpoint HIT")

    # Activity mapping (verified against dataset)
    # 0 = Squat, 3 = Extension, 6 = Gait
    activities = {
        "squat": 0,
        "extension": 3,
        "gait": 6
    }

    response = {}

    for name, folder_id in activities.items():
        print(f"➡️ Processing activity: {name} (ID={folder_id})")

        try:
            rom, rms, rom_summary, rms_summary = processor.get_weekly_progress(
                SUBJECT_ID,
                folder_id,
                DATA_DIR
            )

            print("   ROM:", rom)
            print("   RMS:", rms)
            print("   ROM summary:", rom_summary)
            print("   RMS summary:", rms_summary)

            response[name] = {
                "rom": rom,
                "rms": rms,
                "romSummary": rom_summary,
                "rmsSummary": rms_summary,
                "completion": [90 for _ in rom],  # placeholder adherence
                "currentRom": rom[-1] if len(rom) > 0 else 0,
                "romChange": (
                    f"{round(rom[-1] - rom[0], 1)}°"
                    if len(rom) > 1 else "0°"
                )
            }

        except Exception as e:
            print(f"ERROR processing {name}: {e}")

            # Fail gracefully so frontend still loads
            response[name] = {
                "rom": [],
                "rms": [],
                "romSummary": {},
                "rmsSummary": {},
                "completion": [],
                "currentRom": 0,
                "romChange": "0°"
            }

    print("FINAL RESPONSE:")
    print(response)
    return jsonify(response)

# ===============================
# testing endpoint
# ===============================
@app.route('/api/live-data', methods=['POST'])
def live_data():
    print("\n🔥 /api/live-data endpoint HIT")

    data = request.get_json()

    if not data:
        print("No JSON received")
        return jsonify({"error": "No data received"}), 400

    imu_list = data.get("imu", [])
    emg_list = data.get("emg", [])

    print("   IMU packets:", len(imu_list))
    print("   EMG packets:", len(emg_list))

    if not imu_list or not emg_list:
        print("Invalid data format")
        return jsonify({"error": "Invalid data format"}), 400

    try:
        live_rom, live_rms = processor.process_live_packet(
            imu_list,
            emg_list
        )

        response = {
            "liveRom": round(float(live_rom), 2),
            "liveRms": round(float(live_rms), 5)
        }

        print("LIVE RESPONSE:", response)
        return jsonify(response)

    except Exception as e:
        print("Live processing error:", e)
        return jsonify({"error": "Processing failure"}), 500


# ===============================
# RUN SERVER
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
