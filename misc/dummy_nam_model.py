################################################################################
# NAM Groningen 2017 Model: DeepNL/Utrecht University/Seismology
#
#   Thomas Cullison - t.a.cullison@uu.nl
################################################################################

import numpy as np

nx = 4*60
ny = 4*60
nz = 60


my_xdata = np.zeros(3).astype(np.float32)
my_ydata = np.zeros(3).astype(np.float32)
my_zdata = np.zeros(3).astype(np.float32)

my_xdata[0] = 1.0
my_ydata[0] = 1.0
my_zdata[0] = 1.0

my_xdata[1] = 1.0
my_ydata[1] = 1.0
my_zdata[1] = 1.0
mydz = int(my_zdata[1])

my_xdata[2] = nx
my_ydata[2] = ny
my_zdata[2] = nz

zvp = np.arange((nz),dtype=np.short) + 3000
zvs = np.arange((nz),dtype=np.short) + 1500
zrh = 2000 - np.arange(nz,dtype=np.short)

myprops = np.ones((3,nx,ny,nz)).astype(np.short)
myprops[0,:,:,:] = zvp
myprops[1,:,:,:] = zvs
myprops[2,:,:,:] = zrh

print('props.shape:',myprops.shape)

ofilename = './dummy_model_z'
print('Saving compressed subsurface model to disk at: %s%d_%s' %(ofilename,mydz,'props'))
np.savez_compressed(ofilename+str(int(mydz))+'_props.npz',props=myprops[:,:,:,:],xd=my_xdata,yd=my_ydata,zd=my_zdata)
