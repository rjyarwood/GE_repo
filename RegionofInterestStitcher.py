import cv2
import numpy as np
import time


class ROIStitcher:
    def __init__(self, path):
        self._path = path
        
        self._ROI0 = np.load(path + "/ROI_0/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
        self._ROI1 = np.load(path + "/ROI_1/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
        self._ROI2 = np.load(path + "/ROI_2/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
        self._ROI3 = np.load(path + "/ROI_3/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
        self._ROI4 = np.load(path + "/ROI_4/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
        self._ROI5 = np.load(path + "/ROI_5/Thermal_Camera/thermal_cam_temps.npy", mmap_mode='r', allow_pickle=True)
        
        self._xdim = 3 * np.size(self._ROI0,1)
        self._ydim = 2 * np.size(self._ROI0,0)
        self._totalROI = self._xdim * self._ydim
        self._stitched = [[0 for i in range(self._xdim)] for j in range(self._ydim)]
        for x in range(np.size(self._ROI0,0)):
            tmp = self._ROI0[x]
            tmp = np.append(tmp, self._ROI1[x])
            tmp = np.append(tmp, self._ROI2[x])
            
            self._stitched[x] = tmp
            
        for x in range(np.size(self._ROI0,0)):
           tmp = self._ROI3[x]
           tmp = np.append(tmp, self._ROI4[x])
           tmp = np.append(tmp, self._ROI5[x])
            
           self._stitched[x+np.size(self._ROI0,0)] = tmp
            
            
            
            
            
            
    @property         
    def stitched(self):
        return self._stitched
