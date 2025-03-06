import unittest
from src.controllers.pid_controller import PIDController

class TestPIDController(unittest.TestCase):
    def setUp(self):
        self.pid = PIDController(kp=1.0, ki=0.1, kd=0.05)
        self.pid.setpoint = 0.0  # Desired value

    def test_compute(self):
        # Test with a positive error
        error = 10.0
        output = self.pid.compute(error)
        self.assertGreater(output, 0)

        # Test with a negative error
        error = -10.0
        output = self.pid.compute(error)
        self.assertLess(output, 0)

        # Test with zero error
        error = 0.0
        output = self.pid.compute(error)
        self.assertEqual(output, 0)

    def test_integral_windup(self):
        # Simulate a large error over time
        for _ in range(100):
            self.pid.compute(10.0)
        self.assertGreater(self.pid.integral, 0)

    def test_derivative(self):
        # Test the derivative calculation
        self.pid.compute(10.0)
        self.pid.compute(5.0)
        self.assertNotEqual(self.pid.previous_error, 0)

if __name__ == '__main__':
    unittest.main()