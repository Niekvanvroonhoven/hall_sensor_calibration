import math

class CalibrationLogicProcessor:
    def __init__(self, calibration_angle=0.0, max_history_length=100, peak_threshold=0.5, peak_window_size=11):
        # 1. Memory for data and settings
        self.data_history = []
        self.max_history_length = max_history_length
        self.peak_threshold = peak_threshold
        self.peak_window_size = peak_window_size + (peak_window_size + 1)%2

        # 2. Tracking angles
        self.calibration_angle = calibration_angle

    def clear_history(self):
        self.data_history.clear()

       
    def get_time_series_peaks(self):
        if len(self.data_history) < self.peak_window_size:
            return None

        peaks = []

        for start_ind in range(len(self.data_history) - self.peak_window_size + 1):
            window = self.data_history[start_ind:start_ind + self.peak_window_size]

            sensor_values = [x["sensor"] for x in window]

            center = self.peak_window_size // 2

            if (
                sensor_values[center] == max(sensor_values)
                and min(sensor_values) >= self.peak_threshold
            ):
                peak_index = start_ind + center

                peaks.append({
                    "index": peak_index,
                    "angle": self.data_history[peak_index]["angle"]
                })

        return peaks if peaks else None 


    def find_delta_angle(self):
        #this fucntion expects only one peak to be found
        peaks = self.get_time_series_peaks()

        if peaks is None:
            return None

        for peak in peaks:
            peak_idx = peak["index"]

            # Need 2 samples before and after
            if peak_idx < 2 or peak_idx >= len(self.data_history) - 2:
                continue

            directions = [
                self.data_history[i]["direction"]
                for i in range(peak_idx - 2, peak_idx + 3)
            ]

            # Ignore if any direction is unknown
            if None in directions:
                continue

            # Reject peak if direction changes inside window
            if len(set(directions)) != 1:
                continue

            return peak["angle"]


        return None


    def process_messages(self, sensor_readout, predicted_angle):
        # Determine direction
        direction = None

        if self.data_history:
            previous_angle = self.data_history[-1]["angle"]

            # shortest signed angular difference
            delta = (predicted_angle - previous_angle + 180) % 360 - 180

            if delta > 0:
                direction = "CCW"
            elif delta < 0:
                direction = "CW"
            else:
                direction = self.data_history[-1].get("direction")

        new_entry = {
            "sensor": sensor_readout,
            "angle": predicted_angle,
            "direction": direction,
        }

        self.data_history.append(new_entry)

        if len(self.data_history) > self.max_history_length:
            self.data_history.pop(0)

        # 3. Attempt to find a new delta angle 
        calculated_delta = self.find_delta_angle()

        # 4. Evaluate the calculated delta against our rules
        if calculated_delta is not None:
            # Wipe the array so we don't double count this peak
            self.clear_history() 
            # Return the true flag and the new delta
            return {
                "delta_angle": calculated_delta
            }

        # 5. Default return if no peak was found, or if drift was under threshold
        return {
            "delta_angle": None
        }
    



# ==========================================
# TEST HARNESS
# ==========================================
def run_simulation():
    # Initialize with a smaller window for quicker testing
    processor = CalibrationLogicProcessor(peak_threshold=0.6, peak_window_size=5)
    
    print("Starting continuous calibration simulation...\n")
    print(f"{'Step':<6} | {'Angle':<7} | {'Sensor':<7} | {'Direction':<10} | {'Result'}")
    print("-" * 55)

    # Simulate a mechanism rotating clockwise.
    # Angles count down: 20, 15, 10, 5, 0, 355, 350...
    target_peak_angle = 345
    angles = [(20 - i) % 360 for i in range(125)]

    for i, angle in enumerate(angles):
        # Simulate an analog sensor that spikes cleanly at 'target_peak_angle'
        angular_distance = min(abs(angle - target_peak_angle), 360 - abs(angle - target_peak_angle))
        
        # Create a bell-curve (Gaussian) shaped peak
        if angular_distance == 0:
            sensor_val = 0.95 # Peak
        elif angular_distance <= 5:
            sensor_val = 0.75 # Shoulders
        elif angular_distance <= 10:
            sensor_val = 0.40 # Base
        else:
            sensor_val = 0.10 # Noise floor

        # Process the simulated message
        result = processor.process_messages(sensor_val, angle)
        
        # Fetch the calculated direction for the console output
        current_dir = processor.data_history[-1]["direction"] if processor.data_history else "None"

        print(f"{i+1:<6} | {angle:>3}°   | {sensor_val:.3f}   | {str(current_dir):<10} | {result}")

        # Break if calibration was successful
        if result["delta_angle"] is not None:
            print(f"\n✅ SUCCESS: Calibration triggered! True peak isolated at angle: {result['delta_angle']}°")
            break

if __name__ == "__main__":
    run_simulation()