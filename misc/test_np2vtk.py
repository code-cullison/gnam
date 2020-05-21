import pandas as pd
import numpy as np
import random as rnd
from pyevtk.hl import pointsToVTK
from pyevtk.hl import gridToVTK

#Data = np.array([[[1,2,3],[4,5,6],[7,8,9]],[[11,12,13],[14,15,16],[17,18,19]]],'f')
Data = np.array([[[1.11,2.11],[1.21,2.21]],[[1.12,2.12],[1.22,2.22]]])
dshape = Data.shape
print('Data:\n',Data)
#flat_data_array = Data.transpose(2,1,0).flatten()
flat_data_array = Data.flatten()
print('flat_Data:\n',flat_data_array)

x = np.arange(1.0,10.0,0.1)
y = np.arange(1.0,10.0,0.1)
z = np.arange(1.0,10.0,0.1)
z2 = 2*np.arange(1.0,10.0,0.1)
pointsToVTK("./line_points", x, y, z, data = {"elev" : z2})

# Dimensions
nx, ny, nz = 6, 6, 2
lx, ly, lz = 1.0, 1.0, 1.0
dx, dy, dz = lx/nx, ly/ny, lz/nz

ncells = nx * ny * nz
npoints = (nx + 1) * (ny + 1) * (nz + 1)

# Coordinates
X = np.arange(0, lx + 0.1*dx, dx, dtype='float64')
Y = np.arange(0, ly + 0.1*dy, dy, dtype='float64')
Z = np.arange(0, lz + 0.1*dz, dz, dtype='float64')

x = np.zeros((nx + 1, ny + 1, nz + 1))
y = np.zeros((nx + 1, ny + 1, nz + 1))
z = np.zeros((nx + 1, ny + 1, nz + 1))

# We add some random fluctuation to make the grid
# more interesting
for k in range(nz + 1):
    for j in range(ny + 1):
        for i in range(nx + 1):
            x[i,j,k] = X[i] + (0.5 - rnd.random()) * 0.1 * dx
            y[i,j,k] = Y[j] + (0.5 - rnd.random()) * 0.1 * dy
            z[i,j,k] = Z[k] + (0.5 - rnd.random()) * 0.1 * dz

# Variables
pressure = np.random.rand(ncells).reshape( (nx, ny, nz))
temp = np.random.rand(npoints).reshape( (nx + 1, ny + 1, nz + 1))

#gridToVTK("./structured", x, y, z, cellData = {"pressure" : pressure}, pointData = {"temp" : temp})
gridToVTK("./structured", x, y, z, pointData = {"temp" : temp})
