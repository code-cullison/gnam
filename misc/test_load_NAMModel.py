################################################################################
# NAM Groningen 2017 Model: DeepNL/Utrecht University/Seismology
#
#   Purpose: To create VTK files of the Groning Subsurface Volume
#
#   Thomas Cullison - t.a.cullison@uu.nl
################################################################################

from sys import argv
import pandas as pd
import numpy as np
from pyevtk.hl import gridToVTK


####################################################
## Load and decopress data 

assert len(argv) == 2

ifilename = argv[1]

data = np.load(ifilename)
props = data['props']

xdata = data['xd']
ydata = data['yd']
zdata = data['zd']

print('xd:\n',xdata)
print('yd:\n',ydata)
print('zd:\n',zdata)


####################################################
## display center z-col for QC'ing

nx = xdata[2]
hnx = int(nx/2 + 0.5)
ny = ydata[2]
hny = int(ny/2 + 0.5)
print('props.shape:',props.shape)
print('VP[%d,%d,:]:\n' %(hnx,hny), props[0,hnx,hnx,:])
print('VS[%d,%d,:]:\n' %(hnx,hny), props[1,hnx,hnx,:])
print('Rho[%d,%d,:]:\n' %(hnx,hny),props[2,hnx,hnx,:])


####################################################
## compute x, y, z coordinates

xmin = xdata[0]
dx   = xdata[1]
nx   = xdata[2]
xmax = xmin + (nx-1)*dx

ymin = ydata[0]
dy   = ydata[1]
ny   = ydata[2]
ymax = ymin + (ny-1)*dy

zmin = zdata[0]
dz   = zdata[1]
nz   = zdata[2]
zmax = zmin + (nz-1)*dz

xc = np.arange(xmin,xmax+1,dx)
yc = np.arange(ymin,ymax+1,dy)
zc = np.arange(0,-zmax-1,-dz).astype(np.float32)


####################################################
## Write VTK file with all three properties

print('props.shape:',props.shape)
t_props = props.transpose(0,3,2,1)
print('t_props.shape:',t_props.shape)  # QC'ing

ofilename = ifilename[:ifilename.rfind('.')]
print('Writting file at: %s' %('./' + ofilename + '.vtr'))

# this will create and write to a structured grid VTK file
gridToVTK(ofilename, xc, yc, zc, pointData = \
        {"pvel" : t_props[0,:,:,:].flatten(),"svel" : t_props[1,:,:,:].flatten(), "rho" : t_props[2,:,:,:].flatten()})
