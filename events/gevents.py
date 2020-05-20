from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from pyproj import Proj, transform
from gnam.model.bbox import bbox as bb
from gnam.events.mtensors import mtensors as tensors
import numpy as np
import copy


class gevents:

    _emag_min = None
    _year_min = None
    _client = None
    _bbox = None
    _icat = None
    _ocat = None
    _ecat = None
    _mts  = None
    _ekeys = None

    def __init__(self,emag_min,bbox=None,year_min=2016):

        self._emag_min = emag_min
        if bbox is not None:
            self._bbox = copy.deepcopy(bbox)
        self._year_min = UTCDateTime(year_min, 1, 1, 0, 0, 0, 0)
        
        self._client = Client('KNMI')
        self._ocat = self._client.get_events(minmagnitude=self._emag_min,starttime=self._year_min)
        self._icat = self._client.get_events(minmagnitude=self._emag_min,starttime=self._year_min)
        self._ecat = self._client.get_events(minmagnitude=self._emag_min,starttime=self._year_min)

        nrem = 0
        ncom = 0
        lrem = []
        lcom = []

        #create list of events to remove

        if self._bbox is not None:
            wgs84_proj = Proj('epsg:4326')
            nl_proj    = Proj('epsg:28992')

            for ic in range(len(self._icat)):
                if self._icat[ic].origins[0].earth_model_id is None:
                    lrem.append(ic)
                    nrem += 1
                    continue

                '''
                if len(self._icat[ic].event_descriptions) == 1:
                    lrem.append(ic)
                    nrem += 1
                    continue

                if self._icat[ic].event_descriptions[1]['text'] != 'The Netherlands':
                    lrem.append(ic)
                    nrem += 1
                    continue
                else:
                    e_lon = self._icat[ic].origins[0].longitude
                    e_lat = self._icat[ic].origins[0].latitude
                    ex,ey = transform(wgs84_proj,nl_proj,e_lat,e_lon)
                    if not self._bbox.coordIsIn(ex,ey):
                        lrem.append(ic)
                        nrem += 1
                        continue
                    else:
                        lcom.append(ic)
                        ncom += 1
                        continue
                '''
                e_lon = self._icat[ic].origins[0].longitude
                e_lat = self._icat[ic].origins[0].latitude
                ex,ey = transform(wgs84_proj,nl_proj,e_lat,e_lon)
                if not self._bbox.coordIsIn(ex,ey):
                    lrem.append(ic)
                    nrem += 1
                    continue
                else:
                    lcom.append(ic)
                    ncom += 1
                    continue

        else:
            for ic in range(len(self._icat)):
                if self._icat[ic].origins[0].earth_model_id is None:
                    lrem.append(ic)
                    nrem += 1
                    continue

                if len(self._icat[ic].event_descriptions) == 1:
                    lrem.append(ic)
                    nrem += 1
                    continue

                if self._icat[ic].event_descriptions[1]['text'] != 'The Netherlands':
                    lrem.append(ic)
                    nrem += 1
                    continue
                else:
                    nloc_n = self._icat[ic].origins[0].earth_model_id.id.find('North')
                    if nloc_n == -1:
                        lrem.append(ic)
                        nrem += 1
                        continue
                    else:
                        lcom.append(ic)
                        ncom += 1
                        continue

        #remove the events that are not from the north
        for rem in lrem[::-1]:
            del self._icat[rem]

        #remove the events form the north (this way we have the complement catalog
        for com in lcom[::-1]:
            del self._ecat[com]

        self._ekeys = list(range(len(self._icat)))

    #end __init__()

    def __getitem__(self,key):
        return self._icat[key]

    def __len__(self):
        return len(self._icat)

    
    def __str__(self):
        return str(self._icat)

    def getEventKeys(self):
        return self._ekeys

    def getIncCatalog(self):
        return self._icat


    def getOrigCatalog(self):
        return self._ocat


    def getExcCatalog(self):
        return self._ecat


    def _getCoords(self,_cat):
        wgs84_proj = Proj('epsg:4326')
        nl_proj    = Proj('epsg:28992')

        e_xy = np.zeros((len(_cat),2),dtype=np.float32)

        for ie in range(len(_cat)):
            e_lon = _cat[ie].origins[0].longitude
            e_lat = _cat[ie].origins[0].latitude
            ex,ey = transform(wgs84_proj,nl_proj,e_lat,e_lon)
            e_xy[ie,0] = ex
            e_xy[ie,1] = ey

        return e_xy

    def _getLocalCoords(self,_cat):

        #get global coords
        xy = self._getCoords(_cat)
        
        #get bbox
        lbbox = self._bbox

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


    def getIncCoords(self):
        return self._getCoords(self._icat)

    def getOrigCoords(self):
        return self._getCoords(self._ocat)

    def getExcCoords(self):
        return self._getCoords(self._ecat)

    def getLocalIncCoords(self):
        return self._getLocalCoords(self._icat)

    def getLocalOrigCoords(self):
        return self._getLocalCoords(self._ocat)

    def getLocalExcCoords(self):
        return self._getLocalCoords(self._ecat)


    def getEventCoord(self,ie):
        wgs84_proj = Proj('epsg:4326')
        nl_proj    = Proj('epsg:28992')

        e = self[ie]

        e_xy = np.zeros((2))
        e_lon = e.origins[0].longitude
        e_lat = e.origins[0].latitude
        ex,ey = transform(wgs84_proj,nl_proj,e_lat,e_lon)
        e_xy[0] = ex
        e_xy[1] = ey

        return e_xy


    def getLocalEventCoord(self,ie):

        #get global coords
        xy = self.getEventCoord(ie)
        
        #get bbox
        lbbox = self._bbox

        #shift global coords to (0,0)
        oc = lbbox.getOrigin()
        xy[0] -= oc[0]
        xy[1] -= oc[1]

        #rotate coordinates to local (rotate clockwise)
        rdeg = lbbox.getRotDeg()
        theta = rdeg*np.pi/180
        rmi = np.array([[np.cos(-theta),-np.sin(-theta)],[np.sin(-theta),np.cos(-theta)]])

        xy = rmi.dot(xy)

        return xy


    def getBBox(self):
        return self._bbox


    def attacheTensors(self,mts):

        self._mts = []
        for mt in mts:
            for e in self._icat:
                etime = e.time
                mtime = mt['Date']
                if (etime.year == mtime.year) & (etime.month == mtime.month) & (etime.day == mtime.day):
                    self._mts.append((e,mt))


    def getIncEventTensorPairs(self):
        assert (self._mts != None)
        return self._mts

