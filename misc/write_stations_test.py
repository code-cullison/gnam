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
#xy[:,0] += mybbox[0] + 13000
xy[:,1] += mybbox[1] - 3500
rbbox_x += mybbox[0] + 12800
#rbbox_x += mybbox[0] + 13000
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
stname = list(df.index)
print('list of rows:',stname)

xcoords = df[['Rijksdriehoek X [m]']].to_numpy().astype(np.float32)
xcoords = xcoords.reshape(xcoords.shape[0])
ycoords = df[['Rijksdriehoek Y [m]']].to_numpy().astype(np.float32)
ycoords = ycoords.reshape(ycoords.shape[0])

print('len(xcoords):',len(xcoords))
print('len(ycoords):',len(ycoords))
print('len(stname):',len(stname))

print('xcoords[::13]:',xcoords[::13])
print('ycoords[::13]:',ycoords[::13])
xycoords = np.append(xcoords,ycoords).reshape((2,len(xcoords))).T
print('xycoords:\n',xycoords[::13,:])


acoords = np.array([[rbbox_x[0],rbbox_y[0]],[rbbox_x[1],rbbox_y[1]],[rbbox_x[2],rbbox_y[2]],[rbbox_x[3],rbbox_y[3]]])
boxcoords = list(map(tuple, acoords))
print('boxcoords:',boxcoords)

poly = Polygon(boxcoords)
print('poly:',poly)

xyPoints = list(map(Point, xycoords))
is_iside = np.ones((len(xycoords[:,0])),dtype=bool)
is_oside = np.zeros((len(xycoords[:,0])),dtype=bool)
for i in range(len(xyPoints)):
    if not poly.contains(xyPoints[i]):
        is_iside[i] = False
        is_oside[i] = True

print('is_iside:\n', is_iside)

i_stations = xycoords[is_iside]
o_stations = xycoords[is_oside]

xyc = np.transpose([np.tile(xc, len(yc)), np.repeat(yc, len(xc))])

'''
oo_xy = np.copy(xy)
i_oo = np.argmin(xy[:,1])
oo_xy[:,0] -= xy[i_oo,0]
oo_xy[:,1] -= xy[i_oo,1]

i_stations[:,0] -= xy[i_oo,0]
i_stations[:,1] -= xy[i_oo,1]

o_stations[:,0] -= xy[i_oo,0]
o_stations[:,1] -= xy[i_oo,1]

rbbox_x -= xy[i_oo,0]
rbbox_y -= xy[i_oo,1]

mypoints[:,0] -= xy[i_oo,0] 
mypoints[:,1] -= xy[i_oo,1]

for i in range(len(mypoints)):
    mypoints[i] = rmi.dot(mypoints[i])

xyc[:,0] -= xy[i_oo,0]
xyc[:,1] -= xy[i_oo,1]
for i in range(len(xyc[:,0])):
    xyc[i] = rmi.dot(xyc[i])


xy = oo_xy
xy = oo_xy

tbbx = np.copy(rbbox_x)
tbby = np.copy(rbbox_y)

rbbox_x[0] = rmi.dot(np.array([tbbx[0],tbby[0]]))[0]
rbbox_y[0] = rmi.dot(np.array([tbbx[0],tbby[0]]))[1]
rbbox_x[1] = rmi.dot(np.array([tbbx[1],tbby[1]]))[0]
rbbox_y[1] = rmi.dot(np.array([tbbx[1],tbby[1]]))[1]
rbbox_x[2] = rmi.dot(np.array([tbbx[2],tbby[2]]))[0]
rbbox_y[2] = rmi.dot(np.array([tbbx[2],tbby[2]]))[1]
rbbox_x[3] = rmi.dot(np.array([tbbx[3],tbby[3]]))[0]
rbbox_y[3] = rmi.dot(np.array([tbbx[3],tbby[3]]))[1]
rbbox_x[4] = rbbox_x[0]
rbbox_y[4] = rbbox_y[0]

for i in range(len(i_stations[:,0])):
    i_stations[i] = rmi.dot(i_stations[i])

for i in range(len(o_stations[:,0])):
    o_stations[i] = rmi.dot(o_stations[i])


for i in range(len(xy[:,0])):
    xy[i,:] = rmi.dot(xy[i,:])

xy = xy.astype(np.float32)

xy[xy < 0] = 0  
xy = 100*(xy//100)
'''


rdic = dict(zip(stname, i_stations))
print('rdic:\n',rdic)
print('len(rdic):\n',len(rdic))

str_stations = []
for i in range(len(rdic)):
    stat = stname[i]
    str_stations.append('%s %s %.2f %.2f %.2f %.2f\n' %(stat,'NAM',rdic[stat][1],rdic[stat][0],0,0))

f = open('./STATIONS_test', 'w')
f.writelines(str_stations)
f.close()



print('x:\n',x)
print('y:\n',y)
X, Y = np.meshgrid(xc, yc)
Z = surf


fig0, ax0 = plt.subplots(1,figsize=(8,8))


ax0.fill(rbbox_x,rbbox_y,c='white',zorder=1) ## bounding box in rotated coord for rotated coords
ax0.plot(rbbox_x,rbbox_y,c='black',zorder=4) ## bounding box in rotated coord for rotated coords
#ax0.plot(rbbox_x-oo_xy[i_oo,0],rbbox_y-oo_xy[i_oo,1],c='black',zorder=4) ## bounding box in rotated coord for rotated coords
ax0.scatter(mypoints[:,0],mypoints[:,1],s=1,c='black',zorder=3)
ax0.scatter(xyc[:,0],xyc[:,1],s=1,c=surf.flatten(),cmap=plt.cm.jet,norm=mynorm_slice,zorder=0)
ax0.scatter(xy[:,0],xy[:,1],s=1,c=slice_surf,cmap=plt.cm.jet,norm=mynorm_slice,zorder=2)
#ax0.scatter(xy[i_oo,0],xy[i_oo,1],s=100,c='black',marker='*')
#ax0.scatter(xy[:,0]-oo_xy[i_oo,0],xy[:,1]-oo_xy[i_oo,1],s=1,c=slice_surf,cmap=plt.cm.jet,norm=mynorm_slice,zorder=2)
#ax0.scatter(xcoords,ycoords,s=50,c='black',marker='v',zorder=5)
ax0.scatter(o_stations[:,0],o_stations[:,1],s=50,c='black',marker='X',zorder=5)
ax0.scatter(i_stations[:,0],i_stations[:,1],s=50,c='black',marker='v',zorder=5)
ax0.set_title('myFig 0')
ax0.set_title('Scatter (both coord systems)')

plt.show()
'''
'''
