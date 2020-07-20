from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from obspy.imaging.beachball import beach
from pyproj import Proj, transform
from gnam.model.bbox import bbox as bb
from gnam.events.moment_tensor import moment_tensor
#from gnam.events.gevents import gevents as gevents
import pandas as pd
import numpy as np
import copy


class mtensors:


    _df    = None
    _nmt   = 0
    _l_mts = None

    def __init__(self,cvs_fname):

        self._df  = pd.io.parsers.read_csv(cvs_fname,sep=',',index_col=0)
        self._nmt = self._df.shape[0]

        dates = self.get_dates()
        assert len(dates) == self._nmt

        mags  = self.get_mags()
        assert len(mags) == self._nmt

        lats  = self.get_lats()
        assert len(lats) == self._nmt

        lons  = self.get_lons()
        assert len(lons) == self._nmt

        xc    = self.get_xcoords()
        #print('inside xc:\n',xc)
        assert len(xc) == self._nmt

        yc    = self.get_ycoords()
        assert len(yc) == self._nmt

        zc    = self.get_zcoords()
        assert len(zc) == self._nmt

        zcb   = self.get_zcoord_bounds()
        assert len(zcb) == self._nmt

        strks = self.get_strikes()
        assert len(strks) == self._nmt

        dips  = self.get_dip()
        assert len(dips) == self._nmt

        rakes = self.get_rake()
        assert len(rakes) == self._nmt

        iso   = self.get_iso_percents()
        assert len(iso) == self._nmt

        isob  = self.get_iso_percent_bounds()
        assert len(isob) == self._nmt

        clvd  = self.get_clvd_percents()
        assert len(clvd) == self._nmt

        clvdb = self.get_clvd_percent_bounds()
        assert len(clvdb) == self._nmt

        self._l_mts = []
        for m in range(self._nmt):
            #FIXME: allow function pointer?
            ML = mags[m]
            MW = ML
            if ML <= 2.0: 
                MW = 0.056262*ML**2 + 0.65553*ML + 0.4968 
            #p = 1.5*MW + 9.1 #KNMI/NAM Relation (Kanamori 1977)
            p = 1.5*MW + 16.1 # in dyn-cm instead of N-m as abaove
            M0 = 10**p
            new_mt = moment_tensor(dates[m],mags[m],lats[m],lons[m],xc[m],    \
                                   yc[m],zc[m],zcb[m],strks[m],dips[m],       \
                                   rakes[m],iso[m],isob[m],clvd[m],clvdb[m],M0)
            self._l_mts.append(new_mt)


    def __getitem__(self,key):
        return self._l_mts[key]

    def __str__(self):
        return str(self._df)

    def __len__(self):
        return self._nmt
        

    def _get_values_list(self,key):
        col_keys = self._df.keys()
        assert (key in col_keys)
        vals = self._df[key].to_numpy()
        l_vals = []

        if key == 'Date':
            for d in vals:
                l_vals.append(UTCDateTime(d))
        else:
            for v in vals:
                l_vals.append(v)

        return l_vals


    def get_dates(self):
        return self._get_values_list('Date')

    def get_mags(self):
        return self._get_values_list('ML')

    def get_lats(self):
        return self._get_values_list('Latitude')

    def get_lons(self):
        return self._get_values_list('Longitude')

    def get_xcoords(self):
        return self._get_values_list('X-rd')

    def get_ycoords(self):
        return self._get_values_list('Y-rd')

    def get_zcoords(self):
        return self._get_values_list('Depth')

    def get_zcoord_bounds(self):
        return self._get_values_list('Depth +/-')

    def get_strikes(self):
        return self._get_values_list('Strike')

    def get_dip(self):
        return self._get_values_list('Dip')

    def get_rake(self):
        return self._get_values_list('Rake')

    def get_iso_percents(self):
        return self._get_values_list('Perc ISO')

    def get_iso_percent_bounds(self):
        return self._get_values_list('Perc ISO +/-')

    def get_clvd_percents(self):
        return self._get_values_list('Perc CLVD')

    def get_clvd_percent_bounds(self):
        return self._get_values_list('Perc CLVD +/-')


    def get_df(self):
        return self._df

    def get_moment_tensor_list(self):
        return self._l_mts

    def get_aki_beachballs(self,diam=50,fc='blue'):

        l_bball = []
        for imt in range(self._nmt):
            mt = self._l_mts[imt].get_aki_tensor_utri()
            xc = self._l_mts[imt]['XC']
            yc = self._l_mts[imt]['YC']
            #print('x,y = %f,%f' %(xc,yc))
            ball = beach(mt, xy=(xc, yc), width=diam, facecolor=fc)
            l_bball.append(ball)

        return l_bball

    def get_cmt_beachballs(self,diam=50,fc='blue'):

        l_bball = []
        for imt in range(self._nmt):
            mt = self._l_mts[imt].get_cmt_tensor_utri()
            xc = self._l_mts[imt]['XC']
            yc = self._l_mts[imt]['YC']
            ball = beach(mt, xy=(xc, yc), width=diam, facecolor=fc)
            l_bball.append(ball)

        return l_bball


    def update_utcdatetime(self,ecat):

        new_l_mts = []
        #ie_start = 0
        for mt in self._l_mts:
            #for ie in range(ie_start,len(ecat)):
            for ie in range(len(ecat)):
                etime = ecat[ie].origins[0].time
                mtime = mt['Date']
                if (etime.year == mtime.year) & (etime.month == mtime.month) & (etime.day == mtime.day):
                    mt.set_utc_datetime(etime)
                    #ie_start = ie+1
                    #break


    def map_events_2_tensors(self,ecat):

        emap = {}
        for mt in self._l_mts:
            for ie in range(len(ecat)):
                etime = ecat[ie].origins[0].time
                mtime = mt['Date']
                if (etime.year == mtime.year) & (etime.month == mtime.month) & (etime.day == mtime.day):
                    emap[ie] = mt

        return emap


