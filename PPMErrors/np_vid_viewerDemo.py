import cv2
import numpy as np
import datetime
from PPMManipulatorForVid import PPMManipulatorForVid


class NpVidViewer:
    def __init__(self, filename: str, window_name="Video"):
        self._array = np.load(filename, mmap_mode='r', allow_pickle=True)
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
        self._timestamp = None
        self._speed = 1
        self._window_name = window_name
        self._num_frames = self.array.shape[0]

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

    def play_video(self):
        pause = False
        self._timestamp = 1
        while True:
            key = cv2.waitKey(self.speed)
            if not pause:
                img = self.array[self.timestamp - 1]
                obj = PPMManipulatorForVid(img)
                obj.findErrorsArray()
                
                normalized_img = obj.drawErrors()
                normalized_img = cv2.normalize(normalized_img, normalized_img, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
                normalized_img = cv2.applyColorMap(normalized_img, cv2.COLORMAP_INFERNO)
                cv2.imshow(self.window_name, normalized_img)
                self._timestamp = self._timestamp + 1
                print(self.timestamp)
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
