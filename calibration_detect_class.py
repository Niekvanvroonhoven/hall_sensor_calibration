import math

class CalibrationLogicProcessor:
    def __init__(self, calibration_angle=0.0, max_history_length=100, peak_threshold=0.5, noise_window=5):
        # 1. Memory for data and settings
        self.data_history = []
        self.max_history_length = max_history_length
        self.peak_threshold = peak_threshold
        self.noise_window = noise_window

        # 2. Tracking angles
        self.calibration_angle = calibration_angle

    def clear_history(self):
        self.data_history.clear()

    def check_history_buffer(self):
        #this is an internal function just to remove samples that are not needed
        while self.data_history and self.data_history[0] < self.peak_threshold / 2:
            self.data_history.pop(0)

    def find_delta_angle(self):     #TODO rewrite this entire function  
        total_required = self.noise_window + self.measurement_window - 1
        if len(self.data_history) < total_required:
            return None

        # 1. Extract and smooth the recent data
        smoothed_readings = []
        corresponding_angles = []
        
        for i in range(self.measurement_window):
            end_idx = len(self.data_history) - i
            start_idx = end_idx - self.noise_window
            
            slice_to_average = self.data_history[start_idx:end_idx]
            avg_sensor = sum(item['sensor'] for item in slice_to_average) / self.noise_window
            angle = slice_to_average[-((self.noise_window)//2+1)]['angle'] # angle halfway the noise window
            
            smoothed_readings.insert(0, avg_sensor)
            corresponding_angles.insert(0, angle)

        # 2. Prevent False Positives: Did the motor change direction?
        # We ensure the angles are moving continuously in one direction
        is_increasing = corresponding_angles[0] < corresponding_angles[1]
        for i in range(1, len(corresponding_angles) - 1):
            current_increases = corresponding_angles[i] < corresponding_angles[i+1]
            if current_increases != is_increasing:
                # The motor reversed direction inside this window. Abort.
                return None

        # 3. Find the middle point of our evaluation window
        mid_index = self.measurement_window // 2
        mid_sensor_val = smoothed_readings[mid_index]
        mid_angle_val = corresponding_angles[mid_index]

        # 4. Check if it meets the criteria for a peak, so more then threshold
        if (mid_sensor_val < self.peak_threshold):
            return None
            
        is_peak = True
        for i, val in enumerate(smoothed_readings):
            if i == mid_index:
                continue
            # The middle point must be strictly greater than surrounding points
            if val >= mid_sensor_val:
                is_peak = False
                break
                
        # 5. Calculate delta if a peak was verified
        if is_peak:
            raw_delta = self.calibration_angle - mid_angle_val
            
            # Shortest path calculation to handle 2 pi wrap around
            delta_angle = (raw_delta + math.pi) % (2*math.pi) - math.pi
            return delta_angle
            
        return None

    def process_messages(self, sensor_readout, predicted_angle):
        #cleanup buffer if needed
        self.check_history_buffer()

        # Do not add the data when the array is already empty and the value is way less than the threshold
        if (not self.data_history) and (sensor_readout < self.peak_threshold/2):
            return {
                "delta_angle": None
            }

        # 1. Add new entry
        new_entry = {
            'sensor': sensor_readout,
            'angle': predicted_angle
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