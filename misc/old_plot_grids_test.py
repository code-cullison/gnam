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
zmax = (-zmin) + (nz-1)*dz
print('zmax:', zmax)

xc = np.arange(xmin,xmax+1,dx)
yc = np.arange(ymin,ymax+1,dy)
#zc = np.arange(0,-zmax-1,-dz).astype(np.float32)
zc = np.arange(zmin,-zmax-1,-dz).astype(np.float32)
rzc = np.copy(zc[::-1])

#rprops = np.copy(props[0,:,:,::-1])
rprops = np.copy(props[:,:,:,::-1])

print('xc.shape:\n',xc.shape)
print('yc.shape:\n',yc.shape)
print('zc.shape:\n',zc.shape)
print('rzc.shape:\n',rzc.shape)

print('xc:\n',xc)
print('yc:\n',yc)
print('zc:\n',zc)
print('rzc:\n',rzc)


print('props.shape:',props.shape)
print()

print('xd:\n',xdata)
print('yd:\n',ydata)
print('zd:\n',zdata)
print()

t_props = props.transpose(0,3,2,1)
print('tprops.shape:', t_props.shape)
surf = t_props[0,20,:,:]
print('surf.shape:', surf.shape)
del props

mysf = sf.Reader('FieldShapeFile/Groningen_field')
print('mysf:',mysf)
print('mysf.shapes():',mysf.shapes())
s = mysf.shape(0)
mypoints = np.asarray(s.points)
mybbox = s.bbox
print('mybbox:',mybbox)

bx = np.array([mybbox[0],mybbox[0],mybbox[2],mybbox[2],mybbox[0]])
by = np.array([mybbox[1],mybbox[3],mybbox[3],mybbox[1],mybbox[1]])

vl = np.array([0,0.87*(mybbox[3]-mybbox[1])])
dvl = ((0.87*(mybbox[3]-mybbox[1]))**2)**0.5
nvl = dvl//100 + 1
y = np.arange(nvl)*100
print('nvl:',nvl)
print('y :',y)
vb = np.array([0.85*(mybbox[2]-mybbox[0]),0])
dvb = ((0.85*(mybbox[2]-mybbox[0]))**2)**0.5
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

xy_xmin = np.min(x)
xy_xmax = np.max(x)
xy_ymin = np.min(y)
xy_ymax = np.max(y)

rot_bx = np.array([xy_xmin,xy_xmin,xy_xmax,xy_xmax,xy_xmin])
rot_by = np.array([xy_ymin,xy_ymax,xy_ymax,xy_ymin,xy_ymin])
rbbox_x = np.zeros_like(rot_bx)
rbbox_y = np.zeros_like(rot_by)

rbbox_x[0] = rm.dot(np.array([rot_bx[0],rot_by[0]]))[0]
rbbox_y[0] = rm.dot(np.array([rot_bx[0],rot_by[0]]))[1]
rbbox_x[1] = rm.dot(np.array([rot_bx[1],rot_by[1]]))[0]
rbbox_y[1] = rm.dot(np.array([rot_bx[1],rot_by[1]]))[1]
rbbox_x[2] = rm.dot(np.array([rot_bx[2],rot_by[2]]))[0]
rbbox_y[2] = rm.dot(np.array([rot_bx[2],rot_by[2]]))[1]
rbbox_x[3] = rm.dot(np.array([rot_bx[3],rot_by[3]]))[0]
rbbox_y[3] = rm.dot(np.array([rot_bx[3],rot_by[3]]))[1]
rbbox_x[4] = rbbox_x[0]
rbbox_y[4] = rbbox_y[0]

for i in range(len(xy[:,0])):
    xy[i,:] = rm.dot(xy[i,:])

xy[:,0] += mybbox[0] + 12800
xy[:,1] += mybbox[1] - 3500
rbbox_x += mybbox[0] + 12800
rbbox_y += mybbox[1] - 3500

