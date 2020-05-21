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
print('VP[%d,%d,:]:\n' %(hnx,hny), props[0,hnx,hny,:])
print('VS[%d,%d,:]:\n' %(hnx,hny), props[1,hnx,hny,:])
print('Rho[%d,%d,:]:\n' %(hnx,hny),props[2,hnx,hny,:])

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

# QC'ing
'''
sub_props = props[:,::2,::2,::10]
sub_xc = xc[::2]
sub_yc = yc[::2]
sub_zc = zc[::10]
hnx = int(hnx/int(2))
hny = int(hny/int(2))
print('sub_props.shape:',sub_props.shape)
print('sub_VP[%d,%d,:]:\n' %(hnx,hny), sub_props[0,hnx,hny,:])
print('sub_VS[%d,%d,:]:\n' %(hnx,hny), sub_props[1,hnx,hny,:])
print('sub_Rho[%d,%d,:]:\n' %(hnx,hny),sub_props[2,hnx,hny,:])
print('xc_min,sub_xc_min = (%f,%f)' %(xc[0],sub_xc[0]))
print('xc_max,sub_xc_max = (%f,%f)' %(xc[-1],sub_xc[-1]))
print('yc_min,sub_yc_min = (%f,%f)' %(yc[0],sub_yc[0]))
print('yc_max,sub_yc_max = (%f,%f)' %(yc[-1],sub_yc[-1]))
print('zc_min,sub_zc_min = (%f,%f)' %(zc[0],sub_zc[0]))
print('zc_max,sub_zc_max = (%f,%f)' %(zc[-1],sub_zc[-1]))

assert False
'''


####################################################
## smooth model properties

print()
print('#######  Smoothing  ############################################')
print()

z_sig = 5*(50/dz) # tested at dz=20m and was good, so assume scale by that)
y_sig = z_sig*(dz/dy)
x_sig = z_sig*(dz/dx)

print('Smoothing in z-direction (sigma=%f)' %z_sig)

perc_10 = int(nx/10 + 0.5)
for ix in range(nx):
    for iy in range(ny):
        props[0,ix,iy,:] = gaussian_filter1d(props[0,ix,iy,:], z_sig) #VP
        props[1,ix,iy,:] = gaussian_filter1d(props[1,ix,iy,:], z_sig) #VS
        props[2,ix,iy,:] = gaussian_filter1d(props[2,ix,iy,:], z_sig) #Rho
    if (ix % perc_10) == 0:
        print('Currently %d percent finished smoothing in z-direction' % int((ix//perc_10)*10))
print('Currently 100 percent finished smoothing in z-direction')
print()

print('Smoothing in y-direction (sigma=%f)' %y_sig)
props = props.transpose(0,1,3,2)
print('props.shape:',props.shape)
perc_10 = int(nx/10 + 0.5)
for ix in range(nx):
    for iz in range(nz):
        props[0,ix,iz,:] = gaussian_filter1d(props[0,ix,iz,:], y_sig) #VP
        props[1,ix,iz,:] = gaussian_filter1d(props[1,ix,iz,:], y_sig) #VS
        props[2,ix,iz,:] = gaussian_filter1d(props[2,ix,iz,:], y_sig) #Rho
    if (ix % perc_10) == 0:
        print('Currently %d percent finished smoothing in y-direction' % int((ix//perc_10)*10))
print('Currently 100 percent finished smoothing in y-direction')
print()

print('Smoothing in x-direction (sigma=%f)' %x_sig)
props = props.transpose(0,2,3,1)
print('props.shape:',props.shape)
perc_10 = int(nz/10 + 0.5)
for iz in range(nz):
    for iy in range(ny):
        props[0,iz,iy,:] = gaussian_filter1d(props[0,iz,iy,:], x_sig) #VP
        props[1,iz,iy,:] = gaussian_filter1d(props[1,iz,iy,:], x_sig) #VS
        props[2,iz,iy,:] = gaussian_filter1d(props[2,iz,iy,:], x_sig) #Rho
    if (iz % perc_10) == 0:
        print('Currently %d percent finished smoothing in x-direction' % int((iz//perc_10)*10))
print('Currently 100 percent finished smoothing in x-direction')
print()
print('Finished all smoothing...')


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

'''
if len(xc)%2 != 0:
    print('xc.shape:',xc.shape)
    xc = xc[:-1]
    print('after xc.shape:',xc.shape)
    assert len(xc)%2 == 0
    props = props[:,:,:,:-1]

if len(yc)%2 != 0:
    print('yc.shape:',yc.shape)
    yc = yc[:-1]
    print('after yc.shape:',yc.shape)
    assert len(yc)%2 == 0
    props = props[:,:,:-1,:]

if len(zc)%2 != 0:
    print('zc.shape:',zc.shape)
    zc = zc[:-1]
    print('after zc.shape:',zc.shape)
    assert len(zc)%2 == 0
    props = props[:,:-1,:,:]
'''

print('subsample props.shape:\n',props.shape)
print('subsample zc.shape:\n',zc.shape)
print('subsample zc:\n',zc)

zdata[0] = zc[0]

xdata[1] *= 2.0
ydata[1] *= 2.0
zdata[1] *= 10.0

xdata[2] = len(xc)
ydata[2] = len(yc)
zdata[2] = len(zc)


####################################################
## Write VTK file with all three properties

#tp_shape = props.transpose(0,3,2,1).shape
ofilename = 'subsamp_smth_' + ifilename[:ifilename.rfind('.')]
print('Saving compressed subsurface model to disk at: %s\n' %(ofilename))
np.savez_compressed(ofilename + '.npz', props=props.transpose(0,3,2,1),xd=xdata,yd=ydata,zd=zdata)

# QC'ing
print('subsample props.shape:',props.transpose(0,3,2,1).shape)
print('xdata:',xdata)
print('ydata:',ydata)
print('zdata:',zdata)

'''
xdata[0] *= 0.001
xdata[1] *= 0.001
ydata[0] *= 0.001
ydata[1] *= 0.001
zdata[0] *= 0.001
zdata[1] *= 0.001
'''

'''
print('Writing Mesh Files:\n')
spec_data = {'props': props.transpose(0,3,2,1),'xd': xdata,'yd': ydata,'zd': zdata}
gmu = GMUtils()
gmu.writeSpecfem3DMesh('./MESH-default', spec_data)

print('#######  Writing VTK file  ####################################')
print('Writting file at: %s' %('./' + ofilename + '.vtr'))

# this will create and write to a structured grid VTK file
gridToVTK(ofilename, xc, yc, zc, pointData = \
        {"pvel" : props[0,:,:,:].flatten(),"svel" : props[1,:,:,:].flatten(), "rho" : props[2,:,:,:].flatten()})
'''
