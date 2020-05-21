################################################################################
# NAM Groningen 2017 Model: DeepNL/Utrecht University/Seismology
#
#   Thomas Cullison - t.a.cullison@uu.nl
################################################################################

import numpy as np
from NAMModel import NAMModel
from GMUtils import GMUtils


##############################################################
# Testing Driver (main)
mymod = NAMModel('./data/Vo_maps.txt','./data/horizons.txt')

mymod.readRawData()

mydz = 10
myMaxDepth = 6000
mydata = mymod.computeRecVol(mydz,myMaxDepth)

myprops = mydata[0]
my_xdata = mydata[1]
my_ydata = mydata[2]
my_zdata = mydata[3]

print('myprops.shape:',myprops.shape)
print('my_xdata:',my_xdata)
print('my_ydata:',my_ydata)
print('my_zdata:',my_zdata)

#xmin_clip = 0.3
#xmax_clip = 0.65
xmin_clip = 0.0
xmax_clip = 1.1
ix_min = int(xmin_clip*my_xdata[2] + 0.5)
if ix_min < 0: 
    ix_min = int(0)
ix_max = int(xmax_clip*my_xdata[2] + 1.5) # 0.5 (rounding) 1.0 (upto-bound)
if my_xdata[2] < ix_max:
    ix_max = int(my_xdata[2])
c_nx = int(ix_max - ix_min)
my_xdata[0] += ix_min*my_xdata[1]
my_xdata[2] = c_nx

#ymin_clip = 0.2
#ymax_clip = 0.9
ymin_clip = 0.0
ymax_clip = 1.0
iy_min = int(ymin_clip*my_ydata[2] + 0.5)
if iy_min < 0: 
    iy_min = int(0)
iy_max = int(ymax_clip*my_ydata[2] + 1.5) # 0.5 (rounding) 1.0 (upto-bound)
if my_ydata[2] < iy_max:
    iy_max = int(my_ydata[2])
c_ny = int(iy_max - iy_min)
my_ydata[0] += iy_min*my_ydata[1]
my_ydata[2] = c_ny

myprops = np.copy(myprops[:,ix_min:ix_max,iy_min:iy_max,:])

# QC'ing
print('clip myprops.shape:',myprops.shape)
print('clip my_xdata:',my_xdata)
print('clip my_ydata:',my_ydata)
print('clip my_zdata:',my_zdata)

'''
data = {'props': myprops,'xd': my_xdata,'yd': my_ydata,'zd': my_zdata}
gmu = GMUtils()
gmu.writeSpecfem3DMesh('./MESH-default', data)
'''

#ofilename = './rect_gron_model_clipped_z'
ofilename = './rect_gron_model_full_z'
print('Saving compressed subsurface model to disk at: %s%d_%s' %(ofilename,mydz,'props'))
np.savez_compressed(ofilename+str(int(mydz))+'_props.npz',props=myprops[:,:,:,:],xd=my_xdata,yd=my_ydata,zd=my_zdata)
