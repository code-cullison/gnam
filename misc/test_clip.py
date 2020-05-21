################################################################################
# NAM Groningen 2017 Model: DeepNL/Utrecht University/Seismology
#
#   Thomas Cullison - t.a.cullison@uu.nl
################################################################################

import numpy as np

myprops = np.ones((3, 1450, 1198, 601))
my_xdata = np.array([2.074625e+05, 5.000000e+01, 1.450000e+03])
my_ydata = np.array([5.559625e+05, 5.000000e+01, 1.198000e+03])
my_zdata = np.array([  0.,  10., 601.])

print('myprops.shape:',myprops.shape)
print('my_xdata:',my_xdata)
print('my_ydata:',my_ydata)
print('my_zdata:',my_zdata)

xmin_clip = 0.3
xmax_clip = 0.65
ix_min = int(xmin_clip*my_xdata[2] + 0.5)
if ix_min < 0: 
    ix_min = int(0)
ix_max = int(xmax_clip*my_xdata[2] + 1.5)
if my_xdata[2] < ix_max:
    ix_max = int(my_xdata[2])
c_nx = int(ix_max - ix_min + 1)
my_xdata[0] += ix_min*my_xdata[1]
my_xdata[2] = c_nx

ymin_clip = 0.2
ymax_clip = 1.0
iy_min = int(ymin_clip*my_ydata[2] + 0.5)
if iy_min < 0: 
    iy_min = int(0)
iy_max = int(ymax_clip*my_ydata[2] + 1.5)
if my_ydata[2] < iy_max:
    iy_max = int(my_ydata[2])
c_ny = int(iy_max - iy_min + 1)
my_ydata[0] += iy_min*my_ydata[1]
my_ydata[2] = c_ny

myprops = np.copy(myprops[:,ix_min:ix_max,iy_min:iy_max,:])

print('clip myprops.shape:',myprops.shape)
print('clip my_xdata:',my_xdata)
print('clip my_ydata:',my_ydata)
print('clip my_zdata:',my_zdata)
