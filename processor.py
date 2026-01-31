import numpy as np
import os
from pathlib import Path

def calculate_rms(emg_signal):
    """
    Optimized RMS calculation.
    Supports both single channel (1D) and multiple channels (2D).
    """
    if emg_signal.ndim == 2:
        # Vectorized RMS across time axis for all 8 channels
        return np.sqrt(np.mean(emg_signal**2, axis=1))
    return np.sqrt(np.mean(emg_signal**2))

def calculate_rom(imu_data):
    """Calculates Max Flexion using gravity vector trigonometry."""
    if imu_data.shape[1] < 3:
        return 0.0
    
    # Using Ay and Az to find the inclination angle
    ay = imu_data[:, 1]
    az = imu_data[:, 2]
    
    # Calculate angles for every sample point in the trial
    angles = np.abs(np.degrees(np.arctan2(ay, az)))
    return np.max(angles)

def process_live_packet(imu_list, emg_list):
    """
    New function to handle real-time data from Rachel/Maria's microcontrollers.
    Converts incoming lists to numpy and returns instant metrics.
    """
    imu = np.array(imu_list)
    emg = np.array(emg_list)
    
    live_rom = calculate_rom(imu)
    # Average RMS across all 8 channels for a single intensity metric
    live_rms = np.mean(calculate_rms(emg))
    
    return round(float(live_rom), 1), round(float(live_rms), 5)

def get_weekly_progress(subject_id, activity_folder, base_path):
    """Fetches historical data for trends."""
    rom_data = []
    rms_data = []
    
    path = Path(base_path) / subject_id / str(activity_folder)
    if not path.exists():
        return [0], [0]

    # Numeric sort for Trial_1, Trial_2, etc.
    trials = sorted(path.glob("Trial_*"), key=lambda x: int(x.name.split('_')[1]))
    
    for trial in trials:
        imu_file = trial / "imu.npy"
        emg_file = trial / "emg.npy"

        if imu_file.exists():
            imu = np.load(imu_file)
            rom_data.append(round(float(calculate_rom(imu)), 1))
        
        if emg_file.exists():
            emg = np.load(emg_file)
            # Calculate mean intensity across all 8 channels
            avg_rms = np.mean(calculate_rms(emg))
            rms_data.append(round(float(avg_rms), 5))

    return (rom_data if rom_data else [0]), (rms_data if rms_data else [0])