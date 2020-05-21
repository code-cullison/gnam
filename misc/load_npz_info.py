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


####################################################
## Load and decopress data 

assert len(argv) == 2

ifilename = argv[1]

data = np.load(ifilename)
props = data['props']


# QC'ing
'''
print('props.shape:',props.shape)
tp_shape = props.transpose(0,3,2,1).shape
print('tp_shape:',tp_shape)
sm_shape = props.transpose(0,1,3,2).transpose(0,2,3,1).shape
print('sm_shape:',sm_shape)
assert tp_shape == sm_shape
assert False
'''

xdata = data['xd']
ydata = data['yd']
zdata = data['zd']

print('xd:\n',xdata)
print('yd:\n',ydata)
print('zd:\n',zdata)


## display center z-col for QC'ing

nx = xdata[2]
hnx = int(nx/2 + 0.5)
hnx = hnx + int(hnx%2)
ny = ydata[2]
hny = int(ny/2 + 0.5)
hny = hny + int(hny%2)
print('props.shape:',props.shape)
#print('VP[%d,%d,:]:\n' %(hnx,hny), props[0,hnx,hny,:])
#print('VS[%d,%d,:]:\n' %(hnx,hny), props[1,hnx,hny,:])
#print('Rho[%d,%d,:]:\n' %(hnx,hny),props[2,hnx,hny,:])

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
zc = np.arange(zmin,-zmax-1,-dz).astype(np.float32)


print('xc:\n',xc)
print('yc:\n',yc)
print('zc:\n',zc)


print('props.shape:',props.shape)
print()

print('xd:\n',xdata)
print('yd:\n',ydata)
print('zd:\n',zdata)
print()
