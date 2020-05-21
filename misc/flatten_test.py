import numpy as np

xyz = np.zeros((5,5,5))

for ix in range(5):
    for iy in range(5):
        for iz in range(5):
            xyz[ix,iy,iz] = ix + 10*iy + 100*iz

print(xyz)

xyz = xyz.reshape((5,5,5))

print(xyz)

xyz = xyz.flatten()

print(xyz)

xyz = xyz.reshape((5,5,5))

print(xyz)
