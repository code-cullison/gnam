import numpy as np
import pandas as pd
from obspy import Stream
from obspy import Trace


def trim_resample_stream(st,t0,tN,dt):

    _st = st.copy()
    for i in range(len(st)):

        _utc_t0 = _st[i].stats.starttime
        _t0 = _st[i].times()[0]
        _tN = _st[i].times()[-1]
        _samp = _st[i].stats.sampling_rate
        _dt = 1/_samp

        station = _st[i].stats.station
        channel = _st[i].stats.channel
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

        if dt != _dt:
            _st[i].resample(int(1/dt))

        _st[i].trim(_utc_t0+t0,_utc_t0+t0+tN)

    return _st

def bandpass_stream(st,f1,f2,nc=4):
    _st = st.copy()
    _st.filter('bandpass',freqmin=f1,freqmax=f2,corners=nc,zerophase=True)
    return _st

def conform_and_bandpass_streams_for_adjsrc(obs_st,syn_st,resamp,tN,f1,f2):

    assert len(obs_st) == len(syn_st)
    obs_st.sort()
    syn_st.sort()

    obs_st.resample(resamp)
    syn_st.resample(resamp)
    obs_st.filter('bandpass',freqmin=f1,freqmax=f2,corners=4,zerophase=True)
    syn_st.filter('bandpass',freqmin=f1,freqmax=f2,corners=4,zerophase=True)
    o_t0 = obs_st[0].stats.starttime
    s_t0 = syn_st[0].stats.starttime
    o_tN = o_t0 + tN
    s_tN = s_t0 + tN
    obs_st.trim(o_t0,o_tN)
    syn_st.trim(s_t0,s_tN)

    for i in range(len(obs_st)):

        assert obs_st[i].stats.network == syn_st[i].stats.network
        assert obs_st[i].stats.station == syn_st[i].stats.station
        assert obs_st[i].stats.channel == syn_st[i].stats.channel

        o_tzero = obs_st[i].times()[0] 
        o_tend  = obs_st[i].times()[-1] 
        s_tzero = syn_st[i].times()[0] 
        s_tend  = syn_st[i].times()[-1] 
        assert o_tzero == 0.0 and s_tzero == 0.0
        assert o_tend == s_tend


