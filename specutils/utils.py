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

def conform_and_bandpass_streams_for_adjsrc(obs_st,syn_st,f1,f2):

    assert len(obs_st) == len(syn_st)
    _obs_st = obs_st.copy()
    _syn_st = syn_st.copy()

    _obs_st.sort()
    _syn_st.sort()

    for i in range(len(_obs_st)):

        assert _obs_st[i].stats.network == _syn_st[i].stats.network
        assert _obs_st[i].stats.station == _syn_st[i].stats.station
        assert _obs_st[i].stats.channel == _syn_st[i].stats.channel

        o_t0 = _obs_st[i].times()[0]
        o_tN = _obs_st[i].times()[-1]
        o_dt = _obs_st[i].stats.delta

        s_t0 = _syn_st[i].times()[0]
        s_tN = _syn_st[i].times()[-1]
        s_dt = _syn_st[i].stats.delta

        assert o_t0 <= 0.0 and s_t0 <= 0.0

        _tN = o_tN
        if s_tN < _tN:
            _tN = s_tN

        _dt = o_dt
        if s_dt < _dt:
            _dt = s_dt

        _filt_obs_st = bandpass_stream(_obs_st,f1,f2,nc=4)
        _filt_syn_st = bandpass_stream(_syn_st,f1,f2,nc=4)
        _filt_obs_st = trim_resample_stream(_filt_obs_st,_t0,_tN,_dt)
        _filt_syn_st = trim_resample_stream(_filt_syn_st,_t0,_tN,_dt)

    return (_filt_obs_st,_filt_syn_st)


