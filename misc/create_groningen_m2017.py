import pandas as pd
import numpy as np
from pyevtk.hl import gridToVTK

max_d = 5000.0
dz    = 20.0

print()
print()
print('#######   Vo Maps   #############################################')
print()
vo_frame = pd.read_csv('data/Vo_maps.txt', delim_whitespace=True)
print(vo_frame)
print()

# get x,y coordinates from the vo_frame (Vo_map)
x_coords = vo_frame[['XSSP']].to_numpy().astype(np.float32)
y_coords = vo_frame[['YSSP']].to_numpy().astype(np.float32)

# get P-veloctiy function intersects
ns_vel = vo_frame[['NS']].to_numpy().astype(np.float32)
ck_vel = vo_frame[['CK']].to_numpy().astype(np.float32)
me_vel = vo_frame[['ME']].to_numpy().astype(np.float32)

# free mem (garbage collection is not always enough to prevent mem pressure)
del vo_frame

# Find min and max x_coord for bounding-box, VTK x_coords, and horizon indices
xmin =  np.amin(x_coords)
xmax =  np.amax(x_coords)
dx = 50 # based on 2017 Vo_maps.txt and horizons.txt
x = np.arange(xmin,xmax+1,dx)
nx = len(x)
ix = np.copy(x_coords)
ix = (ix - xmin)/dx
ix = ix.astype(int)
del x_coords

# Find min and max y_coord for bounding-box, VTK x_coords, and horizon indices
ymin =  np.amin(y_coords)
ymax =  np.amax(y_coords)
dy = 50 # based on 2017 Vo_maps.txt and horizons.txt
y = np.arange(ymin,ymax+1,dy)
ny = len(y)
iy = np.copy(y_coords)
iy = (iy - ymin)/dy
iy = iy.astype(int)
del y_coords

# show number of z points
nz = int((max_d/dz)+1)

# show number of all points
nxyz = nx*ny*nz


print('#######   Horizons   ############################################')
print()
ho_frame = pd.read_csv('data/horizons.txt', delim_whitespace=True)
print(ho_frame)
print()

# get horizon depths per x,y and convert into indices
ns_b = ((ho_frame[['NS_B']].to_numpy()[:,0])/dz + 0.5).astype(int)
ck_b = ((ho_frame[['CK_B']].to_numpy()[:,0])/dz + 0.5).astype(int)
ze_t = ((ho_frame[['ZE_T']].to_numpy()[:,0])/dz + 0.5).astype(int)
fl_t = ((ho_frame[['float_T']].to_numpy()[:,0])/dz + 0.5).astype(int)
fl_b = ((ho_frame[['float_B']].to_numpy()[:,0])/dz + 0.5).astype(int)
zz_t = ((ho_frame[['ZEZ2A_T']].to_numpy()[:,0])/dz + 0.5).astype(int)
ro_t = ((ho_frame[['RO_T']].to_numpy()[:,0])/dz + 0.5).astype(int)
dc_t = ((ho_frame[['DC_T']].to_numpy()[:,0])/dz + 0.5).astype(int)

# free mem (garbage collection is not always enough to prevent mem pressure)
del ho_frame



# create/fill-in P-vel for subsurface
print()
print('#######  Calculating P-vels   ###################################')
print()


print('nx:',nx)
print('ny:',ny)
print('nz:',nz)
print('Total Subsurface Points:',nxyz)

# initalize array for subsurface P-vel values
# NOTE: were there is no coverage P-vels will be zero (instead of -99999)
pv = np.zeros((nx,ny,nz)).astype(np.float32)
print('pv.shape:',pv.shape)
print()

# track every 5% increment below
perc_5 = int(len(ix)/20 + 0.5)

for ixy in range(len(ix)):

    for iz in range(ns_b[ixy]+1):
        pv[ix[ixy],iy[ixy],iz] = ns_vel[ixy] + iz*dz*0.25

    for iz in range(ns_b[ixy]+1,ck_b[ixy]+1):
        pv[ix[ixy],iy[ixy],iz] = ck_vel[ixy] + iz*dz*2.3

    for iz in range(ck_b[ixy]+1,ze_t[ixy]):
        pv[ix[ixy],iy[ixy],iz] = me_vel[ixy] + iz*dz

    for iz in range(ze_t[ixy],fl_t[ixy]):
        pv[ix[ixy],iy[ixy],iz] = 4400

    for iz in range(fl_t[ixy],fl_b[ixy]+1):
        pv[ix[ixy],iy[ixy],iz] = 5900

    for iz in range(fl_b[ixy]+1,zz_t[ixy]):
        pv[ix[ixy],iy[ixy],iz] = 4400

    for iz in range(zz_t[ixy],ro_t[ixy]):
        pv[ix[ixy],iy[ixy],iz] = 5900

    for iz in range(ro_t[ixy],dc_t[ixy]):
        pv[ix[ixy],iy[ixy],iz] = 3900

    for iz in range(dc_t[ixy],nz):
        pv[ix[ixy],iy[ixy],iz] = int(0.541*dz*iz + 2572.3)
    if (ixy % perc_5) == 0:
        print(pv[ix[ixy],iy[ixy],:])
        print('Currently %d percent finished' % int((ixy//perc_5)*5))
print(pv[ix[-1],iy[-1],:])
print('Currently 100 percent finished')


# clean up memory (again garbage collection not always good enough)
del ns_vel
del ck_vel
del me_vel

del ns_b
del ck_b
del ze_t
del fl_t
del fl_b
del zz_t
del ro_t
del dc_t

del ix
del iy


# create x,y,z coordinates for VTK file
x_c = x  # sytle trick to make future maintanence easier
y_c = y  # sytle trick to make future maintanence easier
z_c = np.arange(0,-max_d-1,-dz).astype(np.float32)

# reshape (flatten) P-vels for VTK writer and for VTK format
pv_float = pv.astype(np.ushort)
del pv # more cleanup
tran_flat_pv = pv_float.transpose(2,1,0).flatten()
del pv_float # more cleanup

# this will write to a structured grid VTK file
gridToVTK("./test_groningen", x_c, y_c, z_c, pointData = {"vel" : tran_flat_pv})

