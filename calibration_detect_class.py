import math

'''
calling the process message function will return a message containing the delta angle, defined as the current physical motor angle minus the predicted motor angle
'''

class CalibrationLogicProcessor:
    def __init__(self, calibration_angle=0.0, history_buffer_size=11, peak_threshold=0.5):
        # 1. Memory for data and settings
        self.data_history = []
        self.history_buffer_size = history_buffer_size + (history_buffer_size +1)%2 #make the window odd sized so it has a center
        self.peak_threshold = peak_threshold

        # 2. Tracking angles
        self.calibration_angle = calibration_angle

    def clear_history(self):
        self.data_history.clear()

       
    def check_if_peak(self):
        if len(self.data_history) < self.history_buffer_size:
            return None
        
        # extract sensor values
        sensor_values = [x["sensor"] for x in self.data_history]
        center = self.history_buffer_size // 2

        # check if all the values are above the threshold and the middle samle is the maximum
        if (sensor_values[center] == max(sensor_values)
            and min(sensor_values) >= self.peak_threshold):
            return self.data_history[center]["angle"]
        else:
            return None


    def find_delta_angle(self):
        #if the buffer is not full we dont have a peak
        if len(self.data_history) < self.history_buffer_size:
            return None
        
        #check if we have a peak
        peak_angle = self.check_if_peak()

        directions = [
            self.data_history[i]["direction"]
            for i in range(1, self.history_buffer_size)
        ]

        # there must be a peak AND the directions must be the same and not None
        if (None in directions) or (peak_angle is None) or (len(set(directions)) != 1):
            return None

        return self.calibration_angle - peak_angle


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

        if len(self.data_history) > self.history_buffer_size:
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
    processor = CalibrationLogicProcessor(peak_threshold=0.6, history_buffer_size=5)
    
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