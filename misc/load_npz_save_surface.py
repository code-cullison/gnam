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
import matplotlib.pyplot as plt
import shapefile as sf


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
zc = np.arange(0,-zmax-1,-dz).astype(np.float32)


print('xc:\n',xc)
print('yc:\n',yc)
print('zc:\n',zc)


print('props.shape:',props.shape)
print()

print('xd:\n',xdata)
print('yd:\n',ydata)
print('zd:\n',zdata)
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
vb = np.array([0.9*(mybbox[2]-mybbox[0]),0])

degree = 30
theta = degree*np.pi/180
rm = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])

rvl = rm.dot(vl)
rvb = rm.dot(vb)

tv = np.array([mybbox[0]+rvl[0],mybbox[1]+rvl[1]])
vtopr = np.array([tv[0]+rvb[0],tv[1]+rvb[1]])
rbb = np.array([mybbox[0],mybbox[1],vtopr[0],vtopr[1]])

rbx = np.array([mybbox[0],tv[0],vtopr[0],rvb[0]+mybbox[0],mybbox[0]]) + 15000
rby = np.array([mybbox[1],tv[1],vtopr[1],rvb[1]+mybbox[1],mybbox[1]]) - 8000


fig, ax = plt.subplots(1,figsize=(8,8))
#ax.scatter(x, y)
#ax.fill(x,y)
#_extent = [xc[0]/1000 , xc[-1]/1000, yc[0]/1000 , yc[-1]/1000]
_extent = [xc[0], xc[-1], yc[0], yc[-1]]
#ax.fill(bx,by,c='blue')
ax.plot(bx,by,c='black')
ax.plot(rbx,rby,c='yellow')
ax.imshow(surf[::-1,:], extent=_extent, cmap=plt.cm.jet)
ax.scatter(mypoints[:,0],mypoints[:,1],s=1,c='green')
plt.show()

