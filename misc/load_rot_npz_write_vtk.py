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
#print('props:]\n',props)

#coords = np.load('coord_rotated_hack_100.npz')


xdata = data['xd']
ydata = data['yd']
zdata = data['zd']

xc = xdata
yc = ydata
zc = np.copy(zdata[::-1])

nxyz = len(xc)*len(yc)*len(zc)

print('nxyz = ',nxyz)
print('props.shape:',props.shape)
#props = props.reshape((len(zc),len(yc),len(xc)))
props = props.reshape((3,len(zc),len(yc),len(xc)))
print('props.shape:',props.shape)
#tprops = props.transpose(2,1,0)
#print('tprops.shape(2,1,0):',tprops.shape)
#tprops = props.transpose(0,1,2)
#print('tprops.shape(0,1,2):',tprops.shape)
#props = props.transpose(2,1,0)
#print('tprops.shape(2,1,0):',props.shape)
props = props.transpose(0,3,2,1)
print('tprops.shape(0,3,2,1):',props.shape)

print('xd:\n',xc)
print('yd:\n',yc)
print('zd:\n',zc)


## display center z-col for QC'ing

print('props.shape:',props.shape)
#print('VP[%d,%d,:]:\n' %(10,10), props[10,10,:])
print('VP[0,%d,%d,:]:\n' %(10,10), props[0,10,10,:])
#rprops = np.copy(props[:,:,::-1])
#print('VP[%d,%d,:]:\n' %(10,10), rprops[10,10,:])
rprops = np.copy(props[:,:,:,::-1])
print('VP[0,%d,%d,:]:\n' %(10,10), rprops[0,10,10,:])

####################################################
## compute x, y, z coordinates

'''
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
## Write VTK file with all three properties

print('#######  Writing VTK file  ####################################')
ofilename = ifilename[:ifilename.rfind('.')]
print('Writting file at: %s' %('./' + ofilename + '.vtr'))

# this will create and write to a structured grid VTK file
rprops = np.copy(rprops.transpose(0,3,2,1))
gridToVTK(ofilename, xc, yc, zc, pointData = {"pvel" : rprops[0,:,:,:].flatten(),"svel" : rprops[1,:,:,:].flatten(), "rho" : rprops[2,:,:,:].flatten()})
#gridToVTK(ofilename, xc, yc, zc, pointData = {"pvel" : np.copy(rprops.transpose(2,1,0)).flatten()})
'''
'''
