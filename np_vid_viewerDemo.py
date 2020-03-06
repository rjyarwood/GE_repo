import cv2
import numpy as np
import datetime
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
from PPMManipulatorForVid import PPMManipulatorForVid

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()



class NpVidViewer:
    def __init__(self, filename: str, window_name="Video"):
        """
                self._ROI0 = np.load(filename + "/ROI_0/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
                self._ROI1 = np.load(filename + "/ROI_1/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
                self._ROI2 = np.load(filename + "/ROI_2/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
                self._ROI3 = np.load(filename + "/ROI_3/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
                self._ROI4 = np.load(filename + "/ROI_4/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
                self._ROI5 = np.load(filename + "/ROI_5/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
        """
        self._File = np.load(filename + "/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)       
        self._fileName =  filename + "/Thermal_Camera/thermal_cam_temps.npy"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
        self._timestamp = None
        self._speed = 1
        self._window_name = window_name
        self._num_frames = self._File.shape[0]
        self._xdim = 3 * np.size(self._File,2)
        self._ydim = 2 * np.size(self._File,1)
        #self._num_frames = self._ROI0.shape[0]
        #self._xdim = 3 * np.size(self._ROI0,2)
        #self._ydim = 2 * np.size(self._ROI0,1)
        #self._stitched = [[0 for i in range(self._xdim)] for j in range(self._ydim)]
        size = (self._xdim+2,self._ydim)
        self._img_array = []
        self._vid = cv2.VideoWriter('test.avi',cv2.VideoWriter_fourcc(*'FFV1'), 15, size)


    @property
    def num_frames(self):
        return self._num_frames

    @property
    def window_name(self):
        return self._window_name

    @property
    def array(self):
        return self._array

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        if new_speed < 1:
            self._speed = 1
        elif new_speed > 1000:
            self._speed = 1000
        else:
            self._speed = new_speed

    @property
    def timestamp(self):
        return self._timestamp

    def stitchFrames(self):
        for x in range(np.size(self._ROI0,1)):
           tmp = self._ROI0[self.timestamp,x,:]
           tmp = np.append(tmp, self._ROI1[self.timestamp,x,:])
           tmp = np.append(tmp, self._ROI2[self.timestamp,x,:])
            
           self._stitched[x] = tmp
            
        for x in range(np.size(self._ROI0,1)):
           tmp = self._ROI3[self.timestamp,x,:]
           tmp = np.append(tmp, self._ROI4[self.timestamp,x,:])
           tmp = np.append(tmp, self._ROI5[self.timestamp,x,:])
            
           self._stitched[x+np.size(self._ROI0,1)] = tmp

    def play_video(self):
        pause = False
        self._timestamp = 0
        #fig = plt.figure()
        #viewer = fig.add_subplot(111)
        #fig.show()
        while True:
            key = cv2.waitKey(self.speed)
            if not pause:
                #self.stitchFrames()
                #print(self._File)
                plt.imsave("1",self._File[self._timestamp],format='png')
                #plt.imsave("1",self._stitched,format='png')
                #maxim = max(max(x) for x in img)
                #if maxim != 174:
                    #print(maxim)
                obj = PPMManipulatorForVid(self._File[self._timestamp])
                #obj = PPMManipulatorForVid(self._stitched)
                obj.findErrorsArray()
                #print("back")
                printProgressBar(self.timestamp, np.size(self._File,0), prefix = 'Progress:', suffix = 'Complete', length = 50)
                
                #normalized_img = cv2.imread("1")
                normalized_img = obj.drawErrors()
                height, width, layers = normalized_img.shape
                self._size = (width,height)
                #print("normalized")
                #viewer.clear()
                #viewer.imshow(normalized_img)
                #fig.canvas.draw()
                #print(normalized_img)
                #print("drawn errors")

                print(self._size)
                



                normalized_img = cv2.normalize(normalized_img, normalized_img, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)



                #normalized_img = cv2.normalize(normalized_img, normalized_img, 0, 65535, cv2.NORM_MINMAX, cv2.CV_16U)
                #print(normalized_img.shape)
                normalized_img = cv2.applyColorMap(normalized_img, cv2.COLORMAP_INFERNO)

                #self._vid.write(frame);
                #16_bit_vid.release();                

                cv2.imwrite("2.png", normalized_img)
                self._vid.write(normalized_img)
                cv2.imshow(self.window_name, normalized_img)
                self._timestamp = self._timestamp + 1
                #print("incremented timestamp")
                #print(self.timestamp)
                
            elif pause:
                if key == ord('s'):
                    np.savetxt('tc_temps-' + str(i + 1) + ".csv", img, fmt='%d', delimiter=",")

            if key == ord('q'):
                break
            elif key == ord('p'):
                pause = not pause
            elif  self.timestamp >= self.num_frames:
                break
        cv2.destroyAllWindows
        
