from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from pyproj import Proj, transform
from gnam.model.bbox import bbox as bb
import pandas as pd
import numpy as np
import copy


class moment_tensor:


    _data = None

    _aki_tensor = None
    _cmt_tensor = None

    def __init__(self,date,mag,lat,lon,x,y,z,sz,strike,dip,rake,iso,siso,cldv,scldv,M0=1.0,rdeg=0):

        mod_strike = strike + rdeg
        if 360 <= mod_strike:
            mod_strike -= 360
        elif mod_strike < 0:
            mod_strike += 360

        self._data = {}
        self._data['Date'      ] = UTCDateTime(date)
        self._data['ML'        ] = mag
        self._data['M0'        ] = M0
        self._data['Lat'       ] = lat
        self._data['Lon'       ] = lon
        self._data['XC'        ] = x
        self._data['YC'        ] = y
        self._data['ZC'        ] = z
        self._data['ZC +/-'    ] = sz
        self._data['rotdeg'    ] = rdeg
        self._data['o-Strike'  ] = strike
        self._data['Strike'    ] = mod_strike
        self._data['Dip'       ] = dip
        self._data['Rake'      ] = rake
        self._data['ISO%'      ] = iso
        self._data['ISO%  +/-' ] = siso
        self._data['CLDV%'     ] = cldv
        self._data['CLDB% +/-' ] = scldv


        deg2rad = np.pi/180
        rstrike = deg2rad*mod_strike
        rdip    = deg2rad*dip
        rrake   = deg2rad*rake

        #Aki and Richards
        Mxx = -( np.sin(rdip)*np.cos(rrake)*np.sin(2*rstrike) + np.sin(2*rdip)*np.sin(rrake)*(np.sin(rstrike)**2) )
        Myy =  ( np.sin(rdip)*np.cos(rrake)*np.sin(2*rstrike) - np.sin(2*rdip)*np.sin(rrake)*(np.cos(rstrike)**2) )
        #Mzz =  (np.sin(2*rdip)*np.sin(rrake))
        Mzz = -( Mxx + Myy )
        Mxy =  ( np.sin(rdip)*np.cos(rrake)*np.cos(2*rstrike) + 0.5*np.sin(2*rdip)*np.sin(rrake)*np.sin(2*rstrike) )
        Mxz = -( np.cos(rdip)*np.cos(rrake)*np.cos(rstrike)   + np.cos(2*rdip)*np.sin(rrake)*np.sin(rstrike) )
        Myz = -( np.cos(rdip)*np.cos(rrake)*np.sin(rstrike)   - np.cos(2*rdip)*np.sin(rrake)*np.cos(rstrike) )

        Mxx *= M0
        Myy *= M0
        Mzz *= M0
        Mxy *= M0
        Mxz *= M0
        Myz *= M0

        self._aki_tensor = {'Mxx':Mxx,'Myy':Myy,'Mzz':Mzz,'Mxy':Mxy,'Mxz':Mxz,'Myz':Myz}
        self._data['Aki & Richards Tensor'] = self._aki_tensor

        # Harvard CMT
        Mtt = Mxx
        Mpp = Myy
        Mrr = Mzz
        Mtp = -1.0*Mxy
        Mrt = Mxz
        Mrp = -1.0*Myz

        self._cmt_tensor = {'Mtt':Mtt,'Mpp':Mpp,'Mrr':Mrr,'Mtp':Mtp,'Mrt':Mrt,'Mrp':Mrp}
        self._data['Harvard CMT'] = self._cmt_tensor


    def __getitem__(self,key):
        return self._data[key]

    def __str__(self):
        return str(self._data)

    def set_utc_datetime(self,utc_dt):
        assert type(utc_dt) == type(UTCDateTime())
        self._data['Date'] = utc_dt
        

    def get_aki_tensor_dict(self):
        return self._aki_tensor

    def get_aki_tensor_matrix(self):

        aki_matrix = np.zeros((3,3))
        aki_matrix[0,0] = self._aki_tensor['Mxx']
        aki_matrix[1,1] = self._aki_tensor['Myy']
        aki_matrix[2,2] = self._aki_tensor['Mzz']

        aki_matrix[0,1] = self._aki_tensor['Mxy']
        aki_matrix[1,0] = self._aki_tensor['Mxy']

        aki_matrix[0,2] = self._aki_tensor['Mxz']
        aki_matrix[2,0] = self._aki_tensor['Mxz']

        aki_matrix[1,2] = self._aki_tensor['Myz']
        aki_matrix[2,1] = self._aki_tensor['Myz']

        return aki_matrix

    def get_aki_tensor_utri(self):

        #match obspy format (M11, M22, M33, M12, M13, M23)
        aki_array = np.zeros((6))
        aki_array[0] = self._aki_tensor['Mxx']
        aki_array[1] = self._aki_tensor['Myy']
        aki_array[2] = self._aki_tensor['Mzz']
        aki_array[3] = self._aki_tensor['Mxy']
        aki_array[4] = self._aki_tensor['Mxz']
        aki_array[5] = self._aki_tensor['Myz']

        return aki_array


    def get_cmt_tensor_dict(self):
        return self._cmt_tensor

    def get_cmt_tensor_matrix(self):

        cmt_matrix = np.zeros((3,3))
        cmt_matrix[0,0] = self._cmt_tensor['Mrr']
        cmt_matrix[1,1] = self._cmt_tensor['Mtt']
        cmt_matrix[2,2] = self._cmt_tensor['Mpp']

        cmt_matrix[0,1] = self._cmt_tensor['Mrt']
        cmt_matrix[1,0] = self._cmt_tensor['Mrt']

        cmt_matrix[0,2] = self._cmt_tensor['Mrp']
        cmt_matrix[2,0] = self._cmt_tensor['Mrp']

        cmt_matrix[1,2] = self._cmt_tensor['Mtp']
        cmt_matrix[2,1] = self._cmt_tensor['Mtp']

        return cmt_matrix

    def get_cmt_tensor_utri(self):

        #match obspy format (M11, M22, M33, M12, M13, M23)
        cmt_array = np.zeros((6))
        cmt_array[0] = self._cmt_tensor['Mrr']
        cmt_array[1] = self._cmt_tensor['Mtt']
        cmt_array[2] = self._cmt_tensor['Mpp']
        cmt_array[3] = self._cmt_tensor['Mrt']
        cmt_array[4] = self._cmt_tensor['Mrp']
        cmt_array[5] = self._cmt_tensor['Mtp']

        return cmt_array


