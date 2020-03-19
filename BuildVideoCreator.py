import cv2
import numpy as np
import datetime
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
from PPMManipulatorForVid import PPMManipulatorForVid
from reflection_remover import ReflectionRemover
from Stitcher import stitcher 

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

    """NpVidViewer
    Stores information relating to a video to be able to easily display a video from a numpy array

    Attributes
    ----------
    _remove_reflection : bool
        Whether or not to remove the reflection from each frame while playing the video.
    _array
        Numpy array of thermal cam temps loaded from the file.
    _speed : int
        Delay between each frame in ms.
    _window_name : str
        Name of the window for the video to be displayed in.
    _timestamps
        Numpy array of the thermal camera timestamps.
    _melt_pool_data
        Numpy array of the melt pool data.
    _mp_data_index : int
        Current index of `_melt_pool_data` numpy array.
    _lower_bounds
        List of lower bounds of part. Used to remove the bottom reflection.
    _ROIs[] : npy
        Array/List of Numpy arrays for ROIs
    _dims : (size)
        Dimensions of ROIs to be stitched
    """

    def __init__(self,
                 filename: str,
                 melt_pool_data,
                 tc_times,
                 window_name="Video",
                 remove_reflection=False,
                 remove_lower=False,
                 ROI = False,
                 col = 1,
                 row = 1):

        """Create an NpVidViewer Object.
        @Params:
            file_name (str)         - Required  : Name of the numpy file that contains the thermal cam temps.
            melt_pool_data (str)    - Required  : Name of the numpy file that contains the melt pool data.
            tc_times (str)          - Required  : Name of the numpy file that contains the thermal camera timestamps.
            window_name (str)       - Optional  : Name of the window that the video will be displayed in.
            remove_reflection (bool)- Optional  : Run the remove reflection function if true.
            remove_lower (bool)     - Optional  : Run the remove_lower reflection function if true.
            ROI (bool)              - Optional  : Open multiple ROIs if True
            col (int)               - Optional  : Number of ROI horizontally in stitched img (if desired)
            row (int)               - Optional  : Number of ROI vertically in stitched img (if desired)      
        """

        self._remove_reflection = remove_reflection
        self._remove_lower = remove_lower
        self._dims = (row, col)
        self.ROI = ROI
        self._ROIs = []
        

        if(self.ROI):
            for x in range(int(row) * int(col)):
                self._ROIs.append(np.load(filename +"/ROI_" + str(x) + "/Thermal_Camera/thermal_cam_temps.npy" , mmap_mode="r", allow_pickle=True))
        else:
            self._array = np.load(filename + "/Thermal_Camera/thermal_cam_temps.npy", mmap_mode="r", allow_pickle=True)

        self._speed = 1
        self._window_name = window_name
        if ROI:
            self._num_frames = self._ROIs[1].shape[0]
        else:
            self._num_frames = self._array.shape[0]

        self._timestamps = np.load(tc_times, allow_pickle=True)

        if melt_pool_data is not False and ROI:
            for x in range(len(self._ROIs)):
                self._melt_pool_data = np.load(filename +"/ROI_" + str(x) + melt_pool_data, allow_pickle=True)
        elif melt_pool_data is not False:
            self._melt_pool_data = np.load(melt_pool_data, allow_pickle=True)

        self._mp_data_index = 0
        self.match_vid_to_meltpool()
        self._lower_bounds = self.find_lower_bounds()

    def find_lower_bounds(self):
        """Find the lower bounds of the piece.

        Returns
        -------
        max_locations
            List of the first points at the zero level below the each max temp.
        """
        img_array = self.array
        i = 0
        # Find the x and y value of the max temp
        max_x = np.where(img_array[0] == np.amax(img_array[0]))[1][0]
        max_y = np.where(img_array[0] == np.amax(img_array[0]))[0][0]

        # Find the x value of the max temp of the next frame
        next_max_x = np.where(img_array[1] == np.amax(img_array[1]))[1][0]

        # Create lists of the x and y values of the max temperatures
        max_x_locations = []
        max_y_locations = []

        # While the laser is moving to the right. (i.e. the next location > current location)
        while max_x < next_max_x:
            max_x_locations.append(max_x)
            max_y_locations.append(max_y)
            i = i + 1
            max_x = np.where(img_array[i] == np.amax(img_array[i]))[1][0]
            next_max_x = np.where(
                img_array[i + 1] == np.amax(img_array[i + 1]))[1][0]
            max_y = np.where(img_array[i] == np.amax(img_array[i]))[0][0]

        max_locations = []
        j = 0
        for i in range(max_x_locations[0], max_x_locations[-1]):
            if i > max_x_locations[j]:
                j = j + 1
            max_locations.append((i, max_y_locations[j]))
        return max_locations

    @property
    def lower_bounds(self):
        """Return the lower bounds"""
        return self._lower_bounds

    def match_vid_to_meltpool(self):
        """Shuffle the meltpool data and thermal camera data together based on timestamp"""
        self._matched_array = []
        for i in range(0, self.array.shape[0]):
            if self.mp_data_index + 1 < self.melt_pool_data.shape[0]:
                if self.timestamps[i] >= self.melt_pool_data[self.mp_data_index
                                                             + 1][0]:
                    self.mp_data_index = self.mp_data_index + 1
            self._matched_array.append([
                i, self.timestamps[i],
                self.melt_pool_data[self.mp_data_index][0],
                self.melt_pool_data[self.mp_data_index][1],
                self.melt_pool_data[self.mp_data_index][2],
                self.melt_pool_data[self.mp_data_index][3],
                self.melt_pool_data[self.mp_data_index][4]
            ])

    def save_video(self, filename="Video.avi", framerate=60):
        """Generate video based on `_array` information, and save under `filename`.

        Parameters
        ----------
        filename : str
            Name to save the video file as.
        framerate : int
            Framerate to generate the video with.
        """
        height = self.array[0].shape[0]
        width = self.array[0].shape[1]
        size = (width, height)
        out = cv2.VideoWriter(filename,
                              cv2.VideoWriter_fourcc("f", "m", "p", "4"),
                              framerate, size)
        for i in range(0, self.array.shape[0]):
            percent = (i / self.array.shape[0]) * 100
            print("Saving video: " + str("%.2f" % percent) + "%")
            img = self.array[i]
            normalized_img = img.copy()
            if self.remove_reflection:
                ReflectionRemover.remove(normalized_img,
                                         zero_level_threshold=180,
                                         max_temp_threshold=700)

            normalized_img = cv2.normalize(normalized_img, normalized_img, 0,
                                           255, cv2.NORM_MINMAX, cv2.CV_8UC1)
            normalized_img = cv2.applyColorMap(normalized_img,
                                               cv2.COLORMAP_INFERNO)

            self.add_mp_data_to_img(normalized_img, i)

            out.write(normalized_img)

        out.release()

    @property
    def remove_reflection(self):
        """Return `_remove_reflection` attribute"""
        return self._remove_reflection

    @property
    def num_frames(self):
        """Return `_num_frames` attritbute. The number of frames in the video."""
        return self._num_frames

    def video_timestamp(self, frame):
        """Return the timestamp of the video based on the frame."""
        return self.matched_array[frame][1]

    def mp_timestamp(self, frame):
        """Return the timestamp of the melt pool data based on the frame."""
        return self.matched_array[frame][2]

    def mp_x(self, frame):
        """Return the meltpool x value based on the frame"""
        return self.matched_array[frame][3]

    def mp_y(self, frame):
        """Return the meltpool y value based on the frame"""
        return self.matched_array[frame][4]

    def mp_z(self, frame):
        """Return the meltpool z value based on the frame"""
        return self.matched_array[frame][5]

    def mp_area(self, frame):
        """Return the meltpool area value based on the frame"""
        return self.matched_array[frame][6]

    @property
    def matched_array(self):
        """Return the array of meltpool and video matched values"""
        return self._matched_array

    @property
    def mp_data_index(self):
        """Return the current index of the meltpool data array"""
        return self._mp_data_index

    @mp_data_index.setter
    def mp_data_index(self, value: int):
        """Set the `_mp_data_index` ensuring it is within bounds of the `_melt_pool_data` array."""
        if value < 0:
            self._mp_data_index = 0
        elif value > self._melt_pool_data.shape[0]:
            self._mp_data_index = self._melt_pool_data.shape[:0][0]
        else:
            self._mp_data_index = value

    @property
    def melt_pool_data(self):
        """Return the `_melt_pool_data` array"""
        return self._melt_pool_data

    @property
    def window_name(self):
        """Return the name of the window"""
        return self._window_name

    @property
    def array(self):
        """Return the array containing the thermal cam temp data"""
        return self._array

    @property
    def speed(self):
        """Return `_speed`"""
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        """Set the speed, ensuring it is within OpenCV bounds of 1 <= speed <= 1000"""
        if new_speed < 1:
            self._speed = 1
        elif new_speed > 1000:
            self._speed = 1000
        else:
            self._speed = new_speed

    @property
    def timestamps(self):
        """Return the thermal camera timestamps"""
        return self._timestamps

    def print_info(self, frame):
        """Print the information about the current frame to console"""
        print(
            "Frame: " + str(frame),
            "| TC time: " +
            str(self.mp_timestamp(frame).replace(microsecond=0)),
            "| MP time: " +
            str(self.mp_timestamp(frame).replace(microsecond=0)),
            "| MP X: " + str(self.mp_x(frame)),
            "| MP Y: " + str(self.mp_y(frame)),
            "| MP Z: " + str(self.mp_z(frame)),
            "| MP Area: " + str(self.mp_area(frame)),
        )

    def update_image(self, frame: int):
        """Normalize the array data. Apply the colormap, and add meltpool data to the image.

        Parameters
        ----------
        frame : int
            The current frame of the video
        Returns
        -------
        normalized_img
            Numpy array of the updated image of the current frame.
        """
        
        if(self.ROI):
            obj = stitcher(self._ROIs, frame)
            img = obj.start()
        else:
            img = self.array[frame]
           
        normalized_img = img.copy()
        if self.remove_reflection:
            ReflectionRemover.remove(
                normalized_img,
                zero_level_threshold=180,
                max_temp_threshold=700,
                remove_lower=True,
                lower_bounds=self.lower_bounds,
            )
        
        errorObj = PPMManipulatorForVid(normalized_img)
        errorObj.findErrorsArray()
        normalized_img = errorObj.drawErrors()

        normalized_img = cv2.normalize(normalized_img, normalized_img, 0, 255,
                                       cv2.NORM_MINMAX, cv2.CV_8UC1)
        normalized_img = cv2.applyColorMap(normalized_img,
                                           cv2.COLORMAP_INFERNO)

        self.add_mp_data_to_img(normalized_img, frame)

        #self.print_info(frame)
        return normalized_img

    def add_mp_data_to_img(self, img, frame):
        """Add meltpool data to the image.
        
        Parameters
        ----------
        img
            Image to add the meltpool data text to
        frame : int
            Frame number to grab meltpool data for
        """
        img_height = img.shape[:1][0]
        font = cv2.FONT_HERSHEY_DUPLEX
        font_size = img_height / 480
        font_color = (255, 255, 255)
        img = cv2.putText(
            img,
            "X: " + str(self.mp_x(frame)),
            (50, int((1 / 16) * img_height)),
            font,
            font_size,
            font_color,
        )
        img = cv2.putText(
            img,
            "Y: " + str(self.mp_y(frame)),
            (50, int((2 / 16) * img_height)),
            font,
            font_size,
            font_color,
        )
        img = cv2.putText(
            img,
            "Z: " + str(self.mp_z(frame)),
            (50, int((3 / 16) * img_height)),
            font,
            font_size,
            font_color,
        )
        img = cv2.putText(
            img,
            "Area: " + str(self.mp_area(frame)),
            (50, int((4 / 16) * img_height)),
            font,
            font_size,
            font_color,
        )

    def play_video(self, speed=1):
        """Play the video.

        Arguments
        ---------
        speed : int
            Delay in ms between showing each frame. Must be 1-1000.
        """
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 640, 480)
        self.speed = speed
        pause = False
        frame = 0
        while True:
            key = cv2.waitKey(self.speed)
            if not pause:
                    
                img = self.update_image(frame)
                
                cv2.imshow(self.window_name, img)
                printProgressBar(frame,self._num_frames)
                frame = frame + 1
            elif pause:
                if key == ord("s"):
                    np.savetxt(
                        "tc_temps-" + str(frame + 1) + ".csv",
                        img,
                        fmt="%d",
                        delimiter=",",
                    )
                elif key == ord("l"):
                    frame = frame + 10
                    img = self.update_image(frame)
                    cv2.imshow(self.window_name, img)
                elif key == ord("j"):
                    if frame > 10:
                        frame = frame - 10
                    else:
                        frame = 0
                    img = self.update_image(frame)
                    cv2.imshow(self.window_name, img)

            if key == ord("q"):
                break
            elif key == ord("k"):
                pause = not pause
            elif frame >= self.num_frames:
                break
        cv2.destroyAllWindows()
