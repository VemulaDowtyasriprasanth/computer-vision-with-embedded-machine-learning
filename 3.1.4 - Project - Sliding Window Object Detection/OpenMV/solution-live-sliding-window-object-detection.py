"""
Solution: OpenMV Sliding Window Object Detection

Continuously captures images and performs inference on a sliding window to detect objects.

Author: EdgeImpulse, Inc.
Date: August 4, 2021
License: Apache-2.0 (apache.org/licenses/LICENSE-2.0)
"""

import sensor, image, time, tf, math

# Settings
model_file = "trained.tflite"           # Location of TFLite model file
labels_file = "labels.txt"              # Location of labels file
target_label = "dog"                    # Which label we're looking for
target_threshold = 0.6                  # Draw box if output probability is equal to or over this
width = 160                             # Width of frame (pixels)
height = 120                            # Height of frame (pixels)
window_width = 48                       # Window width (input to CNN)
window_height = 48                      # Window height (input to CNN)
stride = 24                             # How many pixels to move window each step
pixel_format = sensor.GRAYSCALE         # This model only supports grayscale

# Configure camera
sensor.reset()
sensor.set_pixformat(pixel_format)      # Set pixel format to RGB565 or GRAYSCALE
sensor.set_framesize(sensor.QQVGA)       # Set frame size to QQVGA (160x120)
sensor.set_windowing((width, height))   # Crop sensor frame to this resolution
sensor.skip_frames(time = 2000)         # Let the camera adjust

# Extract labels from labels file
labels = [line.rstrip('\n').rstrip('\r') for line in open(labels_file)]

# Compute number of window steps
num_horizontal_windows = math.floor((width - window_width) / stride) + 1
num_vertical_windows = math.floor((height - window_height) / stride) + 1

# Find the index of the target label
target_idx = labels.index(target_label)

# Start clock (for measureing FPS)
clock = time.clock()

# Main while loop
inference_count = 0
while(True):

    # Update timer
    clock.tick()

    # Get image from camera
    img = sensor.snapshot()

    # >>> ENTER YOUR CODE HERE <<<
    # Loop over all possible windows, crop/copy image under window, perform inference on windowed
    # image, compare output to threshould, print out info (x, y, w, h) of all bounding boxes
    # that meet or exceed that threshold

    # Slide window across image and perform inference on each sub-image
    bboxes = []
    for vertical_window in range(num_vertical_windows):
        for horizontal_window in range(num_horizontal_windows):

            # Crop out image under window
            x = horizontal_window * stride
            y = vertical_window * stride
            window_img = img.copy(roi=(x, y, window_width, window_height))

            # Do inference. OpenMV tf classify returns a list of prediction objects.
            objs = tf.classify(model_file, window_img)

            # We should only get one item in the predictions list, so we extract the
            # output probabilities from that.
            predictions = objs[0].output()

            # Remember bounding box location if target inference probability is over threshold
            if predictions[target_idx] >= target_threshold:
                bboxes.append((x, y, window_width, window_height, predictions[target_idx]))

    # Draw bounding boxes on preview image
    for bb in bboxes:
        img.draw_rectangle((bb[0], bb[1], bb[2], bb[3]))

    # Print bounding box locations
    print("---")
    print("Boxes:")
    for bb in bboxes:
        print(" " + "x:" + str(bb[0]) + " y:" + str(bb[1]) + " w:" + str(bb[2]) +
                " h:" + str(bb[3]) + " prob:" + str(bb[4]))
    print("FPS:", clock.fps())
