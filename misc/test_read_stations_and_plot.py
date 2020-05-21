import numpy as np
import pandas as pd

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

print('xcoords.shape:', xcoords.shape)
print('xcoords:\n',xcoords)
print('ycoords.shape:', ycoords.shape)
print('ycoords:\n',ycoords)
