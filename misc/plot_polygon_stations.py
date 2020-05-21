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
import numpy as np
import pandas as pd
import scipy as sp
from scipy import ndimage
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import shapefile as sf
from scipy.interpolate import RegularGridInterpolator
from shapely.geometry import Point, Polygon

nsize = 10000
randpts = 1500*np.random.rand(nsize,2)
ltup_rpts = list(map(Point, randpts))
#print('ltup_rpts:\n',*ltup_rpts)

acoords = np.array([[500.0, 500.0], [500.0, 1000.0], [1000.0, 1000.0], [1000.0, 500.0]])
boxcoords = list(map(tuple, acoords))
print('boxcoords:',boxcoords)
#print(tuple(map(tuple, arr)))

#boxcoords = [(500.0, 500.0), (500.0, 1000.0), (1000.0, 1000.0), (1000.0, 500.0)]
poly = Polygon(boxcoords)
print('poly:',poly)
tpnt = Point((750,750))
print('test point:',tpnt)
print('tpnt in poly:',poly.contains(tpnt))
#print('Contains:\n',poly.contains(*ltup_rpts)) #FIXME: can't fix, not build this way


is_iside = np.zeros((nsize),dtype=bool)
is_oside = np.ones((nsize),dtype=bool)
for i in range(nsize):
    if poly.contains(ltup_rpts[i]):
        #print('ith pnt:', ltup_rpts[i])
        #print('is_contained:', poly.contains(ltup_rpts[i]))
        is_iside[i] = True
        #print('is_iside[%d]:' %(i),is_iside[i])
        is_oside[i] = False

print('is_iside:\n', is_iside)

i_randpts = randpts[is_iside]
print('i_randpts:\n', i_randpts)
o_randpts = randpts[is_oside]
print('o_randpts:\n', o_randpts)

fig, ax = plt.subplots(1,figsize=(8,8))

ax.fill(acoords[:,0],acoords[:,1],c='yellow',zorder=0) ## bounding box in rotated coord for rotated coords
ax.scatter(i_randpts[:,0],i_randpts[:,1],s=10,c='green',zorder=1)
ax.scatter(o_randpts[:,0],o_randpts[:,1],s=10,c='blue',zorder=2)
#ax.scatter(randpts[:,0],randpts[:,1],s=10,c='black',zorder=1)

degree = 30
theta = degree*np.pi/180
rm = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])

rot_coords = np.zeros_like(acoords)
for i in range(len(acoords[:,0])):
    rot_coords[i,:] = rm.dot(acoords[i,:])

rboxcoords = list(map(tuple, rot_coords))
print('boxcoords:',rboxcoords)
rpoly = Polygon(rboxcoords)

ris_iside = np.zeros((nsize),dtype=bool)
ris_oside = np.ones((nsize),dtype=bool)
for i in range(nsize):
    if rpoly.contains(ltup_rpts[i]):
        #print('ith pnt:', ltup_rpts[i])
        #print('is_contained:', rpoly.contains(ltup_rpts[i]))
        ris_iside[i] = True
        #print('ris_iside[%d]:' %(i),ris_iside[i])
        ris_oside[i] = False

print('ris_iside:\n', ris_iside)

ri_randpts = randpts[ris_iside]
print('ri_randpts:\n', ri_randpts)
ro_randpts = randpts[ris_oside]
print('o_randpts:\n', ro_randpts)

fig1, ax1 = plt.subplots(1,figsize=(8,8))
ax1.fill(rot_coords[:,0],rot_coords[:,1],c='yellow',zorder=0) ## bounding box in rotated coord for rotated coords
ax1.scatter(ri_randpts[:,0],ri_randpts[:,1],s=10,c='green',zorder=1)
ax1.scatter(ro_randpts[:,0],ro_randpts[:,1],s=10,c='blue',zorder=2)

plt.show()

