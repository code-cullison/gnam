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
    _event_stations_dict = None
    _event_streams_dict = None
    _inventory_dict = None
    _bh_stns = None
    _prefilt = None
    _chan_keys = None
    _evnt_keys = None
    _ekey_event_dict = None


    def __init__(self,ge,bh_stns=(3,4),prefilt=(0.4, 0.5, 45.0, 47.5)):

        self._ge = ge
        self._event_stations_dict = {}
        self._event_streams_dict = {}
        self._inventory_dict = {}
        self._bh_stns = bh_stns
        self._prefilt = prefilt
        self._chan_keys = []
        self._chan_keys.append('Z')
        self._chan_keys.append('1')
        self._chan_keys.append('2')
        self._evnt_keys = []
        self._ekey_event_dict = {}

        client = Client("KNMI")

        #get station inventories for locations and borehole depths
        for b in self._bh_stns:
            sb = str(b)
            gstats_str = 'G0*'+sb+',G1*'+sb+',G2*'+sb+',G3*'+sb+',G4*'+sb+',G5*'+sb+',G6*'+sb+',G70*'+sb
            self._inventory_dict[b] = client.get_stations(network="NL", station=gstats_str , level="response")


        wgs84_proj = Proj('epsg:4326')
        nl_proj    = Proj('epsg:28992')
        ecat = self._ge.getIncCatalog()
        ne = 0
        for e in ecat:
            l_istations = []
            l_estations = []
            l_error_stats = []
            t1 = e.origins[0].time
            t2 = t1 + 16384//200 + 1 #FIXME
            try:
                if t1.year < 2016:
                    raise KNMIBadDate
            except KNMIBadDate:
                print('Data is too old (before 2016) for the FDSN data at KNMI') #FIXME
                continue

            b_stations_dict = {}
            b_streams_dict = {}
            for b in self._bh_stns:
                
                streams_dict = {}
                stations_dict = {}

                stz = Stream()
                st1 = Stream()
                st2 = Stream()

                network = self._inventory_dict[b][0]

                ns = 0
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
                            stz += client.get_waveforms(network.code, station.code, "*", "HHZ", \
                                                              t1, t1 + 60, attach_response = True)
                            
                            # Northish component
                            st1 += client.get_waveforms(network.code, station.code, "*", "HH1", \
                                                              t1, t1 + 60, attach_response = True)
                            
                            # Eastish component
                            st2 += client.get_waveforms(network.code, station.code, "*", "HH2", \
                                                              t1, t1 + 60, attach_response = True)
                            
                        except:
                            l_error_stats.append(station)
                            continue

                        l_istations.append(station)

                    else:
                        l_estations.append(station)


                stations_dict['included'] = l_istations
                stations_dict['excluded'] = l_estations
                stations_dict['error'] = l_error_stats

                stz.detrend(type='demean')
                stz.remove_response()
                st1.detrend(type='demean')
                st1.remove_response()
                st2.detrend(type='demean')
                st2.remove_response()
                streams_dict['Z'] = stz
                streams_dict['1'] = st1
                streams_dict['2'] = st2

                b_stations_dict[b] = stations_dict
                b_streams_dict[b] = streams_dict

            self._evnt_keys.append(ne)
            self._ekey_event_dict[ne] = e
            self._event_stations_dict[ne] = b_stations_dict
            self._event_streams_dict[ne] = b_streams_dict
            ne += 1


    #end __init__()

    def __str__(self):
        return str(self._event_stations_dict)

    def getEventKeys(self):
        return self._evnt_keys

    def getEventDict(self):
        return self._ekey_event_dict

    def getBoreholeKeys(self):
        return self._bh_stns


    def _getStream(self,ekey,bkey,ckey,detrend=True,rem_resp=True):
        assert (ekey in self._event_stations_dict)
        assert (bkey in self._event_stations_dict[ekey])
        assert (ckey in self._chan_keys)

    def getStreamZ(self,ekey,bkey):
        return self._getStream(ekey,bkey,'Z')

    def getStream1(self,bkey):
        return self._getStream(ekey,bkey,'1')

    def getStream2(self,bkey):
        return self._getStream(ekey,bkey,'2')


    def _getStations(self,ekey,bkey,skey):
        assert (ekey in self._event_stations_dict)
        assert (bkey in self._event_stations_dict[ekey])
        assert (skey in self._event_stations_dict[ekey][bkey])
        return self._event_stations_dict[ekey][bkey][skey]

    def getIncludedStations(self,ekey,bkey):
        return self._getStations(ekey,bkey,'included')

    def getExcludedStations(self,ekey,bkey):
        return self._getStations(ekey,bkey,'excluded')

    def getErrorStations(self,ekey,bkey):
        return self._getStations(ekey,bkey,'error')


    def _getCoords(self,stations):
        wgs84_proj = Proj('epsg:4326')
        nl_proj    = Proj('epsg:28992')

        s_xy = np.zeros((len(stations),2),dtype=np.float32)

        si = 0
        for s in stations:

            s_lon = s.longitude
            s_lat = s.latitude
            ex,ey = transform(wgs84_proj,nl_proj,s_lat,s_lon)
            s_xy[si,0] = ex
            s_xy[si,1] = ey

            si += 1

        return s_xy

    def getIncStationCoords(self,ekey,bkey):
        stations = self.getIncludedStations(ekey,bkey)
        return self._getCoords(stations)

    def getExcStationCoords(self,ekey,bkey):
        stations = self.getExcludedStations(ekey,bkey)
        return self._getCoords(stations)

    def getErrStationCoords(self,ekey,bkey):
        stations = self.getErrorStations(ekey,bkey)
        return self._getCoords(stations)



