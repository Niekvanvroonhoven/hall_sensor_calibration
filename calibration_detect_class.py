import math
import random

'''
calling the process message function will return a message containing the delta angle, defined as the current physical motor angle minus the predicted motor angle
'''

class CalibrationLogicProcessor:
    def __init__(self, calibration_angle=0.0, history_size=11, peak_threshold=0.5):
        # 1. Memory for data and settings
        self.data_history = []
        self.history_size = history_size + (history_size +1)%2 #make the window odd sized so it has a center
        self.peak_threshold = peak_threshold

        # 2. Tracking angles
        self.calibration_angle = calibration_angle

    def clear_history(self):
        self.data_history.clear()

    def get_direction(self, predicted_angle):
        if not self.data_history:
            return None

        previous_angle = self.data_history[-1]["angle"]
        # shortest signed angular difference
        delta = (predicted_angle - previous_angle + 180) % 360 - 180

        if delta > 0:
            return "CCW"
        elif delta < 0:
            return "CW"
        else:
            return None
        
    def check_change_direction(self):
        #clears buffer when we have a change in direction
        directions = [
            self.data_history[i]["direction"]
            for i in range(1, len(self.data_history))
        ]

        if (None in directions) or (len(set(directions)) != 1):
            self.clear_history()


     
    def check_if_peak(self):
        if len(self.data_history) < self.history_size:
            return None
        
        # extract sensor values
        sensor_values = [x["sensor"] for x in self.data_history]
        center = self.history_size // 2

        # check if all the values are above the threshold and the middle samle is the maximum
        if (sensor_values[center] == max(sensor_values)
            and min(sensor_values) >= self.peak_threshold
            and sensor_values[center] > sensor_values[0]
            and sensor_values[center] > sensor_values[-1]):
            return self.data_history[center]["angle"]
        else:
            return None


    def find_delta_angle(self):    
        #check if we have a peak and return the delta angle
        peak_angle = self.check_if_peak()

        if peak_angle == None:
            return None
        else:
            return self.calibration_angle - peak_angle


    def process_messages(self, sensor_readout, predicted_angle):

        direction = self.get_direction(predicted_angle)
        new_entry = {
            "sensor": sensor_readout,
            "angle": predicted_angle,
            "direction": direction,
        }

        self.data_history.append(new_entry)

        if len(self.data_history) > self.history_size:
            self.data_history.pop(0)

        #clears buffer when we have a change in direction
        self.check_change_direction()

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
# REALISTIC TEST HARNESS
# ==========================================

def calculate_sensor_value(current_angle, real_peak_angle, noise_floor, snr_db, radius=10.0, gap=2.0):
    """
    Simulates a magnetic sensor reading based on spatial distance and field strength.
    """
    # 1. Calculate the shortest angular distance to the real peak
    angular_dist = min(abs(current_angle - real_peak_angle), 360 - abs(current_angle - real_peak_angle))
    angular_dist_rad = math.radians(angular_dist)

    # 2. Calculate physical distance in space from sensor to target
    # d^2 = gap^2 + 2 * radius^2 * (1 - cos(theta))
    distance = math.sqrt(gap**2 + 2 * radius**2 * (1 - math.cos(angular_dist_rad)))

    # 3. Calculate Magnetic Field Strength (~ 1/d^3 for dipole)
    # Normalized so that field_strength = 1.0 when perfectly aligned (distance == gap)
    field_strength = (gap / distance)**3

    # 4. Apply Noise Floor (scale signal so peak is 1.0)
    signal = field_strength * (1.0 - noise_floor) + noise_floor

    # 5. Add Gaussian Noise based on SNR
    # SNR(dB) = 20 * log10(Signal_Amplitude / Noise_Amplitude)
    if snr_db < float('inf'):
        sigma = 10 ** (-snr_db / 20.0)
        noise = random.gauss(0, sigma)
    else:
        noise = 0.0

    # Clip between 0 and 1.5 to simulate ADC limits with some headroom
    return max(0.0, min(1.5, signal + noise))


def run_realistic_simulation(real_peak_angle, movements, sampling_rate_hz=100, snr_db=40, noise_floor=0.1):
    # Initialize processor with a larger window for realistic sampling rates
    processor = CalibrationLogicProcessor(peak_threshold=0.6, history_size=11)
    
    print("=====================================================")
    print(" STARTING REALISTIC CONTINUOUS CALIBRATION SIMULATION")
    print("=====================================================")
    print(f"Target Peak Angle : {real_peak_angle}°")
    print(f"Sampling Rate     : {sampling_rate_hz} Hz")
    print(f"SNR               : {snr_db} dB")
    print(f"Noise Floor       : {noise_floor}")
    print("-" * 55)

    dt = 1.0 / sampling_rate_hz
    step_count = 0

    # Execute each movement in the array
    for move_idx, (start_angle, end_angle, rpm) in enumerate(movements):
        print(f"\n>>> MOVEMENT {move_idx + 1}: {start_angle}° to {end_angle}° at {rpm} RPM <<<")
        print(f"{'Step':<6} | {'Angle':<7} | {'Sensor':<7} | {'Direction':<10} | {'Result'}")
        
        if rpm == 0:
            continue

        # Per instructions: Positive RPM = CW (decreasing angle). Negative RPM = CCW (increasing angle)
        is_cw = rpm > 0
        deg_per_sec = abs(rpm) * 360.0 / 60.0
        angular_step = deg_per_sec * dt

        # Calculate total degrees to travel to know when to stop
        if is_cw:
            total_travel = (start_angle - end_angle) % 360
        else:
            total_travel = (end_angle - start_angle) % 360
            
        if total_travel == 0:
            total_travel = 360 # Full rotation if start == end

        current_travel = 0.0
        current_angle = start_angle

        # Run the time-step loop for this movement
        while current_travel < total_travel:
            # 1. Read Sensor
            sensor_val = calculate_sensor_value(current_angle, real_peak_angle, noise_floor, snr_db)

            # 2. Process
            result = processor.process_messages(sensor_val, current_angle)
            current_dir = processor.data_history[-1]["direction"] if processor.data_history else "None"

            # 3. Print Output (throttle terminal spam by printing every Nth step or if peak found)
            if step_count % max(1, int(sampling_rate_hz / 10)) == 0 or result["delta_angle"] is not None:
                print(f"{step_count:<6} | {current_angle:>6.1f}° | {sensor_val:.3f}   | {str(current_dir):<10} | {result}")

            if result["delta_angle"] is not None:
                print(f"\n✅ SUCCESS: Calibration triggered! True peak isolated at angle: {result['delta_angle']}°")
                # We don't break the loop here so you can see it continue and trigger again if it crosses the peak twice!

            # 4. Advance physics state
            if is_cw:
                current_angle = (current_angle - angular_step) % 360
            else:
                current_angle = (current_angle + angular_step) % 360

            current_travel += angular_step
            step_count += 1

if __name__ == "__main__":
    # Configuration
    REAL_PEAK = 180.0
    
    # Array of tuples: (start_angle, end_angle, rpm)
    # Movement 1: CW from 200 down past 180 to 90
    # Movement 2: CCW from 90 up past 180 to 200
    MOVEMENTS = [
        (200, 90, 30),   # +30 RPM = Clockwise
        (90, 200, -30)   # -30 RPM = Counter-Clockwise
    ]

    # Try tweaking the SNR down to 20dB to see how noise affects the logic!
    run_realistic_simulation(
        real_peak_angle=REAL_PEAK, 
        movements=MOVEMENTS, 
        sampling_rate_hz=1_000, 
        snr_db=30,          # High SNR for a clean signal
        noise_floor=0.1
    )