vp_min = np.min(surf)
vp_max = np.max(surf)
mynorm = Normalize(vp_min,vp_max)

slice_surf = np.zeros((len(x)*len(y)))
rgi_surf = RegularGridInterpolator((yc,xc),surf)
nxy = len(xy[:,0])
for ixy in range(nxy):
    slice_surf[ixy] = rgi_surf((xy[ixy,1],xy[ixy,0]))

vp_min_s = np.min(slice_surf)
vp_max_s = np.max(slice_surf)
mynorm_slice = Normalize(vp_min_s,vp_max_s)
'''

slice_props = np.zeros((3,len(x)*len(y)*len(rzc)))
print('slice_props.shape', slice_props.shape)
print('rprops.shape', rprops.shape)
rgi_vp = RegularGridInterpolator((xc,yc,rzc),rprops[0])
rgi_vs = RegularGridInterpolator((xc,yc,rzc),rprops[1])
rgi_rho = RegularGridInterpolator((xc,yc,rzc),rprops[2])
#r_vp = np.zeros((len(x)*len(y)*len(rzc)),dtype=np.float32)
for iz in range(len(rzc)):
    z = rzc[iz]
    for ixy in range(nxy):
        #r_vp[ixy + nxy*iz] = rgi((xy[ixy,0],xy[ixy,1],z))
        slice_props[0,ixy + nxy*iz] = rgi_vp((xy[ixy,0],xy[ixy,1],z))
        slice_props[1,ixy + nxy*iz] = rgi_vs((xy[ixy,0],xy[ixy,1],z))
        slice_props[2,ixy + nxy*iz] = rgi_rho((xy[ixy,0],xy[ixy,1],z))

ofilename = './rotated_rect_gron_model_full_z'
print('Saving compressed subsurface model to disk at: %s%d_%s' %(ofilename,100,'props'))
np.savez_compressed(ofilename+str(int(100))+'_props.npz',props=slice_props,xd=x,yd=y,zd=rzc)
'''
'''
'''

df = pd.io.parsers.read_csv("Gloc.csv",sep=",",index_col=0)
print(df)
print()

df = df.drop(columns=['Latitude [deg]', 'Longitude [deg]', 'Surface elevation [m]'])
print(df)
print()

df = df[df['Depth below surface [deg]'] == 200]
print(df)
print()

df = df.drop(columns=['Depth below surface [deg]'])
print(df)
print()

xcoords = df[['Rijksdriehoek X [m]']].to_numpy().astype(np.float32)
xcoords = xcoords.reshape(xcoords.shape[0])
ycoords = df[['Rijksdriehoek Y [m]']].to_numpy().astype(np.float32)
ycoords = ycoords.reshape(ycoords.shape[0])


