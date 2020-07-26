#####!/quanta1/home/tcullison/miniconda3/envs/mypy3/bin/python

import sys, getopt
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

import obspy
from obspy import Stream
from obspy import Trace

def trim_resample_stream(st,t0,tN,resamp):

    for i in range(len(st)):

        _resamp = st[i].stats.sampling_rate
        _utc_t0 = st[i].stats.starttime
        _t0 = st[i].times()[0]
        _tN = st[i].times()[-1]

        station = st[i].stats.station
        channel = st[i].stats.channel
        tr_str = station + '.' + channel
        if t0 < _t0 or _tN < tN:
            print('There was an error trimming trace:',tr_str)
            print('f() t0:',t0)
            print('f() _t0:',_t0)
            print('f() tN:',tN)
            print('f() _tN:',_tN)
            print('f() dt:',dt)
            print('f() _dt:',_dt)
            assert False

        if resamp != _resamp:
            st[i].resample(resamp)

        st[i].trim(_utc_t0+t0,_utc_t0+t0+tN)

    return(_utc_t0+t0,_utc_t0+t0+tN)

def bandpass_stream(st,f1,f2,nc=4):
    st.filter('bandpass',freqmin=f1,freqmax=f2,corners=nc,zerophase=True)

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

def read_all_spec_ascii_that_match_2_stream(fqdpath,match_str):

    if fqdpath[-1] != '/':
        fqdpath += '/'
    e_st = Stream()
    for file in os.listdir(fqdpath):
        if 0 <= file.find(match_str):
            st = spec_ascii_2_stream(fqdpath+file)
            e_st += st
    return e_st.sort()

def write_stream_2_spec_ascii(st,ofqdpath,is_zne=False):

        for tr in st:
            spec_pair_list = [] #time,amplitude pairs

            tr_spec_chan = '.' + tr.stats.channel + '.'

            if is_zne:
                #Example of filename: 'NL.G094.FXX.semd'
                tr_spec_chan = '.BOO.'
                comp_char = tr.stats.channel[2]
                if comp_char == 'Z':
                    tr_spec_chan = '.FXZ.'
                elif comp_char == 'E':
                    tr_spec_chan = '.FXX.'
                elif comp_char == 'N':
                    tr_spec_chan = '.FXY.'
                else:
                    print('Uh-oh! Spaghetti Os!')
                    assert False

            tr_filename = 'NL.' + tr.stats.station + tr_spec_chan + 'semd'

            for it in range(tr.count()):
                spec_pair_list.append('%E   %E\n' %(tr.times()[it],tr.data[it]))

            ofqpname = ofqdpath + '/' + tr_filename
            f = open(ofqpname, 'w')
            f.writelines(spec_pair_list)
            f.close()


def main(argv):
    idir = None
    odir = None
    f1 = None
    f2 = None
    t0 = None
    tN = None
    sr = None
    try:
        opts, args = getopt.getopt(argv,'h:',['idir=','odir=','f1=','f2=','t0=','tN=','sr='])
    except getopt.GetoptError:
        print('Error rwftr.py --idir <input dir> --odir <output dir> \
                      --f1 <high pass freq> --f2 <low pass freq> \
                      --t0 <first time sample> --tN <last time sample> \
                      --sr <sample rate>')
        print('Error')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
             print('rwftr.py --idir <input dir> --odir <output dir> \
                           --f1 <high pass freq> --f2 <low pass freq> \
                           --t0 <first time sample> --tN <last time sample> \
                           --sr <sample rate>')
             sys.exit()
        elif opt in ("--idir"):
            idir = arg
        elif opt in ("--odir"):
            odir = arg
        elif opt in ("--f1"):
            f1 = float(arg)
        elif opt in ("--f2"):
            f2 = float(arg)
        elif opt in ("--t0"):
            t0 = float(arg)
        elif opt in ("--tN"):
            tN = float(arg)
        elif opt in ("--sr"):
            sr = int(arg)
    if not idir or not odir:
        print('--idir and --odir must be set')
        sys.exit()
    print('Input Directory: ', idir)
    print('Output Directory:', odir)
    if f1 and not f2:
        print('if options --f1 is set, --f2 must also be set')
        sys.exit()
    if f2 and not f1:
        print('if options --f2 is set, --f1 must also be set')
        sys.exit()
    if f1 != None and f2:
        print('f1:', f1)
        print('f2:', f2)
    if f1 and not f2:
        print('if options --f1 is set, --f2 must also be set')
    if t0 != None and tN != None:
        print('t0:', t0)
        print('tN:', tN)
    if sr:
        print('sample rate:', sr)


    ############################################################
    #
    # Read SPECFEM Traces from idir and create ObsPy.Stream
    #
    ############################################################

    print('Reading traces from:',idir)
    st = read_all_spec_ascii_that_match_2_stream(idir,'.semd')
    print('Done reading traces')
    if sr != None or (t0 != None and tN != None):
        if t0 == None:
            t0 = st[0].times()[0]
        if tN == None:
            tN = st[0].times()[-1]
        if sr == None:
            sr = st[0].stats.sample_rate
        print('Trimming and/or resampling traces')
        trim_resample_stream(st,t0,tN,sr)
        print('Done trimming and/or resampling traces')
    if f1 != None and f2 != None:
        print('Bandpass filtering traces')
        bandpass_stream(st,f1,f2,nc=4)
        print('Done bandpass filtering traces')
    print('Writing Stream to:',odir)
    write_stream_2_spec_ascii(st,odir,is_zne=False)
    print('Done')



if __name__ == "__main__":
    main(sys.argv[1:])
