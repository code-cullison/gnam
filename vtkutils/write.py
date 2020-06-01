################################################################################
# NAM Groningen 2017 Model: DeepNL/Utrecht University/Seismology
#
#   Purpose: 
#            1) load numpy npz files of the Groning Subsurface Volume
#            2) smooth each property volume (i.e. VP, VS, Rho)
#            3) create and ouput VTK files for viewing
#
#   Thomas Cullison - t.a.cullison@uu.nl
################################################################################

import numpy as np
from pyevtk.hl import gridToVTK
from pyproj import Proj, transform
import datetime

def write_vtk_gridded_model_3d(fqpname,props,xdata,ydata,zdata):


    nprop = len(props[:,0,0,0])
    assert nprop == 4
    assert len(props[0,:,0,0]) == xdata[2]
    assert len(props[0,0,:,0]) == ydata[2]
    assert len(props[0,0,0,:]) == zdata[2]

    # local coordinates
    xc = xdata[1]*np.arange(0,xdata[2])
    yc = ydata[1]*np.arange(0,ydata[2])
    zc = -zdata[1]*np.arange(0,zdata[2])
    xc = np.ravel(xc,order='F') #gridToVTK requires FORTRAN contiguous type
    yc = np.ravel(yc,order='F') #gridToVTK requires FORTRAN contiguous type
    zc = np.ravel(zc,order='F') #gridToVTK requires FORTRAN contiguous type


    ####################################################
    ## Write VTK file with all three properties

    ofilename = fqpname + '.vtr'

    tprops = np.copy(props) #using np.copy() maybe faster if no reordering
    tprops = tprops.transpose(0,3,2,1)

    rpvel = np.ravel(tprops[0,:,:,:].flatten(),order='F')
    rsvel = np.ravel(tprops[1,:,:,:].flatten(),order='F')
    rrho  = np.ravel(tprops[2,:,:,:].flatten(),order='F')
    rQ    = np.ravel(tprops[3,:,:,:].flatten(),order='F')

    gridToVTK(ofilename,xc,yc,zc,pointData={"pvel":rpvel,"svel":rsvel,"rho":rrho,"Q":rQ})