xy_xmin = 100*(np.min(xy[:,0])//100)
xy_xmax = 100*(np.max(xy[:,0])//100 +1)
xy_ymin = 100*(np.min(xy[:,1])//100)
xy_ymax = 100*(np.max(xy[:,1])//100 +1)

#rbx = np.array([xy_xmin,xy_xmin,xy_xmax,xy_xmax,xy_xmin])
#rby = np.array([xy_ymin,xy_xmax,xy_ymax,xy_ymin,xy_ymin])
rbx = np.array([xy_xmin,xy_xmin,xy_xmax,xy_xmax,xy_xmin])
rby = np.array([xy_ymin,xy_ymax,xy_ymax,xy_ymin,xy_ymin])

print('rbx:',rbx)
print('rby:',rby)

print('x:\n',x)
print('y:\n',y)
X, Y = np.meshgrid(xc, yc)
Z = surf

xyc = np.transpose([np.tile(xc, len(yc)), np.repeat(yc, len(xc))])

fig0, ax0 = plt.subplots(1,figsize=(8,8))

#ax0.pcolormesh(X, Y, Z, cmap=plt.cm.jet, norm=mynorm_slice, )
#ax0.plot(rbx,rby,c='black') ## bounding box in default coord for rotated coords
ax0.fill(rbbox_x,rbbox_y,c='white',zorder=1) ## bounding box in rotated coord for rotated coords
ax0.plot(rbbox_x,rbbox_y,c='black',zorder=4) ## bounding box in rotated coord for rotated coords
#ax0.scatter(mypoints[:,0],mypoints[:,1],s=1,c='green')
ax0.scatter(mypoints[:,0],mypoints[:,1],s=1,c='black',zorder=3)
ax0.scatter(xyc[:,0],xyc[:,1],s=1,c=surf.flatten(),cmap=plt.cm.jet,norm=mynorm_slice,zorder=0)
#ax0.scatter(xyc[:,0],xyc[:,1],s=1,c=surf.flatten(),cmap=plt.cm.jet,norm=mynorm,zorder=0)
ax0.scatter(xy[:,0],xy[:,1],s=1,c=slice_surf,cmap=plt.cm.jet,norm=mynorm_slice,zorder=2)
ax0.scatter(xcoords,ycoords,s=50,c='black',marker='v',zorder=5)
ax0.set_title('myFig 0')
ax0.set_title('Scatter (both coord systems)')

'''
fig, ax = plt.subplots(1,figsize=(8,8))

#ax.pcolormesh(X, Y, Z, cmap=plt.cm.jet, norm=mynorm_slice, )
ax.scatter(xyc[:,0],xyc[:,1],s=1,c=surf.flatten(),cmap=plt.cm.jet,norm=mynorm_slice,zorder=0)
ax.fill(rbbox_x,rbbox_y,c='white',zorder=1) ## bounding box in rotated coord for rotated coords
#ax.plot(rbx,rby,c='black') ## bounding box in default coord for rotated coords
#ax.plot(rbbox_x,rbbox_y,c='black') ## bounding box in rotated coord for rotated coords
ax.scatter(xy[:,0],xy[:,1],s=1,c=slice_surf,cmap=plt.cm.jet,norm=mynorm_slice,zorder=2)
ax.scatter(mypoints[:,0],mypoints[:,1],s=1,c='black',zorder=3)
#ax.scatter(mypoints[:,0],mypoints[:,1],s=1,c='green')
#ax.scatter(xcoords,ycoords,s=50,c='black',marker='v')
#ax.scatter(rbx,rby,c='green',s=5)
ax.set_title('Scatter (either coord systems)')

fig5, ax5 = plt.subplots(1,figsize=(8,8))

ax5.pcolormesh(X, Y, Z, cmap=plt.cm.jet, norm=mynorm, )
ax5.scatter(xy[:,0],xy[:,1],s=1,c=slice_surf,cmap=plt.cm.jet,norm=mynorm)
ax5.scatter(mypoints[:,0],mypoints[:,1],s=1,c='green')
ax5.scatter(xcoords,ycoords,s=50,c='black',marker='v')
ax5.set_title('myFig 2')

fig6, ax6 = plt.subplots(1,figsize=(8,8))

ax6.pcolormesh(X, Y, Z, cmap=plt.cm.jet, norm=mynorm, )
ax6.scatter(xy[:,0],xy[:,1],s=200,c=slice_surf,cmap=plt.cm.jet,norm=mynorm_slice)
ax6.scatter(mypoints[:,0],mypoints[:,1],s=1,c='green')
ax6.scatter(xcoords,ycoords,s=50,c='black',marker='v')
ax6.set_title('myFig 3')


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

'''
plt.show()


'''
print('oo_xy.dtype:',oo_xy.dtype)

print('STARTHEAR')
print(oo_xy.dtype)
for i in range(len(oo_xy[:,0])):
    print('oo_xy[%d,:] = ' %(i), oo_xy[i,:])


print('STARTHEAR')
print('x:\n',x)
print('y:\n',y)
'''
