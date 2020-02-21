#!/usr/local/bin/python3
import pandas as pd
from numpy import genfromtxt
import matplotlib.pyplot as plt
import seaborn as sns
import sys 
import cv2
import numpy as np

file = open(sys.argv[1], 'r')
for line in file:
    line = line.rstrip()
    print(line)
    image = genfromtxt(line, delimiter=',')
    cv2.imshow('image', image)
    if cv2.waitKey(1) == 27:
        break
