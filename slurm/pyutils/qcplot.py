#!/quanta1/home/tcullison/miniconda3/envs/mypy3.8/bin/python

import sys, getopt
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

import obspy
from obspy import Stream
from obspy import Trace


def read_spec_ascii_triggers(fqpname):

    df       = pd.io.parsers.read_csv(fqpname,sep='=',header=None, usecols=[0,1])
    data     = df[[1]].to_numpy().astype(np.float32).flatten()
    triggers = np.zeros_like(data)
    triggers[0] = data[0]
    triggers[1] = data[2]
    triggers[2] = data[1]
    triggers[3] = data[3]
    fhdr     = fqpname.split('/')[-1].split('.')
    key      = fhdr[0] + '.' + fhdr[1] 
    return (key,triggers)


def read_all_spec_ascii_windows(fqdpath,match_str):

    trig_dict = {}
    if fqdpath[-1] != '/':
        fqdpath += '/'
    for file in os.listdir(fqdpath):
        if 0 <= file.find(match_str):
            (key,triggers) = read_spec_ascii_triggers(fqdpath+file)
            trig_dict[key] = triggers

    return trig_dict

def create_pdf_plot(comp,ofqdn,e_st,e_cst=None,trig_dict=None):

    ntrace = len(e_st)//3
    loop_range = range(len(e_st[:3*ntrace:3]))        
    comp_list = ['Z','Y','X']
    clist_st  = ['black','green','orangered']
    clist_cst = ['gray','limegreen','orange']
    plt_h = 2
    plt_w = 14
    plt_scale = ntrace
    fig, ax = plt.subplots(plt_scale,figsize=(plt_w,plt_h*plt_scale))
    fig.tight_layout()
    for i in loop_range:        

        if 0 <= comp:
            station_id = e_st[i*3+comp].stats.station
            ax[i].plot(e_st[i*3+comp].times(), e_st[i*3+comp].data, c=clist_st[comp], zorder=1)
            overlay_title = 'Station: %s, Base: %s(%s)' %(station_id,comp_list[comp],clist_st[comp])
            if e_cst != None:
                ax[i].plot(e_cst[i*3+comp].times(),e_cst[i*3+comp].data,c=clist_cst[comp],linestyle='dashed',zorder=0)
                overlay_title += ', Compare: %s(%s)' %(comp_list[comp],clist_cst[comp])

        else:
            station_id = e_st[i*3].stats.station
            ax[i].plot(e_st[i*3].times(),   e_st[i*3].data,   c=clist_st[0], zorder=1)
            ax[i].plot(e_st[i*3+1].times(), e_st[i*3+1].data, c=clist_st[1], zorder=1)
            ax[i].plot(e_st[i*3+2].times(), e_st[i*3+2].data, c=clist_st[2], zorder=1)
            overlay_title = 'Station: %s, Base: %s(%s), %s(%s), %s(%s)' \
            %(station_id,comp_list[0],clist_st[0],comp_list[1],clist_st[1],comp_list[2],clist_st[2])
            if e_cst != None:
                ax[i].plot(e_cst[i*3].times(),   e_cst[i*3].data,   c=clist_cst[0],linestyle='dashed',zorder=0)
                ax[i].plot(e_cst[i*3+1].times(), e_cst[i*3+1].data, c=clist_cst[1],linestyle='dashed',zorder=0)
                ax[i].plot(e_cst[i*3+2].times(), e_cst[i*3+2].data, c=clist_cst[2],linestyle='dashed',zorder=0)

        
        if trig_dict != None:
            amin = np.min(e_st[i*3].data)
            amin = np.min(np.array([amin,np.min(e_st[i*3+1].data)]))
            amin = np.min(np.array([amin,np.min(e_st[i*3+2].data)]))
            if e_cst != None:
                amin = np.min(np.array([amin,np.min(e_cst[i*3].data)]))
                amin = np.min(np.array([amin,np.min(e_cst[i*3+1].data)]))
                amin = np.min(np.array([amin,np.min(e_cst[i*3+2].data)]))
            amax = np.max(e_st[i*3].data)
            amax = np.max(np.array([amax,np.max(e_st[i*3+1].data)]))
            amax = np.max(np.array([amax,np.max(e_st[i*3+2].data)]))
            if e_cst != None:
                amax = np.max(np.array([amax,np.max(e_cst[i*3].data)]))
                amax = np.max(np.array([amax,np.max(e_cst[i*3+1].data)]))
                amax = np.max(np.array([amax,np.max(e_cst[i*3+2].data)]))

            wkey  =       e_st[i*3+comp].stats.network
            wkey += '.' + e_st[i*3+comp].stats.station
            ax[i].vlines(x=trig_dict[wkey][0], ymin=amin, ymax=amax, colors='red')
            ax[i].vlines(x=trig_dict[wkey][1], ymin=amin, ymax=amax, colors='red',linestyle='dashed')
            ax[i].vlines(x=trig_dict[wkey][2], ymin=amin, ymax=amax, colors='blue')
            ax[i].vlines(x=trig_dict[wkey][3], ymin=amin, ymax=amax, colors='blue',linestyle='dashed')

        ax[i].set_title(overlay_title)
        ax[i].set_xlabel("time (s)")
        ax[i].set_ylabel("displacement (m)")

        ax[i].grid(b=True, which='major', color='#666666', linestyle='-')
        ax[i].minorticks_on()
        ax[i].grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    #plt.show()

    fig.savefig(ofqdn, bbox_inches='tight')


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


