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

from sys import argv
import pandas as pd
import numpy as np
from pyevtk.hl import gridToVTK
from scipy.ndimage import gaussian_filter1d
from GMUtils import GMUtils


####################################################
## Load and decopress data 

assert len(argv) == 2

ifilename = argv[1]

data = np.load(ifilename)
props = data['props']
props = props.transpose(0,3,2,1)


xdata = data['xd']
ydata = data['yd']
zdata = data['zd']

print('xd:\n',xdata)
print('yd:\n',ydata)
print('zd:\n',zdata)


## display center z-col for QC'ing

'''
nx = xdata[2]
hnx = int(nx/2 + 0.5)
hnx = hnx + int(hnx%2)
ny = ydata[2]
hny = int(ny/2 + 0.5)
hny = hny + int(hny%2)
print('props.shape:',props.shape)
print('VP[%d,%d,:]:\n' %(hnx,hny), props[0,hnx,hny,:])
print('VS[%d,%d,:]:\n' %(hnx,hny), props[1,hnx,hny,:])
print('Rho[%d,%d,:]:\n' %(hnx,hny),props[2,hnx,hny,:])
'''

####################################################
## compute x, y, z coordinates

xmin = xdata[0]
dx   = xdata[1]
nx   = int(xdata[2])
xmax = xmin + (nx-1)*dx

ymin = ydata[0]
dy   = ydata[1]
ny   = int(ydata[2])
ymax = ymin + (ny-1)*dy

zmin = zdata[0]
dz   = zdata[1]
nz   = int(zdata[2])
zmax = zmin + (nz-1)*dz

xc = np.arange(xmin,xmax+1,dx)
yc = np.arange(ymin,ymax+1,dy)
zc = np.arange(0,-zmax-1,-dz).astype(np.float32)

'''
####################################################
## Subsample to 100 m^c cells

print()
print('#######  Subsampling  #########################################')
print()
print('props.shape:\n',props.shape)
print('zc.shape:\n',zc.shape)
props = np.copy(props[:,5::10,::2,::2])
xc = np.copy(xc[::2])
yc = np.copy(yc[::2])
zc = np.copy(zc[5::10])

print('clipped props.shape:\n',props.shape)
print('clipped zc.shape:\n',zc.shape)
print('clipped zc:\n',zc)

zdata[0] = zc[0]

xdata[1] *= 2.0
ydata[1] *= 2.0
zdata[1] *= 10.0

xdata[2] = len(xc)
ydata[2] = len(yc)
zdata[2] = len(zc)
'''


####################################################
## Write VTK file with all three properties

#tp_shape = props.transpose(0,3,2,1).shape
ofilename = 'subsamp_smth_' + ifilename[:ifilename.rfind('.')]
print('Saving compressed subsurface model to disk at: %s\n' %(ofilename))
np.savez_compressed(ofilename + '.npz', props=props.transpose(0,3,2,1),xd=xdata,yd=ydata,zd=zdata)

# QC'ing
print('clip props.shape:',props.transpose(0,3,2,1).shape)
print('xdata:',xdata)
print('ydata:',ydata)
print('zdata:',zdata)

print('Writing Mesh Files:\n')
spec_data = {'props': props.transpose(0,3,2,1),'xd': xdata,'yd': ydata,'zd': zdata}
gmu = GMUtils()
gmu.writeSpecfem3DMesh('./MESH-default', spec_data)

'''
print('#######  Writing VTK file  ####################################')
print('Writting file at: %s' %('./' + ofilename + '.vtr'))

# this will create and write to a structured grid VTK file
gridToVTK(ofilename, xc, yc, zc, pointData = \
        {"pvel" : props[0,:,:,:].flatten(),"svel" : props[1,:,:,:].flatten(), "rho" : props[2,:,:,:].flatten()})
'''
