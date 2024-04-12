import math
import re
import shutil
import subprocess
import time
import threading
import cv2
import prior
import ai2thor
import random
import os
import pickle
import copy
import numpy as np
from ai2thor.controller import Controller
from scipy.spatial import distance
from typing import Tuple
from collections import deque
from glob import glob
from PIL import Image
import matplotlib.pyplot as plt

# Download procthor dataset
dataset = prior.load_dataset("procthor-10k")

house = dataset["train"][3]
type(house), house.keys(), house

# Set ai2thor controller
c = Controller(width=1600, height=900, makeAgentsVisible=False, renderInstanceSegmentation=True)
c.reset(house) 



# Add a top view camera
event = c.step(action="GetMapViewCameraProperties")
event = c.step(action="AddThirdPartyCamera", **event.metadata["actionReturn"])
top_view_rgb = cv2.cvtColor(c.last_event.events[0].third_party_camera_frames[-1], cv2.COLOR_BGR2RGB)



# get reachable positions
reachable_positions_ = c.step(action="GetReachablePositions").metadata["actionReturn"]
reachable_positions = positions_tuple = [(p["x"], p["y"], p["z"]) for p in reachable_positions_]

xs = [rp[0] for rp in reachable_positions]
zs = [rp[2] for rp in reachable_positions]

fig, ax = plt.subplots(1, 1)
ax.scatter(xs, zs)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_title("Reachable Positions in the Scene")
ax.set_aspect("equal")
#plt.show()


# Get 2d_map png image based on Reachable Positions
scaling_factor = 10  # Adjust this value as needed
scaled_xs = [int(x * scaling_factor) for x in xs]
scaled_zs = [int(z * scaling_factor) for z in zs]

width = max(scaled_xs) - min(scaled_xs) + 1
height = max(scaled_zs) - min(scaled_zs) + 1

image = np.zeros((height, width), dtype=np.uint8)

for x, z in zip(scaled_xs, scaled_zs):
    x_index = x - min(scaled_xs)
    z_index = z - min(scaled_zs)
    image[z_index, x_index] = 255  # Mark as free space (255)

# Use dilation to connect nearby points
kernel = np.ones((3,3), np.uint8)  # Adjust the kernel size as needed
image = cv2.dilate(image, kernel, iterations=1)

# Flip the image vertically
image = cv2.flip(image, 0)

# Magnify the image by 100x (scaling factor * magnification = 50)
magnification = 5
magnified_image = cv2.resize(image, (width * magnification, height * magnification), interpolation=cv2.INTER_NEAREST)



cv2.imshow('Reachable Positions (Magnified)', magnified_image)
cv2.imwrite('_2d_map.png', magnified_image)
cv2.imwrite('_top_view.png', top_view_rgb)
cv2.waitKey(0)


