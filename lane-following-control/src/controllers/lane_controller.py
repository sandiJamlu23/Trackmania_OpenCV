class LaneController:
    def __init__(self, pid_controller):
        self.pid_controller = pid_controller

    def follow_lane(self, lane_position, vehicle_position):
        """
        Controls the vehicle's steering based on the lane position.
        
        :param lane_position: The position of the detected lane.
        :param vehicle_position: The current position of the vehicle.
        :return: Steering angle for the vehicle.
        """
        error = lane_position - vehicle_position
        steering_angle = self.pid_controller.compute(error)
        return steering_angle