import numpy as np
from shapely.geometry import Point, Polygon

class bbox:

    _c_loop = []
    _rotdeg = None
    _origin = []
    

    def __init__(self, c_loop, rotdeg=0):

        assert len(c_loop) == 5
        assert len(c_loop[0]) == 2

        self._c_loop = c_loop.copy()
        self._rotdeg = rotdeg
        self._origin = np.array([self._c_loop[0,0],self._c_loop[0,1]])

    def __str__(self):
        bbdic = {'c_loop':self._c_loop,'rotdeg':self._rotdeg,'origin':self._origin}
        return str(bbdic)


    def rotate(self,new_rotdeg):

        theta = new_rotdeg*np.pi/180
        rm = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])

        old_c_loop = self._c_loop.copy()
        old_c_loop[:,0] -= self._origin[0]
        old_c_loop[:,1] -= self._origin[1]


        self._c_loop[0,:] = rm.dot(old_c_loop[0,:])
        self._c_loop[1,:] = rm.dot(old_c_loop[1,:])
        self._c_loop[2,:] = rm.dot(old_c_loop[2,:])
        self._c_loop[3,:] = rm.dot(old_c_loop[3,:])
        self._c_loop[4,:] = self._c_loop[0,:]

        del old_c_loop

        self._c_loop[:,0] += self._origin[0]
        self._c_loop[:,1] += self._origin[1]

        self._rotdeg = new_rotdeg


    def translate(self,shift_x,shift_y):

        self._origin[0] += shift_x
        self._origin[1] += shift_y
        self._c_loop[:,0] += shift_x
        self._c_loop[:,1] += shift_y


    def getCLoop(self):
        return self._c_loop


    def getRotDeg(self):
        return self._rotdeg


    def getOrigin(self):
        return self._origin


    def separateByInOut(self,xcoords,ycoords):
        xycoords = np.append(xcoords,ycoords).reshape((2,len(xcoords))).T

        acoords = np.array([self._c_loop[0,:],self._c_loop[1,:],self._c_loop[2,:],self._c_loop[3,:]])
        boxcoords = list(map(tuple, acoords))

        poly = Polygon(boxcoords)

        xyPoints = list(map(Point, xycoords))
        is_iside = np.ones((len(xycoords[:,0])),dtype=bool)
        is_oside = np.zeros((len(xycoords[:,0])),dtype=bool)
        for i in range(len(xyPoints)):
            if not poly.contains(xyPoints[i]):
                is_iside[i] = False
                is_oside[i] = True


        i_stations = xycoords[is_iside]
        o_stations = xycoords[is_oside]

        return (i_stations,o_stations)


    def coordIsIn(self,xc,yc):
        acoords = np.array([self._c_loop[0,:],self._c_loop[1,:],self._c_loop[2,:],self._c_loop[3,:]])
        boxcoords = list(map(tuple, acoords))

        poly = Polygon(boxcoords)

        p = Point(xc,yc)

        isin = False
        if poly.contains(p):
            isin = True

        return isin



