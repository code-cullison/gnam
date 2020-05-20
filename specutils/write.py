from obspy import Stream
from pyproj import Proj, transform
from gnam.events.gstations import gstations
from gnam.events.mtensors import mtensors
from gnam.model.bbox import bbox
import numpy as np
import datetime


def write_stations(fqpname,gs,ekey,bkeys):

    str_stations = []
    for bkey in bkeys:
        station_codes  = gs.getIncStationCodes(ekey,bkey)
        station_coords = gs.getLocalIncStationCoords(ekey,bkey)
        stations       = gs.getIncludedStations(ekey,bkey)
        
        hdict = dict(zip(station_codes, station_coords))

        for i in range(len(hdict)):
            stat = station_codes[i]
            burial = stations[i].channels[0].depth
            str_stations.append('%s %s %.2f %.2f %.2f %.2f\n' %(stat,'NL',hdict[stat][1],hdict[stat][0],0,burial))

    f = open(fqpname, 'w')
    f.writelines(str_stations)
    f.close()


def write_cmtsolution(fqpname,mt,lx,ly):

    t = mt['Date']
    d_km = mt['ZC']/1000.0
    header_str = '%s %s %s %s %s %s %s %s %s %s %s %s %s\n' \
    %('PDE',t.year,t.month,t.day,t.hour,t.minute,t.second,ly,lx,d_km,0,0,'DEEPNL')
    #%('PDE',t.year,t.month,t.day,t.hour,t.minute,t.second,mt['YC'],mt['XC'],d_km,0,0,'DEEPNL')

    cmt = mt.get_cmt_tensor_utri()

    cmtlines_str = []
    cmtlines_str.append('event name:    %s\n' %(int(t.timestamp)))
    cmtlines_str.append('time shift:    %s\n' %('0.0000'))
    cmtlines_str.append('half duration: %s\n' %('0.0000'))
    cmtlines_str.append('latorUTM:      %s\n' %(ly))
    cmtlines_str.append('longorUTM:     %s\n' %(lx))
    #cmtlines_str.append('latorUTM:      %s\n' %(mt['YC']))
    #cmtlines_str.append('longorUTM:     %s\n' %(mt['XC']))
    cmtlines_str.append('depth:         %s\n' %(d_km))
    cmtlines_str.append('Mrr:           %s\n' %(cmt[0]))
    cmtlines_str.append('Mtt:           %s\n' %(cmt[1]))
    cmtlines_str.append('Mpp:           %s\n' %(cmt[2]))
    cmtlines_str.append('Mrt:           %s\n' %(cmt[3]))
    cmtlines_str.append('Mrp:           %s\n' %(cmt[4]))
    cmtlines_str.append('Mtp:           %s'   %(cmt[5]))

    f = open(fqpname, 'w')
    f.write(header_str)
    f.writelines(cmtlines_str)
    f.close()

