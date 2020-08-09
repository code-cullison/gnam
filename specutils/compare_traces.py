#!/quanta1/home/tcullison/miniconda3/envs/mypy3/bin/python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import sys, getopt

import obspy
from obspy import Stream
from obspy import Trace

def main(argv):
   tr_fname1 = ''
   tr_fname2 = ''
   f1 = None
   f2 = None
   try:
      opts, args = getopt.getopt(argv,'h:',['tr1=','tr2=','f1=','f2='])
   except getopt.GetoptError:
      print('compare_traces.py --tr1 <trace1 filename> --tr2 <trace2 filename>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('compare_traces.py --tr1 <trace1 filename> --tr2 <trace2 filename>')
         sys.exit()
      elif opt in ("--tr1"):
         tr_fname1 = arg
      elif opt in ("--tr2"):
         tr_fname2 = arg
      elif opt in ("--f1"):
         f1 = float(arg)
      elif opt in ("--f2"):
         f2 = float(arg)
   print('Trace-1 file is:', tr_fname1)
   print('Trace-2 file is:', tr_fname2)
   if f1 and f2:
       print('Window f1:', f1)
       print('Window f2:', f2)

   df1 = pd.io.parsers.read_csv(tr_fname1,sep="\s+",header=None, usecols=[0,1])
   data1 = df1[[1]].to_numpy().astype(np.float32).flatten()
   fhdr1 = tr_fname1.split('.')
   stats1 = {'network': fhdr1[0], 'station': fhdr1[1], 'location': '',
            'channel': fhdr1[2], 'npts': len(data1), 'delta': 0.001}
   syntime1 = df1[[0]].to_numpy().astype(np.float64).flatten()
   stats1['starttime'] = syntime1[0]
   st1 = Stream([Trace(data=data1, header=stats1)])

   df2 = pd.io.parsers.read_csv(tr_fname2,sep="\s+",header=None, usecols=[0,1])
   data2 = df2[[1]].to_numpy().astype(np.float32).flatten()
   fhdr2 = tr_fname2.split('.')
   stats2 = {'network': fhdr2[0], 'station': fhdr2[1], 'location': '',
            'channel': fhdr2[2], 'npts': len(data2), 'delta': 0.001}
   syntime2 = df2[[0]].to_numpy().astype(np.float64).flatten()
   stats2['starttime'] = syntime2[0]
   st2 = Stream([Trace(data=data2, header=stats2)])

   if f1 and f2:
       st = st1 + st2
       st.filter('bandpass',freqmin=f1,freqmax=f2)
       #st.filter('bandpass',freqmin=f1,freqmax=f2,corners=4,zerophase=True)

   '''
   x = np.linspace(0,2*np.pi,1000)
   y = np.sin(x)
   '''

   fig, ax = plt.subplots(1,figsize=(12,3))
   #ax.plot(x,y)

   pcolors = ['black','orange']
   ax.plot(st1[0].times(),st1[0].data,c=pcolors[0],zorder=0)
   ax.plot(st2[0].times(),st2[0].data,c=pcolors[1],zorder=1)

   station1 = st1[0].stats.station
   station2 = st1[0].stats.station

   overlay_title = 'Trace-1: %s (%s), Trace-2: %s (%s)' %(str(station1),pcolors[0],str(station2),pcolors[1])

   ax.set_title(overlay_title)
   ax.set_xlabel("time (s)")
   ax.set_ylabel("displacement (m)")

   plt.grid(b=True, which='major', color='#666666', linestyle='-')
   plt.minorticks_on()
   plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

   plt.show()

if __name__ == "__main__":
   main(sys.argv[1:])
