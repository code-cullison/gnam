import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter1d
import time

class gridmod3d:

    _subprops = None
    _nprops   = None

    _ncells  = None
    _npoints = None
    _deltas  = None
    _gorigin = None
    _rotdeg  = None
    _rotrad  = None

    _axorder = None

    shape = None
    

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

    def __str__(self):
        str_dict = { 'ncells':self._ncells,'npoints':self._npoints, \
                     'deltas':self._deltas,'origin':self._gorigin,  \
                     'rotation (degres)':self._rotdeg,              \
                     'rotation (rads)':self._rotrad,                \
                     'shape':self.shape,'Axis Order':self._axorder  }
        return str(str_dict)


    def _rotate_translate_xy_coords(self,xyc,deg):

        if deg != 0:
            rad = deg*np.pi/180
            rrm = np.array([[np.cos(rad),-np.sin(rad)],[np.sin(rad),np.cos(rad)]]) 

            for i in range(xyc.shape[0]):
                xyc[i,:] = rrm.dot(xyc[i,:])

        xyc[:,0] += self._gorigin[0]
        xyc[:,1] += self._gorigin[1]

        return xyc


    def _subsample(self,xf,yf,zf,use_half_z=False):

        _xf  = int(xf+0.5)
        _yf  = int(yf+0.5)
        _hzf = int(0.5*zf + 0.5)
        _zf  = int(2*_hzf)

        save_axorder = self._axorder.copy()
        self.changeAxOrder({'X':0,'Y':1,'Z':2})

        if use_half_z:
            self._subprops = np.copy(self._subprops[:,::_xf,::_yf,_hzf::zf])
        else:
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

    def subsample(self,xf,yf,zf):
        return self._subsample(xf,yf,zf,False)

    def subsample_half_z(self,xf,yf,zf):  # for specfem
        return self._subsample(xf,yf,zf,True)

    def _getLocalCoordsCellsByAxis(self,key):

        assert (key == 'X') or (key == 'Y') or (key == 'Z')

        ax_dict = {'X':0,'Y':1,'Z':2}

        i = ax_dict[key]

        i = self._axorder[key]
        ld = self._deltas[i]
        ln = self._ncells[i]
        imin = 0.5*ld
        imax = imin + (ln-1)*ld + 0.5*ld
        return np.arange(imin,imax,ld)

    def _getLocalCoordsPointsByAxis(self,key):

        assert (key == 'X') or (key == 'Y') or (key == 'Z')

        ax_dict = {'X':0,'Y':1,'Z':2}

        i = ax_dict[key]
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

    def _getGlobalCoordsXY(self,as_points=True):

        if as_points:
            lxy = self.getLocalCoordsPointsXY()
        else:
            lxy = self.getLocalCoordsCellsXY()

        gxy = self._rotate_translate_xy_coords(lxy,self._rotdeg)

        return gxy

    def getGlobalCoordsPointsXY(self):
        return self._getGlobalCoordsXY(as_points=True)

    def getGlobalCoordsCellsXY(self):
        return self._getGlobalCoordsXY(as_points=False)

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

        temp_props = np.copy(self._subprops.transpose(itrans),order='C')
        del self._subprops # clean up memory because thses can be big
        self._subprops = temp_props

        self._axorder['X'] = dic['X']
        self._axorder['Y'] = dic['Y']
        self._axorder['Z'] = dic['Z']

        self.shape = self._subprops.shape


    def getNPArray(self):
        return np.copy(self._subprops)

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

        #print('self.shape:',self.shape)
        save_axorder = self._axorder.copy()
        self.changeAxOrder({'X':2,'Y':1,'Z':0})
        #print('self.shape:',self.shape)

        #FIXME: need to check coordinate bounds
        xc,yc,zc,xyc = self.getCoordsXYZTuple(local)
        del xyc # not needed
        snxyc = sxyc.shape[0]
        #print('snxyc:',snxyc)

        snz = len(zc)
        zperc = 1.0/snz
        slice_props = np.zeros((self._nprops,snxyc*snz),dtype=np.float32)
        for p in range(self._nprops):
            #print('index.order: %d,%d,%d,%d' %(self._nprops,len(zc),len(yc),len(xc)))
            rgi = RegularGridInterpolator((zc,yc,xc),self._subprops[p])
            start_p = time.time()
            for iz in range(snz):
                start_z = time.time()
                #print('interpolating z%% %f' %(100*iz*zperc))
                z = zc[iz]
                for ixy in range(snxyc):
                    slice_props[p,ixy + snxyc*iz] = rgi((z,sxyc[ixy,1],sxyc[ixy,0]))
                z_time = time.time() - start_z
                #print('Exec Time for one z-loop:',z_time)
            p_time = time.time() - start_p
            #print('Exec Time for one P-loop:',p_time)

        self.changeAxOrder(save_axorder)

        #temp_props = np.copy(slice_props.reshape((self._nprops,snz,sny,snx)),order='C')
        #del slice_props
            
        #return temp_props
        return slice_props

    def slice_volume_by_bbox( self,sbbox,sdx=-1,sdy=-1,sdz=-1):

        if sdx == -1:
            sdx = self._deltas[0]
        if sdy == -1:
            sdy = self._deltas[1]
        if sdz == -1:
            sdz = self._deltas[2]

        cl = sbbox.getCLoop()
        ldeg = sbbox.getRotDeg()

        xmin = np.min(cl[:,0])
        xmax = np.max(cl[:,0])
        ymin = np.min(cl[:,0])
        ymax = np.max(cl[:,0])
        zmax = self._npoints[2]*self._deltas[2] 
        zmin = self._gorigin[2]

        xspan = xmax - xmin
        yspan = ymax - ymin
        zspan = zmax - zmin

        lnx = int(xspan/sdx) + int(1) ## +1: for npoints
        lny = int(yspan/sdy) + int(1) ## +1: for npoints
        lnz = int(zspan/sdz) + int(1) ## +1: for npoints

        lxc = sdx*np.arange(lnx)
        lyc = sdy*np.arange(lny)
        lzc = sdz*np.arange(lnz)

        lxyc = np.transpose([np.tile(lxc, len(lyc)), np.repeat(lyc, len(lxc))])

        gxyc = self._rotate_translate_xy_coords(lxyc,ldeg)

        return self.sliceVolumeValsFromCoordsXY(gxyc,local=False)

        

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


    def get_npoints(self):
        return self._npoints

    def get_deltas(self):
        return self._deltas

    def get_gorigin(self):
        return self._gorigin

    #def sliceVolumeGrid3D(rdeg,rnxyz,roxyz,rdxyz):