def main(argv):
    idir  = None
    odir  = None
    icdir = None
    iwdir = None
    ofname = None
    comp  = -1
    st    = None
    cst   = None
    trigs = None
    comp_str = 'ZYX'
    try:
        opts, args = getopt.getopt(argv,'hzyx',['idir=','odir=','icdir=','iwdir=','ofname='])
    except getopt.GetoptError:
        print('Error rwftr.py --idir <input dir> --odir <output dir> \
                              --icdir <input compare dir> --iwdir <input window dir> \
                              --ofname <output plot file name>')
        print('Error')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Error rwftr.py --idir <input dir> --odir <output dir> \
                                  --icdir <input compare dir> --iwdir <input window dir> \
                                  --ofname <output plot file name>')
            sys.exit()
        if opt == '-z':
            comp = 0
            comp_str = 'Z'
        if opt == '-y':
            comp = 1
            comp_str = 'Y'
        if opt == '-x':
            print('in -x')
            comp = 2
            comp_str = 'X'
        elif opt in ("--idir"):
            idir = arg
        elif opt in ("--odir"):
            odir = arg
        elif opt in ("--icdir"):
            icdir = arg
        elif opt in ("--iwdir"):
            iwdir = arg
        elif opt in ("--ofname"):
            ofname = arg
    if not idir or not odir or not ofname:
        print('--idir, --odir, and --ofname must be set')
        sys.exit()
    print('Input Directory:', idir)
    ofqdn = odir
    if odir[-1] != '/':
        ofqdn += '/'
    ofqfname = ofname
    if icdir != None:
        ofqfname += '.compare'
    if iwdir != None:
        ofqfname += '.windows'
    ofqfname += '.' + comp_str + '.pdf'
    ofqdn += ofqfname
    print('Output Filename:', ofqfname)
    if icdir:
        print('Input Compare Directory: ', icdir)
    if iwdir:
        print('Input Windowing Directory: ', iwdir)


    ############################################################
    #
    # Read SPECFEM Traces from idir and create ObsPy.Stream
    #
    ############################################################

    print('Reading input traces from:',idir)
    st = read_all_spec_ascii_that_match_2_stream(idir,'.semd')
    st.resample(250)
    print('Done reading input traces')
    if icdir:
        print('Reading compare traces from:',icdir)
        cst = read_all_spec_ascii_that_match_2_stream(icdir,'.semd')
        cst.resample(250)
        print('Done reading compare traces')
    if iwdir:
        print('Reading windows from:',iwdir)
        trigs = read_all_spec_ascii_windows(iwdir,'.window')
        print('Done reading windows')

    print('Writing plot to:',ofqdn)
    create_pdf_plot(comp,ofqdn,st,cst,trigs)
    print('Done')



if __name__ == "__main__":
    main(sys.argv[1:])
