def log(message):
    """Logs a message to the console."""
    print(f"[LOG] {message}")

def clamp(value, min_value, max_value):
    """Clamps a value between a minimum and maximum range."""
    return max(min(value, max_value), min_value)

def calculate_distance(point1, point2):
    """Calculates the Euclidean distance between two points."""
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5