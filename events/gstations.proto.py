from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from obspy import Stream
from pyproj import Proj, transform
from gnam.events.gevents import gevents as ge
from gnam.model.bbox import bbox as bb
import numpy as np
import copy


class gstations:
    
    _ge = None
    _stz = None
    _st1 = None
    _st2 = None
    _bbox = None
    _istat_dic = None
    _estat_dic = None
    _error_dic = None
    _evnt_keys = None
    _prefilt = None
    _inventory = None

    def __init__(self,ge,prefilt=(0.4, 0.5, 45.0, 47.5)):

        self._ge = ge
        self._prefilt = prefilt
        self._istat_dic = {}
        self._estat_dic = {}
        self._error_dic = {}

        gstats = 'G0*3,G0*4,G1*3,G1*4,G2*3,G2*4,G3*3,G3*4,G4*3,G4*4,G5*3,G5*4,G6*3,G6*4,G70*3,G70*4'
        client = Client("KNMI")
        self._inventory = client.get_stations(network="NL", station=gstats , level="response")

        self._stz = Stream()
        self._st1 = Stream()
        self._st2 = Stream()

        wgs84_proj = Proj('epsg:4326')
        nl_proj    = Proj('epsg:28992')
        cat = self._ge.getIncCatalog()
        self._evnt_keys = []
        ne = 0
        for c in cat:
            l_istations = []
            l_estations = []
            l_error_stats = []
            t1 = c.origins[0].time
            t2 = t1 + 16384//200 + 1 #FIXME
            try:
                if t1.year < 2016:
                    raise KNMIBadDate
            except KNMIBadDate:
                print('Data is too old (before 2016) for the FDSN data at KNMI') #FIXME
                continue
            print('num inventory:',len(self._inventory))
            print('inventory[0]:\n', self._inventory[0])
            for network in self._inventory:
                print('network:\n', network)
                for station in network:
                    e_lon = station.longitude
                    e_lat = station.latitude
                    ex,ey = transform(wgs84_proj,nl_proj,e_lat,e_lon)

                    is_in   = True
                    is_bbox = False
                    if self._ge.getBBox() is not None:
                        is_bbox = True

                    if is_bbox: 
                        is_in = self._ge.getBBox().coordIsIn(ex,ey)

                    if (is_bbox and is_in) or (~is_bbox and is_in) :
                        try:
                            # Z component
                            self._stz += client.get_waveforms(network.code, station.code, "*", "HHZ", \
                                                              t1, t1 + 60, attach_response = True)
                            
                            # Northish component
                            self._st1 += client.get_waveforms(network.code, station.code, "*", "HH1", \
                                                              t1, t1 + 60, attach_response = True)
                            
                            # Eastish component
                            self._st2 += client.get_waveforms(network.code, station.code, "*", "HH2", \
                                                              t1, t1 + 60, attach_response = True)
                            
                        except:
                            l_error_stats.append(station)
                            continue

                        l_istations.append(station)

                    else:
                        l_estations.append(station)


            self._istat_dic[ne] = l_istations
            self._estat_dic[ne] = l_estations
            self._error_dic[ne] = l_error_stats
            self._evnt_keys.append(ne)
            ne += 1

        self._stz.remove_response()
        self._stz.detrend(type='demean')
        self._st1.remove_response()
        self._st1.detrend(type='demean')
        self._st2.remove_response()
        self._st2.detrend(type='demean')
    #end __init__()

    def __str__(self):
        str_stream = Stream()
        str_stream += self._stz
        str_stream += self._st1
        str_stream += self._st2
        return str(str_stream)

    def _getStationStream(self,key):
        
        if key == 'z':
            return self._stz

        elif key == '1':
            return self._st1

        elif key == '2':
            return self._st2

        else:
            assert False


    def getIncStationStreamZ(self):
        return self._getStationStream('z')


    def getIncStationStream1(self):
        return self._getStationStream('1')


    def getIncStationStream2(self):
        return self._getStationStream('2')


    def getIncDictionary(self):
        return self._istat_dic 


    def getExcDictionary(self):
        return self._estat_dic 


    def getErrorDictionary(self):
        return self._error_dic 


    def getEventKeys(self):
        return self._evnt_keys


    def _getCoords(self,ie,dic):
        wgs84_proj = Proj('epsg:4326')
        nl_proj    = Proj('epsg:28992')

        l_stations = dic[ie]
        s_xy = np.zeros((len(l_stations),2),dtype=np.float32)

        si = 0
        for s in l_stations:

            s_lon = s.longitude
            s_lat = s.latitude
            ex,ey = transform(wgs84_proj,nl_proj,s_lat,s_lon)
            s_xy[si,0] = ex
            s_xy[si,1] = ey

            si += 1

        return s_xy


    def getIncStationCoords(self, ie):
        return self._getCoords(ie,self._istat_dic)


    def getExcStationCoords(self, ie):
        return self._getCoords(ie,self._estat_dic)


    def getErrorStationCoords(self, ie):
        return self._getCoords(ie,self._error_dic)



