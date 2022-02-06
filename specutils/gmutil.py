################################################################################
# NAM Groningen 2017 Model: DeepNL/Utrecht University/Seismology
#
#   Thomas Cullison - t.a.cullison@uu.nl
################################################################################

import numpy as np
import time
from tqdm import trange, tqdm_notebook

mod_perc = 10

class gmutil:

    dummy = ''

    def __init__(self):
      dummy = 'still dumb'


    #############################################
    #
    # Create and write nodes file
    #
    #############################################
    def writeNodes2File(self,fpath,gm3d):

        '''
        props = data['props']
        xdata = data['xd']
        ydata = data['yd']
        zdata = data['zd']
        print('writeNodes: props.shape:',props.shape)

        nx = int(xdata[2])
        ny = int(ydata[2])
        nz = int(zdata[2])

        dx = int(xdata[1])
        dy = int(ydata[1])
        dz = int(zdata[1])

        nxp1 = int(nx + 1)
        nyp1 = int(ny + 1)
        nzp1 = int(nz + 1)

        xmin = xdata[0]
        ymin = ydata[0]
        zmin = zdata[0]
        '''

        props = gm3d.getNPArray()

        nx    = gm3d.get_npoints()[0]
        ny    = gm3d.get_npoints()[1]
        nz    = gm3d.get_npoints()[2]
        
        dx    = gm3d.get_deltas()[0]
        dy    = gm3d.get_deltas()[1]
        dz    = gm3d.get_deltas()[2]

        nxp1 = int(nx + 1)
        nyp1 = int(ny + 1)
        nzp1 = int(nz + 1)

        # local cordiante but FIXME: model must have z start had half dz
        xmin = 0.0
        ymin = 0.0
        zmin = -1*gm3d.get_gorigin()[2]
#         print('dz:',dz)
#         print('zmin:',zmin)
        assert zmin == -0.5*dz



        #
        # 8 nodes define each cell
        #
        np_x = xmin - 0.5*dx + dx*np.arange(nxp1).reshape((1,nxp1))
        np_y = ymin - 0.5*dy + dy*np.arange(nyp1).reshape((nyp1,1))
        np_z = zmin + 0.5*dz - dz*np.arange(nzp1)
        np_z = np_z[::-1]

