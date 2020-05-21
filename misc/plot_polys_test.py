import numpy as np
import scipy as sp
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt


#x = np.cos(np.linspace(0,2*np.pi,6))
#y = np.sin(np.linspace(0,2*np.pi,6))
x = np.array([2,1,1,0,0,1,1,2,2,3,3,2])
y = np.array([0,0,1,1,2,2,3,3,2,2,1,1])
x = np.append(x,x[0])
y = np.append(y,y[0])

ixy = np.arange(len(x))
np.random.shuffle(ixy)

print('before x,y:', *(x,y))
x = x[::-1]
y = y[::-1]
#x = x[ixy]
#y = y[ixy]
#tx = x[3]
#x[3] = x[0]
#x[0] = tx
#ty = y[3]
#y[3] = y[0]
#y[0] = ty
print('after  x,y:', *(x,y))

fig, ax = plt.subplots(1,figsize=(5, 5))
#ax.scatter(x, y)
ax.fill(x,y)
#_extent = [x[0] , x[-1], y[0] , y[-1]]
#ax.imshow(data.T[::-1,:], extent=_extent, cmap=plt.cm.jet)
plt.show()

