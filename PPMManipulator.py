#!/usr/bin/python3
import subprocess
import os
import gzip
import shutil
import sys
import time
import numpy
import cv2


class PPMManipulator:

   #Sets the initial values to null or 0 and sets constants and file paths
    def __init__(self, argument,rawFilePath,placementFolderPath):
        self.placementFolderPath = placementFolderPath
        self.rawFile = rawFilePath + argument
        self.rawPPM = placementFolderPath + "/BasePPM"
        self.dumpFilePath = placementFolderPath + "/HexDump"
        self.formattedDumpFile = placementFolderPath +"/FormattedDump"
        self.errorsFilePath = placementFolderPath + "/Errors"
        self.transitionFilePath = placementFolderPath + "/Transitions"
        self.cColorizedPath = placementFolderPath + "/BasePPMColorized.jpg"
        self.errors = []
        self.errorLoc = []
        self.errorLocx = []
        self.errorLocy = []
        self.errorNo = 0
        self.cirColor = (255,0,0)
        
    @property    
    def errorImg(self):
        return self.errorImg


    #This Extracts the PPM to the new folder
    #The first Parameter is the location of the compressed folder, the second is the location for the new folder
    def unzipGz(self):
        with gzip.open(self.rawFile, 'rb') as f:
            with open(self.rawPPM, 'wb') as f2:
                f2.write(f.read())

    #This function will call a shell command for hexdump and then copy the output to a new file
    #The first parameter is the path to the folder with the PPM and the PPMFile is the name of the PPMFile
    def dumpHex(self):
      #This creates the command to be sent
        cmd=[]
        cmd.append("hexdump")
        cmd.append(self.rawPPM)
      #This is creating a new file as a destination for the hexdump
        with open(self.dumpFilePath, 'wb') as f_out:
            f_out.write(subprocess.check_output(cmd))
        
  
    
    #This function intends to make the DumpFile easier to search through
    #dumpFilePath should be the path to the raw dump file and cleanFilePath is the destination for the partially formatted result
    def cleanDump(self):
        with open(self.dumpFilePath, 'r+') as f_in:
            line = f_in.readlines()
            lines = []
            for s in line:
                lines.append(s.replace(" ", "\n"))
        #Creating a temporary file to write then read from
            with open("1", 'w+') as f_out:
                f_out.writelines(lines)
            with open("1", 'r+') as f_out:
                shift = f_out.readlines()
        #Creates to file for the final result
                final = open(self.formattedDumpFile, 'w+')
        #Removes all the line labels and unnecessary info
                count = 0
                for z in shift:
                    count += 1
                    if (len(z) != 5) or (count < 27):
                         continue
                    else:
                         final.writelines(z)
                    
       #This will close the open files and delete temporary files
        final.close()
        os.remove("1")



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


    #Finds all the instances of the transition in question
    #cleanFilePath is the formatted dump file, transitionFilePath is a new file listing all transitions, errorCount is the #number of errors in file          
    def transitionFinder(self):
        with open(self.formattedDumpFile, 'r+') as data:
            line = data.readlines()
            flips = open(self.transitionFilePath, 'w+')
            count = 0
            errors = True
            temp = "00"
            errorCount = 0
         #Finding the transitions
            for x in line: 
                if x.startswith("00") and not(temp.startswith("00")):
                    flips.writelines(str(temp) + " -> " + str(x))
                    count += 1
                #finds if no error occured during the transition
                    if int(x,16) >= 0x00ae:
                        errors = False
                        errorCount += 1
            
                temp = x
      #appends info at bottom of file
        if errors == True:
            flips.writelines("All " + str(count) + " Transitions Produced An Error\n")
        else:
            flips.writelines("There were " + str(errorCount) + " Transitions that did not produce an error\n")
        if count == self.errorNo:
            flips.writelines("This Includes All Errors In File")
        else:
            flips.writelines("There are " + str((self.errorNo - count)) + " Additional Errors")
        flips.close

  

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
        image = cv2.imread(self.cColorizedPath,0)
        for x in range(len(self.errorLocx)):
            col = self.errorLocx[x]
            row = self.errorLocy[x]
            #print(str(row) + ", " + str(col))
            center = (row, col)
            image = cv2.circle(image, center, 2, self.cirColor,1)
        image = cv2.applyColorMap(image, cv2.COLORMAP_INFERNO)
        cv2.imshow('ErrorsShown',image)
        path = self.cColorizedPath.rstrip(".jpg") + "Circled.jpg"
        cv2.imwrite(path,image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

   #This reads a .txt version of the PPM that is given in decimal figures
    def readPPMtxt(self):
        path = self.rawPPM + ".txt"
        rowIndex = 0
        row = open(path, 'r+')
        xline = row.readline()
        while xline:
            rowIndex += 1
            with open("2", 'w+') as col:
                col.writelines(xline.replace(", ",'\n'))
            with open("2", 'r+') as col:
                yline = col.readline()
                colIndex = 0
                while yline:
                    if len(yline) == 6 or colIndex == 479:
                        yline = col.readline()
                        continue
                    colIndex += 1
                    #print(str(yline) + " " + str(colIndex))
                    if int(yline.rstrip('\n')) < 174:
                        self.errorLocx.append(colIndex)
                        self.errorLocy.append(rowIndex)
                    yline = col.readline()
            os.remove("2")
            xline = row.readline()
        row.close()
        print(len(self.errorLocx))
    
  # This would be called in main script to eliminate extra typing
    def run(self):
        #self.unzipGz()
        self.dumpHex()
        self.cleanDump()
        self.findErrors()
        self.transitionFinder()
        self.colorization()
        self.readPPMtxt()
        self.drawErrors()
       

