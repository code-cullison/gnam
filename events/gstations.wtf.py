from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from obspy import Stream
from pyproj import Proj, transform
from gnam.events.gevents import gevents as ge
from gnam.model.bbox import bbox as bb
import numpy as np
import copy
import time


class gstations:
    
    _ge = None
    _knmi_inventory_dict = None
    _inventory_dict = None
    _exc_inventory_dict = None
    _inc_inventory_dict = None
    _bh_stns = None
    _prefilt = None
    _setup_time = None


    def __init__(self,ge,bh_stns=(3,4),prefilt=(0.4, 0.5, 45.0, 47.5)):

        start_t = time.time()

        self._ge = ge
        self._knmi_inventory_dict = {}
        self._inventory_dict = {}
        self._inc_inventory_dict = {}
        self._exc_inventory_dict = {}
        self._bh_stns = bh_stns
        self._prefilt = prefilt
        self._evnt_keys = []
        self._ekey_event_dict = {}

        client = Client("KNMI")

        #get station inventories for locations and borehole depths
        for b in self._bh_stns:
            sb = str(b)
            gstats_str = 'G0*'+sb+',G1*'+sb+',G2*'+sb+',G3*'+sb+',G4*'+sb+',G5*'+sb+',G6*'+sb+',G70*'+sb
            self._knmi_inventory_dict[b] = client.get_stations(network="NL", station=gstats_str , level="response")


        if self._ge.getBBox() is None:

            for b in self._bh_stns:
                self._inc_inventory_dict[b] = self._knmi_inventory_dict[b] 

                network = self._knmi_inventory_dict[b][0]
                exc_inv_b = Inventory( networks=[network.code], source='Thomas_Cullison')
                self._exc_inventory_dict[b] = exc_inv_b

        else:

            wgs84_proj = Proj('epsg:4326')
            nl_proj    = Proj('epsg:28992')

            for b in self._bh_stns:
                
                network = self._knmi_inventory_dict[b][0]

                inc_inv_b = Inventory( networks=[network.code], source='Thomas_Cullison')
                exc_inv_b = Inventory( networks=[network.code], source='Thomas_Cullison')

                ns = 0
                for station in network:
                    e_lon = station.longitude
                    e_lat = station.latitude
                    ex,ey = transform(wgs84_proj,nl_proj,e_lat,e_lon)

                    is_in = self._ge.getBBox().coordIsIn(ex,ey)

                    if is_in:
                        inc_inv_b.append(station)
                    else:
                        exc_inv_b.append(station)


                self._inc_inventory_dict[b] = inc_inv_b 
                self._exc_inventory_dict[b] = exc_inv_b 

            #end b loop

            self._inventory_dict['included'] = self._inc_inventory_dict
            self._inventory_dict['excluded'] = self._exc_inventory_dict

        self._setup_time = time.time() - start_t

    #end __init__()

    def __str__(self):
        return self._inventory_dict

    def getSetupTime(self):
        return self._setup_time

    def getBoreholeKeys(self):
        return self._bh_stns

    def _getStream(self,ekey,bkey,ckey,t2=-1):

        assert (0 <= ekey) & (ekey < len(self._ge))
        assert (bkey in self._bh_stns)
        assert (ckey == 'Z') | (ckey == '1') | (ckey == '2')

        e = self._ge[ekey]
        t1 = e.origins[0].time
        if t2 < 0:
            t2 = t1 + 16384//200 + 1

        try:
            if t1.year < 2016:
                raise KNMIBadDate
        except KNMIBadDate:
            print('Data is too old (before 2016) for the FDSN data at KNMI') #FIXME
            continue


        network = self._knmi_inventory_dict[x][0]

        stz = Stream()
        st1 = Stream()
        st2 = Stream()

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
