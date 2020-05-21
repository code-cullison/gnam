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
rzc = np.copy(zc[::-1])

rprops = np.copy(props[0,:,:,::-1])


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

rsurf = ndimage.rotate(np.copy(surf[::-1,:]), -degree)
xyc = np.transpose([np.tile(xc, len(yc)), np.repeat(yc, len(xc))])

xyc_xmin = np.min(xyc[:,0])
xyc_ymin = np.min(xyc[:,1])
print('xyc_xmin:',xyc_xmin)
print('xyc_ymin:',xyc_ymin)

xyc[:,0] -= xyc_xmin
xyc[:,1] -= xyc_ymin

for i in range(len(xyc[:,0])):
    xyc[i,:] = rmi.dot(xyc[i,:])

rx0 = np.min(xyc[:,0])
rx1 = np.max(xyc[:,0])
ry0 = np.min(xyc[:,1])
ry1 = np.max(xyc[:,1])

rxc = np.copy(xc) - xyc_xmin
ryc = np.copy(yc) - xyc_ymin

rextent = [ry1,rx0,ry0,rx1]
print('rextent:',rextent)

for i in range(len(xy[:,0])):
    xy[i,:] = rm.dot(xy[i,:])
xy[:,0] += mybbox[0] + 15000
xy[:,1] += mybbox[1] - 8000
#print('xy.shape:',xy.shape)
#print('xy[:,0]:\n',xy[:,0])
#print('nx*ny:\n',len(x)*len(y))


#xy[:,0] -= xyc_xmin
#xy[:,1] -= xyc_ymin

#for i in range(len(xy[:,0])):
    #xy[i,:] = rmi.dot(xy[i,:])
#print('xy.shape:',xy.shape)
#print('xy[:,0]:\n',xy[:,0])
#print('nx*ny:\n',len(x)*len(y))
#

rpoints = np.copy(mypoints)

rpoints[:,0] -= xyc_xmin
rpoints[:,1] -= xyc_ymin

for i in range(len(rpoints[:,0])):
    rpoints[i,:] = rmi.dot(rpoints[i,:])


print('mypoints.shape:',mypoints.shape)
print('rpoints.shape:',rpoints.shape)
rbbox = np.zeros_like(mybbox)
rbbox[0] = rmi.dot([mybbox[0],mybbox[1]])[0]
rbbox[1] = rmi.dot([mybbox[0],mybbox[1]])[1]
rbbox[2] = rmi.dot([mybbox[2],mybbox[3]])[0]
rbbox[3] = rmi.dot([mybbox[2],mybbox[3]])[1]
print('mybbox:',mybbox)
print('rbbox :',rbbox)

#print('x :',x)
#for i in range(len(x)):
    #x[i] = rm.dot([x[i],0])[0]
#
#for j in range(len(y)):
    #y[j] = rm.dot([0,y[j]])[1]
#
#x += mybbox[0] + 15000
#y += mybbox[1] - 8000



rgi = RegularGridInterpolator((xc,yc,rzc),rprops)
r_vp = np.zeros((len(x),len(y),len(rzc)),dtype=np.float32)
'''
for ix in range(len(x)):
    for iy in range(len(y)):
        for iz in range(len(rzc)):
            r_vp[ix,iy,iz] = rgi((x[ix],y[iy],rzc[iz]))

'''
ofilename = './rotated_rect_gron_model_full_z100'
#ofilename = './coord_rotated_hack_'
print('Saving compressed subsurface model to disk at: %s%d_%s' %(ofilename,100,'props'))
np.savez_compressed(ofilename+str(int(100))+'_props.npz',props=r_vp,xd=x,yd=y,zd=rzc)
#np.savez_compressed(ofilename+str(int(100))+'.npz',xd=x,yd=y,zd=zc)

'''
rc_surf = 2400*np.ones((len(y),len(x)))

        

rvl = rm.dot(vl)
rvb = rm.dot(vb)

tv = np.array([mybbox[0]+rvl[0],mybbox[1]+rvl[1]])
vtopr = np.array([tv[0]+rvb[0],tv[1]+rvb[1]])
rbb = np.array([mybbox[0],mybbox[1],vtopr[0],vtopr[1]])

rbx = np.array([mybbox[0],tv[0],vtopr[0],rvb[0]+mybbox[0],mybbox[0]]) + 15000
rby = np.array([mybbox[1],tv[1],vtopr[1],rvb[1]+mybbox[1],mybbox[1]]) - 8000

'''

'''
fig, ax = plt.subplots(1,figsize=(8,8))
#ax.scatter(x, y)
#ax.fill(x,y)
#_extent = [xc[0]/1000 , xc[-1]/1000, yc[0]/1000 , yc[-1]/1000]
#_extent = [xc[0], xc[-1], yc[0], yc[-1]]
#_extent = [x[0], x[-1], y[0], y[-1]]

#X, Y = np.meshgrid(x, y)

#Z = X * np.sinc(X ** 2 + Y ** 2)

#plt.pcolormesh(X, Y, Z, cmap = cm.gray)


##ax.fill(bx,by,c='blue')
#ax.plot(bx,by,c='black')
#ax.plot(rbx,rby,c='yellow')
#ax.imshow(surf[::-1,:], extent=_extent, cmap=plt.cm.jet)
#ax.imshow(rsurf, extent=rextent, cmap=plt.cm.jet)
#ax.imshow(rsurf, cmap=plt.cm.jet)
ax.scatter(xy[:,0],xy[:,1],s=1,c='yellow')
#ax.scatter(mypoints[:,0],mypoints[:,1],s=1,c='black')
ax.scatter(rpoints[:,0],rpoints[:,1],s=1,c='black')
#fig2, ax2 = plt.subplots(1,figsize=(8,8))
#ax2.imshow(surf, cmap=plt.cm.jet)
plt.show()

'''
print('STARTHERE')
for i in range(len(xy)):
    print('xy[%d,0] = %f' %(i,xy[i,0]))

xy_xmin = np.min(xy[:,0])
xy_ymin = np.min(xy[:,1])

xy[:,0] -= xy_xmin
xy[:,1] -= xy_ymin
print('STARTHERE')
for i in range(len(xy)):
    print('xy[%d,0] = %f' %(i,xy[i,0]))


print('STARTHERE')
for i in range(len(xy[:,0])):
    xy[i,:] = rmi.dot(xy[i,:])
    print('xy[%d,0] = %f' %(i,xy[i,0]))



