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
import scipy as sp
from scipy import ndimage
import matplotlib.pyplot as plt
import shapefile as sf
from scipy.interpolate import RegularGridInterpolator


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
zc = np.arange(0,-zmax-1,-dz).astype(np.float32)
rzc = np.copy(zc[::-1])


print('xc:\n',xc)
print('yc:\n',yc)
print('zc:\n',zc)


print('props.shape:',props.shape)
print()


t_props = props.transpose(0,3,2,1)
print('tprops.shape:', t_props.shape)
surf = t_props[0,0,:,:]
print('surf.shape:', surf.shape)

mysf = sf.Reader('FieldShapeFile/Groningen_field')
print('mysf:',mysf)
print('mysf.shapes():',mysf.shapes())
s = mysf.shape(0)
mypoints = np.asarray(s.points)
mybbox = s.bbox
print('mybbox:',mybbox)

bx = np.array([mybbox[0],mybbox[0],mybbox[2],mybbox[2],mybbox[0]])
by = np.array([mybbox[1],mybbox[3],mybbox[3],mybbox[1],mybbox[1]])

vl = np.array([0,0.99*(mybbox[3]-mybbox[1])])
dvl = ((0.99*(mybbox[3]-mybbox[1]))**2)**0.5
nvl = dvl//100 + 1
y = np.arange(nvl)*100
print('nvl:',nvl)
print('y :',y)
vb = np.array([0.9*(mybbox[2]-mybbox[0]),0])
dvb = ((0.9*(mybbox[2]-mybbox[0]))**2)**0.5
nvb = dvb//100 + 1
x = np.arange(nvb)*100
print('nvb:',nvb)


xy = np.transpose([np.tile(x, len(y)), np.repeat(y, len(x))])
print('xy.shape:',xy.shape)
print('xy:\n',xy)

degree = 30
theta = degree*np.pi/180
rm = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
rmi = np.array([[np.cos(-theta),-np.sin(-theta)],[np.sin(-theta),np.cos(-theta)]])


for i in range(len(xy[:,0])):
    xy[i,:] = rm.dot(xy[i,:])
xy[:,0] += mybbox[0] + 15000
xy[:,1] += mybbox[1] - 8000

xy_xmin = 100*(np.min(xy[:,0])//100)
xy_xmax = 100*(np.max(xy[:,0])//100 +1)
xy_ymin = 100*(np.min(xy[:,1])//100)
xy_ymax = 100*(np.max(xy[:,1])//100 +1)

rbx = np.array([xy_xmin,xy_xmin,xy_xmax,xy_xmax,xy_xmin])
rby = np.array([xy_ymin,xy_ymax,xy_ymax,xy_ymin,xy_ymin])


print('y:\n',y)
X, Y = np.meshgrid(xc, yc)
Z = surf

fig, ax = plt.subplots(1,figsize=(8,8))

##ax.fill(bx,by,c='blue')
#ax.plot(bx,by,c='black')
ax.pcolormesh(X, Y, Z, cmap = plt.cm.jet)
ax.scatter(xy[:,0],xy[:,1],s=1,c='yellow')
ax.plot(rbx,rby,c='green')
#ax.scatter(rbx,rby,c='green',s=5)
ax.scatter(mypoints[:,0],mypoints[:,1],s=1,c='black')


o_xc = np.copy(xc) - xc[0]
o_yc = np.copy(yc) - yc[0]

o_xy = np.copy(xy)
o_xy[:,0] -= xc[0]
o_xy[:,1] -= yc[0]

o_mypoints = np.copy(mypoints)
o_mypoints[:,0] -= xc[0]
o_mypoints[:,1] -= yc[0]

o_X, o_Y = np.meshgrid(o_xc, o_yc)
o_Z = surf

fig2, ax2 = plt.subplots(1,figsize=(8,8))
ax2.pcolormesh(o_X, o_Y, o_Z, cmap = plt.cm.jet)
ax2.scatter(o_xy[:,0],o_xy[:,1],s=1,c='yellow')
ax2.scatter(o_mypoints[:,0],o_mypoints[:,1],s=1,c='black')

oo_xy = np.copy(o_xy)
i_oo = np.argmin(oo_xy[:,1])
oo_xy[:,0] -= o_xy[i_oo,0]
oo_xy[:,1] -= o_xy[i_oo,1]


fig3, ax3 = plt.subplots(1,figsize=(8,8))
ax3.pcolormesh(o_X, o_Y, o_Z, cmap = plt.cm.jet)
ax3.scatter(oo_xy[:,0],oo_xy[:,1],s=1,c='yellow')
ax3.scatter(o_mypoints[:,0],o_mypoints[:,1],s=1,c='black')


for i in range(len(oo_xy[:,0])):
    oo_xy[i,:] = rmi.dot(oo_xy[i,:])

oo_xy = oo_xy.astype(np.float32)

oo_xy[oo_xy < 0] = 0  
oo_xy = 100*(oo_xy//100)

fig4, ax4 = plt.subplots(1,figsize=(8,8))
ax4.pcolormesh(o_X, o_Y, o_Z, cmap = plt.cm.jet)
ax4.scatter(oo_xy[:,0],oo_xy[:,1],s=1,c='yellow')
ax4.scatter(o_mypoints[:,0],o_mypoints[:,1],s=1,c='black')

plt.show()

