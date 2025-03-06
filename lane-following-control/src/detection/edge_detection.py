import cv2
import numpy as np

def detect_edges(image, low_threshold=50, high_threshold=150):
    """
    Applies Canny edge detection to the input image.

    :param image: Input image in which edges are to be detected.
    :param low_threshold: Lower threshold for the Canny edge detector.
    :param high_threshold: Upper threshold for the Canny edge detector.
    :return: Image with detected edges.
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_image, low_threshold, high_threshold)
    return edges