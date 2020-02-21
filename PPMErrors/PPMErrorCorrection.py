#RJ Yarwood
#rjyarwood@student.ysu.edu

import cv2
import sys
from PIL import Image
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

#Place Goal PPM in a folder named GE or edit this line
path = "../GE/" + sys.argv[1]

#this will open the PPM and place it in a numpy array
im = np.array(Image.open(path))

#this will get the size of the image/array so that it can be iterated through later
rows = im.shape[0]
cols = im.shape[1]

#iterating through the array and will fix any error pixels found
for x in range(0,rows):
    for y in range(0,cols):
        if int(im[x,y]) < 174:
            im[x,y] += 256

#this will create a new image that is labeled as a 16 bit version
newFile = sys.argv[1] + "16bit"
#this will save the new image, the extension can be changed but png was used as a placeholder as it has full
#support for 16 bit color
plt.imsave(newFile,im,format='png')

#this reads the png into OpenCV so it can be manipulated through that
image = cv2.imread(newFile)
image = cv2.applyColorMap(image,cv2.COLORMAP_INFERNO)
cv2.imshow('colorized',image)
cv2.imwrite(sys.argv[1].rstrip('.PPM') + "_OpenCV.png",image)
cv2.waitKey(0)
cv2.destroyAllWindows()

