#!/usr/bin/python3
import subprocess
import os
import gzip
import shutil
import sys
import time
import numpy
import cv2
from PPMManipulator import PPMManipulator


#This will make a folder for the given PPM File to store all appropriate files
#The parameter is the location to create the new folder
def createFolder(folderPath):
    os.mkdir(folderPath)
    os.mknod(folderPath + "/BasePPM")
               
#This should be chnged:
GEFilePath = "../GE/"
GETestFilePath = "../GE_TEST_13/"




inFile = sys.argv[1]
folderPath = GEFilePath + inFile.rstrip(".PPM.gz")
createFolder(folderPath)




obj = PPMManipulator(inFile,GETestFilePath,folderPath)
obj.unzipGz()

readPPMcommand = []
readPPMcommand.append("./readPPM")
readPPMcommand.append(folderPath + "/BasePPM")
subprocess.call(readPPMcommand)

obj.run()

