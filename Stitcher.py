

class stitcher:

    def __init__(self,  ROIs, dim):
        self._dims = dim
        self._totalROIs = self._dims[0] * self._dims[1]
        self._ROIs = np.ndarray(shape = (self._dims[0], self._dims[1]))
        for x in range(self._dims[0])
            self._threads.append(threading.Thread(target=stitch, args=self._ROIs[:,x])

        
        

    def stitch(self, ROI):

        for x in range(np.size(ROI,1)):
           tmp = ROI[self.timestamp,x,:]
           tmp = np.append(tmp, self._ROI1[self.timestamp,x,:])
           tmp = np.append(tmp, self._ROI2[self.timestamp,x,:])
            
           self._row[x] = tmp




    def start(self):
        for x in range(self._dims[0])
            self._threads(x).start()
            self._threads(x).join()


