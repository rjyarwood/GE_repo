#!/usr/bin/python3
import subprocess
import os
import gzip
import shutil
import sys
import time
import numpy as np
import cv2



class PPMManipulatorForVid:

   #Sets the initial values to null or 0 and sets constants and file paths
    def __init__(self,rawPPM):
        self.rawPPM = rawPPM
        self.colorizedPPM = 0
        self.errors = []
        self.errorLoc = []
        self.errorLocx = []
        self.errorLocy = []
        self.errorNo = 0
        self.cirColor = (255,255,255)
        

    @property    
    def errorImg(self):
        return self.errorImg

    #This will find all the numbers that are out of bounds
    #cleanFilePath is the location of the formatted dump errorsFilePath is where the error numbers should be written
    def findErrors(self):
        with open(self.formattedDumpFile, 'r') as data:
            line = data.readlines()
        count = 0
        self.errorNo
       #checking for out of bounds numbers
        for x in line:
            if int(x,16) < 0x00ae:
                self.errorNo += 1
                self.errors.append(x)
                self.errorLoc.append(count)
            count += 1

        with open(self.errorsFilePath, 'w+') as newFile:
            for z in self.errors:
                newFile.writelines(z)


   #This will make the PPM colorized
    def colorization(self):
        img = cv2.imread(self.rawPPM, 0)
        normalized_img = img.copy()
        normalized_img = cv2.normalize(img, normalized_img, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        normalized_img = cv2.applyColorMap(normalized_img, cv2.COLORMAP_INFERNO)
        cv2.imshow('colorized',normalized_img)
        cv2.imwrite(self.rawPPM + "PythonColorized.jpg",normalized_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    #draws circles of the color that is given in the constructor
    def drawErrors(self):
        #image = cv2.imread("1")
        image = cv2.imread("1")
        for x in range(len(self.errorLocx)):
            col = self.errorLocx[x]
            row = self.errorLocy[x]
            #print("\n"+ str(row) + "," + str(col)+"\n")
            center = (row, col)
            #print("got loc")
            #cv2.imshow("test?",image)
            #print("shown")
            image = cv2.circle(image, center, 2, self.cirColor,1)
            #print("circlied")
        return image
        #image = cv2.applyColorMap(image, cv2.COLORMAP_INFERNO)
        #cv2.imshow('ErrorsShown',image)
        #path = self.cColorizedPath.rstrip(".jpg") + "Circled.jpg"
        #cv2.imwrite(path,image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

  
    def findErrorsArray(self):
        x = 0
        for row in self.rawPPM:
            x += 1
            y = 0
            for cell in row:
                y += 1
                #print(cell)
                if(int(cell) < 174):
                    #print("adding to error")
                    self.errorLocx.append(x)
                    self.errorLocy.append(y)
                    print("ERROR FOUND: " + str(cell) + "(" + str(x) + "," + str(y) + ")")


        
       

