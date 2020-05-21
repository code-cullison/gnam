import numpy as np

pv = np.load('./groningen_m2017_1mspc.npz')['arr_0']
print('pv.shape:',pv.shape)
print('pv[500,500,:]:\n',pv[500,500,:])
print()
