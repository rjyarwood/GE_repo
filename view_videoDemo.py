import argparse
import cv2
import numpy as np
import datetime
import os
from np_vid_viewerDemo import NpVidViewer

PARSER = argparse.ArgumentParser()
PARSER.add_argument("file", type=str, help="The name of the file to load.")

ARGS = PARSER.parse_args()

FILE_NAME = ARGS.file

VIEWER = NpVidViewer(FILE_NAME)

VIEWER.play_video()
