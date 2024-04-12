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
import copy
import pickle
import numpy as np
from ai2thor.controller import Controller
from scipy.spatial import distance
from typing import Tuple
from collections import deque
from glob import glob
from PIL import Image
import matplotlib.pyplot as plt

# Using procthor dataset
dataset = prior.load_dataset("procthor-10k")

#################################### Using procthor-10k #################################################
room_type = "train"
room_counter = 3
house = dataset[room_type][room_counter]
type(house), house.keys(), house

#################################### Using ArchitecTHOR ##################################################
#house_type = 'Archi'
#room_counter = 00
#room_type = "ArchitecTHOR-Test-"
# room_type = "ArchitecTHOR-Val-"
#house = room_type + (str(room_counter).zfill(2))



# Set ai2thor controller
c = Controller(width=800, height=600, makeAgentsVisible=True, renderInstanceSegmentation=True)
c.reset(house)

robots = [{'name': 'robot1', 'skills': ['Turn']}]
no_robot = len(robots)
print(robots)

agent_event = c.step(dict(action='Initialize', agentMode="default", snapGrid=False, gridSize=0.25, rotateStepDegrees=20, visibilityDistance=1000, fieldOfView=90, agentCount=no_robot))

# Set Robot's position
agent_event = c.step(dict(action='Teleport', position=dict(x=10.04, y=0.7, z=0.68), agentId=0), forceAction=True)

# Capture First Scene
cv2.imshow('Side1', agent_event.events[0].cv2img)
#cv2.imwrite('Scene_side1.png', agent_event.events[0].cv2img)
cv2.waitKey(0)

# Capture Second Scene
agent_event = c.step(action="RotateRight", degrees=90, agentId=0, speed=1, fixedDeltaTime=0.02)
cv2.imshow('Side2', agent_event.events[0].cv2img)
#cv2.imwrite('Scene_side2.png', agent_event.events[0].cv2img)
cv2.waitKey(0)

# Capture Third Scene
agent_event = c.step(action="RotateRight", degrees=90, agentId=0)
cv2.imshow('Side3', agent_event.events[0].cv2img)
#cv2.imwrite('Scene_side3.png', agent_event.events[0].cv2img)
cv2.waitKey(0)

# Capture Fourth Scene
agent_event = c.step(action="RotateRight", degrees=90, agentId=0)
cv2.imshow('Side4', agent_event.events[0].cv2img)
#cv2.imwrite('Scene_side4.png', agent_event.events[0].cv2img)
cv2.waitKey(0)
