import pandas as pd
import numpy as np
from pyevtk.hl import gridToVTK

max_d = 5000.0
dz    = 200.0

#vo_frame = pd.read_csv('data/Vo_maps.txt', delimiter = ' ')
#vo_frame = pd.read_csv('data/Vo_maps.txt', delimiter = r"\s+")
vo_frame = pd.read_csv('data/Vo_maps.txt', delim_whitespace=True)
print(vo_frame)
x_coords = vo_frame[['XSSP']].to_numpy().astype(np.float32)
y_coords = vo_frame[['YSSP']].to_numpy().astype(np.float32)
ns_vel = vo_frame[['NS']].to_numpy().astype(np.ushort)
ck_vel = vo_frame[['CK']].to_numpy().astype(np.ushort)
me_vel = vo_frame[['ME']].to_numpy().astype(np.ushort)
del vo_frame

ho_frame = pd.read_csv('data/horizons.txt', delim_whitespace=True)
print(ho_frame)
ns_b = ho_frame[['NS_B']].to_numpy()[:,0]
ck_b = ho_frame[['CK_B']].to_numpy()[:,0]
ze_t = ho_frame[['ZE_T']].to_numpy()[:,0]
fl_t = ho_frame[['float_T']].to_numpy()[:,0]
fl_b = ho_frame[['float_B']].to_numpy()[:,0]
zz_t = ho_frame[['ZEZ2A_T']].to_numpy()[:,0]
ro_t = ho_frame[['RO_T']].to_numpy()[:,0]
dc_t = ho_frame[['DC_T']].to_numpy()[:,0]
del ho_frame
print('dc max:', np.amax(dc_t))

#print('ns_b.shape:\n',ns_b.shape)
#print('ns_b:\n',ns_b)
ns_b = ns_b/dz + 0.5
ns_b = ns_b.astype(int)
ck_b = ck_b/dz + 0.5
ck_b = ck_b.astype(int)
ze_t = ze_t/dz + 0.5
ze_t = ze_t.astype(int)
fl_t = fl_t/dz + 0.5
fl_t = fl_t.astype(int)
fl_b = fl_b/dz + 0.5
fl_b = fl_b.astype(int)
zz_t = zz_t/dz + 0.5
zz_t = zz_t.astype(int)
ro_t = ro_t/dz + 0.5
ro_t = ro_t.astype(int)
dc_t = dc_t/dz + 0.5
dc_t = dc_t.astype(int)
#print('ns_b:\n',ns_b)
print('dc_t[0]:\n',dc_t[0])
#print('len(ns_b):',len(ns_b))
#print('len(ns_vel):',len(ns_vel))


#print(vo_frame[['XSSP','YSSP']])
#print(x_coords)
#print(x_coords.shape)
xmin =  np.amin(x_coords)
xmax =  np.amax(x_coords)
print('xmin:',xmin)
print('xmax:',xmax)
dx = 50
x = np.arange(xmin,xmax+1,dx)
nx = len(x)
ix = np.copy(x_coords)
ix = (ix - xmin)/dx
ix = ix.astype(int)
del x_coords
print('onx:', (xmax-xmin)/dx + 1)
print('x[0]:',x[0])
print('x[-1]:',x[-1])
print('ix:',ix)
print('len(ix):',len(ix))

#print(y_coords)
#print(y_coords.shape)
ymin =  np.amin(y_coords)
ymax =  np.amax(y_coords)
print('ymin:',ymin)
print('ymax:',ymax)
dy = 50
y = np.arange(ymin,ymax+1,dy)
ny = len(y)
iy = np.copy(y_coords)
iy = (iy - ymin)/dy
iy = iy.astype(int)
del y_coords
print('ony:', (ymax-ymin)/dy + 1)
print('y[0]:',y[0])
print('y[-1]:',y[-1])
print('iy:',iy)
print('len(iy):',len(iy))

print('nx:',nx)
print('ny:',ny)

nz = int((max_d/dz)+1)
print('nz:',nz)

nxyz = nx*ny*nz
print('nxyz:',nxyz)
#z = np.arange(0,10*nz,dz).reshape(1,1,nz)
#print(z.shape)

#print('z[0,0,-1]:',z[0,0,-1])

#pv = np.ones((nx,ny,1)) * z
#pv = np.ones((nx,ny,nz)) * -1.0
pv = np.zeros((nx,ny,nz)).astype(np.ushort) * -1.0
#print('pv.shape:',pv.shape)
#print('pv:\n',pv)

rt = 2.50001
irt = int(rt+0.5)
print('irt =',irt)

'''
mya = np.array([2.2,2.5001])+0.5
print(mya)
mya = mya.astype(int)
print(mya)
'''


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

#tvel = np.arange(nx*ny*nz).astype(np.float32)
x_c = x
y_c = y
z_c = np.arange(0,-max_d-1,-dz).astype(np.float32)
print('z_c:\n',z_c)
print('pv.shape',pv.shape)
print('flat_pv.shape',pv.flatten().shape)
#print('x_c.shape:',x_c.shape)
#print('y_c.shape:',y_c.shape)
#print('z_c.shape:',z_c.shape)
#gridToVTK("./test_structured", x_c, y_c, z_c, pointData = {"tvel" : tvel})

#pv_float = pv.astype(np.float32)
pv_float = pv.astype(np.ushort)
#del pv
tran_flat_pv = pv_float.transpose(2,1,0).flatten()
#tran_flat_pv = pv.transpose(2,1,0).flatten()
del pv
#del pv_float

#tran_flat_pv = pv.transpose(2,1,0).flatten()
#del pv
#gridToVTK("./test_groningen", x_c, y_c, z_c, pointData = {"vel" : pv.transpose(2,1,0).flatten()})
gridToVTK("./test_groningen", x_c, y_c, z_c, pointData = {"vel" : tran_flat_pv})
