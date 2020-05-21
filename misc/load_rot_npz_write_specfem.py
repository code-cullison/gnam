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
from GMUtils import GMUtils


####################################################
## Load and decopress data 

assert len(argv) == 2

ifilename = argv[1]

data = np.load(ifilename)
print('data:',*data)



xc = data['xd']
yc = data['yd']
zc = np.copy(-1*data['zd'][::-1])

props = np.copy(data['props'].reshape((3,len(zc),len(yc),len(xc)))[:,::-1,:,:])
print('props.shape:',props.shape)
props = props.transpose(0,3,2,1)

print('xc:\n',xc)
print('yc:\n',yc)
print('zc:\n',zc)

xdata = np.zeros((3),dtype=np.float32)
ydata = np.zeros((3),dtype=np.float32)
zdata = np.zeros((3),dtype=np.float32)

xdata[0] = xc[0]
xdata[1] = xc[1] - xc[0]
xdata[2] = len(xc)

ydata[0] = yc[0]
ydata[1] = yc[1] - yc[0]
ydata[2] = len(yc)

zdata[0] = -zc[0]
zdata[1] = zc[1] - zc[0]
zdata[2] = len(zc)

print('xd:\n',xdata)
print('yd:\n',ydata)
print('zd:\n',zdata)


'''
'''
spec_data = {'props': props,'xd': xdata,'yd': ydata,'zd': zdata}
gmu = GMUtils()
gmu.writeSpecfem3DMesh('./MESH-default', spec_data)
