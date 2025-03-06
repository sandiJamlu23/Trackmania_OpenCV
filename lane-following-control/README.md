# README.md

# Lane Following Control

This project implements a lane following control system for autonomous vehicles. It utilizes computer vision techniques to detect lane lines and applies a PID control algorithm to steer the vehicle accordingly.

## Project Structure

```
lane-following-control
├── src
│   ├── controllers
│   │   ├── lane_controller.py
│   │   └── pid_controller.py
│   ├── detection
│   │   ├── edge_detection.py
│   │   └── lane_detection.py 
│   ├── processing
│   │   ├── image_processor.py
│   │   └── warping.py
│   ├── utils
│   │   ├── config.py
│   │   └── helpers.py
│   └── main.py
├── tests
│   ├── test_lane_detection.py
│   └── test_pid_controller.py
├── config
│   └── settings.yaml
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd lane-following-control
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the lane following control system, execute the following command:
```
python src/main.py
```

## Configuration

Configuration settings can be modified in the `config/settings.yaml` file. This includes parameters for lane detection and PID control.

## Testing

Unit tests are provided to ensure the functionality of the lane detection and PID controller. To run the tests, use:
```
pytest tests/
```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.