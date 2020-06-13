from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from obspy import Stream
from pyproj import Proj, transform
from gnam.events.gevents import gevents as ge
from gnam.model.bbox import bbox as bb
import numpy as np
import copy
import datetime


class gstations:
    
    _ge = None
    _event_stations_dict = None
    _event_streams_dict = None
    _inventory_dict = None
    _prefilt = None
    _evnt_keys = None
    _bh_stns = None
    _skeys = None
    _ekey_event_dict = None


    def __init__(self,ge,tend=-1,bkeys=(3,4),prefilt=(0.4, 0.5, 45.0, 47.5)):

        self._ge = ge
        self._event_stations_dict = {}
        self._event_streams_dict = {}
        self._inventory_dict = {}
        self._prefilt = prefilt
        self._evnt_keys = []
        self._bh_stns = bkeys
        self._skeys = ('included','excluded','error')
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
        tot_ne = len(ecat)
        for e in ecat:
            print('Getting Stations from Event: (%d out of %d)' %(ne,tot_ne))
            t1 = e.origins[0].time
            if tend < 0:
                t2 = t1 + 16384//200 + 1 #FIXME
            try:
                if t1.year < 2016:
                    raise KNMIBadDate
            except KNMIBadDate:
                print('Data is too old (before 2016) for the FDSN data at KNMI') #FIXME
                continue

            #t2 = t1 + 2 #FIXME: just for testing

            t2 = t1 + tend 

            print()
            print('T2:',t2)
            print()

            b_stations_dict = {}
            b_streams_dict = {}
            for b in self._bh_stns:
                print('Getting Stations from Chanel: %d' %(b))

                l_istations = []
                l_estations = []
                l_error_stats = []
                
                streams_dict = {}
                stations_dict = {}

                stz = Stream()
                st1 = Stream()
                st2 = Stream()

                network = self._inventory_dict[b][0]

                ns = 0
                for station in network:
                    print('Getting Station: %d' %(ns))
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
                                                              t1, t2, attach_response=False)
                                                              #t1, t2, attach_response = True)
                            
                            # Northish component
                            st1 += client.get_waveforms(network.code, station.code, "*", "HH1", \
                                                              t1, t2, attach_response=False)
                                                              #t1, t2, attach_response = True)
                            
                            # Eastish component
                            st2 += client.get_waveforms(network.code, station.code, "*", "HH2", \
                                                              t1, t2, attach_response=False)
                                                              #t1, t2, attach_response = True)
                            
                        except:
                            l_error_stats.append(station)
                            continue

                        l_istations.append(station)

                    else:
                        l_estations.append(station)

                    ns += 1


                stations_dict['included'] = l_istations
                stations_dict['excluded'] = l_estations
                stations_dict['error'] = l_error_stats

                stz.attach_response(self._inventory_dict[b])
                stz.detrend(type='demean')
                stz.remove_response(output="DISP")

                st1.attach_response(self._inventory_dict[b])
                st1.detrend(type='demean')
                st1.remove_response(output="DISP")

                st2.attach_response(self._inventory_dict[b])
                st2.detrend(type='demean')
                st2.remove_response(output="DISP")

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


    def _getStream(self,ekey,bkey,ckey):
        assert (ekey in self._event_streams_dict)
        assert (bkey in self._event_streams_dict[ekey])
        assert (ckey in self._event_streams_dict[ekey][bkey])
        return self._event_streams_dict[ekey][bkey][ckey]

    def getStreamZ(self,ekey,bkey):
        return self._getStream(ekey,bkey,'Z')

    def getStream1(self,ekey,bkey):
        return self._getStream(ekey,bkey,'1')

    def getStream2(self,ekey,bkey):
        return self._getStream(ekey,bkey,'2')


    def _getStations(self,ekey,bkey,skey):
        assert (ekey in self._event_stations_dict)
        assert (bkey in self._event_stations_dict[ekey])
        assert (skey in self._event_stations_dict[ekey][bkey])
        return self._event_stations_dict[ekey][bkey][skey]

    def getIncludedStations(self,ekey,bkey):
        return self._getStations(ekey,bkey,'included')
        #return self._getStations(ekey,bkey,self._skeys(0))

    def getExcludedStations(self,ekey,bkey):
        return self._getStations(ekey,bkey,'excluded')
        #return self._getStations(ekey,bkey,self._skeys(1))

    def getErrorStations(self,ekey,bkey):
        return self._getStations(ekey,bkey,'error')
        #return self._getStations(ekey,bkey,self._skeys(2))


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

    def _getLocalCoords(self,stations):

        #get global coords
        xy = self._getCoords(stations)
        
        #get bbox
        lbbox = self._ge.getBBox()

        #shift global coords to (0,0)
        oc = lbbox.getOrigin()
        xy[:,0] -= oc[0]
        xy[:,1] -= oc[1]

        #rotate coordinates to local (rotate clockwise)
        rdeg = lbbox.getRotDeg()
        theta = rdeg*np.pi/180
        rmi = np.array([[np.cos(-theta),-np.sin(-theta)],[np.sin(-theta),np.cos(-theta)]])

        for i in range(len(xy[:,0])):
            xy[i,:] = rmi.dot(xy[i,:])

        return xy


    def _getCodes(self,stations):

        l_station_codes = []
        for s in stations:
            l_station_codes.append(s.code)

        return l_station_codes


    def getIncStationCodes(self,ekey,bkey):
        stations = self.getIncludedStations(ekey,bkey)
        return self._getCodes(stations)

    def getExcStationCodes(self,ekey,bkey):
        stations = self.getExcludedStations(ekey,bkey)
        return self._getCodes(stations)

    def getErrStationCodes(self,ekey,bkey):
        stations = self.getErrorStations(ekey,bkey)
        return self._getCodes(stations)


    def getIncStationCoords(self,ekey,bkey):
        stations = self.getIncludedStations(ekey,bkey)
        return self._getCoords(stations)

    def getExcStationCoords(self,ekey,bkey):
        stations = self.getExcludedStations(ekey,bkey)
        return self._getCoords(stations)

    def getErrStationCoords(self,ekey,bkey):
        stations = self.getErrorStations(ekey,bkey)
        return self._getCoords(stations)


    def getLocalIncStationCoords(self,ekey,bkey):
        stations = self.getIncludedStations(ekey,bkey)
        return self._getLocalCoords(stations)

    def getLocalExcStationCoords(self,ekey,bkey):
        stations = self.getExcludedStations(ekey,bkey)
        return self._getLocalCoords(self,stations)

    def getLocalErrStationCoords(self,ekey,bkey):
        stations = self.getErrludedStations(ekey,bkey)
        return self._getLocalCoords(self,stations)

    def saveStreams2File(self,dname,rfname):
        sav_stream = Stream()
        for ekey in self._evnt_keys:
            for bkey in self._bh_stns:
                sav_stream += self.getStreamZ(ekey,bkey)
                sav_stream += self.getStream1(ekey,bkey)
                sav_stream += self.getStream2(ekey,bkey)
        
        now = datetime.datetime.now()
        tstamp = '_' + now.day + '_' + now.month + '_' + now.year + '.' + now.hour + '.' + now.min
        path_fname = dname + rfname + tstamp
        sav_stream.write(path_fname, format="MSEED")


    def correct_stations(self,func_p):

        skeys = ('included','excluded','error')
        for ekey in self._evnt_keys:
            for bkey in self._bh_stns:
                for skey in skeys:
                #for skey in self._skeys:

                    stations = self._getStations(ekey,bkey,skey)
                    func_p(stations)
                    self._event_stations_dict[ekey][bkey][skey] = stations


    def get_inventory(self,bkey):
        return self._inventory_dict[bkey]
