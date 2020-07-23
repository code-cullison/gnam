import os
import numpy as np
import pandas as pd
from obspy import Stream
from obspy import Trace


def spec_ascii_2_stream(fqpname):

    df = pd.io.parsers.read_csv(fqpname,sep='\s+',header=None, usecols=[0,1])
    data = df[[1]].to_numpy().astype(np.float32).flatten()
    times = df[[0]].to_numpy().astype(np.float32).flatten()
    fhdr = fqpname.split('/')[-1].split('.')
    stats = {'network': fhdr[0], 'station': fhdr[1], 'location': '',
            'channel': fhdr[2], 'npts': len(data), 'delta': times[1]-times[0]}
    syntime = df[[0]].to_numpy().astype(np.float64).flatten()
    stats['starttime'] = syntime[0]
    return Stream([Trace(data=data, header=stats)])

def all_spec_ascii_that_match_2_stream(fqdpath,match_str):

    e_st = Stream()
    for file in os.listdir(fqdpath):
        if 0 <= file.find(match_str):
            st = spec_ascii_2_stream(fqdpath+file)
            e_st += st
    return e_st.sort()
