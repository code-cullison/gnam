################################################################################
# NAM Groningen 2017 Model: DeepNL/Utrecht University/Seismology
#
#   Thomas Cullison - t.a.cullison@uu.nl
################################################################################

import pandas as pd
import numpy as np


class nammodel:

    # hard coded: see NAM 2017 report on Groningen Model
    _slp_ns_u  = 0.25   # vp slope     : see NAM 2017 report
    _slp_ns_b  = 2.3    # vp slope     : see NAM 2017 report
    _slp_ck_b  = 1.0    # vp slope     : see NAM 2017 report

    _slp_dc    = 0.541  # vp slope     : see NAM 2017 report
    _isec_dc   = 2572.3 # vp intersect : see NAM 2017 report
    _vp_max_dc = 5000   # max vp       : see NAM 2017 report

    _vp_ze     = 4400   # constant vp  : see NAM 2017 report
    _vp_fltr   = 5900   # constant vp  : see NAM 2017 report
    _vp_zz     = 4400   # constant vp  : see NAM 2017 report
    _vp_base   = 5900   # constant vp  : see NAM 2017 report
    _vp_ro     = 3900   # constant vp  : see NAM 2017 report

    _nx = -1
    _ny = -1
    _is_nxy = False #change once parameters are set

    _pdf_xmin = np.nan
    _pdf_xmax = np.nan
    _pdf_ymin = np.nan
    _pdf_ymax = np.nan

    _dx = 50 # meters, hard coded: see NAM 2017 report
    _dy = 50 # meters, hard coded: see NAM 2017 report

    _vo_pathfname = '' # path and file name to Vo_maps.txt
    _ho_pathfname = '' # path and file name to horizons.txt

    _vo_pdframe = pd.DataFrame() # pandas dataframe for Vo_maps.txt
    _ho_pdframe = pd.DataFrame() # pandas dataframe for horizons.txt
    _is_pdframes = False #change once dataframes are created 

    # x and y coordinates from the raw Vo_maps.txt == horizons.txt
    # NOTE: these coordiante represnt only the coordinates within
    #       the irregular shape polygone 2017 data region
    _pdf_xcoords = np.empty(0,dtype=np.float32) 
    _pdf_ycoords = np.empty(0,dtype=np.float32)
    _is_xycoords = False # changed when arrays are created


    def __init__(self,vo_pathfname,ho_pathfname):
        self._vo_pathfname = vo_pathfname
        self._ho_pathfname = ho_pathfname

        print()
        print()
        print('#######   Vo Maps   #############################################')
        print()
        self._vo_pdframe = pd.read_csv(self._vo_pathfname, delim_whitespace=True)
        print(self._vo_pdframe)
        print()

        print('#######   Horizons   ############################################')
        print()
        self._ho_pdframe = pd.read_csv(self._ho_pathfname, delim_whitespace=True)
        print(self._ho_pdframe)
        print()

        self._is_pdframes = True


        # create np arrays for x and y coordinates
        self._pdf_xcoords = self._vo_pdframe[['XSSP']].to_numpy().astype(np.float32)
        self._pdf_ycoords = self._vo_pdframe[['YSSP']].to_numpy().astype(np.float32)

        self._is_xycoords = True

        print('pdf_xcoords',self._pdf_xcoords)
        print('pdf_ycoords',self._pdf_ycoords)
        print()

        # calc nx
        self._pdf_xmin = np.amin(self._pdf_xcoords)
        self._pdf_xmax = np.amax(self._pdf_xcoords)
        assert ((self._pdf_xmax - self._pdf_xmin)%self._dx) == 0
        self._nx       = int(1) + int((self._pdf_xmax - self._pdf_xmin)/self._dx)

        # calc ny
        self._pdf_ymin = np.amin(self._pdf_ycoords)
        self._pdf_ymax = np.amax(self._pdf_ycoords)
        assert ((self._pdf_ymax - self._pdf_ymin)%self._dy) == 0
        self._ny       = int(1) + int((self._pdf_ymax - self._pdf_ymin)/self._dy)

        self._is_nxy = True

        print('nx,ny = %d,%d' %(self._nx,self._ny))
        print()


    def computeGriddedModel3D(self,dz,maxDepth):

        assert self._is_pdframes
        assert self._is_xycoords 
        assert self._is_nxy 

        nz = int(maxDepth/dz + 1) #NOTE round to zero on purpose

        print('nx   =',self._nx)
        print('ny   =',self._ny)
        print('nz   =',nz)
        print('nxyz =',self._nx*self._ny*nz)

        # get P-veloctiy function intersects
        #NOTE: used + 0.5 for rounding to nearest when creating model -- see below
        ns_vel = self._vo_pdframe[['NS']].to_numpy().astype(np.float32) + 0.5
        ck_vel = self._vo_pdframe[['CK']].to_numpy().astype(np.float32) + 0.5
        me_vel = self._vo_pdframe[['ME']].to_numpy().astype(np.float32) + 0.5

        print('ns_vel:/n',ns_vel)
        print('ck_vel:/n',ck_vel)
        print('me_vel:/n',me_vel)


        # get horizon depths per x,y and convert into indices
        nu_b = ((self._ho_pdframe[['NU_B']].to_numpy()[:,0])/dz + 0.5).astype(int)
        ns_b = ((self._ho_pdframe[['NS_B']].to_numpy()[:,0])/dz + 0.5).astype(int)
        ck_b = ((self._ho_pdframe[['CK_B']].to_numpy()[:,0])/dz + 0.5).astype(int)
        ze_t = ((self._ho_pdframe[['ZE_T']].to_numpy()[:,0])/dz + 0.5).astype(int)
        fl_t = ((self._ho_pdframe[['float_T']].to_numpy()[:,0])/dz + 0.5).astype(int)
        fl_b = ((self._ho_pdframe[['float_B']].to_numpy()[:,0])/dz + 0.5).astype(int)
        zz_t = ((self._ho_pdframe[['ZEZ2A_T']].to_numpy()[:,0])/dz + 0.5).astype(int)
        ro_t = ((self._ho_pdframe[['RO_T']].to_numpy()[:,0])/dz + 0.5).astype(int)
        dc_t = ((self._ho_pdframe[['DC_T']].to_numpy()[:,0])/dz + 0.5).astype(int)

        print('ns_b:/n',ns_b)
        print('ck_b:/n',ck_b)
        print('ze_t:/n',ze_t)
        print('fl_t:/n',fl_t)
        print('fl_b:/n',fl_b)
        print('zz_t:/n',zz_t)
        print('ro_t:/n',ro_t)
        print('dc_t:/n',dc_t)


        ix = np.copy(self._pdf_xcoords)
        ix = (ix - self._pdf_xmin)/self._dx
        ix = ix.astype(int)

        iy = np.copy(self._pdf_ycoords)
        iy = (iy - self._pdf_ymin)/self._dy
        iy = iy.astype(int)

        props = np.zeros((3,self._nx,self._ny,nz),order='C').astype(np.short)
        print('props.shape:',props.shape)
        print()


    #############################################
    # Compute subsurface properties at depth

        print('Computing the FULL rectangular volume for NAM 2017 model')

        # track every 5% increment below
        perc_5 = int(len(ix)/20 + 0.5)

        # scaling factors for VP
        #NOTE: I used arange instead of linspace for consistance in accuracy (consistent precision)
        #NOTE: used arrays (extra memory) to speed up computation
        z_ns_u = np.arange(nz,dtype=np.float)*dz*self._slp_ns_u
        z_ns_b = np.arange(nz,dtype=np.float)*dz*self._slp_ns_b
        z_ck_b = np.arange(nz,dtype=np.float)*dz*self._slp_ck_b
        z_dc   = np.arange(nz,dtype=np.float)*dz*self._slp_dc + self._isec_dc
        z_dc[z_dc > self._vp_max_dc] = self._vp_max_dc  # see NAM 2017 report on Groningen Model

        # scaling factors for computing VS from VP
        vs_nb_u      = 1/(4.782 + np.arange(nz,dtype=np.float)*dz*0.0047)
        vs_ns_b_slp  = 1/3.2
        vs_ck_b_slp  = 0.6045
        vs_ck_b_isec = -415.6
        vs_ze_t_slp  = 0.7423
        vs_ze_t_isec = -745.003
        vs_fl_t      = 2486
        vs_fl_b      = 3238
        vs_zz_t      = 2486
        vs_ro_t      = 3238
        vs_dc_t      = 2286
        vs_dc_b_slp  = 0.927
        vs_dc_b_isec = -1547.313


        rho_scale  = 1000                   #(convert from g/cm^3 to kg/m^3
        spm2uspft  = 1000000/3.28084        # convert s/m to us/ft
        rho_nb_u      = 2.04*rho_scale
        rho_ns_b_slp  = -0.00285*spm2uspft
        rho_ns_b_isec = 2.452
        rho_ck_b_slp  = -0.01076*spm2uspft
        rho_ck_b_isec = 3.305
        rho_ze_t_slp  = -0.01*spm2uspft
        rho_ze_t_isec = 3.3
        rho_fl_t      = 2.09*rho_scale
        rho_fl_b      = 2.81*rho_scale
        rho_zz_t      = 2.09*rho_scale
        rho_ro_t      = 2.81*rho_scale
        rho_dc_t      = 2.46*rho_scale
        rho_dc_b      = 2.65*rho_scale

        
        #loop over x,y coords where there is data and fill in RecVol
        for ixy in range(len(ix)):
            
            #create indicies
            iix = ix[ixy]
            iiy = iy[ixy]
            ins = ns_b[ixy]+1
            inu = nu_b[ixy]+1
            ick = ck_b[ixy]+1
            ize = ze_t[ixy]
            ift = fl_t[ixy]
            ifb = fl_b[ixy]+1
            izz = zz_t[ixy]
            iro = ro_t[ixy]
            idc = dc_t[ixy]


            props[0,iix,iiy,:ins] = z_ns_u[:ins] + ns_vel[ixy] 
            props[1,iix,iiy,:inu] = props[0,iix,iiy,:inu] * vs_nb_u[:inu] 
            props[1,iix,iiy,inu:ins] = props[0,iix,iiy,inu:ins] * vs_ns_b_slp
            props[2,iix,iiy,:inu] = rho_nb_u
            props[2,iix,iiy,inu:ins] = ((1/props[0,iix,iiy,inu:ins])*rho_ns_b_slp+rho_ns_b_isec)*rho_scale


            props[0,iix,iiy,ins:ick] = z_ns_b[ins:ick] + ck_vel[ixy] 
            props[1,iix,iiy,ins:ick] = props[0,iix,iiy,ins:ick]*vs_ck_b_slp + vs_ck_b_isec
            props[2,iix,iiy,ins:ick] = ((1/props[0,iix,iiy,ins:ick])*rho_ck_b_slp+rho_ck_b_isec)*rho_scale


            props[0,iix,iiy,ick:ize] = z_ck_b[ick:ize] + me_vel[ixy] 
            props[1,iix,iiy,ick:ize] = props[0,iix,iiy,ick:ize]*vs_ze_t_slp + vs_ze_t_isec
            props[2,iix,iiy,ick:ize] = ((1/props[0,iix,iiy,ick:ize])*rho_ze_t_slp+rho_ze_t_isec)*rho_scale


            props[0,iix,iiy,ize:ift] = self._vp_ze
            props[1,iix,iiy,ize:ift] = vs_fl_t
            props[2,iix,iiy,ize:ift] = rho_fl_t


            props[0,iix,iiy,ift:ifb] = self._vp_fltr
            props[1,iix,iiy,ift:ifb] = vs_fl_b
            props[2,iix,iiy,ift:ifb] = rho_fl_b


            props[0,iix,iiy,ifb:izz] = self._vp_zz
            props[1,iix,iiy,ifb:izz] = vs_zz_t
            props[2,iix,iiy,ifb:izz] = rho_zz_t

            #for iz in range(izz,iro):
            props[0,iix,iiy,izz:iro] = self._vp_base
            props[1,iix,iiy,izz:iro] = vs_ro_t
            props[2,iix,iiy,izz:iro] = rho_ro_t

            #for iz in range(iro,idc):
            props[0,iix,iiy,iro:idc] = self._vp_ro
            props[1,iix,iiy,iro:idc] = vs_dc_t
            props[2,iix,iiy,iro:idc] = rho_dc_t

            #for iz in range(idc,nz):
            props[0,iix,iiy,idc:nz] = z_dc[idc:nz]
            props[1,iix,iiy,idc:nz] = \
                    props[0,iix,iiy,idc:nz]*vs_dc_b_slp + vs_dc_b_isec
            props[2,iix,iiy,idc:nz] = rho_dc_b

            if (ixy % perc_5) == 0:
                print(props[0,iix,iiy,:])
                print('Currently %d percent finished computing volume' % int((ixy//perc_5)*5))
        print('Currently 100 percent finished computing volume')
        print('rectanular model dtype:',props.dtype)
        print('rectanular model shape:',props.shape)
        xdata = np.array([self._pdf_xmin,self._dx,self._nx])
        ydata = np.array([self._pdf_ymin,self._dy,self._ny])
        zdata = np.array([0.0,dz,nz])
        
        return (props,xdata,ydata,zdata)


##############################################################
# Testing Driver (main)
'''
mymod = nammodel('./data/Vo_maps.txt','./data/horizons.txt')

mymod.readRawData()

mydz = 50
myMaxDepth = 6000
mydata = mymod.computeRecVol(mydz,myMaxDepth)

myprops = mydata[0]
my_xdata = mydata[1]
my_ydata = mydata[2]
my_zdata = mydata[3]

ofilename = './rect_gron_model_z'
"""
print('Saving compressed VP model to disk at: %s%d_%s' %(ofilename,mydz,'vp'))
np.savez_compressed(ofilename+str(int(mydz))+'_vp.npz',props=myprops[0,:,:,:],xd=my_xdata,yd=my_ydata,zd=my_zdata)
print('Saving compressed VS model to disk at: %s%d_%s' %(ofilename,mydz,'vs'))
np.savez_compressed(ofilename+str(int(mydz))+'_vs.npz',props=myprops[1,:,:,:],xd=my_xdata,yd=my_ydata,zd=my_zdata)
print('Saving compressed Rho model to disk at: %s%d_%s' %(ofilename,mydz,'rho'))
np.savez_compressed(ofilename+str(int(mydz))+'_rho.npz',props=myprops[2,:,:,:],xd=my_xdata,yd=my_ydata,zd=my_zdata)
"""
print('Saving compressed VP model to disk at: %s%d_%s' %(ofilename,mydz,'props'))
np.savez_compressed(ofilename+str(int(mydz))+'_props.npz',props=myprops[:,:,:,:],xd=my_xdata,yd=my_ydata,zd=my_zdata)
'''
