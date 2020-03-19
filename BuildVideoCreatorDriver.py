import argparse
import cv2
import numpy as np
import datetime
import os
from BuildVideoCreator import NpVidViewer

PARSER = argparse.ArgumentParser()
PARSER.add_argument("directory", type=str, help="Directory containing files.")
PARSER.add_argument("--ROI", "-o", help="Are their ROIs to be stitched?")
PARSER.add_argument("--Col","-col","-C","-c", help="How many columns?")
PARSER.add_argument("--Row","-row","-R","-r", help="How many rows?")
PARSER.add_argument("--MeltPool","-meltpool","-M","-m", help="MeltPool data available?")


ARGS = PARSER.parse_args()

DIR = ARGS.directory

os.chdir(DIR)

meltpool = True

if ARGS.MeltPool:
    meltpool = ARGS.MeltPool

if ARGS.ROI:
    ROI = ARGS.ROI
    tc_times=DIR+"/thermal_cam_times.npy"
    if meltpool is not False:
        melt_pool_data="/Thermal_Camera/melt_pool_data.npy"
    else:
        melt_pool_data = False
else:
    ROI = False
    tc_times = DIR+"/Thermal_Camera/thermal_cam_times.npy"
    if meltpool is not False:
        melt_pool_data=DIR+"/Thermal_Camera/melt_pool_data.npy"
    else:
        melt_pool_data = False
    
if ARGS.Col:
    Col = ARGS.Col
else:
    Col = 1

if ARGS.Row:
    Row = ARGS.Row
else:
    Row = 1

print(melt_pool_data)
VIEWER = NpVidViewer(
    DIR,
    melt_pool_data=melt_pool_data,
    tc_times=tc_times,
    window_name = "Video",
    remove_reflection=True,
    remove_lower=True, 
    ROI = ROI,
    col = Col,
    row = Row
)

VIEWER.play_video(1)
