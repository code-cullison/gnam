import numpy as np
import scipy as sp
from scipy.interpolate import RegularGridInterpolator


def f(x,y,z):
    return 100 + z**2 + y**2 + x**2

x = np.linspace(-500,500,6)
y = np.linspace(-500,500,6)
z = np.linspace(-1000,0,21)

#print('*np.meshgrid:\n',*np.meshgrid(x, y, z, indexing='ij', sparse=True))
data = f(*np.meshgrid(x, y, z, indexing='ij', sparse=True))
print('data.shape:\n',data.shape)
print('data:\n',data)

my_rgi = RegularGridInterpolator((x,y,z),data)

xv = 200.1
yv = -100.1
zv = -100.1
rval = 100 + xv**2 + yv**2 + zv**2

ipts = np.array([xv,yv,zv])
ival = my_rgi(ipts)

print('(rval,ival)=(%f,%f)' %(rval,ival))

