import cv2
import numpy as np

def warp_image(image, src_points, dst_points):
    """
    Applies a perspective warp to the input image.

    :param image: The input image to be warped.
    :param src_points: The source points for the warp.
    :param dst_points: The destination points for the warp.
    :return: The warped image.
    """
    # Get the transformation matrix
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    # Apply the warp
    warped_image = cv2.warpPerspective(image, matrix, (image.shape[1], image.shape[0]))
    return warped_image