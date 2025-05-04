# Comprehensive Lane Following Control

This project implements a real-time lane detection and autonomous driving system using computer vision and threading for improved performance. It is designed for use with screen-captured driving games or simulations, leveraging OpenCV for image processing and pydirectinput for automated keyboard control.

## Features

- **Real-time lane detection** using color masking and perspective transforms
- **Sliding window algorithm** for robust lane line fitting
- **Curvature and offset calculation** for steering decisions
- **Threaded architecture** for parallel screen capture, processing, and control
- **Performance monitoring** (CPU, memory, FPS)
- **Visualization** of lane detection and driving statistics
- **Crash and performance analytics** with plotting tools

## Requirements

- Python 3.7+
- OpenCV (`opencv-python`)
- NumPy
- Matplotlib
- mss
- pydirectinput
- pyautogui
- pygetwindow
- keyboard
- line_profiler (optional, for profiling)
- seaborn, pandas (for analytics/plots)

Install dependencies with:

```sh
pip install opencv-python numpy matplotlib mss pydirectinput pyautogui pygetwindow keyboard line_profiler seaborn pandas
```

## Usage

1. **Configure your screen region** in the code (default: `{"top": 300, "left": 50, "width": 400, "height": 300}`).
2. **Run the notebook** or convert it to a Python script.
3. The system will:
    - Capture the game window
    - Detect lane lines in real time
    - Calculate steering and speed
    - Send keyboard commands to control the vehicle
    - Display real-time visualization and statistics

**Note:** Make sure your game window matches the expected region and resolution for best results.

## Project Structure

- `comprehensive_lane.ipynb` — Main notebook with all code (lane detection, threading, driving logic, analytics)
- `/my_game_screenshots/` — Example images for testing (update path as needed)
- Other folders (e.g., `opencv/`, `lane-following-control/`) — Not directly used by this notebook

## How it Works

1. **Image Capture:** Uses `mss` to grab a region of the screen.
2. **Lane Detection:** Applies HSV masking for green lanes, perspective transform, and sliding window search.
3. **Control Logic:** Calculates steering and speed based on lane position and curvature.
4. **Threading:** Separate threads for capture, processing, control, and visualization for maximum performance.
5. **Driving:** Uses `pydirectinput` to send keyboard commands (`W`, `A`, `D`, `Space`) to the game.
6. **Performance Analytics:** Includes tools for crash analysis and CPU/memory usage plotting.

## Example

![Lane Detection Example](example_lane_detection.png)

## Performance

- Typical CPU usage: ~30-60%
- Memory usage: ~84%
- Real-time FPS: 10-30 (depending on hardware and settings)

## Notes

- You may need to adjust ROI and color thresholds for your specific game/environment.
- For best results, run the script as administrator and ensure the game window is not minimized.
- The code is modular and can be extended for other lane colors or more advanced control logic.

## License

MIT License

---

*This project is for educational and research purposes. Use responsibly!*
