import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter1d
import time
import copy

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


    def _rotate_xy_coords(self,xyc,deg):

        if deg != 0:
            rad = deg*np.pi/180
            rrm = np.array([[np.cos(rad),-np.sin(rad)],[np.sin(rad),np.cos(rad)]]) 

            for i in range(xyc.shape[0]):
                xyc[i,:] = rrm.dot(xyc[i,:])

        return xyc

    def _rotate_translate_xy_coords(self,xyc,deg):

        xyc = self._rotate_xy_coords(xyc,deg)

        xyc[:,0] += self._gorigin[0]
        xyc[:,1] += self._gorigin[1]

        return xyc


    def subsample(self, isx=0,iex=None,idx=2, \
                        isy=0,iey=None,idy=2, \
                        isz=0,iez=None,idz=2  ):

        _isx = int(isx+0.5)
        _isy = int(isy+0.5)
        _isz = int(isz+0.5)

        _iex = iex
        _iey = iey
        _iez = iez
        if iex is not None:
            _iex = int(iex+0.5)
        if iey is not None:
            _iey = int(iey+0.5)
        if iez is not None:
            _iez = int(iez+0.5)

        _idx = int(idx+0.5)
        _idy = int(idy+0.5)
        _idz = int(idz+0.5)

        save_axorder = self._axorder.copy()
        self.changeAxOrder({'X':0,'Y':1,'Z':2})

        self._subprops = np.copy(self._subprops[:,_isx:_iex:_idx,_isy:_iey:_idy,_isz:_iez:_idz])

        nx = self._subprops.shape[1]
        ny = self._subprops.shape[2]
        nz = self._subprops.shape[3]

        dx = self._deltas[0]*_idx
        dy = self._deltas[1]*_idy
        dz = self._deltas[2]*_idz

        ox = self._gorigin[0] + _isx*self._deltas[0]
        oy = self._gorigin[1] + _isy*self._deltas[1]
        oz = self._gorigin[2] + _isz*self._deltas[2]

        self._npoints = (nx,ny,nz)
        self._ncells  = (nx-1,ny-1,nz-1)
        self._deltas  = (dx,dy,dz)
        self._gorigin = (ox,oy,oz)

        self.changeAxOrder(save_axorder)

        self.shape = self._subprops.shape
        

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

        print('self.shape:',self.shape)
        save_axorder = self._axorder.copy()
        self.changeAxOrder({'X':2,'Y':1,'Z':0})
        print('self.shape:',self.shape)

        #FIXME: need to check coordinate bounds
        xc,yc,zc,xyc = self.getCoordsXYZTuple(local)

        xmin = np.min(xc)
        xmax = np.max(xc)
        ymin = np.min(yc)
        ymax = np.max(yc)
        print('mxmin,mxmax = %f,%f:' %(xmin,xmax))
        print('mymin,mymax = %f,%f:' %(ymin,ymax))
        del xyc # not needed
        snxyc = sxyc.shape[0]
        sxmin = np.min(sxyc[:,0])
        sxmax = np.max(sxyc[:,0])
        symin = np.min(sxyc[:,1])
        symax = np.max(sxyc[:,1])
        print('sxmin,sxmax = %f,%f:' %(sxmin,sxmax))
        print('symin,symax = %f,%f:' %(symin,symax))
        print('snxyc:',snxyc)

        snz = len(zc)
        zperc = 1.0/snz
        slice_props = np.zeros((self._nprops,snz,snxyc),dtype=np.float32)
        for p in range(self._nprops):
            print('index.order: %d,%d,%d,%d' %(self._nprops,len(zc),len(yc),len(xc)))
            #rgi = RegularGridInterpolator((zc,yc,xc),self._subprops[p])
            start_p = time.time()
            for iz in range(snz):
                start_z = time.time()
                rgi = RegularGridInterpolator((yc,xc),self._subprops[p,iz,:,:])
                print('interpolating z%% %f' %(100*iz*zperc))
                z = zc[iz]
                for ixy in range(snxyc):
                    #print('interp_x,interp_y = %f,%f' %(sxyc[ixy,0],sxyc[ixy,1]))
                    slice_props[p,iz,ixy] = rgi((sxyc[ixy,1],sxyc[ixy,0]))
                z_time = time.time() - start_z
                print('Exec Time for one z-loop:',z_time)
            p_time = time.time() - start_p
            print('Exec Time for one P-loop:',p_time)

        self.changeAxOrder(save_axorder)

        #temp_props = np.copy(slice_props.reshape((self._nprops,snz,sny,snx)),order='C')
        #del slice_props
            
        #return temp_props
        return slice_props

    def slice_volume_by_bbox( self,sbbox,sdx=-1,sdy=-1,sdz=-1):

        sbbox = copy.deepcopy(sbbox)

        if sdx == -1:
            sdx = self._deltas[0]
        if sdy == -1:
            sdy = self._deltas[1]

        orig = sbbox.getOrigin()
        ldeg = sbbox.getRotDeg()

        cl = sbbox.getCLoop()
        bxmin = np.min(cl[:,0])
        bxmax = np.max(cl[:,0])
        bymin = np.min(cl[:,1])
        bymax = np.max(cl[:,1])
        print('bxmin,bxmax = %f,%f:' %(bxmin,bxmax))
        print('bymin,bymax = %f,%f:' %(bymin,bymax))
        
        # rotate to local coordinates
        if ldeg != 0:
            sbbox.rotate(-ldeg)
            cl = sbbox.getCLoop()

        # get the span of x and y
        x0 = cl[0,0] # corner-0
        x3 = cl[3,0] # corner-3
        y0 = cl[0,1] # corner-0
        y1 = cl[1,1] # corner-1

        xspan = np.abs(x3 - x0)
        yspan = np.abs(y1 - y0)

        # create new local x and y coordinates
        lnx = int(xspan/sdx +0.5) + int(1) ## +1: for npoints
        lny = int(yspan/sdy +0.5) + int(1) ## +1: for npoints

        lxc = sdx*np.arange(lnx)
        lyc = sdy*np.arange(lny)

        # create xy coordinate pairs for interpolating
        lxyc = np.transpose([np.tile(lxc, len(lyc)), np.repeat(lyc, len(lxc))])

        # rotate xy coordinates in to global coordinate frame
        if ldeg != 0:
            lxyc = self._rotate_xy_coords(lxyc,ldeg)

        # translate xy coordiantes to global origin
        lxyc[:,0] += orig[0]
        lxyc[:,1] += orig[1]
        gxyc = lxyc
        gxmin = np.min(gxyc[:,0])
        gxmax = np.max(gxyc[:,0])
        gymin = np.min(gxyc[:,1])
        gymax = np.max(gxyc[:,1])
        print('gxmin,gxmax = %f,%f:' %(gxmin,gxmax))
        print('gymin,gymax = %f,%f:' %(gymin,gymax))
        print('gxyc.shape:',gxyc.shape)

        # slice by coordinates
        sprops = self.sliceVolumeValsFromCoordsXY(gxyc,local=False)
        print('nz,ny,nx = %d,%d,%d' %(self._npoints[2],lny,lnx))
        print('Before Reshape: ', sprops.shape)

        #return sprops

        # reshape into 4D ndarray
        sprops = sprops.reshape((self._nprops,self._npoints[2],lny,lnx))
        print('After Reshape:  ', sprops.shape)

        # Transpose in to order: {'X':0,'Y':1,'Z':2}
        sprops = sprops.transpose(0,3,2,1)
        print('After Transpose:', sprops.shape)
        
        # paramters for new gridmod3d
        nx = lnx
        ny = lny
        nz = self._npoints[2]
        dx = sdx
        dy = sdy
        dz = self._deltas[2]
        ox = orig[0]
        oy = orig[1]
        oz = self._gorigin[2]
        axorder = {'X':0,'Y':1,'Z':2}
        nprops = self._nprops
        rdeg = ldeg

        # return a new gridmod3d 
        return gridmod3d(sprops,nprops,axorder,(nx,ny,nz),(dx,dy,dz),(ox,oy,oz),rdeg)

    #end slice_from_bbox()


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
        for ip in range(self._nprops):
        #for iz in range(nz):
            for iz in range(nz):
            #for iy in range(ny):
                for iy in range(ny):
                #for ip in range(self._nprops):
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
        for ip in range(self._nprops):
        #for ix in range(nx):
            for ix in range(nx):
            #for iz in range(nz):
                for iz in range(nz):
                #for ip in range(self._nprops):
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
        for ip in range(self._nprops):
        #for ix in range(nx):
            for ix in range(nx):
            #for iy in range(ny):
                for iy in range(ny):
                #for ip in range(self._nprops):
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

