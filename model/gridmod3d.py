import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter1d

class gridmod3d:

    _subprops = np.nan
    _nprops = np.nan

    _ncells  = ()
    _npoints = ()
    _deltas  = ()
    _gorigin = ()
    _rotdeg  = np.nan
    _rotrad  = np.nan

    _axorder = {}

    shape = ()
    

    def __init__(self,subprops,nprops,axorder,dims,deltas,gorigin=(0,0,0),rotdeg=0):

        assert len(subprops) == nprops
        assert len(subprops[0,:,0,0]) == dims[0]
        assert len(subprops[0,0,:,0]) == dims[1]
        assert len(subprops[0,0,0,:]) == dims[2]
        assert len(dims) == len(deltas)
        assert len(dims) == len(gorigin)
        assert len(dims) == len(axorder)
        assert self._checkAxOrderDict(axorder)

        self._subprops = np.copy(subprops)
        self._nprops = nprops
        self._deltas = deltas

        self._gorigin = gorigin

        self._npoints = dims
        self._ncells = (dims[0]-1,dims[1]-1,dims[2]-1)

        self._axorder = axorder

        self._rotdeg = rotdeg
        self._rotrad = self._rotdeg*np.pi/180

        self.shape = self._subprops.shape

    def __getitem__(self,key):
        return self._subprops[key]

    def subsample(self,xf,yf,zf):

        _xf  = int(xf+0.5)
        _yf  = int(yf+0.5)
        _hzf = int(0.5*zf + 0.5)
        _zf  = int(2*_hzf)

        save_axorder = self._axorder.copy()
        self.changeAxOrder({'X':0,'Y':1,'Z':2})

        self._subprops = np.copy(self._subprops[:,::_xf,::_yf,::zf])

        nx = self._subprops.shape[1]
        ny = self._subprops.shape[2]
        nz = self._subprops.shape[3]

        dx = self._deltas[0]*_xf
        dy = self._deltas[1]*_yf
        dz = self._deltas[2]*_zf

        self._npoints = (nx,ny,nz)
        self._ncells  = (nx-1,ny-1,nz-1)
        self._deltas  = (dx,dy,dz)

        self.changeAxOrder(save_axorder)

        self.shape = self._subprops.shape

    def _getLocalCoordsCellsByAxis(self,key):

        assert isinstance(key, str)

        i = self._axorder[key]
        ld = self._deltas[i]
        ln = self._ncells[i]
        imin = 0.5*ld
        imax = imin + (ln-1)*ld + 0.5*ld
        return np.arange(imin,imax,ld)

    def _getLocalCoordsPointsByAxis(self,key):

        assert isinstance(key, str)

        i = self._axorder[key]
        ld = self._deltas[i]
        ln = self._npoints[i]
        imin = 0
        imax = imin + (ln-1)*ld + 0.5*ld
        return np.arange(imin,imax,ld)

    def getLocalCoordsCellsX(self):
         return self._getLocalCoordsCellsByAxis('X')

    def getLocalCoordsCellsY(self):
         return self._getLocalCoordsCellsByAxis('Y')

    def getLocalCoordsCellsZ(self):
         return self._getLocalCoordsCellsByAxis('Z')

    def getLocalCoordsPointsX(self):
         return self._getLocalCoordsPointsByAxis('X')

    def getLocalCoordsPointsY(self):
         return self._getLocalCoordsPointsByAxis('Y')

    def getLocalCoordsPointsZ(self):
         return self._getLocalCoordsPointsByAxis('Z')

    def getLocalCoordsCellsXY(self):

        lcx = self.getLocalCoordsCellsX()
        lcy = self.getLocalCoordsCellsY()

        return np.transpose([np.tile(lcx, len(lcy)), np.repeat(lcy, len(lcx))])

    def getLocalCoordsPointsXY(self):

        lcx = self.getLocalCoordsPointsX()
        lcy = self.getLocalCoordsPointsY()

        return np.transpose([np.tile(lcx, len(lcy)), np.repeat(lcy, len(lcx))])

    def _checkAxOrderDict(self,dic):
        isgood = False
        isgood = isinstance(dic, dict)
        if not isgood:
            return False
        isgood = isgood & (len(dic) == 3)
        if not isgood:
            return False
        isgood = isgood & ('X' in dic.keys())
        if not isgood:
            return False
        dicX = dic['X']
        isgood = isgood & ((dicX == 0) | (dicX == 1) | (dicX == 2))
        if not isgood:
            return False
        isgood = isgood & ('Y' in dic.keys())
        if not isgood:
            return False
        dicY = dic['Y']
        isgood = isgood & ((dicY == 0) | (dicY == 1) | (dicY == 2))
        if not isgood:
            return False
        isgood = isgood & ('Z' in dic.keys())
        if not isgood:
            return False
        dicZ = dic['Z']
        isgood = isgood & ((dicZ == 0) | (dicZ == 1) | (dicZ == 2))
        if not isgood:
            return False
        isgood = isgood & (dicX != dicY) & (dicX != dicZ) & (dicY != dicZ)
        
        return isgood

    def changeAxOrder(self,dic):

        assert self._checkAxOrderDict(dic)

        itrans = np.zeros((4),dtype=np.int)

        odicX = self._axorder['X']+1
        odicY = self._axorder['Y']+1
        odicZ = self._axorder['Z']+1

        #print('old axorder:',self._axorder)

        ndicX = dic['X']+1
        ndicY = dic['Y']+1
        ndicZ = dic['Z']+1

        itrans[ndicX] = odicX
        itrans[ndicY] = odicY
        itrans[ndicZ] = odicZ

        #print('itrans:',itrans)

        self._subprops = np.copy(self._subprops.transpose(itrans))

        self._axorder['X'] = dic['X']
        self._axorder['Y'] = dic['Y']
        self._axorder['Z'] = dic['Z']

        self.shape = self._subprops.shape


    def getNPArray(self):
        return np.copy(self._subprops)


    def getRotatedCoordsXY(self,rad,rnx,rny,rox,roy,rdx,rdy):

        rxc = np.arange(rnx)*rdx
        rxy = np.arange(rny)*rdy

        rxyc = np.transpose([np.tile(rxc, len(ryc)), np.repeat(ryc, len(rxc))])
        rrm = np.array([[np.cos(rad),-np.sin(rad)],[np.sin(rad),np.cos(rad)]]) 

        for i in range(rxyc.shape[0]):
            rxyc[i,:] = rrm.dot(arr[i,:])

        rxyc[:,0] += rox
        rxyc[:,1] += roy

        return rxyc

    def depthValsSliceFromZIndex(self,iz):

        assert (0 <= iz) & (iz <= self._npoints[2])

        save_axorder = self._axorder.copy()
        self.changeAxOrder({'X':2,'Y':1,'Z':0})

        slice_dprops = np.copy(self._subprops[:,iz,:,:])

        self.changeAxOrder(save_axorder)

        return slice_dprops

    def depthValsSliceFromZFloat(self,z):

        zc = self.getLocalCoordsPointsZ()
        assert (zc[0] <= z) & (z <= zc[-1])

        xc = self.getLocalCoordsPointsX()
        yc = self.getLocalCoordsPointsY()
        xyc = self.getLocalCoordsPointsXY()
        nxyc = xyc.shape[0]

        save_axorder = self._axorder.copy()
        self.changeAxOrder({'X':2,'Y':1,'Z':0})

        slice_dprops = np.zeros((self._nprops,xyc.shape[0]))
        for p in range(self._nprops):
            rgi = RegularGridInterpolator((zc,yc,xc),self._subprops[p])
            trim_props = slice_dprops[p,:]
            for ixy in range(nxyc):
                trim_props[ixy] = rgi((z,xyc[ixy,1],xyc[ixy,0]))

        self.changeAxOrder(save_axorder)

        return slice_dprops

    def getCoordsXYZTuple(self,local=True):

        xc,yc,xyc = self.getCoordsXYTuple(local)
        zc = self.getLocalCoordsPointsZ()

        return (xc,yc,zc,xyc)

    def getCoordsXYTuple(self,local=True):

        xc = self.getLocalCoordsPointsX()
        yc = self.getLocalCoordsPointsY()
        xyc = self.getLocalCoordsPointsXY()

        if not local:

            xc += self._gorigin[0]
            yc += self._gorigin[1]

            xyc[:,0] += self._gorigin[0]
            xyc[:,1] += self._gorigin[1]
        
        return (xc,yc,xyc)

    def depthValsSliceFromXYCoordsZIndex(self,sxyc,iz,local=True):

        assert (0 <= iz) & (iz <= self._npoints[2])

        xc,yc,xyc = self.getCoordsXYTuple(local)

        snxyc = sxyc.shape[0]

        save_axorder = self._axorder.copy()
        self.changeAxOrder({'X':2,'Y':1,'Z':0})

        slice_dprops = np.zeros((self._nprops,sxyc.shape[0]))
        for p in range(self._nprops):
            rgi = RegularGridInterpolator((yc,xc),self._subprops[p,iz,:,:])
            trim_props = slice_dprops[p,:]
            for ixy in range(snxyc):
                trim_props[ixy] = rgi((sxyc[ixy,1],sxyc[ixy,0]))

        self.changeAxOrder(save_axorder)

        return slice_dprops

    def depthValsSliceFromXYCoordsZFloat(self,sxyc,z,local=True):

        xc,yc,zc,xyc = self.getCoordsXYZTuple(local)
        assert (zc[0] <= z) & (z <= zc[-1])

        xc = self.getLocalCoordsPointsX()
        yc = self.getLocalCoordsPointsY()
        xyc = self.getLocalCoordsPointsXY()

        snxyc = sxyc.shape[0]

        save_axorder = self._axorder.copy()
        self.changeAxOrder({'X':2,'Y':1,'Z':0})

        slice_dprops = np.zeros((self._nprops,sxyc.shape[0]))
        for p in range(self._nprops):
            rgi = RegularGridInterpolator((zc,yc,xc),self._subprops[p])
            trim_props = slice_dprops[p,:]
            for ixy in range(snxyc):
                trim_props[ixy] = rgi((z,sxyc[ixy,1],sxyc[ixy,0]))

        self.changeAxOrder(save_axorder)

        return slice_dprops


    def sliceVolumeValsFromCoordsXY(self,sxyc,local=True):

        #FIXME: need to check coordinate bounds
        xc,yc,zc,xyc = self.getCoordsXYZTuple(local)
        snxyc = sxyc.shape[0]

        slice_props = np.zeros((self._nprops,sxyc.shape[0]*len(zc)))
        for p in range(self._nprops):
            rgi = RegularGridInterpolator((xc,yc,zc),self._subprops[p])
            trim_props = slice_props[p,:,:,:]
            for iz in range(len(rzc)):
                z = zc[iz]
                for ixy in range(snxyc):
                    trim_props[ixy + snxyc*iz] = rgi((sxyc[ixy,0],sxyc[ixy,1],z))

        return slice_props

    def smoothX(self,x_sig,x_only=True):

        if not x_only:
            assert self._axorder['X'] == 2

        print('Smoothing in x-direction (sigma=%f)' %x_sig)

        save_axorder = self._axorder.copy()
        if x_only:
            self.changeAxOrder({'X':2,'Y':1,'Z':0})

        ny = self._npoints[1]
        nz = self._npoints[2]
        perc_10 = int(nz/10 + 0.5)
        for iz in range(nz):
            for iy in range(ny):
                for ip in range(self._nprops):
                    self._subprops[ip,iz,iy,:] = gaussian_filter1d(self._subprops[ip,iz,iy,:], x_sig) #VP
            if (iz % perc_10) == 0:
                print('Currently %d percent finished smoothing in x-direction' % int((iz//perc_10)*10))
        print('Currently 100 percent finished smoothing in x-direction')
        print()

        if x_only:
            self.changeAxOrder(save_axorder)

    def smoothY(self,y_sig,y_only=True):

        if not y_only:
            assert self._axorder['Y'] == 2

        print('Smoothing in y-direction (sigma=%f)' %y_sig)

        save_axorder = self._axorder.copy()
        if y_only:
            self.changeAxOrder({'X':0,'Y':2,'Z':1})

        nx = self._npoints[0]
        nz = self._npoints[2]
        perc_10 = int(nx/10 + 0.5)
        for ix in range(nx):
            for iz in range(nz):
                for ip in range(self._nprops):
                    self._subprops[ip,ix,iz,:] = gaussian_filter1d(self._subprops[ip,ix,iz,:], y_sig)
            if (ix % perc_10) == 0:
                print('Currently %d percent finished smoothing in y-direction' % int((ix//perc_10)*10))
        print('Currently 100 percent finished smoothing in y-direction')
        print()

        if y_only:
            self.changeAxOrder(save_axorder)

    def smoothZ(self,z_sig,z_only=True):

        if not z_only:
            assert self._axorder['Z'] == 2

        print('Smoothing in z-direction (sigma=%f)' %z_sig)

        save_axorder = self._axorder.copy()
        if z_only:
            self.changeAxOrder({'X':0,'Y':1,'Z':2})

        nx = self._npoints[0]
        ny = self._npoints[1]
        perc_10 = int(nx/10 + 0.5)
        for ix in range(nx):
            for iy in range(ny):
                for ip in range(self._nprops):
                    self._subprops[ip,ix,iy,:] = gaussian_filter1d(self._subprops[ip,ix,iy,:], z_sig)
            if (ix % perc_10) == 0:
                print('Currently %d percent finished smoothing in z-direction' % int((ix//perc_10)*10))
        print('Currently 100 percent finished smoothing in z-direction')
        print()

        if z_only:
            self.changeAxOrder(save_axorder)

    def smoothXYZ(self,x_sig,y_sig,z_sig):

        save_axorder = self._axorder.copy()

        self.changeAxOrder({'X':0,'Y':1,'Z':2})
        self.smoothZ(z_sig,z_only=False)

        self.changeAxOrder({'X':0,'Y':2,'Z':1})
        self.smoothY(y_sig,y_only=False)

        self.changeAxOrder({'X':2,'Y':1,'Z':0})
        self.smoothX(x_sig,x_only=False)

        self.changeAxOrder(save_axorder)


    #def sliceVolumeGrid3D(rdeg,rnxyz,roxyz,rdxyz):


#return (props,xdata,ydata,zdata)

'''
#values = np.zeros((27)).reshape((3,3,3)).astype(np.int)
mysubprops = np.zeros((3,5,4,3))
'''
'''
mysubprops[0,:,:,:] = np.copy(values)
mysubprops[1,:,:,:] = np.copy(values)
mysubprops[2,:,:,:] = np.copy(values)
'''
'''
mysubprops[:,:,:,1] += 1
mysubprops[:,:,:,2] += 2
mysubprops[:,:,1,:] += 10
mysubprops[:,:,2,:] += 20
mysubprops[:,:,3,:] += 30
mysubprops[:,1,:,:] += 100
mysubprops[:,2,:,:] += 200
mysubprops[:,3,:,:] += 300
mysubprops[:,4,:,:] += 400
mysubprops[1,:,:,:] += 1000
mysubprops[2,:,:,:] += 2000

print('mysubpropsp[0]:\n', mysubprops[0,:,:,:])
mygm = gridmod3d(mysubprops,3,(5,4,3),(100,100,100),(20000,20000,0),30,{'X':0,'Y':1,'Z':2})

mysub = mygm.getNPArray()
print('mysub[0,:,:,:]:\n', mysub[0,:,:,:])

mygm.changeAxOrder({'X':0,'Y':1,'Z':2})
mysubT = mygm.getNPArray()
print('mysubT[0]:\n', mysubT[0,:,:,:])

mygm.changeAxOrder({'X':0,'Y':2,'Z':1})
mysubT = mygm.getNPArray()
print('mysubT[0]:\n', mysubT[0,:,:,:])

mygm.changeAxOrder({'X':1,'Y':0,'Z':2})
mysubT = mygm.getNPArray()
print('mysubT[0]:\n', mysubT[0,:,:,:])

mygm.changeAxOrder({'X':1,'Y':2,'Z':0})
mysubT = mygm.getNPArray()
print('mysubT[0]:\n', mysubT[0,:,:,:])

mygm.changeAxOrder({'X':2,'Y':0,'Z':1})
mysubT = mygm.getNPArray()
print('mysubT[0]:\n', mysubT[0,:,:,:])

mygm.changeAxOrder({'X':2,'Y':1,'Z':0})
mysubT = mygm.getNPArray()
print('mysubT[0]:\n', mysubT[0,:,:,:])

xp = mygm.getLocalCoordsPointsX()
print('xp:\n',xp)

xc = mygm.getLocalCoordsCellsX()
print('xc:\n',xc)

yp = mygm.getLocalCoordsPointsY()
print('yp:\n',yp)

yc = mygm.getLocalCoordsCellsY()
print('yc:\n',yc)

zp = mygm.getLocalCoordsPointsZ()
print('zp:\n',zp)

zc = mygm.getLocalCoordsCellsZ()
print('zc:\n',zc)

xyp = mygm.getLocalCoordsPointsXY()
print('xyp:\n',xyp)

xyc = mygm.getLocalCoordsCellsXY()
print('xyc:\n',xyc)
'''