#         print('np_z:\n',np_z)


        nodes = np.zeros((nyp1,nxp1,2))
        nodes[:,:,0] = nodes[:,:,0] + np_x
        nodes[:,:,1] = nodes[:,:,1] + np_y

        del np_x
        del np_y

        nodes = nodes.reshape(-1,2)

        #############################
        # Write nodes

        f = open('%s/nodes_coords_file' % fpath, 'w')
        f.write('%d\n' %(nxp1*nyp1*nzp1))
        z_stride = 0
        str_nodes = []
        for iiz in tqdm_notebook(range(nzp1),desc="write nodes"):
            for ixy in tqdm_notebook(range(nxp1*nyp1),desc="iterate XY per Z",leave=False):
                str_nodes.append('%9d %10.1f %10.1f %10.1f\n' % (iiz*nxp1*nyp1 + ixy + 1, nodes[ixy,0], nodes[ixy,1], np_z[iiz]))
            if (iiz+1)%mod_perc == 0 or iiz == nzp1-1:
                f.writelines(str_nodes)
                del str_nodes
                str_nodes = []
        f.close()
        del np_z

    #end def writeNodes2File


    #############################################
    #
    # Create and write Mesh files 
    #
    #############################################
    def writeMesh2Files(self,fpath,gm3d):

        #######################
        # Create cells
        mesh      = []
        mats      = []
        nummats   = []
        xminfaces = []
        xmaxfaces = []
        yminfaces = []
        ymaxfaces = []
        zminfaces = []
        zmaxfaces = []

        '''
        props = data['props']
        xdata = data['xd']
        ydata = data['yd']
        zdata = data['zd']

        nx = int(xdata[2])
        ny = int(ydata[2])
        nz = int(zdata[2])

        dx = int(xdata[1])
        dy = int(ydata[1])
        dz = int(zdata[1])

        nxp1 = int(nx + 1)
        nyp1 = int(ny + 1)
        nzp1 = int(nz + 1)
        '''

        props = gm3d.getNPArray()

        nx    = gm3d.get_npoints()[0]
        ny    = gm3d.get_npoints()[1]
        nz    = gm3d.get_npoints()[2]
        
        dx    = gm3d.get_deltas()[0]
        dy    = gm3d.get_deltas()[1]
        dz    = gm3d.get_deltas()[2]

        nxp1 = int(nx + 1)
        nyp1 = int(ny + 1)
        nzp1 = int(nz + 1)

        vp  = props[0,:,:,::-1]
        vs  = props[1,:,:,::-1]
        rho = props[2,:,:,::-1]
        Qu  = props[3,:,:,::-1]

        f = open('%s/mesh_file' % fpath, 'w')
        f.write('%ld\n' % (nx*ny*nz))
        f.close()

        mf = open('%s/materials_file' % fpath, 'w')
        mf.close()

        nmf = open('%s/nummaterial_velocity_file' % fpath, 'w')
        nmf.close()
        
        i_e = 0
        cv = np.zeros((8),dtype=np.int32)
        sgn = -1 
        for iz in tqdm_notebook(range(nz),desc="write files"):
            for iy in tqdm_notebook(range(ny),desc="iterate XY per Z",leave=False):
                for ix in range(nx):

                    #
                    # Work out corner points
                    #
                    
                    # Bottom face
                    #a
                    cv[0] = ix + iy*nxp1 + iz*nyp1*nxp1
                    #b
                    cv[1] = cv[0] + 1
                    #d
                    cv[3] = cv[0] + nxp1
                    #c
                    cv[2] = cv[3] + 1

                    # Top face
                    #e
                    cv[4] = cv[0] + nyp1*nxp1
                    #f
                    cv[5] = cv[4] + 1
                    #h
                    cv[7] = cv[4] + nxp1
                    #g
                    cv[6] = cv[7] + 1
                   
                    cv += 1
                    i_e += 1
                    mi = i_e

                    '''
                    #
                    # Determine physical centre coordinate
                    #
                    mx = 0.5*(np_x[ix] + np_x[ix+1])
                    my = 0.5*(np_y[iy] + np_y[iy+1])
                    mz = 0.5*(np_z[iz] + np_z[iz+1])

                    m_tup = (i_e, cv[0], cv[1], cv[2], cv[3], cv[4], cv[5], cv[6], cv[7], mx, my, mz)
                    mesh.append('%d %d %d %d %d %d %d %d %d %10.1f %10.1f %10.1f\n' %m_tup)
                    '''

                    m_tup = (i_e, cv[0], cv[1], cv[2], cv[3], cv[4], cv[5], cv[6], cv[7])
                    mesh.append('%d %d %d %d %d %d %d %d %d\n' %m_tup)
                    mats.append('%d %d\n' %(i_e,i_e))
                    nummats.append('2 %d %d %d %d 9999 %d 0\n' % (i_e,rho[ix,iy,iz],vp[ix,iy,iz],vs[ix,iy,iz],Qu[ix,iy,iz]))

                    if iz == 0:
                        # Add bottom face
                        zminfaces.append((mi, cv[3], cv[2], cv[1], cv[0]))
                    if iz == (nz - 1):
                        # Add top face
                        zmaxfaces.append((mi, cv[4], cv[5], cv[6], cv[7]))

                    if ix == 0:
                        # Add xmin face
                        xminfaces.append((mi, cv[4], cv[7], cv[3], cv[0]))

                    if ix == (nx - 1):
                        # Add xmax face
                        xmaxfaces.append((mi, cv[6], cv[5], cv[1], cv[2]))

                    if iy == 0:
                        # Add ymin face
                        yminfaces.append((mi, cv[0], cv[1], cv[5], cv[4]))
                        
                    if iy == (ny - 1):
                        ymaxfaces.append((mi, cv[3], cv[7], cv[6], cv[2]))

                #end ix loop
            #end iy loop

            ################################
            # 1. Write mesh
            # 2. Generate materials and associate to mesh cells
            # g. Generate nummaterials 

            if (iz)%mod_perc == 0 or iz == nz-1:

                f = open('%s/mesh_file' % fpath, 'a')
                f.writelines(mesh)
                del mesh
                mesh = []
                f.close()

                mf = open('%s/materials_file' % fpath, 'a')
                mf.writelines(mats)
                del mats
                mats = []
                mf.close()

                nmf = open('%s/nummaterial_velocity_file' % fpath, 'a')
                nmf.writelines(nummats)
                del nummats
                nummats = []
                nmf.close()

            #end if 

        #end iz loop

        #
        # Write boundary faces
        #
        names = ['absorbing_surface_file_xmin',
                 'absorbing_surface_file_xmax',
                 'absorbing_surface_file_ymin',
                 'absorbing_surface_file_ymax',
                 'absorbing_surface_file_bottom',
                 'free_or_absorbing_surface_file_zmax']
        allfaces = [xminfaces, xmaxfaces, yminfaces, ymaxfaces, zminfaces, zmaxfaces]
        for name, faces in zip(names, allfaces):

            f = open('%s/%s' % (fpath, name), 'w')
            f.write('%d\n' % len(faces))
            for face in faces:
                #f.write(' '.join(map(lambda x: str(x + 1), face)))
                f.write(' '.join(map(lambda x: str(x), face)))
                f.write('\n')
            f.close()

    #end def writeMesh2Files


    ###################################################################
    #
    # Create and write Specfem3D Node, Mesh, an other related files 
    #
    ###################################################################
    def writeSpecfem3DMesh(self, fpath, gm3d):

        t_start = time.time()

        self.writeNodes2File(fpath,gm3d)

        self.writeMesh2Files(fpath,gm3d)

#         t_total = (time.time() - t_start)/3600
#         print('runtime (h):', t_total)
        
#         return t_total

    #end def writeSpecfem3DMesh
