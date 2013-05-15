'''
This module contains functions to plot different MT things.

J Peacock
'''

import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator,FormatStrFormatter
import mtpy.core.edi as mtedi
import mtpy.core.z as mtz
import mtpy.analysis.pt as mtpt
import mtpy.analysis.zinvariants as mtinv
import mtpy1.core.z as Z
import mtpy1.utils.latlongutmconversion as utm2ll
import matplotlib.colors as colors
import matplotlib.patches as patches
import matplotlib.colorbar as mcb
import matplotlib.gridspec as gridspec
import mtpy.utils.exceptions as mtexcept
import mtpy.imaging.mtcolors as mtcl


#define text formating for plotting
ckdict = {'phiminang':'$\Phi_{min}$ (deg)','phimin':'$\Phi_{min}$ (deg)',
          'phimaxang':'$\Phi_{max}$ (deg)','phimax':'$\Phi_{max}$ (deg)',
          'phidet':'Det{$\Phi$} (deg)','skew':'Skew (deg)',
          'ellipticity':'Ellipticity','skew_seg':'Skew (deg)'}
          

            
labeldict = {6:'$10^{6}$',
             5:'$10^{5}$',
             4:'$10^{4}$',
             3:'$10^{3}$',
             2:'$10^{2}$',
             1:'$10^{1}$',
             0:'$10^{0}$',
             -1:'$10^{-1}$',
             -2:'$10^{-2}$',
             -3:'$10^{-3}$',
             -4:'$10^{-4}$',
             -5:'$10^{-5}$',
             -6:'$10^{-6}$',
             -7:'$10^{-7}$',}

#define a dictionary for different zones of utm to put stations in correct 
#location
zonedict = dict([(a,ii) for ii,a in enumerate(['a','b','c','d','e','f','g','h',
               'i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x',
               'y','z'])])
               
class MTArrows(object):
    
    def __init__(self,arrow_dict):
        self._arrow_dict = arrow_dict

    def _read_arrow_dict(self):        
    
        #set arrow length
        try:
            self.arrow_size = self._arrow_dict['size']
        except KeyError:
            self.arrow_size = 2.5
            
        #set head length
        try:
            self.arrow_head_length = self._arrow_dict['head_length']
        except KeyError:
            self.arrow_head_length = .15*self.arrow_size
            
        #set head width
        try:
            self.arrow_head_width = self._arrow_dict['head_width']
        except KeyError:
            self.arrow_head_width = .1*self.arrow_size
            
        #set line width
        try:
            self.arrow_lw = self._arrow_dict['lw']
        except KeyError:
            self.arrow_lw = .5*self.arrow_size
            
        #set real color to black
        try:
            self.arrow_color_real = self._arrow_dict['color'][0]
        except KeyError:
            self.arrow_color_real = 'k'
            
        #set imaginary color to black
        try:
            self.arrow_color_imag = self._arrow_dict['color'][1]
        except KeyError:
            self.arrow_color_imag = 'b'
            
        #set threshold of induction arrows to plot
        try:
            self.arrow_threshold = self._arrow_dict['threshold']
        except KeyError:
            self.arrow_threshold = 1
            
        #set arrow direction to point towards or away from conductor
        try:
            self.arrow_direction = self._arrow_dict['direction']
        except KeyError:
            self.arrow_direction = 0
            
class MTEllipse(object):
    """
    helper class for getting ellipse properties from an input dictionary
    
    Arguments:
    ----------
        **ellipse_dict** : dictionary
                          dictionary of parameters for the phase tensor 
                          ellipses with keys:
                              
                          * 'size' -> size of ellipse in points 
                                     *default* is .25
                          
                          * 'colorby' : [ 'phimin' | 'phimax' | 'beta' | 
                                    'skew_seg' | 'phidet' | 'ellipticity' ]
                                    
                                    - 'phimin' -> colors by minimum phase
                                    - 'phimax' -> colors by maximum phase
                                    - 'skew' -> colors by skew
                                    - 'skew_seg' -> colors by skew in 
                                                   discrete segments 
                                                   defined by the range
                                    - 'phidet' -> colors by determinant of
                                                 the phase tensor
                                    - 'ellipticity' -> colors by ellipticity
                                    *default* is 'phimin'
                            
                          * 'range' : tuple (min, max, step)
                                     Need to input at least the min and max
                                     and if using 'skew_seg' to plot
                                     discrete values input step as well
                                     *default* depends on 'colorby'
                                     
                          * 'cmap' : [ 'mt_yl2rd' | 'mt_bl2yl2rd' | 
                                       'mt_wh2bl' | 'mt_rd2bl' | 
                                       'mt_bl2wh2rd' | 'mt_seg_bl2wh2rd' | 
                                       'mt_rd2gr2bl']
                                      
                                   - 'mt_yl2rd'       --> yellow to red
                                   - 'mt_bl2yl2rd'    --> blue to yellow to red
                                   - 'mt_wh2bl'       --> white to blue
                                   - 'mt_rd2bl'       --> red to blue
                                   - 'mt_bl2wh2rd'    --> blue to white to red
                                   - 'mt_bl2gr2rd'    --> blue to green to red
                                   - 'mt_rd2gr2bl'    --> red to green to blue
                                   - 'mt_seg_bl2wh2rd' --> discrete blue to 
                                                           white to red
                                                           
                                                           
    """
    
    def __init__(self, ellipse_dict):
        self._ellipse_dict = ellipse_dict
        
    def _read_ellipse_dict(self):
        
        #--> set the ellipse properties
        
        #set default size to 2
        try:
            self.ellipse_size = self._ellipse_dict['size']
        except KeyError:
            self.ellipse_size = 2
        
        #set default colorby to phimin
        try:
            self.ellipse_colorby = self._ellipse_dict['colorby']
        except KeyError:
            self.ellipse_colorby = 'phimin'
        
        #set color range to 0-90
        try:
            self.ellipse_range = self._ellipse_dict['range']
        except KeyError:
            if self.ellipse_colorby=='skew' or \
                self.ellipse_colorby=='skew_seg':
                
                self.ellipse_range = (-9,9,3)
            
            elif self.ellipse_colorby=='ellipticity':
                self.ellipse_range = (0,1,.1)
            
            else:
                self.ellipse_range = (0,90,5)
                
        try:
            self.ellipse_range[2]
        except IndexError:
            self.ellipse_range = (self.ellipse_range[0], 
                                  self.ellipse_range[1],1)
            
        #set colormap to yellow to red
        try:
            self.ellipse_cmap = self._ellipse_dict['cmap']
        except KeyError:
            if self.ellipse_colorby=='skew':
                self.ellipse_cmap = 'mt_bl2wh2rd'
                
            elif self.ellipse_colorby=='skew_seg':
                self.ellipse_cmap = 'mt_seg_bl2wh2rd'
                
            else:
                self.ellipse_cmap = 'mt_bl2gr2rd'
               
#==============================================================================
#  make an MT object that has all the important information and methods               
#==============================================================================
               
class MTplot(object):
    """
    This class will be able to read in the imporant information from either
    an .edi file or information input by had and can be extended to other 
    file types in the future.  This is a helper class to get all the 
    information needed in one place.
    
    The normal usage is to input an edi file from which all the information
    is read in.  However, it would seem that not everyone uses the .edi format
    so an option is to write you're own class for that particular file type, or
    give it to us to deal with.  Or write enough code to get it into one of 
    the suppported forms as arrays of z or resistivity and phase, or put those
    into a z_object or tipper_object.  
    
    
    Arguments:
    ----------
    
        **filename** : string
                       full path to file to be read in.  At the moment only
                       .edi type files are supported. *default* is None
        
        **z** : np.array((nf, 2, 2), dtype='complex')
                impedance tensor with length of nf -> the number of frequency
                *default* is None
                
        **z_err** : np.array((nf, 2, 2), dtype='real')
                    impedance tensor error estimates, same shape as z.
                    *default* is None
                    
        **res_array** : np.array((nf, 2, 2))
                        array of resistivity values in linear scale.
                        *default* is None
                        
        **res_err_array** : np.array((nf, 2, 2))
                            array of resistivity error estimates, same shape 
                            as res_array. *default* is None
                            
        **phase_array** : np.array((nf, 2, 2))
                          array of phase values in degrees, same shape as 
                          res_array. *default* is None
                          
        **phase_err_array** : np.array((nf, 2, 2))
                              array of phase error estimates, same shape as 
                              phase_array. *default* is None
                              
        **tipper_array** : np.array((nf, 1, 2), dtype='complex')
                           array of tipper values for tx, ty. *default* is None
                           
        **tipper_err_array** : np.array((nf, 1, 2))
                               array of tipper error estimates, same shape as
                               tipper_array. *default* is None
        
        **station** : string
                      name of the station to be plotted. *default* is None
                      
        **period** : np.array(nf)
                     array of periods that coorespond to the components of z
                     *default* is None
                      
        **lat** : float
                 latitude of the station to be plotted in decimal degrees.
                 *default* is None
                 
        **lon** : float
                 longitude of the station to be plotted in decimal degrees.
                 *default* is None
                 
        **elev** : float
                   elevation of the station to be plotted in meters.
                   *default* is None
                              
        **rot_z** : float or np.array(nf)
                    angle (deg) to rotate the data assuming North is 0 and 
                    angle is positive clockwise.  Can be input as an array to
                    rotate different periods by different angles. 
                    *default* is 0
                    
        **z_object** : class mtpy.core.z.Z
                      object of mtpy.core.z.  If this is input be sure the
                      attribute z.frequency is filled.  *default* is None
                      
        **tipper_object** : class mtpy.core.z.Tipper
                            object of mtpy.core.z. If this is input be sure the
                            attribute z.frequency is filled.  
                            *default* is None 
    Attributes:
    -----------
        -z             impedance tensor as an np.array((nf, 2, 2))
            
        -z_err         estimates of impedance tensor error same shape as z
        
        -tipper        tipper elements in an np.array((nf, 1, 2))
        
        -tipper_err    estimates of tipper error, same shape as tipper
        
        -station       station name
        
        -period        period as an np.array(nf)
        
        -lat           latitude in decimal degrees
        
        -lon           longitude in decimal degrees
        
        -elev          elevation in meters
        
        -fn            filename read from
        
     
     These can be get/set by simple dot syntax.  
        
    :Example: ::
        
        >>> mt1 = mtplot.MTplot(r'/home/mt/edifiles/mt01.edi')
        >>> mt1.station
        >>> 'mt01'
        >>> mt1.station = 'pb075'
        >>> mt1.station
        >>> 'pb075'
        
    **Note:** that the format of z and tipper are:
        
        ::
            
          z[ii, :, :] = np.array([[z_xx, Z_xy], [Z_yx, Z_yy]])
          z[ii, 0, 0] = z_xx
          z[ii, 0, 1] = z_xy
          z[ii, 1, 0] = z_yx
          z[ii, 1, 1] = z_yy
          tipper[ii, :, :] = np.array([[tx],[ty]])
          tipper[ii, 0, 0] = tx
          tipper[ii, 0, 1] = ty
        
    Methods:
    --------
        -get_ResPhase        returns a ResPhase object
        -get_PhaseTensor     returns a PhaseTensor object
        -get_Tipper          returns a Tipper object
        -get_Zinvariants     returns a Zinvariants object
        
    :Example: ::
        
        >>> import mtpy.imaging.mtplot as mtplot
        >>> mt1 = mtplot.MTplot(r'/home/mt/edifiles/mt01.edi')
        >>> # if you don't have an .edi file but res and phase
        >>> mt1 = mtplot.MTplot(res_array=res, phase_array=phase, 
        >>> ...                 period=period, station='mt01')
        
        
        
    """
    
    def __init__(self, filename=None, z=None, z_err=None, res_array=None,
                 phase_array=None, res_err_array=None, phase_err_array=None,
                 tipper=None, tipper_err=None, station=None, period=None, 
                 lat=None, lon=None, elev=None, rot_z=0, z_object=None, 
                 tipper_object=None, frequency=None):
                     

        self._station = station
        self._period = period
        self._frequenc = frequency
        self._lat = lat
        self._lon = lon
        self._elev = elev
        self._fn = filename
        self._rot_z = rot_z
        
        #if a z_object is input make it the attribute _Z
        if z_object is not None:
            self._Z = z_object
            if z_object.frequency==None:
                raise mtexcept.MTpyError_Z('Need to set Z.frequency to an'+\
                                           ' array that cooresponds to Z.z')
            self.period = 1./z_object.frequency
        
        #if z_array is input
        elif z is not None:
            #make sure period is input for plotting
            if self.period==None:
                raise mtexcept.MTpyError_Z('Need to input period array to '+\
                                            'compute Resistivity')
                               
            self._Z = mtz.Z(z_array=z, zerr_array=z_err)
            self._Z.frequency = 1./period

        #if a tipper object is input set it to _Tipper
        if tipper_object is not None:
            self._Tipper = tipper_object
        else:
            self._Tipper = mtz.Tipper(tipper_array=tipper, 
                                      tippererr_array=tipper_err,
                                      frequency=frequency)
        
        #--> read in the edi file if its given
        if self._fn is not None:
            if self._fn[-3:]=='edi':
                self._read_edi()
            else:
                not_fn = self._fn[os.path.basename(self._fn).find['.']:]
                raise mtexcept.MTpyError_file_handling('File '+\
                          'type {0} not supported yet.'.format(not_fn))
        
            
        #--> if resistivity and phase are given set the z_array, z_err_array
        if res_array!=None and phase_array!=None:
            if period is None and frequency is None:
                raise mtexcept.MTpyError_Z('Need to input period array for '+\
                                           'plotting')
            
            if not res_array.shape==phase_array.shape:
                raise mtexcept.MTpyError_shape('res_array and phase array '+\
                                               'do not have the same shape')
                                               
            if not res_array.shape[0]==period.shape[0]:
                raise mtexcept.MTpyError_shape('res_array and period array '+\
                                               'do not have the same shape')
            
            self._Z = mtz.Z()
            self._Z.frequency = 1./period
            self.set_res_phase(res_array,phase_array, 
                               res_err_array=res_err_array,
                               phase_err_array=phase_err_array)
                               
            self.set_period(period)

            
    def _read_edi(self):
        """
        read in an .edi file using mtpy.core.edi
        """
        
        edi1 = mtedi.Edi()
        edi1.readfile(self._fn)
        
        #--> set the attributes accordingly
        # impedance tensor and error
        self._Z = edi1.Z
        
        # tipper and error
        if edi1.Tipper==None:
            self._plot_tipper = 'n'
            self.set_tipper(np.zeros((self._Z.z.shape[0], 1, 2),
                                     dtype='complex'))
            self.set_tipper_err(np.zeros((self._Z.z.shape[0], 1, 2)))
            self._Tipper.rotation_angle=np.zeros(self._Z.z.shape[0])
            
        else:
            self._Tipper = edi1.Tipper
            self._plot_tipper = 'y'
            
        # station name
        try:
            self.station = edi1.head['dataid']
        except KeyError:
            print 'Could not get station name set to MT01'
            self.station = 'MT01'
            
        # period
        self.period = 1./edi1.freq
        self.frequency = edi1.freq
        
        # lat, lon and elevation
        self.lat=edi1.lat
        self.lon = edi1.lon
        self.elev = edi1.elev
        
        # put arrays into descending period order, so that the first index
        # is the shortest period.
        
        if self.period[0]>self.period[-1]:
            self.z = self.z[::-1]
            self.zerr = self.zerr[::-1]
            self.tipper = self.tipper[::-1]
            self.tipper_err = self.tipper_err[::-1]
            self.period = self.period[::-1]
            
        
        
    # don't really like this way of programming but I'll do it anyway
    #==========================================================================
    #  make set methods for each of the attributes    
    #==========================================================================
    def _set_z(self, z):
        self._Z.z = z
        
    def _set_z_err(self, z_err):
        self._Z.zerr = z_err
        
    def _set_tipper(self, tipper):
        self._Tipper.tipper = tipper
        self._plot_tipper = 'y'
        
    def _set_tipper_err(self, tipper_err):
        self._Tipper.tippererr = tipper_err
        
    def _set_station(self, station):
        self._station = station
        
    def _set_period(self, period):
        self._period = period
        if self._period[0]>self._period[-1]:
            self._Z.z = self._Z.z[::-1]
            self._Z.zerr = self._Z.zerr[::-1]
            self._period = self._period[::-1]
            if self._Tipper.tipper is not None:
                self._Tipper.tipper = self._Tipper.tipper[::-1]
                self._Tipper.tipper_err = self._Tipper.tipper_err[::-1]
            
        self._Z.frequency = 1./self._period
        self._frequency = 1./self._period
        if self._Tipper.tipper is not None:
            self._Tipper.frequency = 1./self._period
        
    def _set_lat(self, lat):
        self._lat = lat
        
    def _set_lon(self, lon):
        self._lon = lon
        
    def _set_elev(self, elev):
        self._elev = elev
        
    def _set_fn(self, fn):
        self._fn = fn
        if self._fn[-3:]=='edi':
            self._read_edi()
        else:
            not_fn = self._fn[os.path.basename(self._fn).find['.']:]
            raise mtexcept.MTpyError_file_handling('File '+\
                              'type {0} not supported yet.'.format(not_fn))
           
    def _set_rot_z(self, rot_z):
        self._rot_z = rot_z
        
        # be sure to rotate the components if rot_z is set
        try:
            self._Z.rotate(self._rot_z)
            self._Tipper.rotate(self._rot_z)
        except TypeError:
            self._Z.rotation_angle = np.array([rot_z 
                                        for rr in range(self.period.shape[0])])
        
    def _set_res_phase(self, res_array, phase_array, res_err_array=None,
                       phase_err_array=None):        
        self._Z.set_res_phase(res_array, phase_array, res_err_array, 
                              phase_err_array)
        
    def _set_frequency(self, frequency):
        self._frequency = frequency
        
        #make sure things are in order from highest frequency first
        if self._frequency[0]<self._frequency[-1]:
            self._Z.z = self._Z.z[::-1]
            self._Z.zerr = self._Z.zerr[::-1]
            self._period = self._period[::-1]
            if self._Tipper.tipper is not None:
                self._Tipper.tipper = self._Tipper.tipper[::-1]
                self._Tipper.tipper_err = self._Tipper.tipper_err[::-1]
            
        self._Z.frequency = self._frequency
        self._frequency = self._frequency
        if self._Tipper.tipper is not None:
            self._Tipper.frequency = self._frequency
        
        
    #==========================================================================
    # make get methods for each attribute
    #==========================================================================
    def _get_z(self):
        return self._Z.z
        
    def _get_z_err(self):
        return self._Z.zerr

    def _get_tipper(self):
        return self._Tipper.tipper
        
    def _get_tipper_err(self):
        return self._Tipper.tipper_err
        
    def _get_station(self):
        return self._station
        
    def _get_period(self):
        return self._period
        
    def _get_lat(self):
        return self._lat
        
    def _get_lon(self):
        return self._lon
        
    def _get_elev(self):
        return self._elev
        
    def _get_fn(self):
        return self._fn
        
    def _get_rot_z(self):
        return self._rot_z
        
    def _get_frequency(self):
        return self._frequency
        
    #==========================================================================
    # use the property built-in to make these get/set useable behind the scenes
    #==========================================================================
    z = property(_get_z, _set_z, 
                 doc="Impedance tensor in the shape (nz,2,2) complex "+\
                     "numpy.array")
    
    z_err = property(_get_z_err, _set_z_err, 
                 doc="Impedance tensor error same shape as MT.z real "+\
                     "numpy.array")
                  
    tipper = property(_get_tipper, _set_tipper, 
                      doc="Tipper array in the shape (nz, 2) complex "+\
                          "numpy.array")
                       
    tipper_err = property(_get_tipper_err, _set_tipper_err, 
                          doc="Tipper error array same shape as MT.tipper"+\
                              "real numpy.array")
                          
    station = property(_get_station, _set_station, 
                       doc="Name of the station to be plotted")
                       
    period = property(_get_period, _set_period, 
                      doc="array of periods corresponding to MT.z")
                      
    lat = property(_get_lat, _set_lat, 
                   doc="Latitude in decimal degrees of the station")
    
    lon = property(_get_lon, _set_lon,
                   doc="Longitude in decimal degrees of the station")
    
    elev = property(_get_elev, _set_elev, 
                    doc="Elevation of the station in meters")
                    
    fn = property(_get_fn, _set_fn,
                      doc="full path to the file of the station "+\
                          "being plotted")
                      
    rot_z = property(_get_rot_z, _set_rot_z, 
                     doc="Rotation angle positive clockwise assuming North "+\
                         "is 0, can be an array with same shape at z")
                         
    frequency = property(_get_frequency, _set_frequency,
                           doc="frequency array corresponding to elemens in z")
                      
    #==========================================================================
    # define methods to get resphase, phasetensor, invariants
    #
    # --> used uppercase in the function names to signify that it is getting a 
    #     class object
    #==========================================================================

    def get_ResPhase(self):
        """
        returns a ResPhase object from z_object
        
        """
        rp = ResPhase(self._Z)
        return rp

    def get_PhaseTensor(self):
        """
        returns a mtpy.analysis.pt.PhaseTensor object from z_object
        
        """
        pt = mtpt.PhaseTensor(z_object=self._Z)
        pt.frequency = 1./self.period
        
        return pt
    
    def get_Zinvariants(self):
        """
        returns a mtpy.analysis.zinvariants.Zinvariants object
        """
        
        zinv = mtinv.Zinvariants(z_object=self._Z)
        
        return zinv
        
    def get_Tipper(self):
        """
        returns Tipper class
        
        """
        
        tp = Tipper(tipper_object=self._Tipper)
        
        return tp
        
#---- get list of mt objects----------------------------------------------        
def get_mtlst(fn_lst=None, res_object_lst=None, z_object_lst=None, 
               tipper_object_lst=None, mt_object_lst=None):
                 
    """
    gets a list of mt objects from the inputs       
    
    """
    
    #first need to find something to loop over
    try:
        ns = len(fn_lst)
        mt_lst = [MTplot(filename=fn) for fn in fn_lst]
        print 'Reading {0} stations'.format(ns)
        return mt_lst
    except TypeError:
        try:
            ns = len(res_object_lst)
            mt_lst = [MTplot(res_phase_object=res_obj) 
                        for res_obj in res_object_lst]
            try:
                nt = len(tipper_object_lst)
                if nt!=ns:
                    raise mtexcept.MTpyError_inputarguments('length '+\
                          ' of z_lst is not equal to tip_lst'+\
                          '; nz={0}, nt={1}'.format(ns, nt))
                for mt,tip_obj in zip(mt_lst,tipper_object_lst):
                    mt._Tipper = tip_obj 
            except TypeError:
                pass
            print 'Reading {0} stations'.format(ns)
            return mt_lst
        except TypeError:
            try: 
                ns = len(z_object_lst)
                mt_lst = [MTplot(z_object=z_obj) for z_obj in z_object_lst]
                try:
                    nt = len(tipper_object_lst)
                    if nt!=ns:
                        raise mtexcept.MTpyError_inputarguments('length '+\
                              ' of z_lst is not equal to tip_lst'+\
                              '; nz={0}, nt={1}'.format(ns, nt))
                    for mt,tip_obj in zip(mt_lst,tipper_object_lst):
                        mt._Tipper = tip_obj 
                except TypeError:
                    pass
                print 'Reading {0} stations'.format(ns)
                return mt_lst
                
            except TypeError:
                try:
                    ns = len(mt_object_lst)
                    print 'Reading {0} stations'.format(ns)
                    return mt_lst
                except TypeError:
                    raise IOError('Need to input an iteratble list')

#==============================================================================
# object for computing resistivity and phase  
#==============================================================================
class ResPhase(object):
    """
    create a data type for just the resistivity and phase with an attribute 
    period
    """
    def __init__(self, z_object=None, res_array=None, res_err_array=None,
                 phase_array=None, phase_err_array=None, rot_z=0, period=None):
        
        self._Z = z_object
        self.res = res_array
        self.res_err = res_err_array
        self.phase = phase_array
        self.phase_err = phase_err_array
        self.period = period
        
        
        #check to make sure they are the same size
        if self.res!=None or self.phase!=None:
            if self.res.shape!=self.phase.shape:
                raise mtexcept.MTpyError_shape('res_array and phase_array '+\
                                               'are not the same shape')
        
        if self._Z.frequency==None:
            if period is not None:
                self._Z.frequency = 1./period
            else:
                raise mtexcept.MTpyError_Z('Need to set z_object.frequency')
        else:
            self.period = 1./self._Z.frequency
            
        if rot_z!=0:
            self.rotate(rot_z)
            
        #compute the resistivity and phase components
        self.compute_res_phase()
    
    def compute_res_phase(self):
        """
        computes the resistivity and phase and sets each component as an 
        attribute
        """
        
        if self._Z is not None:
            self.res,  self.phase, self.res_err, self.phase_err = \
                                                       self._Z._get_res_phase()
                                                       
        #check to see if a res_err_array was input if not set to zeros
        if self.res_err is None:
            self.res_err = np.zeros_like(self.res)
            
        else:
            #check to see if res and res_err are the same shape
            if self.res.shape!=self.res_err.shape:
                raise mtexcept.MTpyError_shape('res_array and res_err_array '+\
                                               'are not the same shape')

        #check to see if a phase_err_array was input, if not set to zeros
        if self.phase_err is None:
            self.phase_err = np.zeros_like(self.phase)
            
        else:
            #check to see if res and res_err are the same shape
            if self.phase.shape!=self.phase_err.shape:
                raise mtexcept.MTpyError_shape('phase_array and '+\
                                      'phase_err_array are not the same shape')
        
        #--> set the attributes of the class to the components of each        
        self.resxx = self.res[:,0,0]
        self.resxy = self.res[:,0,1]
        self.resyx = self.res[:,1,0]
        self.resyy = self.res[:,1,1]
        
        self.resxx_err = self.res_err[:,0,0]
        self.resxy_err = self.res_err[:,0,1]
        self.resyx_err = self.res_err[:,1,0]
        self.resyy_err = self.res_err[:,1,1]
        
        self.phasexx = self.phase[:,0,0]
        self.phasexy = self.phase[:,0,1]
        self.phaseyx = self.phase[:,1,0]
        self.phaseyy = self.phase[:,1,1]
        
        self.phasexx_err = self.phase_err[:,0,0]
        self.phasexy_err = self.phase_err[:,0,1]
        self.phaseyx_err = self.phase_err[:,1,0]
        self.phaseyy_err = self.phase_err[:,1,1]
        
        self.phaseyx[np.where(self.phaseyx>120)] -= 180 
        self.phaseyx[np.where(self.phaseyx<-90)] += 180
        
        #calculate determinant values
        zdet = np.array([np.linalg.det(zz)**.5 for zz in self._Z.z])
        zdetvar = np.array([np.linalg.det(zzv)**.5 for zzv in self._Z.zerr])
        
        #apparent resistivity
        self.resdet = 0.2*(1./self._Z.frequency)*abs(zdet)**2
        self.resdet_err = 0.2*(1./self._Z.frequency)*\
                                        np.abs(zdet+zdetvar)**2-self.resdet
        
        #phase
        self.phasedet = np.arctan2(zdet.imag,zdet.real)*(180/np.pi)
        self.phasedet_err = np.arcsin(zdetvar/abs(zdet))*(180/np.pi)
        
    def rotate(self, rot_z):
        """
        rotate the impedance tensor by the angle rot_z (deg) assuming 
        0 is North and angle is positve clockwise.
        """
        
        self.rot_z = rot_z
        
        #need to fill the rotation angles in Z for this to work
        try:
            len(self.rot_z)
        except TypeError:
            self._Z.rotation_angle = np.array([rot_z 
                                           for rr in range(self.res.shape[0])])
        if self._Z is not None:
            self._Z.rotate(self.rot_z)
        
        else:
            raise mtexcept.MTpyError_Z('Cannot rotate just resistivity and '+\
                                        'phase data, need to input z')
        
        self.compute_res_phase()
        
#==============================================================================
#  Define a tipper object
#==============================================================================
class Tipper(object):
    """
    Tipper object
    
    Attributes:
    -----------
        -mag_real
        -mag_imag
        -ang_real
        _ang_imag
        
    Methods:
    --------
        -rotate
    """
    
    def __init__(self, tipper_object=None, tipper_array=None, 
                 tipper_err_array=None, rot_t=0, frequency=None):
        
        if tipper_object is not None:
            self._Tipper = tipper_object
        else:
            self._Tipper = mtz.Tipper(tipper_array=tipper_array, 
                                      tippererr_array=tipper_err_array,
                                      frequency=frequency)
                                      
        self.frequency = frequency
        
        if rot_t!=0:
            self.rotate(rot_t)
            
        else:
            self.compute_components()
        
    def compute_components(self):
        
        self.mag_real, self.ang_real, self.mag_imag, self.ang_imag = \
                                                   self._Tipper.mag_direction 

        
    def rotate(self, rot_t):
        
        self.rot_t = rot_t
        self._Tipper.rotate(self.rot_t)
        
        self.compute_components()

#==============================================================================
#  Plot apparent resistivity and phase
#==============================================================================
class PlotResPhase(object):
    """
    Plots Resistivity and phase for the different modes of the MT response.  At
    the moment is supports the input of an .edi file. Other formats that will
    be supported are the impedance tensor and errors with an array of periods
    and .j format.
    
    The normal use is to input an .edi file, however it would seem that not
    everyone uses this format, so you can input the data and put it into 
    arrays or objects like class mtpy.core.z.Z.  Or if the data is in 
    resistivity and phase format they can be input as arrays or a class
    mtpy.imaging.mtplot.ResPhase.  Or you can put it into a class
    mtpy.imaging.mtplot.MTplot.
    
    The plot places the apparent resistivity in log scale in the top panel(s), 
    depending on the plotnum.  The phase is below this, note that 180 degrees
    has been added to the yx phase so the xy and yx phases plot in the same
    quadrant.  Both the resistivity and phase share the same x-axis which is in
    log period, short periods on the left to long periods on the right.  So
    if you zoom in on the plot both plots will zoom in to the same 
    x-coordinates.  If there is tipper information, you can plot the tipper
    as a third panel at the bottom, and also shares the x-axis.  The arrows are
    in the convention of pointing towards a conductor.  The xx and yy 
    components can be plotted as well, this adds two panels on the right.  
    Here the phase is left unwrapped.
    
    To manipulate the plot you can change any of the attributes listed below
    and call redraw_plot().  If you know more aout matplotlib and want to 
    change axes parameters, that can be done by changing the parameters in the
    axes attributes and then call update_plot(), note the plot must be open.
    
    
    Arguments:
    ----------
        **filename** : string
                       filename containing impedance (.edi) is the only 
                       format supported at the moment
                       
        **z_array** : np.array((nf, 2, 2), dtype='complex')
                impedance tensor with length of nf -> the number of frequency
                *default* is None
                
        **z_err_array** : np.array((nf, 2, 2), dtype='real')
                    impedance tensor error estimates, same shape as z.
                    *default* is None
                    
        **res_array** : np.array((nf, 2, 2))
                        array of resistivity values in linear scale.
                        *default* is None
                        
        **res_err_array** : np.array((nf, 2, 2))
                            array of resistivity error estimates, same shape 
                            as res_array. *default* is None
                            
        **phase_array** : np.array((nf, 2, 2))
                          array of phase values in degrees, same shape as 
                          res_array. *default* is None
                          
        **phase_err_array** : np.array((nf, 2, 2))
                              array of phase error estimates, same shape as 
                              phase_array. *default* is None
                              
        **tipper_array** : np.array((nf, 1, 2), dtype='complex')
                           array of tipper values for tx, ty. *default* is None
                           
        **tipper_err_array** : np.array((nf, 1, 2))
                               array of tipper error estimates, same shape as
                               tipper_array. *default* is None
                               
        **z_object** : class mtpy.core.z.Z
                      object of mtpy.core.z.  If this is input be sure the
                      attribute z.frequency is filled.  *default* is None
                      
        **tipper_object** : class mtpy.core.z.Tipper
                            object of mtpy.core.z. If this is input be sure the
                            attribute z.frequency is filled.  
                            *default* is None 
                            
        **mt_object** : class mtpy.imaging.mtplot.MTplot
                        object of mtpy.imaging.mtplot.MTplot
                        *default* is None
                      
        **fignum** : int
                     figure number
                     *default* is 1
                     
        **ffactor** : float
                      scaling factor for computing resistivity from 
                      impedances.
                      *Default* is 1
        
        **rotz** : float
                   rotation angle of impedance tensor (deg or radians), 
                   *Note* : rotaion is clockwise positive
                   *default* is 0
        
        **plotnum** : [ 1 | 2 | 3 ]
                        * 1 for just Ex/By and Ey/Bx *default*
                        * 2 for all 4 components
                        * 3 for off diagonal plus the determinant
    
        **title** : string
                    title of plot
                    *default* is station name
                    
        **plot_tipper** : [ 'yri' | 'yr' | 'yi' | 'n' ]
                          Plots the tipper in a bottom pannel
                          * 'yri'  --> plots the real and imaginar parts
                          * 'yr'   --> plots just the real part
                          * 'yi'   --> plots just the imaginary part
                          
                          **Note:** the convention is to point towards a 
                          conductor.  Can change this by setting the
                          parameter arrow_direction = 1.
                          
        **plot_strike** : [ 'y' | 1 | 2 | 3 | 'n' ]
                          Plots the strike angle from different parameters:
                              * 'y'  --> plots strike angle determined from 
                                         the invariants of Weaver et al. [2000]
                                         and the phase tensor of
                                         Caldwell et al. [2004], if Tipper is 
                                         plotted the strike of the tipper is
                                         also plotted.
                                         
                               * 1  --> plots strike angle determined from 
                                        the invariants of Weaver et al. [2000]
                               * 2  --> plots strike angle determined from 
                                        the phase tensor of 
                                        Caldwell et al. [2004]
                               * 3  --> plots strike angle determined from 
                                        the tipper
                               * 'n' --> doesn't plot the strike, *default*
                               
        **plot_skew** : [ 'y' | 'n' ]
                        plots the skew angle calculated from the phase tensor
                        in the same subfigure as the strike angle.  The axes
                        are labelled on the right hand side.
                            * 'y' --> plots skew angle
                            * 'n' --> does not plot skew angle *default*
                          
        **dpi** : int
                 dots-per-inch resolution, *default* is 300
                    
                        
        :Example: ::
            
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> edifile = r"/home/MT01/MT01.edi"
            >>> rp1 = mtplot.PlotResPhase(edifile, plotnum=2)
            >>> # plots all 4 components
            >>> rp1 = mtplot.PlotResPhase(edifile, plot_tipper='yr')
            >>> # plots the real part of the tipper
            
    Attributes:
    -----------
        -fn             filename to be plotted (only supports .edi so far) 
        -fignum         figure number for plotting
        -plotnum        plot type, see arguments for details 
        -title          title of the plot, *default* is station name
        -dpi            Dots-per-inch resolution of plot, *default* is 300
        -rotz           Rotate impedance tensor by this angle (deg) assuming
                        that North is 0 and angle is positive clockwise
                        
        -plot_tipper    string to tell the program to plot tipper arrows or 
                        not, see accepted values above in arguments
        
        -plot_strike    string or integer telling the program to plot the 
                        strike angle, see values above in arguments
                        
        -plot_skew      string to tell the program to plot skew angle.
                        The skew is plotted in the same subplot as the strike
                        angle at the moment
                        
                
        -period          period array cooresponding to the impedance tensor
        -font_size       size of font for the axis ticklabels, note that the 
                         axis labels will be font_size+2
        
        -axr             matplotlib.axes object for the xy,yx resistivity plot.  
        -axp             matplotlib.axes object for the xy,yx phase plot
        -axt             matplotlib.axes object for the tipper plot
        -ax2r            matplotlib.axes object for the xx,yy resistivity plot
        -ax2p            matplotlib.axes object for the xx,yy phase plot
        -axs             matplotlib.axes object for the strike plot
        -axs2            matplotlib.axes object for the skew plot       
        ..
        
             **Note:** that from these axes object you have control of the
             plot.  You can do this by changing any parameter in the 
             axes object and then calling update_plot()
        
        -erxyr          class matplotlib.container.ErrorbarContainer for 
                        xy apparent resistivity.
        -erxyp          class matplotlib.container.ErrorbarContainer for 
                        xy.
        -eryxr          class matplotlib.container.ErrorbarContainer for 
                        yx apparent resistivity.
        -eryxp          class matplotlib.container.ErrorbarContainer for 
                        yx phase.
        
        ..
        
            **Note:** that from these line objects you can manipulate the 
            error bar properties and then call update_plot()
                     
        -xy_ls           line style for xy and xx components, *default* is None       
        -yx_ls           line style for yx and yy components, *default* is None        
        -det_ls          line style for determinant, *default* is None
        
        -xy_marker       marker for xy and xx, *default* is squares
        -yx_marker       marker for yx and yy, *default* is circles
        -det_marker      marker for determinant, *default* is diamonds
        
        -xy_color        marker color for xy and xx, *default* is blue
        -yx_color        marker color for yx and yy, *default* is red
        -det_color       marker color for determinant, *default* is green
        
        -xy_mfc          marker face color for xy and xx, *default* is None 
        -yx_mfc          marker face color for yx and yy, *default* is None
        -det_mfc         marker face color for determinant, *default* is None
        
        -skew_marker     marker for skew angle, *default* is 'd'
        -skew_color      color for skew angle, *default* is 'orange'
        
        -strike_inv_marker  marker for strike angle determined by invariants
                            *default* is '^'
        -strike_inv_color   color for strike angle determined by invaraiants 
                            *default* is (.2, .2, .7)
        -strike_pt_marker  marker for strike angle determined by pt, 
                           *default* is'v'
        -strike_pt_color   color for strike angle determined by pt
                           *default* is (.7, .2, .2)
        
        -strike_tip_marker  marker for strike angle determined by tipper
                            *default* is '>'
        -strike_tip_color   color for strike angle determined by tipper
                            *default* is (.2, .7, .2)
        
        -marker_size     size of marker in relative dimenstions, *default* is 2
        -marker_lw       line width of marker, *default* is 100./dpi 
        ..
        
         *For more on line and marker styles see matplotlib.lines.Line2D*
        
        -arrow_lw          line width of the arrow, *default* is 0.75
        -arrow_head_width  head width of the arrow, *default* is 0 for no arrow
                           head.  Haven't found a good way to scale the arrow
                           heads in a log scale.
                         
        -arrow_head_height  head width of the arrow, *default* is 0 for no arrow
                            head.  Haven't found a good way to scale the arrow
                            heads in a log scale.
                          
        -arrow_color_real  color of the real arrows, *default* is black
        -arrow_color_imag  color of the imaginary arrows, *default* is blue
        
        -arrow_direction   0 for pointing towards a conductor and -1 for 
                           pointing away from a conductor.
                          

        -xlimits        limits on the x-limits (period), *default* is None
                        which will estimate the min and max from the data, 
                        setting the min as the floor(min(period)) and the max
                        as ceil(max(period)).  Input in linear scale if you
                        want to change the period limits, ie. (.1,1000)
                        
        -res_limits     limits on the resistivity, *default* is None, which 
                        will estimate the min and max from the data, rounding
                        to the lowest and highest increments to the power of 10
                        Input in linear scale if you want to change them, 
                        ie. (1,10000). Note this only sets the xy and yx 
                        components, not the xx and yy.
                        
        -phase_limits   limits on the phase, *default* is (0,90) but will 
                        adapt to the data if there is phase above 90 or below
                        0.  Input in degrees.  Note this only changes the xy
                        and yx components.
                        
        -tipper_limits  limits of the y-axis, *default* is (-1,1)
        
        -skew_limits    limits for skew angle, *default* is (-9,9)
        
        -strike_limits  limits for strike angle, *default* is (-90,90)   
        


    """   
    
    def __init__(self, filename=None, z_array=None, z_err_array=None, 
                 period=None, fignum=1, plotnum=1, title=None, dpi=300, 
                 rotz=0, plot_yn='y', plot_tipper='n', plot_strike='n',
                 plot_skew='n', tipper_array=None, tipper_err_array=None, 
                 tipper_object=None, res_array=None, res_err_array=None,
                 phase_array=None, phase_err_array=None,
                 res_phase_object=None, z_object=None, mt_object=None):
        
        #--> initialize an MTplot object
        if mt_object is None:
            self._mt = MTplot(filename=filename, 
                              z=z_array, 
                              z_err=z_err_array,
                              z_object=z_object,
                              phase_array=phase_array, 
                              res_array=res_array, 
                              phase_err_array=phase_err_array,
                              res_err_array=res_err_array,
                              tipper=tipper_array, 
                              tipper_err=tipper_err_array,
                              tipper_object=tipper_object,
                              period=period)
                              
        else:
            self._mt = mt_object

        
        #if you have a resistivity and phase object 
        if res_phase_object is not None:
            if period is None:
                raise mtexcept.MTpyError_Z('Need to input period array for '+\
                                           'plotting')
            self.rp = res_phase_object
            
        
        #set some of the properties as attributes much to Lars' discontent
        self.fn = filename
        self.fignum = fignum
        self.plotnum = plotnum
        self.title = title
        self.dpi = dpi
        self.rotz = rotz
        
        #-->line properties
        #line style between points
        self.xy_ls='None'        
        self.yx_ls='None'        
        self.det_ls='None'        
        
        #outline color
        self.xy_color = 'b'
        self.yx_color = 'r'
        self.det_color = 'g'
        
        #face color
        self.xy_mfc='None'
        self.yx_mfc='None'
        self.det_mfc='None'
        
        #maker
        self.xy_marker = 's'
        self.yx_marker = 'o'
        self.det_marker = 'd'
        
        #size
        self.marker_size = 2
        
        #marker line width
        self.marker_lw = 100./self.dpi
        
        #set plot limits
        self.xlimits = None
        self.res_limits = None
        self.phase_limits = None
        self.tipper_limits = None
        self.strike_limits = None
        self.skew_limits = None
        
        #set font parameters
        self.font_size = 7
        
        #set period
        self.period = self._mt.period
        
        #set plot tipper or not
        self.plot_tipper = plot_tipper
        
        #plot strike angle or not
        self.plot_strike = plot_strike
        
        #plot skew angle
        self.plot_skew = plot_skew
        
        #set arrow properties
        self.arrow_lw = .75
        self.arrow_head_width = 0.0
        self.arrow_head_height = 0.0
        self.arrow_color_real = 'k'
        self.arrow_color_imag = 'b'
        self.arrow_direction = 0
        
        #skew properties
        self.skew_color = (.85, .35, 0)
        self.skew_marker = 'd'
        
        #strike properties
        self.strike_inv_marker = '^'
        self.strike_inv_color = (.2, .2, .7)
        
        self.strike_pt_marker = 'v'
        self.strike_pt_color = (.7, .2, .2)
        
        self.strike_tip_marker = '>'
        self.strike_tip_color = (.2, .7, .2)


        #plot on initializing
        if plot_yn=='y':
            self.plot()

    def plot(self):
        """
        plotResPhase(filename,fignum) will plot the apparent resistivity and 
        phase for a single station. 
 
        """
        
        #set figure size according to what the plot will be.
        if self.plotnum==1 or self.plotnum==3:
            self.figsize = [5,7]
        
        elif self.plotnum==2:
            self.figsize = [7,7]
            
        #--> rotate the impedance tensor if desired
        if self.rotz!=0:
            self._mt.rot_z = self.rotz
        
        #get the reistivity and phase object
        try:
            self.rp = self._mt.get_ResPhase()
        except AttributeError:
            pass
        
        #set x-axis limits from short period to long period
        if self.xlimits==None:
            self.xlimits = (10**(np.floor(np.log10(self.period[0]))),
                            10**(np.ceil(np.log10((self.period[-1])))))
        if self.phase_limits==None:
            pass
            
        if self.res_limits == None:
            self.res_limits = (10**(np.floor(
                                    np.log10(min([self.rp.resxy.min(),
                                                  self.rp.resyx.min()])))),
                              10**(np.ceil(
                                    np.log10(max([self.rp.resxy.max(),
                                                  self.rp.resyx.max()])))))

        #set some parameters of the figure and subplot spacing
        plt.rcParams['font.size'] = self.font_size
        plt.rcParams['figure.subplot.bottom'] = .1
        plt.rcParams['figure.subplot.top'] = .93
        plt.rcParams['figure.subplot.left'] = .80
        if self.plot_skew=='y':
            plt.rcParams['figure.subplot.right'] = .90
        else:
            plt.rcParams['figure.subplot.right'] = .98
        
        #set the font properties for the axis labels
        fontdict={'size':self.font_size+2, 'weight':'bold'}
        
        #create a grid to place the figures into, set to have 2 rows and 2 
        #columns to put any of the 4 components.  Make the phase plot
        #slightly shorter than the apparent resistivity plot and have the two
        #close to eachother vertically.  If there is tipper add a 3rd row and
        #if there is strike add another row
        if self.plot_tipper.find('y')==0:
            if self.plot_strike!='n' or self.plot_skew=='y':
                gs = gridspec.GridSpec(4, 2, height_ratios=[2, 1.5, 1, 1], 
                                       hspace=.05)
            else:
                gs = gridspec.GridSpec(3, 2, height_ratios=[2, 1.5, 1], 
                                       hspace=.05)
        else:
            if self.plot_strike!='n' or self.plot_skew=='y':
                gs = gridspec.GridSpec(3, 2, height_ratios=[2, 1.5, 1],
                                       hspace=.05)
            else:
                gs = gridspec.GridSpec(2, 2, height_ratios=[2, 1.5], 
                                       hspace=.01)
        
        #make figure instance
        self.fig = plt.figure(self.fignum, self.figsize, dpi=self.dpi)
        
        #--> make figure for xy,yx components
        if self.plotnum==1 or self.plotnum==3:
            #space out the subplots
            gs.update(hspace=.05, wspace=.15, left=.1)
            
            #--> create the axes instances
            if self.plot_tipper.find('y')==0:
                #apparent resistivity axis
                self.axr = self.fig.add_subplot(gs[0,:])
                
                #phase axis that shares period axis with resistivity
                self.axp = self.fig.add_subplot(gs[1,:], sharex=self.axr)
                
                #tipper axis  
                self.axt = self.fig.add_subplot(gs[2,:], sharex=self.axr)
                
                #place y coordinate labels in the same location                
                self.axr.yaxis.set_label_coords(-.075, 0.5)
                self.axp.yaxis.set_label_coords(-.075, 0.5)
                self.axt.yaxis.set_label_coords(-.075, 0.5)
                if self.plot_strike!='n' or self.plot_skew!='n':
                    self.axs = self.fig.add_subplot(gs[3,:], sharex=self.axr)
                    self.axs.yaxis.set_label_coords(-.075, 0.5)
            else:
                #apparent resistivity axis
                self.axr = plt.subplot(gs[0,:])
                
                #phase axis which shares the x axis with the resistivity
                self.axp = plt.subplot(gs[1,:], sharex=self.axr)
                
                #place the y-coordinate labels in the same location
                self.axr.yaxis.set_label_coords(-.075, 0.5)
                self.axp.yaxis.set_label_coords(-.075, 0.5)
                
                #add stike axis if desired
                if self.plot_strike!='n' or self.plot_skew!='n':
                    self.axs = self.fig.add_subplot(gs[2,:], sharex=self.axr)
                    self.axs.yaxis.set_label_coords(-.075, 0.5)
            
        #--> make figure for all 4 components
        elif self.plotnum==2:
            
            #space out the subplots
            gs.update(hspace=.05, wspace=.15, left=.07)
            
            #--> create the axes instances
            if self.plot_tipper.find('y')==0:
                #apparent resistivity axis
                self.axr = self.fig.add_subplot(gs[0,0])
                
                #phase axis that shares period axis with resistivity
                self.axp = self.fig.add_subplot(gs[1,0], sharex=self.axr)
                
                #tipper axis that shares period with resistivity 
                self.axt = self.fig.add_subplot(gs[2,:], sharex=self.axr)
                
                #place y coordinate labels in the same location                
                self.axr.yaxis.set_label_coords(-.095, 0.5)
                self.axp.yaxis.set_label_coords(-.095, 0.5)
                self.axt.yaxis.set_label_coords(-.095, 0.5)
                
                #add strike axis if desired
                if self.plot_strike!='n' or self.plot_skew!='n':
                    self.axs = self.fig.add_subplot(gs[3,:], sharex=self.axr)
                    self.axs.yaxis.set_label_coords(-.095, 0.5)
            else:
                #apparent resistivity axis
                self.axr = plt.subplot(gs[0,0])
                
                #phase axis which shares the x axis with the resistivity
                self.axp = plt.subplot(gs[1,0], sharex=self.axr)
                
                #place the y-coordinate labels in the same location
                self.axr.yaxis.set_label_coords(-.095, 0.5)
                self.axp.yaxis.set_label_coords(-.095, 0.5)
                
                #add strike axis if desired
                if self.plot_strike!='n' or self.plot_skew!='n':
                    self.axs = self.fig.add_subplot(gs[2,:], sharex=self.axr)
                    self.axs.yaxis.set_label_coords(-.095, 0.5)
        
        #---------plot the apparent resistivity--------------------------------
        #--> plot as error bars and just as points xy-blue, yx-red
        #res_xy
        self.ebxyr = self.axr.errorbar(self.period, 
                                       self.rp.resxy, 
                                       marker=self.xy_marker, 
                                       ms=self.marker_size, 
                                       mfc=self.xy_mfc, 
                                       mec=self.xy_color, 
                                       mew=self.marker_lw, 
                                       ls=self.xy_ls, 
                                       yerr=self.rp.resxy_err, 
                                       ecolor=self.xy_color,
                                       capsize=self.marker_size,
                                       elinewidth=self.marker_lw)
        
        #res_yx                              
        self.ebyxr = self.axr.errorbar(self.period, 
                                       self.rp.resyx, 
                                       marker=self.yx_marker, 
                                       ms=self.marker_size, 
                                       mfc=self.yx_mfc,
                                       mec=self.yx_color, 
                                       mew=self.marker_lw,
                                       ls=self.yx_ls, 
                                       yerr=self.rp.resyx_err, 
                                       ecolor=self.yx_color,
                                       capsize=self.marker_size,
                                       elinewidth=self.marker_lw)
                                      
        #--> set axes properties
        plt.setp(self.axr.get_xticklabels(), visible=False)
        self.axr.set_ylabel('App. Res. ($\mathbf{\Omega \cdot m}$)',
                            fontdict=fontdict)
        self.axr.set_yscale('log')
        self.axr.set_xscale('log')
        self.axr.set_xlim(self.xlimits)
        self.axr.set_ylim(self.res_limits)
        self.axr.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                      lw=.25)
        self.axr.legend((self.ebxyr[0],self.ebyxr[0]), 
                        ('$Z_{xy}$','$Z_{yx}$'),
                        loc=3, 
                        markerscale=1, 
                        borderaxespad=.01,
                        labelspacing=.07, 
                        handletextpad=.2, 
                        borderpad=.02)
        
        #-----Plot the phase---------------------------------------------------
        #phase_xy
        self.ebxyp = self.axp.errorbar(self.period, 
                                       self.rp.phasexy, 
                                       marker=self.xy_marker, 
                                       ms=self.marker_size, 
                                       mfc=self.xy_mfc,
                                       mec=self.xy_color, 
                                       mew=self.marker_lw,
                                       ls=self.xy_ls,
                                       yerr=self.rp.phasexy_err, 
                                       ecolor=self.xy_color,
                                       capsize=self.marker_size,
                                       elinewidth=self.marker_lw)
                                      
        #phase_yx: Note add 180 to place it in same quadrant as phase_xy
        self.ebyxp = self.axp.errorbar(self.period, 
                                       self.rp.phaseyx, 
                                       marker=self.yx_marker, 
                                       ms=self.marker_size, 
                                       mfc=self.yx_mfc, 
                                       mec=self.yx_color, 
                                       mew=self.marker_lw,
                                       ls=self.yx_ls, 
                                       yerr=self.rp.phaseyx_err, 
                                       ecolor=self.yx_color,
                                       capsize=self.marker_size,
                                       elinewidth=self.marker_lw)

        #check the phase to see if any point are outside of [0:90]
        if self.phase_limits==None:
            if min(self.rp.phasexy)<0 or min(self.rp.phaseyx)<0:
                 pymin = min([min(self.rp.phasexy), min(self.rp.phaseyx)])
                 if pymin>0:
                    pymin = 0
            else:
                pymin = 0
            
            if max(self.rp.phasexy)>90 or max(self.rp.phaseyx)>90:
                pymax = min([max(self.rp.phasexy), max(self.rp.phaseyx)])
                if pymax<91:
                    pymax = 89.9
            else:
                pymax = 89.9
                
            self.phase_limits = (pymin, pymax)
        
        #--> set axes properties
        self.axp.set_xlabel('Period (s)', fontdict)
        self.axp.set_ylabel('Phase (deg)', fontdict)
        self.axp.set_xscale('log')
        self.axp.set_ylim(self.phase_limits)        
        self.axp.yaxis.set_major_locator(MultipleLocator(15))
        self.axp.yaxis.set_minor_locator(MultipleLocator(5))
        self.axp.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                      lw=.25)
        
        #-----plot tipper------------------------------------------------------              
        if self.plot_tipper.find('y')==0:
            plt.setp(self.axp.xaxis.get_ticklabels(), visible=False)
            
            tp = self._mt.get_Tipper()
            
            txr = tp.mag_real*np.cos(tp.ang_real*np.pi/180+\
                                     np.pi*self.arrow_direction)
            tyr = tp.mag_real*np.sin(tp.ang_real*np.pi/180+\
                                     np.pi*self.arrow_direction)
    
            txi = tp.mag_imag*np.cos(tp.ang_imag*np.pi/180+\
                                     np.pi*self.arrow_direction)
            tyi = tp.mag_imag*np.sin(tp.ang_imag*np.pi/180+\
                                     np.pi*self.arrow_direction)
            
            nt = len(txr)
            
            tiplst=[]
            tiplabel=[]
            
            for aa in range(nt):
                xlenr = txr[aa]*self.period[aa]
                xleni = txi[aa]*self.period[aa]
                
                #scale the arrow head height and width to fit in a log scale
                if np.log10(self.period[aa])<0:
                     hwidth = self.arrow_head_width*\
                                 10**(np.floor(np.log10(self.period[aa])))
                     hheight = self.arrow_head_height*\
                                 10**(np.floor(np.log10(self.period[aa])))
                else:
                    hwidth = self.arrow_head_width/\
                                 10**(np.floor(np.log10(self.period[aa])))
                    hheight = self.arrow_head_height/\
                                 10**(np.floor(np.log10(self.period[aa]))) 
                if np.log10(self.period[aa])<0:
                    alw = self.arrow_lw*self.period[aa]
                else:
                    alw = self.arrow_lw
                #--> plot real arrows
                if self.plot_tipper.find('r')>0:
                    self.axt.arrow(self.period[aa],
                                   0,
                                   xlenr,
                                   tyr[aa],
                                   lw=alw,
                                   facecolor=self.arrow_color_real,
                                   edgecolor=self.arrow_color_real,
                                   head_width=hwidth,
                                   head_length=hheight,
                                   length_includes_head=False)
                    
                    if aa==0:
                        line1=self.axt.plot(0, 0, self.arrow_color_real)
                        tiplst.append(line1[0])
                        tiplabel.append('real')
                                   
                #--> plot imaginary arrows
                if self.plot_tipper.find('i')>0:               
                    self.axt.arrow(self.period[aa],
                                   0,
                                   xleni,
                                   tyi[aa],
                                   lw=alw,
                                   facecolor=self.arrow_color_imag,
                                   edgecolor=self.arrow_color_imag,
                                   length_includes_head=False)
                    if aa==0:              
                        line2=self.axt.plot(0, 0, self.arrow_color_imag)
                        tiplst.append(line2[0])
                        tiplabel.append('imag')
                
            #make a line at 0 for reference
            self.axt.plot(self.period,[0]*nt,'k',lw=.5)
        
          
            self.axt.legend(tiplst,tiplabel,
                            loc='upper left',
                            markerscale=1,
                            borderaxespad=.01,
                            labelspacing=.07,
                            handletextpad=.2,
                            borderpad=.1,
                            prop={'size':self.font_size})

            #set axis properties            
            self.axt.yaxis.set_major_locator(MultipleLocator(.2))               
            self.axt.yaxis.set_minor_locator(MultipleLocator(.1))               
            self.axt.set_xlabel('Period (s)', fontdict=fontdict)
            self.axt.set_ylabel('Tipper', fontdict=fontdict)    
            
            self.axt.set_xscale('log')
            if self.tipper_limits is None:
                tmax = max([np.sqrt(txr.max()**2+tyr.max()**2),
                            np.sqrt(txi.max()**2+tyi.max()**2)])
                if tmax>1:
                    tmax=.899
                            
                tmin = -min([np.sqrt(txr.min()**2+tyr.min()**2),
                            np.sqrt(txi.min()**2+tyi.min()**2)])
                if tmin<-1:
                    tmin=-.899
                            
                self.tipper_limits = (tmin-.1, tmax+.1)
            
            self.axt.set_ylim(self.tipper_limits)
            self.axt.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                          lw=.25)
                          
        #------plot strike angles----------------------------------------------
        if self.plot_strike!='n' or self.plot_skew=='y':
            try:
                plt.setp(self.axp.xaxis.get_ticklabels(), visible=False)
                plt.setp(self.axt.xaxis.get_ticklabels(), visible=False)
            except AttributeError:
                pass
            
            stlst = []
            stlabel=[]
            st_maxlst =[]
            st_minlst =[]
            
            if self.plot_strike=='y' or self.plot_strike==1:
                #strike from invariants
                zinv = self._mt.get_Zinvariants()
                s1 = zinv.strike
                
                #fold angles so go from -90 to 90
                s1[np.where(s1>90)] = s1[np.where(s1>90)]-180
                s1[np.where(s1<-90)] = s1[np.where(s1<-90)]+180
                
                #plot strike with error bars
                ps1 = self.axs.errorbar(self.period, 
                                        s1, 
                                        marker=self.strike_inv_marker, 
                                        ms=self.marker_size, 
                                        mfc=self.strike_inv_color, 
                                        mec=self.strike_inv_color, 
                                        mew=self.marker_lw,
                                        ls='none', 
                                        yerr=zinv.strike_err, 
                                        ecolor=self.strike_inv_color,
                                        capsize=self.marker_size,
                                        elinewidth=self.marker_lw)
                                        
                stlst.append(ps1[0])
                stlabel.append('Z_inv')
                st_maxlst.append(s1.max())
                st_minlst.append(s1.min())
                                        
            if self.plot_strike=='y' or self.plot_strike==2:
                
                #strike from phase tensor
                pt = self._mt.get_PhaseTensor()
                s2, s2_err = pt.azimuth
                
                #fold angles to go from -90 to 90
                s2[np.where(s2>90)] = s2[np.where(s2>90)]-180
                s2[np.where(s2<-90)] = s2[np.where(s2<-90)]+180
                
                #plot strike with error bars
                ps2 = self.axs.errorbar(self.period, 
                                        s2, 
                                        marker=self.strike_pt_marker, 
                                        ms=self.marker_size, 
                                        mfc=self.strike_pt_color, 
                                        mec=self.strike_pt_color, 
                                        mew=self.marker_lw,
                                        ls='none', 
                                        yerr=s2_err, 
                                        ecolor=self.strike_pt_color,
                                        capsize=self.marker_size,
                                        elinewidth=self.marker_lw)
                                        
                stlst.append(ps2[0])
                stlabel.append('PT')
                st_maxlst.append(s2.max())
                st_minlst.append(s2.min())
            
            if self.plot_strike=='y' or self.plot_strike==3:
                #strike from tipper
                tp = self._mt.get_Tipper()
                s3 = tp.ang_real+90
                
                #fold to go from -90 to 90
                s3[np.where(s3>90)] = s3[np.where(s3>90)]-180
                s3[np.where(s3<-90)] = s3[np.where(s3<-90)]+180
                
                #plot strike with error bars
                ps3 = self.axs.errorbar(self.period, 
                                        s3, 
                                        marker=self.strike_tip_marker, 
                                        ms=self.marker_size, 
                                        mfc=self.strike_tip_color, 
                                        mec=self.strike_tip_color, 
                                        mew=self.marker_lw,
                                        ls='none', 
                                        yerr=np.zeros_like(s3), 
                                        ecolor=self.strike_tip_color,
                                        capsize=self.marker_size,
                                        elinewidth=self.marker_lw)
                                        
                stlst.append(ps3[0])
                stlabel.append('Tip')
                st_maxlst.append(s3.max())
                st_minlst.append(s3.min())
            
            #------plot skew angle---------------------------------------------
            if self.plot_skew=='y':
                #strike from phase tensor
                pt = self._mt.get_PhaseTensor()
                sk, sk_err = pt.beta
                
                
                self.axs2 = self.axs.twinx()
                ps4 = self.axs2.errorbar(self.period, 
                                        sk, 
                                        marker=self.beta_marker, 
                                        ms=self.marker_size, 
                                        mfc=self.skew_color, 
                                        mec=self.skew_color, 
                                        mew=self.marker_lw,
                                        ls='none', 
                                        yerr=sk_err, 
                                        ecolor=self.skew_color,
                                        capsize=self.marker_size,
                                        elinewidth=self.marker_lw)
                stlst.append(ps4[0])
                stlabel.append('Skew')
                if self.skew_limits is None:
                    self.skew_limits = (-9,9)
                
                #draw in boundaries where skew is not 3D
                #self.axs2.plot(self.axr.get_xlim(),[-3,-3],
                #               ls='--',
                #               color=self.skew_color,
                #               lw=.35)
                #               
                #self.axs2.plot(self.axr.get_xlim(),[3,3],
                #               ls='--',
                #               color=self.skew_color,
                #               lw=.35)
                # 
                # fill the area in which skew is good
                #self.axs2.fill_between(self.axr.get_xlim(), 
                #                       [-3,-3],
                #                       [3,3],
                #                       facecolor=self.skew_color, 
                #                       alpha=0.35)
                
                self.axs2.set_ylim(self.skew_limits)
                self.axs2.yaxis.set_major_locator(MultipleLocator(3))
                self.axs2.yaxis.set_minor_locator(MultipleLocator(1))
                self.axs2.set_ylabel('Skew', color=self.skew_color)
                self.axs2.set_xscale('log')
                for tl in self.axs2.get_yticklabels():
                    tl.set_color(self.skew_color)
                    
                st_minlst.append(0.0)
                st_maxlst.append(0.0)
                
            #--> set axes properties
            if self.strike_limits is None:
                stmin = min(st_minlst)
                if stmin-3<-90:
                    stmin -= 3
                else:
                    stmin = -89.99
                    
                stmax = max(st_maxlst)
                if stmin+3<90:
                    stmin += 3
                else:
                    stmin = 89.99
                self.strike_limits = (-max([abs(stmin), abs(stmax)]),
                                       max([abs(stmin), abs(stmax)]))
                                        
                
            self.axs.plot(self.axr.get_xlim(),[0,0],color='k',lw=.5)
            
            self.axs.set_ylabel('Strike',
                                fontdict=fontdict)
            self.axs.set_xlabel('Period (s)',
                                fontdict=fontdict)
            self.axs.set_ylim(self.strike_limits)
            self.axs.yaxis.set_major_locator(MultipleLocator(30))
            self.axs.yaxis.set_minor_locator(MultipleLocator(5))
            self.axs.set_xscale('log')
            self.axs.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                          lw=.25)
            try:
                self.axs.legend(stlst, 
                                stlabel,
                                loc=3, 
                                markerscale=1, 
                                borderaxespad=.01,
                                labelspacing=.07, 
                                handletextpad=.2, 
                                borderpad=.02,
                                prop={'size':self.font_size-1})
            except:
                pass

        #===Plot the xx, yy components if desired==============================
        if self.plotnum==2:
            #---------plot the apparent resistivity----------------------------
            self.axr2 = self.fig.add_subplot(gs[0,1], sharex=self.axr)
            self.axr2.yaxis.set_label_coords(-.1, 0.5)
            
            #res_xx
            self.ebxxr = self.axr2.errorbar(self.period, 
                                            self.rp.resxx, 
                                            marker=self.xy_marker, 
                                            ms=self.marker_size, 
                                            mfc=self.xy_mfc,
                                            mec=self.xy_color, 
                                            mew=self.marker_lw,
                                            ls=self.xy_ls, 
                                            yerr=self.rp.resxx_err, 
                                            ecolor=self.xy_color,
                                            capsize=self.marker_size,
                                            elinewidth=self.marker_lw)
            
            #res_yy                              
            self.ebyyr = self.axr2.errorbar(self.period, 
                                            self.rp.resyy, 
                                            marker=self.yx_marker, 
                                            ms=self.marker_size, 
                                            mfc=self.yx_mfc, 
                                            mec=self.yx_color, 
                                            mew=self.marker_lw, 
                                            ls=self.yx_ls, 
                                            yerr=self.rp.resyy_err, 
                                            ecolor=self.yx_color,
                                            capsize=self.marker_size,
                                            elinewidth=self.marker_lw)

            #--> set axes properties
            plt.setp(self.axr2.get_xticklabels(), visible=False)
            self.axr2.set_yscale('log')
            self.axr2.set_xscale('log')
            self.axr2.set_xlim(self.xlimits)
            self.axr2.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                           lw=.25)
            self.axr2.legend((self.ebxxr[0], self.ebyyr[0]), 
                            ('$Z_{xx}$','$Z_{yy}$'),
                            loc=3, markerscale=1, 
                            borderaxespad=.01,
                            labelspacing=.07, 
                            handletextpad=.2, 
                            borderpad=.02)
            
            #-----Plot the phase-----------------------------------------------
            self.axp2=self.fig.add_subplot(gs[1,1], sharex=self.axr)
            
            self.axp2.yaxis.set_label_coords(-.1, 0.5)
            
            #phase_xx
            self.ebxxp = self.axp2.errorbar(self.period, 
                                            self.rp.phasexx, 
                                            marker=self.xy_marker, 
                                            ms=self.marker_size, 
                                            mfc=self.xy_mfc, 
                                            mec=self.xy_color, 
                                            mew=self.marker_lw, 
                                            ls=self.xy_ls, 
                                            yerr=self.rp.phasexx_err,
                                            ecolor=self.xy_color,
                                            capsize=self.marker_size,
                                            elinewidth=self.marker_lw)
                                            
            #phase_yy
            self.ebyyp = self.axp2.errorbar(self.period,
                                            self.rp.phaseyy, 
                                            marker=self.yx_marker,
                                            ms=self.marker_size, 
                                            mfc=self.yx_mfc,
                                            mec=self.yx_color, 
                                            mew=self.marker_lw, 
                                            ls=self.yx_ls, 
                                            yerr=self.rp.phaseyy_err, 
                                            ecolor=self.yx_color,
                                            capsize=self.marker_size,
                                            elinewidth=self.marker_lw)
            
            #--> set axes properties
            self.axp2.set_xlabel('Period (s)', fontdict)
            self.axp2.set_xscale('log')
            self.axp2.set_ylim(ymin=-179.9, ymax=179.9)        
            self.axp2.yaxis.set_major_locator(MultipleLocator(30))
            self.axp2.yaxis.set_minor_locator(MultipleLocator(5))
            self.axp2.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                           lw=.25) 
                           
            if self.plot_tipper.find('y')==0 or self.plot_skew=='y':
                plt.setp(self.axp2.xaxis.get_ticklabels(), visible=False)
                plt.setp(self.axp2.xaxis.get_label(),visible=False)
        
        #===Plot the Determinant if desired====================================                          
        if self.plotnum==3:
                
            #res_det
            self.ebdetr = self.axr.errorbar(self.period, 
                                            self.rp.resdet, 
                                            marker=self.det_marker, 
                                            ms=self.marker_size, 
                                            mfc=self.det_mfc,
                                            mec=self.det_color, 
                                            mew=self.marker_lw, 
                                            ls=self.det_ls, 
                                            yerr=self.rp.resdet_err, 
                                            ecolor=self.det_color,
                                            capsize=self.marker_size,
                                            elinewidth=self.marker_lw)
        
            #phase_det
            self.ebdetp = self.axp.errorbar(self.period, 
                                            self.rp.phasedet, 
                                            marker=self.det_marker, 
                                            ms=self.marker_size, 
                                            mfc=self.det_mfc, 
                                            mec=self.det_color, 
                                            mew=self.marker_lw, 
                                            ls=self.det_ls, 
                                            yerr=self.rp.phasedet_err, 
                                            ecolor=self.det_color,
                                            capsize=self.marker_size,
                                            elinewidth=self.marker_lw)
                                            
            self.axr.legend((self.ebxyr[0],self.ebyxr[0],self.ebdetr[0]),
                            ('$Z_{xy}$','$Z_{yx}$','$\det(\mathbf{\hat{Z}})$'),
                            loc=3,
                            markerscale=1,
                            borderaxespad=.01,
                            labelspacing=.07,
                            handletextpad=.2,
                            borderpad=.02)
        
        
        #make title and show
        if self.title!=None:
            self.fig.suptitle(self.title, fontdict=fontdict)
        else:
            if self._mt.station!=None:
                self.fig.suptitle(self._mt.station, fontdict=fontdict)
        plt.show()
        
    def save_plot(self, save_fn, file_format='pdf', orientation='portrait', 
                  fig_dpi=None, close_plot='y'):
        """
        save_plot will save the figure to save_fn.
        
        Arguments:
        -----------
        
            **save_fn** : string
                          full path to save figure to, can be input as
                          * directory path -> the directory path to save to
                            in which the file will be saved as 
                            save_fn/station_name_ResPhase.file_format
                            
                          * full path -> file will be save to the given 
                            path.  If you use this option then the format
                            will be assumed to be provided by the path
                            
            **file_format** : [ pdf | eps | jpg | png | svg ]
                              file type of saved figure pdf,svg,eps... 
                              
            **orientation** : [ landscape | portrait ]
                              orientation in which the file will be saved
                              *default* is portrait
                              
            **fig_dpi** : int
                          The resolution in dots-per-inch the file will be
                          saved.  If None then the dpi will be that at 
                          which the figure was made.  I don't think that 
                          it can be larger than dpi of the figure.
                          
            **close_plot** : [ y | n ]
                             * 'y' will close the plot after saving.
                             * 'n' will leave plot open
                          
        :Example: ::
            
            >>> # to save plot as jpg
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> p1.save_plot(r'/home/MT/figures', file_format='jpg')
            
        """

        if fig_dpi==None:
            fig_dpi = self.dpi
            
        if os.path.isdir(save_fn)==False:
            file_format = save_fn[-3:]
            self.fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                             orientation=orientation)
            plt.clf()
            plt.close(self.fig)
            
        else:
            save_fn = os.path.join(save_fn,self.station+'_ResPhase.'+
                                    file_format)
            self.fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                        orientation=orientation)
        
        if close_plot=='y':
            plt.clf()
            plt.close(self.fig)
        
        else:
            pass
        
        self.fig_fn = save_fn
        print 'Saved figure to: '+self.fig_fn

    def update_plot(self):
        """
        update any parameters that where changed using the built-in draw from
        canvas.  
        
        Use this if you change an of the .fig or axes properties
        
        :Example: ::
            
            >>> # to change the grid lines to only be on the major ticks
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> [ax.grid(True, which='major') for ax in [p1.axr,p1.axp]]
            >>> p1.update_plot()
        
        """

        self.fig.canvas.draw()
        
    def redraw_plot(self):
        """
        use this function if you updated some attributes and want to re-plot.
        
        :Example: ::
            
            >>> # change the color and marker of the xy components
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> p1.xy_color = (.5,.5,.9)
            >>> p1.xy_marker = '*'
            >>> p1.redraw_plot()
        """
        
        plt.close(self.fig)
        self.plot()
        
    def __str__(self):
        """
        rewrite the string builtin to give a useful message
        """
        
        return "Plots Resistivity and phase for the different modes of the MT \n" +\
              "response.  At the moment it supports the input of an .edi \n"+\
              "file. Other formats that will be supported are the impedance\n"+\
              "tensor and errors with an array of periods and .j format.\n"


class PlotMultipleResPhase(object):
    """
    plots multiple MT responses simultaneously either in single plots or in 
    one plot of subfigures or in a single plot with subfigures for each 
    component.
    
    expecting only one type of input --> can be:
        **fn_lst** : list of filenames to plot
           
         **z_object_lst** : list of mtpy.core.z.Z objects
         
         **res_object_lst** : list of mtpy.imaging.mtplot.ResPhase objects
         
         **tipper_object_lst** : list of mtpy.imaging.mtplot.Tipper objects
         
         **mt_object_lst** : list of mtpy.imaging.mtplot.MTplot objects
         
        
    Arguments:
    ----------
        **fn_lst** : list of filenames to plot
                     ie. [fn_1, fn_2, ...], *default* is None
           
         **z_object_lst** : list of mtpy.core.z.Z objects
                            *default* is None
         
         **res_object_lst** : list of mtpy.imaging.mtplot.ResPhase objects
                              *default* is None
         
         **tipper_object_lst** : list of mtpy.imaging.mtplot.Tipper objects
                                 *default* is None
         
         **mt_object_lst** : list of mtpy.imaging.mtplot.MTplot objects
                             *default* is None
                      
        **fignum** : int
                     figure number
                     *default* is 1
        
        **rot_z** : float or np.ndarray
                   rotation angle of impedance tensor (deg or radians), 
                   *Note* : rotaion is clockwise positive
                   *default* is 0
                   Can input so each station is rotated at a constant angle or
                   each period is rotated differently, or both.
        
        **plotnum** : [ 1 | 2 | 3 ]
                        * 1 for just Ex/By and Ey/Bx *default*
                        * 2 for all 4 components
                        * 3 for off diagonal plus the determinant
                        
        **plot_style** : [ '1' | 'all' | 'compare' ]
                        determines the plotting style:
                            * '1' for plotting each station in a different 
                                  figure. *default*
                                  
                            * 'all' for plotting each station in a subplot
                                    all in the same figure
                            
                            * 'compare' for comparing the responses all in 
                                        one plot.  Here the responses are 
                                        colored from dark to light.  This 
                                        plot can get messy if too many stations
                                        are plotted.  
                                    
    
        **title** : string
                    title of plot
                    *default* is station name
                    
        **plot_tipper** : [ 'yri' | 'yr' | 'yi' | 'n' ]
                          Plots the tipper in a bottom pannel
                          * 'yri'  --> plots the real and imaginar parts
                          * 'yr'   --> plots just the real part
                          * 'yi'   --> plots just the imaginary part
                          
                          **Note:** the convention is to point towards a 
                          conductor.  Can change this by setting the
                          parameter arrow_direction = 1.
                          
        **plot_strike** : [ 'y' | 1 | 2 | 3 | 'n' ]
                          Plots the strike angle from different parameters:
                              * 'y'  --> plots strike angle determined from 
                                         the invariants of Weaver et al. [2000]
                                         and the phase tensor of
                                         Caldwell et al. [2004], if Tipper is 
                                         plotted the strike of the tipper is
                                         also plotted.
                                         
                               * 1  --> plots strike angle determined from 
                                        the invariants of Weaver et al. [2000]
                               * 2  --> plots strike angle determined from 
                                        the phase tensor of 
                                        Caldwell et al. [2004]
                               * 3  --> plots strike angle determined from 
                                        the tipper
                               * 'n' --> doesn't plot the strike, *default*
                               
        **plot_skew** : [ 'y' | 'n' ]
                       string for plotting skew angle.  This is plotted in 
                       the same plot as strike angle at the moment.  
                           * 'y' for plotting the skew
                           * 'n' for not plotting skew *default*
                          
        **dpi** : int
                 dots-per-inch resolution, *default* is 300
                    
                        
        :Example: ::
            
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> import os
            >>> edipath = r"/home/Edifiles"
            >>> edilst = [os.path.join(edipath,edi) 
            >>> ...       for edi in os.listdir(edipath)
            >>> ...       if edi.find('.edi')>0]
            >>> plot each station in a subplot all in one figure with tipper
            >>> rp1 = mtplot.PlotMultipleResPhase(edilst, plotnum=1, 
            >>> ...                                plot_tipper='yr,
            >>> ...                                plot_style='all')

            
    Attributes:
    -----------
        -mt_lst         list of mtplot.MTplot objects made from inputs 
        -fignum         figure number for plotting
        -plotnum        plot type, see arguments for details 
        -title          title of the plot, *default* is station name
        -dpi            Dots-per-inch resolution of plot, *default* is 300
        -rotz           Rotate impedance tensor by this angle (deg) assuming
                        that North is 0 and angle is positive clockwise
                        
        -plot_tipper    string to tell the program to plot tipper arrows or 
                        not, see accepted values above in arguments
        
        -plot_strike    string or integer telling the program to plot the 
                        strike angle, see values above in arguments
        
        -plot_skew      string to tell the program to plot skew angle.
                        The skew is plotted in the same subplot as the strike
                        angle at the moment
                        
                
        -period          period array cooresponding to the impedance tensor
        -font_size       size of font for the axis ticklabels, note that the 
                         axis labels will be font_size+2
        
        -axr             matplotlib.axes object for the xy,yx resistivity plot.  
        -axp             matplotlib.axes object for the xy,yx phase plot
        -axt             matplotlib.axes object for the tipper plot
        -ax2r            matplotlib.axes object for the xx,yy resistivity plot
        -ax2p            matplotlib.axes object for the xx,yy phase plot
        -axs             matplotlib.axes object for the strike plot
        -axs2            matplotlib.axes object for the skew plot
        
        ..
        
             **Note:** that from these axes object you have control of the
             plot.  You can do this by changing any parameter in the 
             axes object and then calling update_plot()
        
        -erxyr          class matplotlib.container.ErrorbarContainer for 
                        xy apparent resistivity.
        -erxyp          class matplotlib.container.ErrorbarContainer for 
                        xy.
        -eryxr          class matplotlib.container.ErrorbarContainer for 
                        yx apparent resistivity.
        -eryxp          class matplotlib.container.ErrorbarContainer for 
                        yx phase.
        
        ..
        
            **Note:** that from these line objects you can manipulate the 
            error bar properties and then call update_plot()
                     
        -xy_ls           line style for xy and xx components, *default* is None       
        -yx_ls           line style for yx and yy components, *default* is None        
        -det_ls          line style for determinant, *default* is None
        
        -xy_marker       marker for xy and xx, *default* is squares
        -yx_marker       marker for yx and yy, *default* is circles
        -det_marker      marker for determinant, *default* is diamonds
        
        -xy_color        marker color for xy and xx, *default* is blue
        -yx_color        marker color for yx and yy, *default* is red
        -det_color       marker color for determinant, *default* is green
        
        -xy_mfc          marker face color for xy and xx, *default* is None 
        -yx_mfc          marker face color for yx and yy, *default* is None
        -det_mfc         marker face color for determinant, *default* is None
        
        -skew_marker     marker for skew angle, *default* is 'd'
        -skew_color      color for skew angle, *default* is 'orange'
        
        -strike_inv_marker  marker for strike angle determined by invariants
                            *default* is '^'
        -strike_inv_color   color for strike angle determined by invaraiants 
                            *default* is (.2, .2, .7)
        -strike_pt_marker  marker for strike angle determined by pt, 
                           *default* is'v'
        -strike_pt_color   color for strike angle determined by pt
                           *default* is (.7, .2, .2)
        
        -strike_tip_marker  marker for strike angle determined by tipper
                            *default* is '>'
        -strike_tip_color   color for strike angle determined by tipper
                            *default* is (.2, .7, .2)
        
        -marker_size     size of marker in relative dimenstions, *default* is 2
        -marker_lw       line width of marker, *default* is 100./dpi 
        ..
        
         *For more on line and marker styles see matplotlib.lines.Line2D*
        
        -arrow_lw          line width of the arrow, *default* is 0.75
        -arrow_head_width  head width of the arrow, *default* is 0 for no arrow
                           head.  Haven't found a good way to scale the arrow
                           heads in a log scale.
                         
        -arrow_head_height  head width of the arrow, *default* is 0 for no arrow
                            head.  Haven't found a good way to scale the arrow
                            heads in a log scale.
                          
        -arrow_color_real  color of the real arrows, *default* is black
        -arrow_color_imag  color of the imaginary arrows, *default* is blue
        
        -arrow_direction   0 for pointing towards a conductor and -1 for 
                           pointing away from a conductor.
                          

        -xlimits        limits on the x-limits (period), *default* is None
                        which will estimate the min and max from the data, 
                        setting the min as the floor(min(period)) and the max
                        as ceil(max(period)).  Input in linear scale if you
                        want to change the period limits, ie. (.1,1000)
                        
        -res_limits     limits on the resistivity, *default* is None, which 
                        will estimate the min and max from the data, rounding
                        to the lowest and highest increments to the power of 10
                        Input in linear scale if you want to change them, 
                        ie. (1,10000). Note this only sets the xy and yx 
                        components, not the xx and yy.
                        
        -phase_limits   limits on the phase, *default* is (0,90) but will 
                        adapt to the data if there is phase above 90 or below
                        0.  Input in degrees.  Note this only changes the xy
                        and yx components.
                        
        -tipper_limits  limits of the y-axis, *default* is (-1,1)
    
    """

    def __init__(self, fn_lst=None, res_object_lst=None,
                 z_object_lst=None, tipper_object_lst=None, mt_object_lst=None,
                 fignum=1, dpi=300, rot_z=0, plot_num=1, plot_style='1', 
                 plot_yn='y', plot_tipper='n',plot_strike='n', plot_skew='n',
                 plotnum=1,title=None):
        """
        Initialize parameters
        """
        
        #--> get the inputs into a list of mt objects
        self.mt_lst = get_mtlst(fn_lst=fn_lst, 
                                 res_object_lst=res_object_lst,
                                 z_object_lst=z_object_lst, 
                                 tipper_object_lst=tipper_object_lst, 
                                 mt_object_lst=mt_object_lst)
        
        #set some of the properties as attributes much to Lars' discontent
        self.fignum = fignum
        self.plotnum = plotnum
        self.plot_style = plot_style
        self.title = title
        self.dpi = dpi
        
        #if rotation angle is an int or float make an array the length of 
        #mt_lst for plotting purposes
        if type(rot_z) is float or type(rot_z) is int:
            self.rot_z = np.array([rot_z]*len(self.mt_lst))
        
        #if the rotation angle is an array for rotation of different 
        #frequency than repeat that rotation array to the len(mt_lst)
        elif type(rot_z) is np.ndarray:
            if rot_z.shape[0]!=len(self.mt_lst):
                self.rot_z = np.repeat(rot_z, len(self.mt_lst))
                
        else:
            self.rot_z = rot_z

        
        #-->line properties
        #line style between points
        self.xy_ls='None'        
        self.yx_ls='None'        
        self.det_ls='None'        
        
        #outline color
        self.xy_color = 'b'
        self.yx_color = 'r'
        self.det_color = 'g'
        
        #face color
        self.xy_mfc='None'
        self.yx_mfc='None'
        self.det_mfc='None'
        
        #maker
        self.xy_marker = 's'
        self.yx_marker = 'o'
        self.det_marker = 'd'
        
        #size
        self.marker_size = 2
        
        #marker line width
        self.marker_lw = 100./self.dpi
        
        #set plot limits
        self.xlimits = None
        self.res_limits = None
        self.phase_limits = None
        self.tipper_limits = None
        self.strike_limits = None
        self.skew_limits = None
        
        #set font parameters
        self.font_size = 6
        
        #set plot tipper or not
        self.plot_tipper = plot_tipper
        
        #plot strike angle or not
        self.plot_strike = plot_strike
        
        #plot skew angle
        self.plot_skew = plot_skew
        
        #set arrow properties
        self.arrow_lw = .75
        self.arrow_head_width = 0.0
        self.arrow_head_height = 0.0
        self.arrow_color_real = 'k'
        self.arrow_color_imag = 'b'
        self.arrow_direction = 0
        
        #skew properties
        self.skew_color = (.85, .35, 0)
        self.skew_marker = 'd'
        
        #strike properties
        self.strike_inv_marker = '^'
        self.strike_inv_color = (.2, .2, .7)
        
        self.strike_pt_marker = 'v'
        self.strike_pt_color = (.7, .2, .2)
        
        self.strike_tip_marker = '>'
        self.strike_tip_color = (.2, .7, .2)
        
        self.label_dict = {-6:'$10^{-6}$',
                           -5:'$10^{-5}$',
                           -4:'$10^{-4}$',
                           -3:'$10^{-3}$',
                           -2:'$10^{-2}$', 
                           -1:'$10^{-1}$', 
                            0:'$10^{0}$',
                            1:'$10^{1}$',
                            2:'$10^{2}$',
                            3:'$10^{3}$',
                            4:'$10^{4}$',
                            5:'$10^{5}$',
                            6:'$10^{6}$',
                            7:'$10^{7}$',
                            8:'$10^{8}$'}

        #plot on initializing
        if plot_yn=='y':
            self.plot()
                            
    #---plot the resistivity and phase
    def plot(self):
        """
        plot the apparent resistivity and phase
        """
        
        if self.plot_style=='1':
            self.plotlst=[]
            
            #--> plot from edi's if given
            for ii,mt in enumerate(self.mt_lst,1):
                p1 = PlotResPhase(mt_object=mt, 
                                  fignum=ii, 
                                  plotnum=self.plotnum, 
                                  dpi=self.dpi, 
                                  rotz=self.rot_z[ii-1], 
                                  plot_yn='n',
                                  plot_tipper=self.plot_tipper,
                                  plot_strike=self.plot_strike,
                                  plot_skew=self.plot_skew)
                
                #make sure all the properties are set to match the users
                #line style between points
                p1.xy_ls = self.xy_ls        
                p1.yx_ls = self.yx_ls        
                p1.det_ls = self.det_ls        
                
                #outline color
                p1.xy_color = self.xy_color 
                p1.yx_color = self.yx_color 
                p1.det_color = self.det_color
                
                #face color
                p1.xy_mfc = self.xy_mfc
                p1.yx_mfc = self.yx_mfc
                p1.det_mfc = self.det_mfc
                
                #maker
                p1.xy_marker = self.xy_marker
                p1.yx_marker = self.yx_marker
                p1.det_marker = self.det_marker 
                
                #size
                p1.marker_size = 2
                
                #set plot limits
                p1.xlimits = self.xlimits
                p1.res_limits = self.res_limits
                p1.phase_limits = self.phase_limits

                #set font parameters
                p1.font_size = self.font_size
                
                #set arrow properties
                p1.arrow_lw = self.arrow_lw
                p1.arrow_head_width = self.arrow_head_width 
                p1.arrow_head_height = self.arrow_head_height
                p1.arrow_color_real = self.arrow_color_real 
                p1.arrow_color_imag = self.arrow_color_imag 
                p1.arrow_direction = self.arrow_direction
                p1.tipper_limits = self.tipper_limits 
                
                #skew properties
                p1.skew_color = self.skew_color
                p1.skew_marker = self.skew_marker
                
                #strike properties
                p1.strike_inv_marker = self.strike_inv_marker
                p1.strike_inv_color = self.strike_inv_color
                
                p1.strike_pt_marker = self.strike_pt_marker
                p1.strike_pt_color = self.strike_pt_color
                
                p1.strike_tip_marker = self.strike_tip_marker
                p1.strike_tip_color = self.strike_tip_color
                
                #--> plot the apparent resistivity and phase
                self.plotlst.append(p1)
                
                p1.plot()
                    
        
        #-----Plot All in one figure with each plot as a subfigure------------        
        if self.plot_style=='all':

            ns = len(self.mt_lst)

            #set some parameters of the figure and subplot spacing
            plt.rcParams['font.size'] = self.font_size
            if self.plot_skew=='y':
                plt.rcParams['figure.subplot.right'] = .94
            else:
                plt.rcParams['figure.subplot.right'] = .98
            plt.rcParams['figure.subplot.bottom'] = .1
            plt.rcParams['figure.subplot.top'] = .93
            
            #set the font properties for the axis labels
            fontdict={'size':self.font_size+2, 'weight':'bold'}
            
            #set figure size according to what the plot will be.
            if self.plotnum==1 or self.plotnum==3:
                self.figsize = [ns*4,6]
                
            elif self.plotnum==2:
                self.figsize = [ns*8,6]
                
            #make a figure instance
            self.fig = plt.figure(self.fignum, self.figsize, dpi=self.dpi)
                
            #make subplots as columns for all stations that need to be plotted
            gs0 = gridspec.GridSpec(1, ns)
                
            #space out the subplots
            gs0.update(hspace=.025, wspace=.025, left=.085)
     
            for ii,mt in enumerate(self.mt_lst):
                #get the reistivity and phase object
                rp = mt.get_ResPhase()
                rp.rotate(self.rot_z[ii])
                
                #set x-axis limits from short period to long period
                if self.xlimits==None:
                    self.xlimits = (10**(np.floor(np.log10(mt.period[0]))),
                                    10**(np.ceil(np.log10((mt.period[-1])))))
                if self.phase_limits==None:
                    pass
                    
                if self.res_limits==None:
                    self.res_limits = (10**(np.floor(
                                    np.log10(min([rp.resxy.min(),
                                                  rp.resyx.min()])))),
                              10**(np.ceil(
                                    np.log10(max([rp.resxy.max(),
                                                  rp.resyx.max()])))))

                # create a grid to place the figures into, set to have 2 rows 
                # and 2 columns to put any of the 4 components.  Make the phase
                # plot slightly shorter than the apparent resistivity plot and 
                # have the two close to eachother vertically.
                
                #--> make figure for xy,yx components
                if self.plotnum==1 or self.plotnum==3:
                    #--> plot tipper
                    if self.plot_tipper.find('y')==0:
                        #--> plot strike and or skew
                        if self.plot_strike=='y' or self.plot_skew=='y':
                            #make subplots for each subplot in the figure
                            ax1 = gridspec.GridSpecFromSubplotSpec(4, 1, 
                                                       subplot_spec=gs0[ii],
                                                       height_ratios=[2,1.5,1,1], 
                                                       hspace=.00)
                            axr = self.fig.add_subplot(ax1[0,0])
                            axp = self.fig.add_subplot(ax1[1,0], sharex=axr)
                            axt = self.fig.add_subplot(ax1[2,0], sharex=axr)
                            axs = self.fig.add_subplot(ax1[3,0], sharex=axr)
                       
                       #--> don't plot strike or skew    
                        else:
                            #make subplots for each subplot in the figure
                            ax1 = gridspec.GridSpecFromSubplotSpec(3, 1, 
                                                       subplot_spec=gs0[ii],
                                                       height_ratios=[2,1.5,1], 
                                                       hspace=.00)
                            axr = self.fig.add_subplot(ax1[0,0])
                            axp = self.fig.add_subplot(ax1[1,0], sharex=axr)
                            axt = self.fig.add_subplot(ax1[2,0], sharex=axr)
                    
                    #--> don't plot tipper but plot skew and or strike
                    elif self.plot_strike=='y' or self.plot_skew=='y':
                        #make subplots for each subplot in the figure
                        ax1 = gridspec.GridSpecFromSubplotSpec(3, 1, 
                                                         subplot_spec=gs0[ii],
                                                         height_ratios=[2,1.5,1], 
                                                         hspace=.00)
                        axr = self.fig.add_subplot(ax1[0,0])
                        axp = self.fig.add_subplot(ax1[1,0], sharex=axr)
                        axs = self.fig.add_subplot(ax1[2,0], sharex=axr)
                   
                    #--> just plot resistivity and phase 
                    else:
                        #make subplots for each subplot in the figure
                        ax1 = gridspec.GridSpecFromSubplotSpec(2, 1, 
                                                         subplot_spec=gs0[ii],
                                                         height_ratios=[2,1.5], 
                                                         hspace=.00)
                        axr = self.fig.add_subplot(ax1[0,0])
                        axp = self.fig.add_subplot(ax1[1,0], sharex=axr)
                        
                    #place the y-coordinate labels in the same location for
                    #each axis
                    if ii==0:
                        axr.yaxis.set_label_coords(-.145, 0.5)
                        axp.yaxis.set_label_coords(-.145, 0.5)
                        if self.plot_tipper.find('y')==0:
                            axt.yaxis.set_label_coords(-.145, 0.5)
                        if self.plot_skew=='y' or self.plot_strike=='y':
                            axs.yaxis.set_label_coords(-.145, 0.5)
                    
                #--> make figure for all 4 components
                elif self.plotnum==2:
                    #--> plot tipper
                    if self.plot_tipper.find('y')==0:
                        #--> plot strike and or skew
                        if self.plot_strike=='y' or self.plot_skew=='y':
                            #make subplots for each subplot in the figure
                            ax1 = gridspec.GridSpecFromSubplotSpec(4, 2, 
                                                       subplot_spec=gs0[ii],
                                                       height_ratios=[2,1.5,1,1], 
                                                       hspace=.00)
                            axr = self.fig.add_subplot(ax1[0,0])
                            axp = self.fig.add_subplot(ax1[1,0], sharex=axr)
                            axr2 = self.fig.add_subplot(ax1[0,1], sharex=axr)
                            axp2 = self.fig.add_subplot(ax1[1,1], sharex=axr)
                            axt = self.fig.add_subplot(ax1[2,:], sharex=axr)
                            axs = self.fig.add_subplot(ax1[3,:], sharex=axr)
                       
                       #--> don't plot strike or skew    
                        else:
                            #make subplots for each subplot in the figure
                            ax1 = gridspec.GridSpecFromSubplotSpec(3, 2, 
                                                       subplot_spec=gs0[ii],
                                                       height_ratios=[2,1.5,1], 
                                                       hspace=.00)
                            axr = self.fig.add_subplot(ax1[0,0])
                            axp = self.fig.add_subplot(ax1[1,0], sharex=axr)
                            axr2 = self.fig.add_subplot(ax1[0,1], sharex=axr)
                            axp2 = self.fig.add_subplot(ax1[1,1], sharex=axr)
                            axt = self.fig.add_subplot(ax1[2,:], sharex=axr)
                    
                    #--> don't plot tipper but plot skew and or strike
                    elif self.plot_strike=='y' or self.plot_skew=='y':
                        #make subplots for each subplot in the figure
                        ax1 = gridspec.GridSpecFromSubplotSpec(3, 2, 
                                                         subplot_spec=gs0[ii],
                                                         height_ratios=[2,1.5,1], 
                                                         hspace=.00)
                        axr = self.fig.add_subplot(ax1[0,0])
                        axp = self.fig.add_subplot(ax1[1,0], sharex=axr)
                        axr2 = self.fig.add_subplot(ax1[0,1], sharex=axr)
                        axp2 = self.fig.add_subplot(ax1[1,1], sharex=axr)
                        axs = self.fig.add_subplot(ax1[2,:], sharex=axr)
                   
                    #--> just plot resistivity and phase 
                    else:
                        #make subplots for each subplot in the figure
                        ax1 = gridspec.GridSpecFromSubplotSpec(2, 2, 
                                                         subplot_spec=gs0[ii],
                                                         height_ratios=[2,1.5], 
                                                         hspace=.00)
                    
                        axr = self.fig.add_subplot(ax1[0,0])
                        axp = self.fig.add_subplot(ax1[1,0], sharex=axr)
                        axr2 = self.fig.add_subplot(ax1[0,1], sharex=axr)
                        axp2 = self.fig.add_subplot(ax1[1,1], sharex=axr)
                    #place the y-coordinate labels in the same location for
                    #each axis
                    if ii==0:
                        axr.yaxis.set_label_coords(-.145, 0.5)
                        axp.yaxis.set_label_coords(-.145, 0.5)
                        if self.plot_tipper.find('y')==0:
                            axt.yaxis.set_label_coords(-.145, 0.5)
                        if self.plot_skew=='y' or self.plot_strike=='y':
                            axs.yaxis.set_label_coords(-.145, 0.5)
                 
                #---------plot the apparent resistivity------------------------
                #--> plot as error bars and just as points xy-blue, yx-red
                #res_xy
                ebxyr = axr.errorbar(mt.period, 
                                     rp.resxy, 
                                     marker=self.xy_marker, 
                                     ms=self.marker_size, 
                                     mfc=self.xy_mfc, 
                                     mec=self.xy_color, 
                                     mew=self.marker_lw, 
                                     ls=self.xy_ls, 
                                     yerr=rp.resxy_err, 
                                     ecolor=self.xy_color,
                                     capsize=self.marker_size,
                                     elinewidth=self.marker_lw)
                
                #res_yx                              
                ebyxr = axr.errorbar(mt.period, 
                                     rp.resyx, 
                                     marker=self.yx_marker, 
                                     ms=self.marker_size, 
                                     mfc=self.yx_mfc,
                                     mec=self.yx_color, 
                                     mew=self.marker_lw,
                                     ls=self.yx_ls, 
                                     yerr=rp.resyx_err, 
                                     ecolor=self.yx_color,
                                     capsize=self.marker_size,
                                     elinewidth=self.marker_lw)
                                              
                #--> set axes properties
                plt.setp(axr.get_xticklabels(), visible=False)
                axr.set_yscale('log')
                axr.set_xscale('log')
                axr.set_xlim(self.xlimits)
                axr.set_ylim(self.res_limits)
                axr.grid(True, alpha=.25, which='both', 
                              color=(.25,.25,.25),
                              lw=.25)
                if ii==0:
                    axr.set_ylabel('App. Res. ($\mathbf{\Omega \cdot m}$)',
                                    fontdict=fontdict)
                    axr.legend((ebxyr[0],ebyxr[0]), 
                                ('$Z_{xy}$','$Z_{yx}$'),
                                loc=3, 
                                markerscale=1, 
                                borderaxespad=.01,
                                labelspacing=.07, 
                                handletextpad=.2, 
                                borderpad=.02)
                else:
                    plt.setp(axr.get_yticklabels(),visible=False)
                    
                    
                  #-----Plot the phase---------------------------------------------------
                #phase_xy
                ebxyp = axp.errorbar(mt.period, 
                                     rp.phasexy, 
                                     marker=self.xy_marker, 
                                     ms=self.marker_size, 
                                     mfc=self.xy_mfc,
                                     mec=self.xy_color, 
                                     mew=self.marker_lw,
                                     ls=self.xy_ls,
                                     yerr=rp.phasexy_err, 
                                     ecolor=self.xy_color,
                                     capsize=self.marker_size,
                                     elinewidth=self.marker_lw)
                                              
                #phase_yx:
                ebyxp = axp.errorbar(mt.period, 
                                     rp.phaseyx, 
                                     marker=self.yx_marker, 
                                     ms=self.marker_size, 
                                     mfc=self.yx_mfc, 
                                     mec=self.yx_color, 
                                     mew=self.marker_lw,
                                     ls=self.yx_ls, 
                                     yerr=rp.phaseyx_err, 
                                     ecolor=self.yx_color,
                                     capsize=self.marker_size,
                                     elinewidth=self.marker_lw)
        
                #check the phase to see if any point are outside of [0:90]
                if self.phase_limits==None:
                    if min(rp.phasexy)<0 or min(rp.phaseyx)<0:
                         pymin = min([min(rp.phasexy), 
                                      min(rp.phaseyx)])
                         if pymin>0:
                            pymin = 0
                    else:
                        pymin = 0
                    
                    if max(rp.phasexy)>90 or max(rp.phaseyx)>90:
                        pymax = min([max(rp.phasexy), 
                                     max(rp.phaseyx)])
                        if pymax<91:
                            pymax = 89.9
                    else:
                        pymax = 89.9
                        
                    self.phase_limits = (pymin, pymax)
                
                #--> set axes properties
                if ii==0:
                    axp.set_ylabel('Phase (deg)', fontdict)
                else:
                    plt.setp(axp.get_yticklabels(), visible=False)
                    
                if self.plot_tipper=='n' and self.plot_skew=='n' and \
                        self.plot_strike=='n':
                    axp.set_xlabel('Period (s)', fontdict)
                    
                axp.set_xscale('log')
                axp.set_ylim(self.phase_limits)        
                axp.yaxis.set_major_locator(MultipleLocator(15))
                axp.yaxis.set_minor_locator(MultipleLocator(5))
                axp.grid(True, alpha=.25, which='both', 
                              color=(.25,.25,.25),
                              lw=.25)
                                  
                tklabels=[self.label_dict[tt] 
                          for tt in np.arange(np.log10(self.xlimits[0]),
                                              np.log10(self.xlimits[1])+1)]
                tklabels[0]=''
                tklabels[-1]=''
                
                axp.set_xticklabels(tklabels,
                                    fontdict={'size':self.font_size})
                                    
                #-----plot tipper------------------------------------------------------              
                if self.plot_tipper.find('y')==0:
                    plt.setp(axp.xaxis.get_ticklabels(), visible=False)
                    
                    tp = mt.get_Tipper()
                    
                    txr = tp.mag_real*np.cos(tp.ang_real*np.pi/180+\
                                             np.pi*self.arrow_direction)
                    tyr = tp.mag_real*np.sin(tp.ang_real*np.pi/180+\
                                             np.pi*self.arrow_direction)
            
                    txi = tp.mag_imag*np.cos(tp.ang_imag*np.pi/180+\
                                             np.pi*self.arrow_direction)
                    tyi = tp.mag_imag*np.sin(tp.ang_imag*np.pi/180+\
                                             np.pi*self.arrow_direction)
                    
                    nt = len(txr)
                    
                    tiplst=[]
                    tiplabel=[]
                    
                    for aa in range(nt):
                        xlenr = txr[aa]*mt.period[aa]
                        xleni = txi[aa]*mt.period[aa]
                        
                        #scale the arrow head height and width to fit in a log scale
                        if np.log10(mt.period[aa])<0:
                             hwidth = self.arrow_head_width*\
                                     10**(np.floor(np.log10(mt.period[aa])))
                             hheight = self.arrow_head_height*\
                                     10**(np.floor(np.log10(mt.period[aa])))
                        else:
                            hwidth = self.arrow_head_width/\
                                    10**(np.floor(np.log10(mt.period[aa])))
                            hheight = self.arrow_head_height/\
                                    10**(np.floor(np.log10(mt.period[aa]))) 
                        if np.log10(mt.period[aa])<0:
                            alw = self.arrow_lw*mt.period[aa]
                        else:
                            alw = self.arrow_lw
                        #--> plot real arrows
                        if self.plot_tipper.find('r')>0:
                            axt.arrow(mt.period[aa],
                                      0,
                                      xlenr,
                                      tyr[aa],
                                      lw=alw,
                                      facecolor=self.arrow_color_real,
                                      edgecolor=self.arrow_color_real,
                                      head_width=hwidth,
                                      head_length=hheight,
                                      length_includes_head=False)
                            
                            if aa==0:
                                line1=axt.plot(0, 0, self.arrow_color_real)
                                tiplst.append(line1[0])
                                tiplabel.append('real')
                                           
                        #--> plot imaginary arrows
                        if self.plot_tipper.find('i')>0:               
                            axt.arrow(mt.period[aa],
                                      0,
                                      xleni,
                                      tyi[aa],
                                      lw=alw,
                                      facecolor=self.arrow_color_imag,
                                      edgecolor=self.arrow_color_imag,
                                      length_includes_head=False)
                            if aa==0:              
                                line2=axt.plot(0, 0, self.arrow_color_imag)
                                tiplst.append(line2[0])
                                tiplabel.append('imag')
                        
                    #make a line at 0 for reference
                    axt.plot(mt.period,[0]*nt,'k',lw=.5)
                
                  
                    if ii==0:
                        axt.legend(tiplst,tiplabel,
                                    loc='upper left',
                                    markerscale=1,
                                    borderaxespad=.01,
                                    labelspacing=.07,
                                    handletextpad=.2,
                                    borderpad=.1,
                                    prop={'size':self.font_size})
                        
                        axt.set_ylabel('Tipper', fontdict=fontdict) 
                    else:
                        plt.setp(axt.get_yticklabels(), visible=False)
        
                    #set axis properties            
                    axt.yaxis.set_major_locator(MultipleLocator(.2))               
                    axt.yaxis.set_minor_locator(MultipleLocator(.1))
                    axt.set_xlabel('Period (s)', fontdict=fontdict)
   
                    
                    axt.set_xscale('log')
                    if self.tipper_limits is None:
                        tmax = max([np.sqrt(txr.max()**2+tyr.max()**2),
                                    np.sqrt(txi.max()**2+tyi.max()**2)])
                        if tmax>1:
                            tmax=.899
                                    
                        tmin = -min([np.sqrt(txr.min()**2+tyr.min()**2),
                                    np.sqrt(txi.min()**2+tyi.min()**2)])
                        if tmin<-1:
                            tmin=-.899
                                    
                        self.tipper_limits = (tmin-.1, tmax+.1)
                    
                    axt.set_ylim(self.tipper_limits)
                    axt.grid(True, alpha=.25, which='both', 
                             color=(.25,.25,.25),
                             lw=.25)
                             
                    tklabels=[self.label_dict[tt] 
                              for tt in np.arange(np.log10(self.xlimits[0]),
                                              np.log10(self.xlimits[1])+1)]
                    tklabels[0]=''
                    tklabels[-1]=''
                
                    axt.set_xticklabels(tklabels,
                                    fontdict={'size':self.font_size})
                    
                #------plot strike angles----------------------------------------------
                if self.plot_strike!='n' or self.plot_skew=='y':
                    try:
                        plt.setp(axp.xaxis.get_ticklabels(), visible=False)
                        plt.setp(axt.xaxis.get_ticklabels(), visible=False)
                    except AttributeError:
                        pass
                    
                    stlst = []
                    stlabel=[]
                    st_maxlst =[]
                    st_minlst =[]
                    
                    if self.plot_strike=='y' or self.plot_strike==1:
                        #strike from invariants
                        zinv = mt.get_Zinvariants()
                        s1 = zinv.strike
                        
                        #fold angles so go from -90 to 90
                        s1[np.where(s1>90)] = s1[np.where(s1>90)]-180
                        s1[np.where(s1<-90)] = s1[np.where(s1<-90)]+180
                        
                        #plot strike with error bars
                        ps1 = axs.errorbar(mt.period, 
                                           s1, 
                                           marker=self.strike_inv_marker, 
                                           ms=self.marker_size, 
                                           mfc=self.strike_inv_color, 
                                           mec=self.strike_inv_color, 
                                           mew=self.marker_lw,
                                           ls='none', 
                                           yerr=zinv.strike_err, 
                                           ecolor=self.strike_inv_color,
                                           capsize=self.marker_size,
                                           elinewidth=self.marker_lw)
                                                
                        stlst.append(ps1[0])
                        stlabel.append('Z_inv')
                        st_maxlst.append(s1.max())
                        st_minlst.append(s1.min())
                                                
                    if self.plot_strike=='y' or self.plot_strike==2:
                        
                        #strike from phase tensor
                        pt = mt.get_PhaseTensor()
                        s2, s2_err = pt.azimuth
                        
                        #fold angles to go from -90 to 90
                        s2[np.where(s2>90)] = s2[np.where(s2>90)]-180
                        s2[np.where(s2<-90)] = s2[np.where(s2<-90)]+180
                        
                        #plot strike with error bars
                        ps2 = axs.errorbar(mt.period, 
                                           s2, 
                                           marker=self.strike_pt_marker, 
                                           ms=self.marker_size, 
                                           mfc=self.strike_pt_color, 
                                           mec=self.strike_pt_color, 
                                           mew=self.marker_lw,
                                           ls='none', 
                                           yerr=s2_err, 
                                           ecolor=self.strike_pt_color,
                                           capsize=self.marker_size,
                                           elinewidth=self.marker_lw)
                                                
                        stlst.append(ps2[0])
                        stlabel.append('PT')
                        st_maxlst.append(s2.max())
                        st_minlst.append(s2.min())
                    
                    if self.plot_strike=='y' or self.plot_strike==3:
                        #strike from tipper
                        tp = mt.get_Tipper()
                        s3 = tp.ang_real+90
                        
                        #fold to go from -90 to 90
                        s3[np.where(s3>90)] = s3[np.where(s3>90)]-180
                        s3[np.where(s3<-90)] = s3[np.where(s3<-90)]+180
                        
                        #plot strike with error bars
                        ps3 = axs.errorbar(mt.period, 
                                           s3, 
                                           marker=self.strike_tip_marker, 
                                           ms=self.marker_size, 
                                           mfc=self.strike_tip_color, 
                                           mec=self.strike_tip_color, 
                                           mew=self.marker_lw,
                                           ls='none', 
                                           yerr=np.zeros_like(s3), 
                                           ecolor=self.strike_tip_color,
                                           capsize=self.marker_size,
                                           elinewidth=self.marker_lw)
                                                
                        stlst.append(ps3[0])
                        stlabel.append('Tip')
                        st_maxlst.append(s3.max())
                        st_minlst.append(s3.min())
                        
                    #------plot skew angle-------------------------------------
                    if self.plot_skew=='y':
                        #strike from phase tensor
                        pt = mt.get_PhaseTensor()
                        sk, sk_err = pt.beta
                        
                        
                        axs2 = axs.twinx()
                        ps4 = axs2.errorbar(mt.period, 
                                            sk, 
                                            marker=self.skew_marker, 
                                            ms=self.marker_size, 
                                            mfc=self.skew_color, 
                                            mec=self.skew_color, 
                                            mew=self.marker_lw,
                                            ls='none', 
                                            yerr=sk_err, 
                                            ecolor=self.skew_color,
                                            capsize=self.marker_size,
                                            elinewidth=self.marker_lw)
                                            
                        stlst.append(ps4[0])
                        stlabel.append('Skew')
                        if self.skew_limits is None:
                            self.skew_limits = (-9,9)
                        
                        
                        axs2.set_ylim(self.skew_limits)
                        axs2.yaxis.set_major_locator(MultipleLocator(3))
                        axs2.yaxis.set_minor_locator(MultipleLocator(1))
                        if ii==len(self.mt_lst)-1:
                            axs2.set_ylabel('Skew', color=self.skew_color)
                        else:
                            plt.setp(axs2.get_yticklabels(), visible=False)
                            
                        axs2.set_xscale('log')
                        for tl in axs2.get_yticklabels():
                            tl.set_color(self.skew_color)
                            
                        st_minlst.append(0.0)
                        st_maxlst.append(0.0)
                        
                    #--> set axes properties
                    if self.strike_limits is None:
                        stmin = min(st_minlst)
                        if stmin-3<-90:
                            stmin -= 3
                        else:
                            stmin = -89.99
                            
                        stmax = max(st_maxlst)
                        if stmin+3<90:
                            stmin += 3
                        else:
                            stmin = 89.99
                        self.strike_limits = (-max([abs(stmin), abs(stmax)]),
                                               max([abs(stmin), abs(stmax)]))
                                                
                        
                    axs.plot(axr.get_xlim(),[0,0],color='k',lw=.5)
                    
                    if ii==0:
                        axs.set_ylabel('Strike',
                                            fontdict=fontdict)
                        try:
                            axs.legend(stlst, 
                                       stlabel,
                                       loc=3, 
                                       markerscale=1, 
                                       borderaxespad=.01,
                                       labelspacing=.07, 
                                       handletextpad=.2, 
                                       borderpad=.02,
                                       prop={'size':self.font_size-1})
                        except:
                            pass
                    else:
                        plt.setp(axs.get_yticklabels(), visible=False)
                    
                    axs.set_xlabel('Period (s)',
                                        fontdict=fontdict)
                    axs.set_ylim(self.strike_limits)
                    axs.yaxis.set_major_locator(MultipleLocator(30))
                    axs.yaxis.set_minor_locator(MultipleLocator(5))
                    axs.set_xscale('log')
                    axs.grid(True, 
                             alpha=.25, 
                             which='both', 
                             color=(.25,.25,.25),
                             lw=.25)
                             
                    tklabels=[self.label_dict[tt] 
                              for tt in np.arange(np.log10(self.xlimits[0]),
                                              np.log10(self.xlimits[1])+1)]
                    tklabels[0]=''
                    tklabels[-1]=''
                
                    axs.set_xticklabels(tklabels,
                                    fontdict={'size':self.font_size})
                    
                    #====Plot the Z_xx, Z_yy components if desired=============
                    if self.plotnum==2:
                        #---------plot the apparent resistivity----------------
                        axr2.yaxis.set_label_coords(-.1, 0.5)
                        
                        #res_xx
                        ebxxr = axr2.errorbar(mt.period, 
                                              rp.resxx, 
                                              marker=self.xy_marker, 
                                              ms=self.marker_size, 
                                              mfc=self.xy_mfc,
                                              mec=self.xy_color, 
                                              mew=self.marker_lw,
                                              ls=self.xy_ls, 
                                              yerr=rp.resxx_err, 
                                              ecolor=self.xy_color,
                                              capsize=self.marker_size,
                                              elinewidth=self.marker_lw)
                        
                        #res_yy                              
                        ebyyr = axr2.errorbar(mt.period, 
                                              rp.resyy, 
                                              marker=self.yx_marker, 
                                              ms=self.marker_size, 
                                              mfc=self.yx_mfc, 
                                              mec=self.yx_color, 
                                              mew=self.marker_lw, 
                                              ls=self.yx_ls, 
                                              yerr=rp.resyy_err, 
                                              ecolor=self.yx_color,
                                              capsize=self.marker_size,
                                              elinewidth=self.marker_lw)
            
                        #--> set axes properties
                        plt.setp(axr2.get_xticklabels(), visible=False)
                        
                        axr2.set_yscale('log')
                        axr2.set_xscale('log')
                        axr2.set_xlim(self.xlimits)
                        axr2.grid(True, 
                                  alpha=.25, 
                                  which='both', 
                                  color=(.25,.25,.25),
                                  lw=.25)
                        if ii==0:
                            axr2.legend((ebxxr[0], ebyyr[0]), 
                                        ('$Z_{xx}$','$Z_{yy}$'),
                                        loc=3, markerscale=1, 
                                        borderaxespad=.01,
                                        labelspacing=.07, 
                                        handletextpad=.2, 
                                        borderpad=.02)
                                            
                        
                        #-----Plot the phase-----------------------------------
                        
                        axp2.yaxis.set_label_coords(-.1, 0.5)
                        
                        #phase_xx
                        ebxxp = axp2.errorbar(mt.period, 
                                              rp.phasexx, 
                                              marker=self.xy_marker, 
                                              ms=self.marker_size, 
                                              mfc=self.xy_mfc, 
                                              mec=self.xy_color, 
                                              mew=self.marker_lw, 
                                              ls=self.xy_ls, 
                                              yerr=rp.phasexx_err,
                                              ecolor=self.xy_color,
                                              capsize=self.marker_size,
                                              elinewidth=self.marker_lw)
                                                        
                        #phase_yy
                        ebyyp = axp2.errorbar(mt.period,
                                              rp.phaseyy, 
                                              marker=self.yx_marker,
                                              ms=self.marker_size, 
                                              mfc=self.yx_mfc,
                                              mec=self.yx_color, 
                                              mew=self.marker_lw, 
                                              ls=self.yx_ls, 
                                              yerr=rp.phaseyy_err, 
                                              ecolor=self.yx_color,
                                              capsize=self.marker_size,
                                              elinewidth=self.marker_lw)
                        
                        #--> set axes properties
                        axp2.set_xlabel('Period (s)', fontdict)
                        axp2.set_xscale('log')
                        axp2.set_ylim(ymin=-179.9, ymax=179.9)        
                        axp2.yaxis.set_major_locator(MultipleLocator(30))
                        axp2.yaxis.set_minor_locator(MultipleLocator(5))
                        axp2.set_xticklabels(tklabels,
                                            fontdict={'size':self.font_size})
                        axp2.grid(True, 
                                  alpha=.25, 
                                  which='both', 
                                  color=(.25,.25,.25),
                                  lw=.25) 
                                   
                
                #===Plot the Determinant if desired============================                          
                if self.plotnum==3:
                        
                    #res_det
                    ebdetr = axr.errorbar(mt.period, 
                                          rp.resdet, 
                                          marker=self.det_marker, 
                                          ms=self.marker_size, 
                                          mfc=self.det_mfc,
                                          mec=self.det_color, 
                                          mew=self.marker_lw, 
                                          ls=self.det_ls, 
                                          yerr=rp.resdet_err, 
                                          ecolor=self.det_color,
                                          capsize=self.marker_size,
                                          elinewidth=self.marker_lw)
                
                    #phase_det
                    ebdetp = axp.errorbar(mt.period, 
                                          rp.phasedet, 
                                          marker=self.det_marker, 
                                          ms=self.marker_size, 
                                          mfc=self.det_mfc, 
                                          mec=self.det_color, 
                                          mew=self.marker_lw, 
                                          ls=self.det_ls, 
                                          yerr=rp.phasedet_err, 
                                          ecolor=self.det_color,
                                          capsize=self.marker_size,
                                          elinewidth=self.marker_lw)
                    
                    #--> set axes properties
                    plt.setp(axr.get_xticklabels(), visible=False)
                    if ii==0:
                        axr.set_ylabel('App. Res. ($\mathbf{\Omega \cdot m}$)',
                                            fontdict=fontdict)
                    else:
                        plt.setp(axr.get_yticklabels(), visible=False)
                                    
                    axr.set_yscale('log')
                    axr.set_xscale('log')
                    axr.set_ylim(self.res_limits)
                    axr.set_xlim(self.xlimits)
                    axr.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                                  lw=.25)
                                  
                    #--> set axes properties
                    axp.set_xlabel('Period (s)', fontdict)
                   
                    if ii==0:
                        axp.set_ylabel('Phase (deg)', fontdict)
                    
                    else:
                        plt.setp(axp.get_yticklabels(), visible=False)
                        
                    axp.set_xscale('log')
                    axp.set_ylim(self.phase_limits)        
                    axp.yaxis.set_major_locator(MultipleLocator(15))
                    axp.yaxis.set_minor_locator(MultipleLocator(5))
                    tklabels=[self.label_dict[tt] 
                              for tt in np.arange(np.log10(self.xlimits[0]),
                                                  np.log10(self.xlimits[1])+1)]
                    tklabels[0]=''
                    tklabels[-1]=''
                    
                    axp.set_xticklabels(tklabels,
                                        fontdict={'size':self.font_size})
                    axp.grid(True, alpha=.25, 
                                  which='both', 
                                  color=(.25,.25,.25),
                                  lw=.25)
                
                
                #make title and show
                axr.set_title(mt.station, fontsize=self.font_size, 
                              fontweight='bold')
                plt.show()
        
        #=====Plot all responses into one plot to compare changes=============
        if self.plot_style=='compare':
            ns = len(self.mt_lst)
            
            #make color lists for the plots going light to dark
            cxy = [(0, 0+float(cc)/ns, 1-float(cc)/ns) for cc in range(ns)]
            cyx = [(1, float(cc)/ns, 0) for cc in range(ns)]
            cdet = [(0, 1-float(cc)/ns, 0) for cc in range(ns)]
            ctipr = [(.75*cc/ns, .75*cc/ns, .75*cc/ns) for cc in range(ns)]
            ctipi = [(float(cc)/ns, 1-float(cc)/ns, .25) for cc in range(ns)]
            cst = [(.5*cc/ns, 0, .5*cc/ns) for cc in range(ns)]
            csk = [(.75*cc/ns, .25*cc/ns, 0) for cc in range(ns)]
            
            #make marker lists for the different components
            mxy=['s','D','x','+','*','1','3','4']*5
            myx=['o','h','8','p','H',7,4,6]*5
            
            legendlst=[]
            stationlst=[]
            tiplst=[]
            stlst=[]
            sklst=[]

            #set some parameters of the figure and subplot spacing
            plt.rcParams['font.size'] = self.font_size
            plt.rcParams['figure.subplot.bottom'] = .1
            plt.rcParams['figure.subplot.top'] = .93
            plt.rcParams['figure.subplot.left'] = .80
            if self.plot_skew=='y':
                plt.rcParams['figure.subplot.right'] = .90
            else:
                plt.rcParams['figure.subplot.right'] = .98
            
            #set the font properties for the axis labels
            fontdict={'size':self.font_size+2, 'weight':'bold'}
            
            #set figure size according to what the plot will be.
            if self.plotnum==1 or self.plotnum==3:
                self.figsize = [5,7]
                
            elif self.plotnum==2:
                self.figsize = [6,6]
                
            #make a figure instance
            self.fig = plt.figure(self.fignum, self.figsize, dpi=self.dpi)
            
            #make subplots
            if self.plot_tipper.find('y')==0:
                if self.plot_strike!='n' or self.plot_skew=='y':
                    gs = gridspec.GridSpec(4, 2, height_ratios=[2, 1.5, 1, 1], 
                                           hspace=.05)
                else:
                    gs = gridspec.GridSpec(3, 2, height_ratios=[2, 1.5, 1], 
                                           hspace=.05)
            else:
                if self.plot_strike!='n' or self.plot_skew=='y':
                    gs = gridspec.GridSpec(3, 2, height_ratios=[2, 1.5, 1],
                                           hspace=.05)
                else:
                    gs = gridspec.GridSpec(2, 2, height_ratios=[2, 1.5], 
                                       hspace=.01) 
            
            #--> make figure for xy,yx components
            if self.plotnum==1 or self.plotnum==3:
                #space out the subplots
                gs.update(hspace=.05, wspace=.15, left=.1)
                
                #--> create the axes instances
                if self.plot_tipper.find('y')==0:
                    #apparent resistivity axis
                    self.axr = self.fig.add_subplot(gs[0,:])
                    
                    #phase axis that shares period axis with resistivity
                    self.axp = self.fig.add_subplot(gs[1,:], sharex=self.axr)
                    
                    #tipper axis  
                    self.axt = self.fig.add_subplot(gs[2,:], sharex=self.axr)
                    
                    #place y coordinate labels in the same location                
                    self.axr.yaxis.set_label_coords(-.075, 0.5)
                    self.axp.yaxis.set_label_coords(-.075, 0.5)
                    self.axt.yaxis.set_label_coords(-.075, 0.5)
                    if self.plot_strike!='n' or self.plot_skew!='n':
                        self.axs = self.fig.add_subplot(gs[3,:], sharex=self.axr)
                        self.axs.yaxis.set_label_coords(-.075, 0.5)
                else:
                    #apparent resistivity axis
                    self.axr = plt.subplot(gs[0,:])
                    
                    #phase axis which shares the x axis with the resistivity
                    self.axp = plt.subplot(gs[1,:], sharex=self.axr)
                    
                    #place the y-coordinate labels in the same location
                    self.axr.yaxis.set_label_coords(-.075, 0.5)
                    self.axp.yaxis.set_label_coords(-.075, 0.5)
                    
                    #add stike axis if desired
                    if self.plot_strike!='n' or self.plot_skew!='n':
                        self.axs = self.fig.add_subplot(gs[2,:], sharex=self.axr)
                        self.axs.yaxis.set_label_coords(-.075, 0.5)
                        
                
            #--> make figure for all 4 components
            elif self.plotnum==2:
                
                #space out the subplots
                gs.update(hspace=.05, wspace=.15, left=.07)
                
                #--> create the axes instances
                if self.plot_tipper.find('y')==0:
                    #apparent resistivity axis
                    self.axr = self.fig.add_subplot(gs[0,0])
                    
                    #phase axis that shares period axis with resistivity
                    self.axp = self.fig.add_subplot(gs[1,0], sharex=self.axr)
                    
                    #tipper axis that shares period with resistivity 
                    self.axt = self.fig.add_subplot(gs[2,:], sharex=self.axr)
                    
                    #place y coordinate labels in the same location                
                    self.axr.yaxis.set_label_coords(-.095, 0.5)
                    self.axp.yaxis.set_label_coords(-.095, 0.5)
                    self.axt.yaxis.set_label_coords(-.095, 0.5)
                    
                    #add strike axis if desired
                    if self.plot_strike!='n' or self.plot_skew!='n':
                        self.axs = self.fig.add_subplot(gs[3,:], 
                                                        sharex=self.axr)
                        self.axs.yaxis.set_label_coords(-.095, 0.5)
                else:
                    #apparent resistivity axis
                    self.axr = plt.subplot(gs[0,0])
                    
                    #phase axis which shares the x axis with the resistivity
                    self.axp = plt.subplot(gs[1,0], sharex=self.axr)
                    
                    #place the y-coordinate labels in the same location
                    self.axr.yaxis.set_label_coords(-.095, 0.5)
                    self.axp.yaxis.set_label_coords(-.095, 0.5)
                    
                    #add strike axis if desired
                    if self.plot_strike!='n' or self.plot_skew!='n':
                        self.axs = self.fig.add_subplot(gs[2,:], 
                                                        sharex=self.axr)
                        self.axs.yaxis.set_label_coords(-.095, 0.5)
                        
            if self.plot_skew=='y':
                self.axs2 = self.axs.twinx()
    
            for ii,mt in enumerate(self.mt_lst):
                    
                #get the reistivity and phase object
                rp = mt.get_ResPhase()
                rp.rotate(self.rot_z[ii])
                
                #set x-axis limits from short period to long period
                if self.xlimits==None:
                    self.xlimits = (10**(np.floor(np.log10(mt.period[0]))),
                                    10**(np.ceil(np.log10((mt.period[-1])))))
                if self.phase_limits==None:
                    self.phase_limits = (0,89.9)
                
                stationlst.append(mt.station)
                
                #=========Plot Z_xy and Z_yx=================================== 
                if self.plotnum==1 or self.plotnum==2:
                    #---------plot the apparent resistivity--------------------
                    #--> plot as error bars and just as points xy-blue, yx-red
                    #res_xy
                    ebxyr = self.axr.errorbar(mt.period, 
                                             rp.resxy, 
                                             marker=mxy[ii], 
                                             ms=self.marker_size, 
                                             mfc='None', 
                                             mec=cxy[ii], 
                                             mew=self.marker_lw, 
                                             ls=self.xy_ls, 
                                             yerr=rp.resxy_err, 
                                             ecolor=cxy[ii],
                                             capsize=self.marker_size,
                                             elinewidth=self.marker_lw)
                    
                    #res_yx                              
                    ebyxr = self.axr.errorbar(mt.period, 
                                             rp.resyx, 
                                             marker=myx[ii], 
                                             ms=self.marker_size, 
                                             mfc='None',
                                             mec=cyx[ii], 
                                             mew=self.marker_lw,
                                             ls=self.yx_ls, 
                                             yerr=rp.resyx_err, 
                                             ecolor=cyx[ii],
                                             capsize=self.marker_size,
                                             elinewidth=self.marker_lw)
                                                  

                    #-----Plot the phase---------------------------------------
                    #phase_xy
                    ebxyp = self.axp.errorbar(mt.period, 
                                             rp.phasexy, 
                                             marker=mxy[ii], 
                                             ms=self.marker_size, 
                                             mfc='None',
                                             mec=cxy[ii], 
                                             mew=self.marker_lw,
                                             ls=self.xy_ls,
                                             yerr=rp.phasexy_err, 
                                             ecolor=cxy[ii],
                                             capsize=self.marker_size,
                                             elinewidth=self.marker_lw)
                                                  
                    #phase_yx: Note add 180 to place it in same quadrant as
                    #phase_xy
                    ebyxp = self.axp.errorbar(mt.period, 
                                             rp.phaseyx, 
                                             marker=myx[ii], 
                                             ms=self.marker_size, 
                                             mfc='None',
                                             mec=cyx[ii], 
                                             mew=self.marker_lw,
                                             ls=self.yx_ls, 
                                             yerr=rp.phaseyx_err, 
                                             ecolor=cyx[ii],
                                             capsize=self.marker_size,
                                             elinewidth=self.marker_lw)
            

                    legendlst.append([ebxyr,ebyxr])             
                    
                    #====Plot the Z_xx, Z_yy components if desired=============
                    if self.plotnum==2:
                        #---------plot the apparent resistivity----------------
                        self.axr2.yaxis.set_label_coords(-.1, 0.5)
                        
                        #res_xx
                        ebxxr = self.axr2.errorbar(mt.period, 
                                                  rp.resxx, 
                                                  marker=mxy[ii], 
                                                  ms=self.marker_size, 
                                                  mfc='None',
                                                  mec=cxy[ii], 
                                                  mew=self.marker_lw,
                                                  ls=self.xy_ls, 
                                                  yerr=rp.resxx_err, 
                                                  ecolor=cxy[ii],
                                                  capsize=self.marker_size,
                                                  elinewidth=self.marker_lw)
                        
                        #res_yy                              
                        ebyyr = self.axr2.errorbar(mt.period, 
                                                  rp.resyy, 
                                                  marker=myx[ii], 
                                                  ms=self.marker_size, 
                                                  mfc='None', 
                                                  mec=cyx[ii], 
                                                  mew=self.marker_lw, 
                                                  ls=self.yx_ls, 
                                                  yerr=rp.resyy_err, 
                                                  ecolor=cyx[ii],
                                                  capsize=self.marker_size,
                                                  elinewidth=self.marker_lw)
            
                                            
                        #-----Plot the phase-----------------------------------
                        
                        self.axp2.yaxis.set_label_coords(-.1, 0.5)
                        
                        #phase_xx
                        ebxxp = self.axp2.errorbar(mt.period, 
                                                  rp.phasexx, 
                                                  marker=mxy[ii], 
                                                  ms=self.marker_size, 
                                                  mfc='None', 
                                                  mec=cxy[ii], 
                                                  mew=self.marker_lw, 
                                                  ls=self.xy_ls, 
                                                  yerr=rp.phasexx_err,
                                                  ecolor=cxy[ii],
                                                  capsize=self.marker_size,
                                                  elinewidth=self.marker_lw)
                                                        
                        #phase_yy
                        ebyyp = self.axp2.errorbar(mt.period,
                                                  rp.phaseyy, 
                                                  marker=myx[ii],
                                                  ms=self.marker_size, 
                                                  mfc='None',
                                                  mec=cyx[ii], 
                                                  mew=self.marker_lw, 
                                                  ls=self.yx_ls, 
                                                  yerr=rp.phaseyy_err, 
                                                  ecolor=cyx[ii],
                                                  capsize=self.marker_size,
                                                  elinewidth=self.marker_lw)
                        

                                   
                
                #===Plot the Determinant if desired============================                          
                if self.plotnum==3:
                        
                    #res_det
                    ebdetr = self.axr.errorbar(mt.period, 
                                              rp.resdet, 
                                              marker=mxy[ii], 
                                              ms=self.marker_size, 
                                              mfc='None',
                                              mec=cdet[ii], 
                                              mew=self.marker_lw, 
                                              ls=self.det_ls, 
                                              yerr=rp.resdet_err, 
                                              ecolor=cdet[ii],
                                              capsize=self.marker_size,
                                              elinewidth=self.marker_lw)
                
                    #phase_det
                    ebdetp = self.axp.errorbar(mt.period, 
                                              rp.phasedet, 
                                              marker=mxy[ii], 
                                              ms=self.marker_size, 
                                              mfc='None', 
                                              mec=cdet[ii], 
                                              mew=self.marker_lw, 
                                              ls=self.det_ls, 
                                              yerr=rp.phasedet_err, 
                                              ecolor=cdet[ii],
                                              capsize=self.marker_size,
                                              elinewidth=self.marker_lw)
                    
                    legendlst.append(ebdetr)
                    
                #-----plot tipper----------------------------------------------              
                if self.plot_tipper.find('y')==0:
                    
                    tp = mt.get_Tipper()
                    
                    txr = tp.mag_real*np.cos(tp.ang_real*np.pi/180+\
                                             np.pi*self.arrow_direction)
                    tyr = tp.mag_real*np.sin(tp.ang_real*np.pi/180+\
                                             np.pi*self.arrow_direction)
            
                    txi = tp.mag_imag*np.cos(tp.ang_imag*np.pi/180+\
                                             np.pi*self.arrow_direction)
                    tyi = tp.mag_imag*np.sin(tp.ang_imag*np.pi/180+\
                                             np.pi*self.arrow_direction)
                    
                    nt = len(txr)
                    
                    for aa in range(nt):
                        xlenr = txr[aa]*mt.period[aa]
                        xleni = txi[aa]*mt.period[aa]
                        
                        #scale the arrow head height and width to fit in a log scale
                        if np.log10(mt.period[aa])<0:
                            hwidth = self.arrow_head_width*\
                                      10**(np.floor(np.log10(mt.period[aa])))
                            hheight = self.arrow_head_height*\
                                      10**(np.floor(np.log10(mt.period[aa])))
                        else:
                            hwidth = self.arrow_head_width/\
                                      10**(np.floor(np.log10(mt.period[aa])))
                            hheight = self.arrow_head_height/\
                                      10**(np.floor(np.log10(mt.period[aa]))) 
                            
                        #--> plot real arrows
                        if self.plot_tipper.find('r')>0:
                            self.axt.arrow(mt.period[aa],
                                           0,
                                           xlenr,
                                           tyr[aa],
                                           lw=self.arrow_lw,
                                           facecolor=ctipr[ii],
                                           edgecolor=ctipr[ii],
                                           head_width=hwidth,
                                           head_length=hheight,
                                           length_includes_head=False)
                            
                                           
                        #--> plot imaginary arrows
                        if self.plot_tipper.find('i')>0:               
                            self.axt.arrow(self.period[aa],
                                           0,
                                           xleni,
                                           tyi[aa],
                                           lw=alw,
                                           facecolor=ctipi[ii],
                                           edgecolor=ctipi[ii],
                                           length_includes_head=False)
                        
                    lt = self.axt.plot(0,0,lw=1, color=ctipr[ii])
                    tiplst.append(lt[0])
                        
                    
            
                #---plot strike------------------------------------------------
                if self.plot_strike=='y' or self.plot_strike==2:
                    
                    #strike from phase tensor
                    pt = mt.get_PhaseTensor()
                    s2, s2_err = pt.azimuth
                    
                    #fold angles to go from -90 to 90
                    s2[np.where(s2>90)] = s2[np.where(s2>90)]-180
                    s2[np.where(s2<-90)] = s2[np.where(s2<-90)]+180
                    
                    #plot strike with error bars
                    ps2 = self.axs.errorbar(mt.period, 
                                            s2, 
                                            marker=mxy[ii], 
                                            ms=self.marker_size, 
                                            mfc=cst[ii], 
                                            mec=cst[ii], 
                                            mew=self.marker_lw,
                                            ls='none', 
                                            yerr=s2_err, 
                                            ecolor=cst[ii],
                                            capsize=self.marker_size,
                                            elinewidth=self.marker_lw)
                                            
                    stlst.append(ps2[0])
                                        
                #------plot skew angle-----------------------------------------
                if self.plot_skew=='y':
                    #strike from phase tensor
                    pt = mt.get_PhaseTensor()
                    sk, sk_err = pt.beta
                    
                    ps4 = self.axs2.errorbar(mt.period, 
                                            sk, 
                                            marker=myx[ii], 
                                            ms=self.marker_size, 
                                            mfc=csk[ii], 
                                            mec=csk[ii], 
                                            mew=self.marker_lw,
                                            ls='none', 
                                            yerr=sk_err, 
                                            ecolor=csk[ii],
                                            capsize=self.marker_size,
                                            elinewidth=self.marker_lw)
    
                    if self.skew_limits is None:
                        self.skew_limits = (-9,9)
                    sklst.append(ps4[0])
                                    
            #-------set axis properties----------------------------------------
            self.axr.set_yscale('log')
            self.axr.set_xscale('log')
            self.axr.set_ylim(self.res_limits)
            self.axr.set_xlim(self.xlimits)
            self.axr.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                          lw=.25)
            plt.setp(self.axr.get_xticklabels(), visible=False)
            
            self.axr.set_ylabel('App. Resistivity ($\Omega \cdot$m)',
                                fontdict=fontdict)
                          
            #check the phase to see if any point are outside of [0:90]
            if self.phase_limits==None:
                self.phase_limits = (0, 89.99)
            
            #--> set axes properties
            self.axp.set_xlabel('Period (s)', fontdict=fontdict)
            self.axp.set_ylabel('Phase (deg)',fontdict=fontdict)
            self.axp.set_xscale('log')
            self.axp.set_ylim(self.phase_limits)        
            self.axp.yaxis.set_major_locator(MultipleLocator(15))
            self.axp.yaxis.set_minor_locator(MultipleLocator(5))
            self.axp.grid(True, alpha=.25, 
                          which='both', 
                          color=(.25,.25,.25),
                          lw=.25)
            
            #make legend
            if self.plotnum==1:
                llst=[ll[0] for ll in legendlst]+[ll[1] for ll in legendlst]
                slst=[ss+'_xy' for ss in stationlst]+\
                     [ss+'_yx' for ss in stationlst]
                     
                self.axr.legend(llst, 
                                slst,
                                loc=3,
                                ncol=2,
                                markerscale=1, 
                                borderaxespad=.01,
                                labelspacing=.07, 
                                handletextpad=.2, 
                                borderpad=.02)
            elif self.plotnum==3:
                llst=[ll[0] for ll in legendlst]
                slst=[ss+'_det' for ss in stationlst]
                     
                self.axr.legend(llst, 
                                slst,
                                loc=3,
                                markerscale=1, 
                                borderaxespad=.01,
                                labelspacing=.07, 
                                handletextpad=.2, 
                                borderpad=.02)

            
            if self.plotnum==2:
                llst=[ll[0] for ll in legendlst]+[ll[1] for ll in legendlst]
                slst=[ss+'_xx' for ss in stationlst]+\
                     [ss+'_yy' for ss in stationlst]
                     
                self.axr2.legend(llst, 
                                 slst,
                                 loc=3,
                                 ncol=2,
                                 markerscale=1, 
                                 borderaxespad=.01,
                                 labelspacing=.07, 
                                 handletextpad=.2, 
                                 borderpad=.02)
                
                self.axr2.set_yscale('log')
                self.axr2.set_xscale('log')
                self.axr2.set_xlim(self.xlimits)
                self.axr2.grid(True, 
                               alpha=.25, 
                               which='both', 
                               color=(.25,.25,.25),
                              lw=.25)
                plt.setp(self.axr2.get_xticklabels(), visible=False)
                                
                #--> set axes properties Phaseyx
                self.axp2.set_xlabel('Period (s)', fontdict)
                self.axp2.set_xscale('log')
                self.axp2.set_ylim(ymin=-179.9, ymax=179.9)        
                self.axp2.yaxis.set_major_locator(MultipleLocator(30))
                self.axp2.yaxis.set_minor_locator(MultipleLocator(5))
                self.axp2.grid(True, 
                               alpha=.25, 
                               which='both', 
                               color=(.25,.25,.25),
                              lw=.25) 
                          
            if self.plot_tipper.find('y')==0:
                self.axt.plot(self.axr.get_xlim(),[0,0],color='k',lw=.5)
                #--> set axis properties Tipper 
                plt.setp(self.axp.get_xticklabels(), visible=False)
                self.axp.set_xlabel('')
                if self.plotnum==2:
                    plt.setp(self.axp2.get_xticklabels(), visible=False)
                    self.axp2.set_xlabel('')
                    
                self.axt.yaxis.set_major_locator(MultipleLocator(.2))               
                self.axt.yaxis.set_minor_locator(MultipleLocator(.1))               
                self.axt.set_xlabel('Period (s)', fontdict=fontdict)
                self.axt.set_ylabel('Tipper', fontdict=fontdict)    
                
                self.axt.set_xscale('log')
                if self.tipper_limits is None:
                    tmax = max([np.sqrt(txr.max()**2+tyr.max()**2),
                                np.sqrt(txi.max()**2+tyi.max()**2)])
                    if tmax>1:
                        tmax=.899
                                
                    tmin = -min([np.sqrt(txr.min()**2+tyr.min()**2),
                                np.sqrt(txi.min()**2+tyi.min()**2)])
                    if tmin<-1:
                        tmin=-.899
                                
                    self.tipper_limits = (tmin-.1, tmax+.1)
                
                self.axt.set_ylim(self.tipper_limits)
                self.axt.grid(True, alpha=.25, 
                              which='both', 
                              color=(.25,.25,.25),
                              lw=.25)
                              
                self.axt.legend(tiplst, 
                                stationlst,
                                loc=3,
                                ncol=2,
                                markerscale=1, 
                                borderaxespad=.01,
                                labelspacing=.07, 
                                handletextpad=.2, 
                                borderpad=.02)
                              
            #--> set axes properties for strike and skew
            if self.plot_strike=='y':
                plt.setp(self.axt.get_xticklabels(), visible=False)
                self.axt.set_xlabel('')
                                        
                if self.strike_limits is None:
                    self.strike_limits = (-89.99, 89.99)
                self.axs.plot(self.axr.get_xlim(),[0,0],color='k',lw=.5)
                
                self.axs.set_ylabel('Strike',
                                    fontdict=fontdict)
                self.axs.set_xlabel('Period (s)',
                                    fontdict=fontdict)
                self.axs.set_ylim(self.strike_limits)
                self.axs.yaxis.set_major_locator(MultipleLocator(30))
                self.axs.yaxis.set_minor_locator(MultipleLocator(5))
                self.axs.set_xscale('log')
                self.axs.grid(True, alpha=.25, 
                              which='both', 
                              color=(.25,.25,.25),
                              lw=.25)
                self.axs.legend(stlst, 
                                stationlst,
                                loc=3,
                                ncol=2,
                                markerscale=1, 
                                borderaxespad=.01,
                                labelspacing=.07, 
                                handletextpad=.2, 
                                borderpad=.02)
           
           #--> set axes properties for skew
            if self.plot_skew=='y':
                self.axs2.set_ylim(self.skew_limits)
                self.axs2.yaxis.set_major_locator(MultipleLocator(3))
                self.axs2.yaxis.set_minor_locator(MultipleLocator(1))
                self.axs2.set_ylabel('Skew', color=self.skew_color)
                self.axs2.set_xscale('log')
                for tl in self.axs2.get_yticklabels():
                    tl.set_color(self.skew_color)
                    
                self.axs2.legend(sklst, 
                                 stationlst,
                                 loc=4,
                                 ncol=2,
                                 markerscale=1, 
                                 borderaxespad=.01,
                                 labelspacing=.07, 
                                 handletextpad=.2, 
                                 borderpad=.02)
                    
            plt.show()

    def update_plot(self):
        """
        update any parameters that where changed using the built-in draw from
        canvas.  
        
        Use this if you change an of the .fig or axes properties
        
        :Example: ::
            
            >>> # to change the grid lines to only be on the major ticks
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> [ax.grid(True, which='major') for ax in [p1.axr,p1.axp]]
            >>> p1.update_plot()
        
        """

        self.fig.canvas.draw()
        
    def redraw_plot(self):
        """
        use this function if you updated some attributes and want to re-plot.
        
        :Example: ::
            
            >>> # change the color and marker of the xy components
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> p1.xy_color = (.5,.5,.9)
            >>> p1.xy_marker = '*'
            >>> p1.redraw_plot()
        """
        
        plt.close(self.fig)
        self.plot()
        
    def __str__(self):
        """
        rewrite the string builtin to give a useful message
        """
        
        return "Plots resistivity and phase for the different modes of the MT \n" +\
              "response for multiple sites. At the moment it supports the \n"+\
              "input of an .edi file. Other formats that will be supported\n"+\
              "are the impedance tensor and errors with an array of periods\n"+\
              "and .j format.\n"        

    
class PlotPhaseTensor(MTEllipse):
    """
    Will plot phase tensor, strike angle, min and max phase angle, 
    azimuth, skew, and ellipticity as subplots on one plot.  It can plot
    the resistivity tensor along side the phase tensor for comparison.
    
    Arguments:
    ----------
    
        **filename** : string
                       filename containing impedance (.edi) is the only 
                       format supported at the moment
                 
        **z_object** : class mtpy.core.z.Z
                      object of mtpy.core.z.  If this is input be sure the
                      attribute z.frequency is filled.  *default* is None
                      
        **mt_object** : class mtpy.imaging.mtplot.MTplot
                        object of mtpy.imaging.mtplot.MTplot
                        *default* is None
                        
        **pt_object** : class mtpy.analysis.pt
                        phase tensor object of mtpy.analysis.pt.  If this is
                        input then the ._mt attribute is set to None cause
                        at the moment cannot tranform the phase tensor to z
                        *default* is None
                        
        **fignum** : int (figure number)
        
        **rot_z** : float (angle in degrees)
                     rotation angle clockwise positive assuming 0 is North.
                     *Default* is 0
                     
        **plot_yn** : [ 'y' | 'n' ]
            
        
        **dpi** : int
                  Dots-per-inch resolution of figure.
                  *Default* is 300
                  
        **ellipse_dict** : dictionary
                          dictionary of parameters for the phase tensor 
                          ellipses with keys:
                          * 'size' -> size of ellipse in points 
                                     *default* is .25
                          
                          * 'colorby' : [ 'phimin' | 'phimax' | 'beta' | 
                                    'skew_seg' | 'phidet' | 'ellipticity' ]
                                    
                                    - 'phimin' -> colors by minimum phase
                                    - 'phimax' -> colors by maximum phase
                                    - 'skew' -> colors by skew
                                    - 'skew_seg' -> colors by skew in 
                                                   discrete segments 
                                                   defined by the range
                                    - 'phidet' -> colors by determinant of
                                                 the phase tensor
                                    - 'ellipticity' -> colors by ellipticity
                                    *default* is 'phimin'
                            
                          * 'range' : tuple (min, max, step)
                                     Need to input at least the min and max
                                     and if using 'skew_seg' to plot
                                     discrete values input step as well
                                     *default* depends on 'colorby'
                                     
                          * 'cmap' : [ 'mt_yl2rd' | 'mt_bl2yl2rd' | 
                                      'mt_wh2bl' | 'mt_rd2bl' | 
                                      'mt_bl2wh2rd' | 'mt_seg_bl2wh2rd' |
                                      'mt_rd2gr2bl' ]
                                      
                                   - 'mt_yl2rd' -> yellow to red
                                   - 'mt_bl2yl2rd' -> blue to yellow to red
                                   - 'mt_wh2bl' -> white to blue
                                   - 'mt_rd2bl' -> red to blue
                                   - 'mt_bl2wh2rd' -> blue to white to red
                                   - 'mt_bl2gr2rd' -> blue to green to red
                                   - 'mt_rd2gr2bl' -> red to green to blue
                                   - 'mt_seg_bl2wh2rd' -> discrete blue to 
                                                         white to red
        

                        
    :Example: ::
        
        #To plot just the phase tensor components
        >>> import mtpy.imaging.mtplot as mtplot
        >>> pt1 = mtplot.PlotPhaseTensor(r"/home/MT/edifiles/MT01.edi")
        
    Attributes:
    -----------
        -ax1      matplotlib.axes object for the phase tensor ellipses
        -cbpt     matplotlib.colors.ColorBarBase object for coloring ellipses
        -ax2      matplotlib.axes object for the strike angle
        -ax3      matplotlib.axes object for minimum and maximum phase
        -ax4      matplotlib.axes object for skew angle
        -ax5      matplotlib.axes object for ellipticity
        
        -font_size  size of font for the axes labels, titles will be +2
        -fignum     number of the figure instance
        -fig_size   size of figure in inches
        -plot_yn    boolean to tell the class to plot on instance creation
        -dpi        dots-per-inch resolution of figure
        
        -strike_inv_marker   marker for strike determined from invariants 
                             in ax2
        -strike_inv_color    color for invariant marker in ax2
        -strike_pt_marker    marker for strike determined from pt in ax2
        -strike_pt_color     color for pt strike in ax2
        -strike_tp_marker    marker for strike determined from Tipper in ax2
        -strike_tp_color     color for tipper strike in ax2
        
        -ptmin_marker  marker for minimum phase in ax3
        -ptmin_color   color for minimum phase markers in ax3
        -ptmax_marker  marker for maximum phase in ax3
        -ptmax_color   color for maximum phase markers in ax3
        
        -skew_marker   marker for skew angle determined from pt in ax4
        -skew_color    color for skew angle in ax4
        
        -ellip_marker  marker for ellipticity determined from pt in ax5
        -ellip_color   color for ellipticity in ax5
        
        -marker_size   size of the marker in all plots
        -marker_lw     width of face lines for markers in all plots
        
        -pt_limits      limits on the minimu phase and maximum phase (deg)
        -strike_limits  limits on the strike angle in degrees, note the strike
                        is calculated to go from -90 to 90.
        -skew_limits    limits on skew angles (deg)
        -ellip_limits   limits on ellipticity ratio from [0,1]
        
        -skew_cutoff    plots a line in ax4 at positive and negative of this 
                        value to visually recognize 3D effects
        -ellip_cutoff   plots a line in ax5 to represent the cutoff of 2D
        
        -ellipse_cmap     color map for coloring ellipses of ax1
        -ellipse_colorby  parameter to color the ellipses by
        -ellipse_range    min and max values for coloring ellipses
        -ellipse_size     scaling factor of ellipses
        -ellipse_spacing  spacing between ellipses
        
        -mt            mtpy.imaging.mtplot.MTplot object (PlotPhaseTensor._mt)
        
        
    """
        
        
    def __init__(self, filename=None, z_object=None, mt_object=None, 
                 pt_object=None, fignum=1, dpi=300, rot_z=0, plot_yn='y',
                 ellipse_dict=None):
        
        #--> get mt object 
        if filename is not None:
            self._mt = MTplot(filename=filename)
        elif z_object is not None:
            self._mt = MTplot(z_object=z_object)
        elif mt_object is not None:
            self._mt = mt_object
        elif pt_object is not None:
            self.pt = pt_object
            self._mt = MTplot()
            self._mt.frequency = self.pt.frequency
            
        self.font_size = 7
        self.dpi = dpi
        self.fignum = fignum
        self.fig_size = [8,8]
        self.rot_z = rot_z
        self.plot_yn=plot_yn
        
        self.ptmin_marker = 'o'
        self.ptmax_marker = 's'
        self.strike_inv_marker = 's'
        self.strike_pt_marker = 'o'
        self.strike_tp_marker = 'v'
        self.skew_marker = 's'
        self.ellip_marker = 's'
        
        self.ptmin_color = 'r'
        self.ptmax_color = 'b'
        self.strike_inv_color = 'c'
        self.strike_pt_color = 'purple'
        self.strike_tp_color= (.5, .5, 0)
        self.skew_color = 'g'
        self.ellip_color = 'orange'

        self.marker_size = 2
        self.marker_lw = .5
        
        self.pt_limits = None
        self.strike_limits = None
        self.ellip_limits = None
        self.skew_limits = None

        self.skew_cutoff = 3
        self.ellip_cutoff = 0.2
        
        #read ellipse dict
        if ellipse_dict is None:
            self._ellipse_dict = {'size':.25}
        else:
            self._ellipse_dict = ellipse_dict
    
        self._read_ellipse_dict()
        
        self.ellipse_spacing = 1

        self.label_dict = {-6:'$10^{-6}$',
                           -5:'$10^{-5}$',
                           -4:'$10^{-4}$',
                           -3:'$10^{-3}$',
                           -2:'$10^{-2}$', 
                           -1:'$10^{-1}$', 
                            0:'$10^{0}$',
                            1:'$10^{1}$',
                            2:'$10^{2}$',
                            3:'$10^{3}$',
                            4:'$10^{4}$',
                            5:'$10^{5}$',
                            6:'$10^{6}$',
                            7:'$10^{7}$',
                            8:'$10^{8}$'} 
                            
        self.cb_position = (.045, .78, .015, .12)
                            
        if self.plot_yn=='y':
            self.plot()

    def plot(self):
        """
        plots the phase tensor elements
        """
        
        #Set plot parameters
        plt.rcParams['font.size']=self.font_size
        plt.rcParams['figure.subplot.left']=.1
        plt.rcParams['figure.subplot.right']=.98
        plt.rcParams['figure.subplot.bottom']=.1
        plt.rcParams['figure.subplot.top']=.95
        plt.rcParams['figure.subplot.wspace']=.21
        plt.rcParams['figure.subplot.hspace']=.5
        
        font_dict = {'size':self.font_size, 'weight':'bold'}
        font_dictt = {'size':self.font_size+2, 'weight':'bold'}
        
        #--> create plot instance
        self.fig = plt.figure(self.fignum, self.fig_size, dpi=self.dpi)
        plt.clf()
        
        #get phase tensor instance
        try:
            self.pt
            self.pt.rotate(self.rot_z)
        except AttributeError:
            self.pt = self._mt.get_PhaseTensor()
            self.pt.rotate(self.rot_z)
            self.zinv = self._mt.get_Zinvariants()
            self.zinv.rotate(self.rot_z)
        
        cmap = self.ellipse_cmap
        ckmin = self.ellipse_range[0]
        ckmax = self.ellipse_range[1]
        try:
            ckstep = float(self.ellipse_range[2])
        except IndexError:
            ckstep = 3
            
        if cmap=='mt_seg_bl2wh2rd':
            bounds = np.arange(ckmin, ckmax+ckstep, ckstep)
            nseg = float((ckmax-ckmin)/(2*ckstep))

        #get the properties to color the ellipses by
        if self.ellipse_colorby=='phiminang' or \
           self.ellipse_colorby=='phimin':
            colorarray = self.pt.phimin[0]
    
                                           
        elif self.ellipse_colorby=='phidet':
             colorarray = np.sqrt(abs(self.pt.det[0]))*(180/np.pi)
             
            
        elif self.ellipse_colorby=='skew' or\
             self.ellipse_colorby=='skew_seg':
            colorarray = self.pt.beta[0]
            
        elif self.ellipse_colorby=='ellipticity':
            colorarray = self.pt.ellipticity[0]
            
        else:
            raise NameError(self.ellipse_colorby+' is not supported')
     
        #-------------plotPhaseTensor-----------------------------------
        self.ax1 = self.fig.add_subplot(3, 1, 1,aspect='equal')
        for ii, ff in enumerate(self._mt.period):
            #make sure the ellipses will be visable
            eheight = self.pt.phimin[0][ii]/self.pt.phimax[0][ii]*\
                                                              self.ellipse_size
            ewidth = self.pt.phimax[0][ii]/self.pt.phimax[0][ii]*\
                                                              self.ellipse_size
        
            #create an ellipse scaled by phimin and phimax and oriented along
            #the azimuth which is calculated as clockwise but needs to 
            #be plotted counter-clockwise hence the negative sign.
            ellipd=patches.Ellipse((np.log10(ff)*self.ellipse_spacing, 0),
                                    width=ewidth,
                                    height=eheight,
                                    angle=90-self.pt.azimuth[0][ii])
                                    
            self.ax1.add_patch(ellipd)
            
        
            #get ellipse color
            if cmap.find('seg')>0:
                ellipd.set_facecolor(mtcl.get_plot_color(colorarray[ii],
                                                         self.ellipse_colorby,
                                                         cmap,
                                                         ckmin,
                                                         ckmax,
                                                         bounds=bounds))
            else:
                ellipd.set_facecolor(mtcl.get_plot_color(colorarray[ii],
                                                         self.ellipse_colorby,
                                                         cmap,
                                                         ckmin,
                                                         ckmax))
            
    
        #----set axes properties-----------------------------------------------
        #--> set tick labels and limits
        xlimits = (np.floor(np.log10(self._mt.period[0])),
                   np.ceil(np.log10(self._mt.period[-1])))
        tklabels=[self.label_dict[np.round(tt)] 
                              for tt in np.arange(xlimits[0],xlimits[-1]+1)]
            

        self.ax1.set_xlim(xlimits)
        self.ax1.set_xticklabels(tklabels, fontdict={'size':self.font_size})
        self.ax1.set_xlabel('Period (s)', fontdict=font_dict)
        self.ax1.set_ylim(ymin=-1.5*self.ellipse_size, 
                          ymax=1.5*self.ellipse_size)
        
        self.ax1.grid(True, 
                     alpha=.25, 
                     which='major', 
                     color=(.25,.25,.25),
                     lw=.25)
        
        plt.setp(self.ax1.get_yticklabels(), visible=False)
        #add colorbar for PT
        self.cbax = self.fig.add_axes(self.cb_position)
        if cmap=='mt_seg_bl2wh2rd':
            #make a color list
            clst = [(cc,cc,1) for cc in np.arange(0,1+1./(nseg),1./(nseg))]+\
                       [(1,cc,cc) for cc in np.arange(1,-1./(nseg),-1./(nseg))]
            
            #make segmented colormap
            mt_seg_bl2wh2rd = colors.ListedColormap(clst)

            #make bounds so that the middle is white
            bounds = np.arange(ckmin-ckstep, ckmax+2*ckstep, ckstep)
            
            #normalize the colors
            norms = colors.BoundaryNorm(bounds, mt_seg_bl2wh2rd.N)
            
            #make the colorbar
            self.cbpt = mcb.ColorbarBase(self.cbax,
                                       cmap=mt_seg_bl2wh2rd,
                                       norm=norms,
                                       orientation='vertical',
                                       ticks=bounds[1:-1])
        else:
            self.cbpt = mcb.ColorbarBase(self.cbax,
                                       cmap=mtcl.cmapdict[cmap],
                                       norm=colors.Normalize(vmin=ckmin,
                                                             vmax=ckmax),
                                        orientation='vertical')
        self.cbpt.set_ticks([ckmin,ckmax])
        self.cbpt.set_ticklabels(['{0:.0f}'.format(ckmin),
                                  '{0:.0f}'.format(ckmax)])
        self.cbpt.ax.yaxis.set_label_position('left')
        self.cbpt.ax.yaxis.set_label_coords(-1.05,.5)
        self.cbpt.ax.yaxis.tick_right()
        self.cbpt.ax.tick_params(axis='y',direction='in')
        self.cbpt.set_label(ckdict[self.ellipse_colorby], 
                            fontdict={'size':self.font_size, 'weight':'bold'})
        
        #---------------plotStrikeAngle-----------------------------------
        self.ax2 = self.fig.add_subplot(3, 2, 3)
        az = self.pt.azimuth[0]
        azerr = self.pt.azimuth[1]
        
        #put the strike into a coordinate system that goes from -90 to 90
        az[np.where(az>90)] = az[np.where(az>90)]-180
        az[np.where(az<-90)] = az[np.where(az<-90)]+180
        
        stlst = []
        stlabel = []
        
        #plot phase tensor strike
        ps2 = self.ax2.errorbar(self._mt.period, 
                                az, 
                                marker=self.strike_pt_marker, 
                                ms=self.marker_size, 
                                mfc=self.strike_pt_color, 
                                mec=self.strike_pt_color, 
                                mew=self.marker_lw,
                                ls='none', 
                                yerr=azerr, 
                                ecolor=self.strike_pt_color,
                                capsize=self.marker_size,
                                elinewidth=self.marker_lw)
                                
        stlst.append(ps2[0])
        stlabel.append('PT')
        try:
            strike = self.zinv.strike
            strikeerr = np.nan_to_num(self.zinv.strike_err)
            #put the strike into a coordinate system that goes from -90 to 90
            strike[np.where(strike>90)] = strike[np.where(strike>90)]-180
            strike[np.where(strike<-90)] = strike[np.where(strike<-90)]+180
            
            #plot invariant strike
            erxy = self.ax2.errorbar(self._mt.period, 
                                    strike, 
                                    marker=self.strike_inv_marker, 
                                    ms=self.marker_size, 
                                    mfc=self.strike_inv_color, 
                                    mec=self.strike_inv_color, 
                                    mew=self.marker_lw,
                                    ls='none', 
                                    yerr=strikeerr, 
                                    ecolor=self.strike_inv_color,
                                    capsize=self.marker_size,
                                    elinewidth=self.marker_lw)
                              
            stlst.append(erxy[0])
            stlabel.append('Z_inv')
        except AttributeError:
            print 'Could not get z_invariants from pt, input z if desired.'
            
        if self._mt.tipper is not None:
            #strike from tipper
            tp = self._mt.get_Tipper()
            s3 = tp.ang_real+90
            
            #fold to go from -90 to 90
            s3[np.where(s3>90)] = s3[np.where(s3>90)]-180
            s3[np.where(s3<-90)] = s3[np.where(s3<-90)]+180
            
            #plot strike with error bars
            ps3 = self.ax2.errorbar(self._mt.period, 
                                    s3, 
                                    marker=self.strike_tp_marker, 
                                    ms=self.marker_size, 
                                    mfc=self.strike_tp_color, 
                                    mec=self.strike_tp_color, 
                                    mew=self.marker_lw,
                                    ls='none', 
                                    yerr=np.zeros_like(s3), 
                                    ecolor=self.strike_tp_color,
                                    capsize=self.marker_size,
                                    elinewidth=self.marker_lw)
                                    
            stlst.append(ps3[0])
            stlabel.append('Tipper')
        
             
        self.ax2.legend(stlst,
                        stlabel,
                        loc='lower left',
                        markerscale=.5*self.marker_size,
                        borderaxespad=.01,
                        labelspacing=.1,
                        handletextpad=.2,
                        ncol=len(stlst),
                        borderpad=.1,
                        columnspacing=.1)
                   
        leg = plt.gca().get_legend()
        ltext  = leg.get_texts()  # all the text.Text instance in the legend
        plt.setp(ltext, fontsize=6)    # the legend text fontsize

        if self.strike_limits==None:
            self.strike_limits = (-89.99, 89.99)
        
        self.ax2.set_yscale('linear')
        self.ax2.set_xscale('log')
        self.ax2.set_xlim(xmax=10**xlimits[-1], xmin=10**xlimits[0])
        self.ax2.set_ylim(self.strike_limits)
        self.ax2.yaxis.set_major_locator(MultipleLocator(20))
        self.ax2.yaxis.set_minor_locator(MultipleLocator(5))
        self.ax2.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                      lw=.25)
        self.ax2.set_ylabel('Angle (deg)',fontdict=font_dict)
        self.ax2.set_title('Strike',fontdict=font_dictt)
        
        #---------plot Min & Max Phase-----------------------------------------
        minphi = self.pt.phimin[0]
        minphierr = self.pt.phimin[1]
        maxphi = self.pt.phimax[0]
        maxphierr = self.pt.phimax[1]

        self.ax3 = self.fig.add_subplot(3, 2, 4,sharex=self.ax2)
        
        ermin = self.ax3.errorbar(self._mt.period,
                                  minphi,
                                  marker=self.ptmin_marker,
                                  ms=self.marker_size,
                                  mfc='None',
                                  mec=self.ptmin_color,
                                  mew=self.marker_lw,
                                  ls='None',
                                  yerr=minphierr,
                                  ecolor=self.ptmin_color,
                                  capsize=self.marker_size,
                                  elinewidth=self.marker_lw)
                                
        ermax = self.ax3.errorbar(self._mt.period,
                                  maxphi,
                                  marker=self.ptmax_marker,
                                  ms=self.marker_size,
                                  mfc='None',
                                  mec=self.ptmax_color,
                                  mew=self.marker_lw,
                                  ls='None',
                                  yerr=maxphierr,
                                  ecolor=self.ptmax_color,
                                  capsize=self.marker_size,
                                  elinewidth=self.marker_lw)
                           
                
        if self.pt_limits==None:
            self.pt_limits = [min([self.pt.phimax[0].min(), 
                                   self.pt.phimin[0].min()])-3, 
                              max([self.pt.phimax[0].max(), 
                                   self.pt.phimin[0].max()])+3]
            if self.pt_limits[0]<-10:
                self.pt_limits[0] = -9.9
            if self.pt_limits[1]>100:
                self.pt_limits[1] = 99.99
        
        self.ax3.set_xscale('log')
        self.ax3.set_yscale('linear')
        
        self.ax3.legend((ermin[0],ermax[0]),
                        ('$\phi_{min}$','$\phi_{max}$'),
                        loc='lower left',
                        markerscale=.5*self.marker_size,
                        borderaxespad=.01,
                        labelspacing=.1,
                        handletextpad=.2,
                        ncol=2,
                        borderpad=.01,
                        columnspacing=.01)
        
        leg = plt.gca().get_legend()
        ltext  = leg.get_texts()  # all the text.Text instance in the legend
        plt.setp(ltext, fontsize=6.5)    # the legend text fontsize
        
        self.ax3.set_ylim(self.pt_limits)
        self.ax3.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                      lw=.25)

        self.ax3.set_ylabel('Phase (deg)', fontdict=font_dict)
        self.ax3.set_title('$\mathbf{\phi_{min}}$ and $\mathbf{\phi_{max}}$',
                       fontdict=font_dictt)

        #-----------------------plotSkew---------------------------------------
        
        skew = self.pt.beta[0]
        skewerr = self.pt.beta[1]

        self.ax4 = self.fig.add_subplot(3, 2, 5,sharex=self.ax2)
        erskew = self.ax4.errorbar(self._mt.period,
                                   skew,
                                   marker=self.skew_marker,
                                   ms=self.marker_size,
                                   mfc='None',
                                   mec=self.skew_color,
                                   mew=self.marker_lw,
                                   ls='None',
                                   yerr=skewerr,
                                   ecolor=self.skew_color,
                                   capsize=self.marker_size,
                                   elinewidth=self.marker_lw)
        
        #plot lines indicating not 3d
        self.ax4.plot([10**xlimits[0], 10**xlimits[-1]],
                      [self.skew_cutoff, self.skew_cutoff],
                      ls='--',
                      color=self.skew_color,
                      lw=1)
                      
        self.ax4.plot([10**xlimits[0], 10**xlimits[-1]],
                      [-self.skew_cutoff, -self.skew_cutoff],
                      ls='--',
                      color=self.skew_color,
                      lw=1)

        
        self.ax4.set_xscale('log')
        self.ax4.set_yscale('linear')
        self.ax4.yaxis.set_major_locator(MultipleLocator(ckstep))

        if self.skew_limits is None:
            self.skew_limits=(-10,10)
        self.ax4.set_ylim(self.skew_limits)
        self.ax4.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                      lw=.25)
        self.ax4.set_xlabel('Period (s)',fontdict=font_dict)
        self.ax4.set_ylabel('Skew Angle (deg)',fontdict=font_dict)
        self.ax4.set_title('Skew Angle',fontdict=font_dictt)
        
        #----------------------plotEllipticity--------------------------------
        ellipticity = self.pt.ellipticity[0]
        ellipticityerr=self.pt.ellipticity[1]

        self.ax5 = self.fig.add_subplot(3, 2, 6, sharex=self.ax2)
        erskew = self.ax5.errorbar(self._mt.period,
                                   ellipticity,
                                   marker=self.ellip_marker,
                                   ms=self.marker_size,
                                   mfc='None',
                                   mec=self.ellip_color,
                                   mew=self.marker_lw,
                                   ls='None',
                                   yerr=ellipticityerr,
                                   ecolor=self.ellip_color,
                                   capsize=self.marker_size,
                                   elinewidth=self.marker_lw)
        
        #draw a line where the ellipticity is not 2d                           
        self.ax5.plot([10**xlimits[0], 10**xlimits[-1]],
                      [self.ellip_cutoff, self.ellip_cutoff],
                      ls='--',
                      color=self.ellip_color,
                      lw=1)
                      
        self.ax5.set_xscale('log')
        self.ax5.set_yscale('linear')

        self.ax5.yaxis.set_major_locator(MultipleLocator(.1))

        self.ax5.set_ylim(ymin=0,ymax=1)
        self.ax5.grid(True, alpha=.25, which='both', color=(.25,.25,.25),
                      lw=.25)
        self.ax5.set_xlabel('Period (s)',fontdict=font_dict)
        self.ax5.set_ylabel('$\mathbf{\phi_{max}-\phi_{min}/\phi_{max}+\phi_{min}}$',
                            fontdict=font_dict)
        self.ax5.set_title('Ellipticity',fontdict=font_dictt)
        
        self.fig.suptitle('Phase Tensor Elements for: '+self._mt.station,
                          fontdict={'size':self.font_size+3, 'weight':'bold'})
                          
    
    def save_plot(self, save_fn, file_format='pdf', orientation='portrait', 
                  fig_dpi=None, close_plot='y'):
        """
        save_plot will save the figure to save_fn.
        
        Arguments:
        -----------
        
            **save_fn** : string
                          full path to save figure to, can be input as
                          * directory path -> the directory path to save to
                            in which the file will be saved as 
                            save_fn/station_name_PhaseTensor.file_format
                            
                          * full path -> file will be save to the given 
                            path.  If you use this option then the format
                            will be assumed to be provided by the path
                            
            **file_format** : [ pdf | eps | jpg | png | svg ]
                              file type of saved figure pdf,svg,eps... 
                              
            **orientation** : [ landscape | portrait ]
                              orientation in which the file will be saved
                              *default* is portrait
                              
            **fig_dpi** : int
                          The resolution in dots-per-inch the file will be
                          saved.  If None then the dpi will be that at 
                          which the figure was made.  I don't think that 
                          it can be larger than dpi of the figure.
                          
            **close_plot** : [ y | n ]
                             * 'y' will close the plot after saving.
                             * 'n' will leave plot open
                          
        :Example: ::
            
            >>> # to save plot as jpg
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotPhaseTensor(r'/home/MT/mt01.edi')
            >>> p1.save_plot(r'/home/MT/figures', file_format='jpg')
            
        """

        if fig_dpi==None:
            fig_dpi = self.dpi
            
        if os.path.isdir(save_fn)==False:
            file_format = save_fn[-3:]
            self.fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                             orientation=orientation)
            plt.clf()
            plt.close(self.fig)
            
        else:
            station = self._mt.station
            if station is None:
                station='MT01'
            save_fn = os.path.join(save_fn, station+'_PhaseTensor.'+
                                    file_format)
            self.fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                        orientation=orientation)
        
        if close_plot=='y':
            plt.clf()
            plt.close(self.fig)
        
        else:
            pass
        
        self.fig_fn = save_fn
        print 'Saved figure to: '+self.fig_fn

    def update_plot(self):
        """
        update any parameters that where changed using the built-in draw from
        canvas.  
        
        Use this if you change an of the .fig or axes properties
        
        :Example: ::
            
            >>> # to change the grid lines to only be on the major ticks
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> [ax.grid(True, which='major') for ax in [p1.axr,p1.axp]]
            >>> p1.update_plot()
        
        """

        self.fig.canvas.draw()
        
    def redraw_plot(self):
        """
        use this function if you updated some attributes and want to re-plot.
        
        :Example: ::
            
            >>> # change the color and marker of the xy components
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> p1.xy_color = (.5,.5,.9)
            >>> p1.xy_marker = '*'
            >>> p1.redraw_plot()
        """
        
        plt.close(self.fig)
        self.plot()
        
    def __str__(self):
        """
        rewrite the string builtin to give a useful message
        """
        
        return "Plots the phase tensor ellipses and other properties such\n"+\
               "strike angle, minimum and maximum phase, skew and ellipticity"


class PlotPhaseTensorPseudoSection(MTEllipse, MTArrows):
    """
    PlotPhaseTensorPseudoSection will plot the phase tensor ellipses in a 
    pseudo section format 
    
    
    Arguments:
    ----------
    
        **filenamelst** : list of strings
                          full paths to .edi files to plot
        
        **ellipse_dict** : dictionary
                          dictionary of parameters for the phase tensor 
                          ellipses with keys:
                              *'size' -> size of ellipse in points 
                                         *default* is 2
                              
                              *'colorby' : [ 'phimin' | 'phimax' | 'beta' | 
                                        'beta_seg' | 'phidet' | 'ellipticity' ]
                                        
                                        -'phimin' -> colors by minimum phase
                                        -'phimax' -> colors by maximum phase
                                        -'beta' -> colors by beta (skew)
                                        -'beta_seg' -> colors by beta in 
                                                       discrete segments 
                                                       defined by the range
                                        -'phidet' -> colors by determinant of
                                                     the phase tensor
                                        -'ellipticity' -> colors by ellipticity
                                        *default* is 'phimin'
                                
                              *'range' : tuple (min, max, step)
                                         Need to input at least the min and max
                                         and if using 'beta_seg' to plot
                                         discrete values input step as well
                                         *default* depends on 'colorby'
                                         
                              *'cmap' : [ 'mt_yl2rd' | 'mt_bl2yl2rd' | 
                                          'mt_wh2bl' | 'mt_rd2bl' | 
                                          'mt_bl2wh2rd' | 'mt_seg_bl2wh2rd' ]
                                          
                                       -'mt_yl2rd' -> yellow to red
                                       -'mt_bl2yl2rd' -> blue to yellow to red
                                       -'mt_wh2bl' -> white to blue
                                       -'mt_rd2bl' -> red to blue
                                       -'mt_bl2wh2rd' -> blue to white to red
                                       -'mt_bl2gr2rd' -> blue to green to red
                                       -'mt_seg_bl2wh2rd' -> discrete blue to 
                                                             white to red
                                         
        
        **stretch** : float or tuple (xstretch, ystretch)
                            is a factor that scales the distance from one 
                            station to the next to make the plot readable.
                            *Default* is 200
        **linedir** : [ 'ns' | 'ew' ]
                      predominant direction of profile line
                      *'ns' -> North-South Line
                      *'ew' -> East-West line
                      **Default* is 'ns'
        
        **stationid** : tuple or list 
                        start and stop of station name indicies.  
                        ex: for MT01dr stationid=(0,4) will be MT01
        
        **rotz** : float
                   angle in degrees to rotate the data clockwise positive.
                   *Default* is 0
        
        **title** : string
                    figure title
                    
        **dpi** : int 
                  dots per inch of the resolution. *default* is 300
                    
                       
        **fignum** : int
                     figure number.  *Default* is 1
        
        **plot_tipper** : [ 'yri' | 'yr' | 'yi' | 'n' ]
                        *'yri' to plot induction both real and imaginary 
                           induction arrows 
                           
                        *'yr' to plot just the real induction arrows
                        
                        *'yi' to plot the imaginary induction arrows
                        
                        *'n' to not plot them
                        
                        * *Default* is 'n' 
                        
                        **Note: convention is to point towards a conductor but
                        can be changed in arrow_dict['direction']**
                         
        **arrow_dict** : dictionary for arrow properties
                        *'size' : float
                                  multiplier to scale the arrow. *default* is 5
                        *'head_length' : float
                                         length of the arrow head *default* is 
                                         1.5
                        *'head_width' : float
                                        width of the arrow head *default* is 
                                        1.5
                        *'lw' : float
                                line width of the arrow *default* is .5
                                
                        *'color' : tuple (real, imaginary)
                                   color of the arrows for real and imaginary
                                   
                        *'threshold': float
                                      threshold of which any arrow larger than
                                      this number will not be plotted, helps 
                                      clean up if the data is not good. 
                                      *default* is 1, note this is before 
                                      scaling by 'size'
                                      
                        *'direction : [ 0 | 1 ]
                                     -0 for arrows to point toward a conductor
                                     -1 for arrow to point away from conductor
    
        **tscale** : [ 'period' | 'frequency' ]
        
                     *'period'    -> plot vertical scale in period
                     
                     *'frequency' -> plot vertical scale in frequency
                     
        **cb_dict** : dictionary to control the color bar
        
                      *'orientation' : [ 'vertical' | 'horizontal' ]
                                       orientation of the color bar 
                                       *default* is vertical
                                       
                      *'position' : tuple (x,y,dx,dy)
                                    -x -> lateral position of left hand corner 
                                          of the color bar in figure between 
                                          [0,1], 0 is left side
                                          
                                    -y -> vertical position of the bottom of 
                                          the color bar in figure between 
                                          [0,1], 0 is bottom side.
                                          
                                    -dx -> width of the color bar [0,1]
                                    
                                    -dy -> height of the color bar [0,1]
        **font_size** : float
                        size of the font that labels the plot, 2 will be added
                        to this number for the axis labels.
                        
        **plot_yn** : [ 'y' | 'n' ]
                      *'y' to plot on creating an instance
                      
                      *'n' to not plot on creating an instance
                      
        **xlim** : tuple(xmin, xmax)
                   min and max along the x-axis in relative distance of degrees
                   and multiplied by xstretch
                   
        **ylim** : tuple(ymin, ymax)
                   min and max period to plot, note that the scaling will be
                   done in the code.  So if you want to plot from (.1s, 100s)
                   input ylim=(.1,100)
    
    To get a list of .edi files that you want to plot -->
    :Example: ::
        >>> import mtpy.imaging.mtplottools as mtplot
        >>> import os
        >>> edipath = r"/home/EDIfiles"
        >>> edilst = [os.path.join(edipath,edi) for edi in os.listdir(edipath)
        >>> ...       if edi.find('.edi')>0]
    
    *If you want to plot minimum phase colored from blue to red in a range of
     20 to 70 degrees you can do it one of two ways--> 
    
    1)          
    :Example: ::
        >>> edict = {'range':(20,70), 'cmap':'mt_bl2gr2rd','colorby':'phimin'}
        >>> pt1 = mtplot.PlotPhaseTensorPseudoSection(edilst,ellipse_dict=edict)
     
    2)
    :Example: ::
        >>> pt1 = mtplot.PlotPhaseTensorPseudoSection(edilst, plot_yn='n')
        >>> pt1.ellipse_colorby = 'phimin'
        >>> pt1.ellipse_cmap = 'mt_bl2gr2rd'
        >>> pt1.ellipse_range = (20,70)
        >>> pt1.plot()
        
    *If you want to add real induction arrows that are scaled by 10 and point
     away from a conductor --> 
    :Example: ::
        >>> pt1.plot_tipper = 'yr'
        >>> pt1.arrow_size = 10
        >>> pt1.arrow_direction = -1
        >>> pt1.redraw_plot()
    
    *If you want to save the plot as a pdf with a generic name -->
    :Example: ::
        >>> pt1.save_figure(r"/home/PTFigures", file_format='pdf', dpi=300)
        File saved to '/home/PTFigures/PTPseudoSection.pdf'

    """
    
    
    def __init__(self, fn_lst=None, res_object_lst=None,
                 z_object_lst=None, tipper_object_lst=None, mt_object_lst=None,
                 ellipse_dict={}, stretch=(50,25), stationid=(0,4), title=None,
                 cb_dict={}, linedir='ns', fignum=1, rot_z=0, figsize=[6,6], 
                 dpi=300, plot_tipper='n', arrow_dict={}, tscale='period', 
                 font_size=7, plot_yn='y', xlim=None, ylim=None):

        #----set attributes for the class-------------------------
        self.mt_lst = get_mtlst(fn_lst=fn_lst, 
                                res_object_lst=res_object_lst,
                                z_object_lst=z_object_lst, 
                                tipper_object_lst=tipper_object_lst, 
                                mt_object_lst=mt_object_lst)
        
        #--> set the ellipse properties
        self._ellipse_dict = ellipse_dict
        self._read_ellipse_dict()
            
        #--> set colorbar properties
        #set orientation to horizontal
        try:
            self.cb_orientation = cb_dict['orientation']
        except KeyError:
            self.cb_orientation = 'vertical'
        
        #set the position to middle outside the plot            
        try:
            self.cb_position = cb_dict['position']
        except KeyError:
            self.cb_position = None
            
        #set the stretching in each direction
        if type(stretch)==float or type(stretch)==int:
            self.xstretch = stretch
            self.ystretch = stretch
        else:
            self.xstretch = stretch[0]
            self.ystretch = stretch[1]
            
        #--> set plot properties    
        self.dpi = dpi
        self.font_size = font_size
        self.tscale = tscale
        self.figsize = figsize
        self.fignum = fignum
        self.linedir = linedir
        self.stationid = stationid
        self.title = title
        self.ystep = 4
        self.xlimits = xlim
        self.ylimits = ylim
        
        #if rotation angle is an int or float make an array the length of 
        #mt_lst for plotting purposes
        if type(rot_z) is float or type(rot_z) is int:
            self.rot_z = np.array([rot_z]*len(self.mt_lst))
        
        #if the rotation angle is an array for rotation of different 
        #frequency than repeat that rotation array to the len(mt_lst)
        elif type(rot_z) is np.ndarray:
            if rot_z.shape[0]!=len(self.mt_lst):
                self.rot_z = np.repeat(rot_z, len(self.mt_lst))
                
        else:
            self.rot_z = rot_z
        
        #--> set induction arrow properties 
        self.plot_tipper = plot_tipper
        
        #--> set arrow properties
        self._arrow_dict = arrow_dict
        self._read_arrow_dict()
        
            
        #--> plot if desired
        self.plot_yn = plot_yn
        if self.plot_yn=='y':
            self.plot()
        
    def plot(self):
        """
        plots the phase tensor pseudo section
        """
            
        plt.rcParams['font.size']=self.font_size
        plt.rcParams['figure.subplot.left']=.08
        plt.rcParams['figure.subplot.right']=.98
        plt.rcParams['figure.subplot.bottom']=.06
        plt.rcParams['figure.subplot.top']=.96
        plt.rcParams['figure.subplot.wspace']=.55
        plt.rcParams['figure.subplot.hspace']=.70
        
        #create a plot instance
        self.fig = plt.figure(self.fignum, self.figsize, dpi=self.dpi)
        self.ax = self.fig.add_subplot(1,1,1,aspect='equal')
        
        #create empty lists to put things into
        self.stationlst = []
        self.offsetlst = []
        minlst = []
        maxlst = []
        plot_periodlst = None
        
        #set local parameters with shorter names
        es = self.ellipse_size
        ck = self.ellipse_colorby
        cmap = self.ellipse_cmap
        ckmin = float(self.ellipse_range[0])
        ckmax = float(self.ellipse_range[1])
        try:
            ckstep = float(self.ellipse_range[2])
        except IndexError:
            ckstep=3
                
        nseg = float((ckmax-ckmin)/(2*ckstep))

        if cmap=='mt_seg_bl2wh2rd':
            bounds = np.arange(ckmin, ckmax+ckstep, ckstep)
        #plot phase tensor ellipses
        for ii,mt in enumerate(self.mt_lst):
            self.stationlst.append(mt.station[self.stationid[0]:self.stationid[1]])
            
            #set the an arbitrary origin to compare distance to all other 
            #stations.
            if ii==0:
                east0 = mt.lon
                north0 = mt.lat
                offset = 0.0
            else:
                east = mt.lon
                north = mt.lat
                if self.linedir=='ew': 
                    if east0<east:
                        offset = np.sqrt((east0-east)**2+(north0-north)**2)
                    elif east0>east:
                        offset = -1*np.sqrt((east0-east)**2+(north0-north)**2)
                    else:
                        offset = 0
                elif self.linedir=='ns':
                    if north0<north:
                        offset = np.sqrt((east0-east)**2+(north0-north)**2)
                    elif north0>north:
                        offset = -1*np.sqrt((east0-east)**2+(north0-north)**2)
                    else:
                        offset=0
                        
            self.offsetlst.append(offset)
            
            #get phase tensor elements and flip so the top is small periods/high 
            #frequency
            pt = mt.get_PhaseTensor()
            pt.rotate(self.rot_z[ii])
            
            periodlst = mt.period[::-1]
            phimax = pt.phimax[0][::-1]
            phimin = pt.phimin[0][::-1]
            azimuth = pt.azimuth[0][::-1]
        
            #if there are induction arrows, flip them as pt
            if self.plot_tipper.find('y')==0:
                tip = mt.get_Tipper()
                tip.rotate(self.rot_z[ii])
                if tip.mag_real is not None:
                    tmr = tip.mag_real[::-1]
                    tmi = tip.mag_imag[::-1]
                    tar = tip.ang_real[::-1]
                    tai = tip.ang_imag[::-1]
                else:
                    tmr = np.zeros(len(mt.period))
                    tmi = np.zeros(len(mt.period))
                    tar = np.zeros(len(mt.period))
                    tai = np.zeros(len(mt.period))
                    
                aheight = self.arrow_head_length 
                awidth = self.arrow_head_width
                alw = self.arrow_lw
                
            #get the properties to color the ellipses by
            if self.ellipse_colorby=='phimin':
                colorarray = pt.phimin[0][::-1]
                
            elif self.ellipse_colorby=='phimax':
                colorarray = pt.phimin[0][::-1]
                
            elif self.ellipse_colorby=='phidet':
                 colorarray = np.sqrt(abs(pt.det[::-1]))*(180/np.pi)
                
            elif self.ellipse_colorby=='skew' or\
                 self.ellipse_colorby=='skew_seg':
                colorarray = pt.beta[0][::-1]
                
            elif self.ellipse_colorby=='ellipticity':
                colorarray = pt.ellipticity[::-1]
                
            else:
                raise NameError(self.ellipse_colorby+' is not supported')
            
            #get the number of periods
            n = len(periodlst)
            
            if ii==0:
                plot_periodlst = periodlst
            
            else:
                if n>len(plot_periodlst):
                    plot_periodlst = periodlst
            
            #get min and max of the color array for scaling later
            minlst.append(min(colorarray))
            maxlst.append(max(colorarray))

            for jj,ff in enumerate(periodlst):
                
                #make sure the ellipses will be visable
                eheight = phimin[jj]/phimax[jj]*es
                ewidth = phimax[jj]/phimax[jj]*es
            
                #create an ellipse scaled by phimin and phimax and orient
                #the ellipse so that north is up and east is right
                #need to add 90 to do so instead of subtracting
                ellipd=patches.Ellipse((offset*self.xstretch,
                                        np.log10(ff)*self.ystretch),
                                        width=ewidth,
                                        height=eheight,
                                        angle=azimuth[jj]+90)
                
                #get ellipse color
                if cmap.find('seg')>0:
                    ellipd.set_facecolor(mtcl.get_plot_color(colorarray[jj],
                                                             self.ellipse_colorby,
                                                             cmap,
                                                             ckmin,
                                                             ckmax,
                                                             bounds=bounds))
                else:
                    ellipd.set_facecolor(mtcl.get_plot_color(colorarray[jj],
                                                             self.ellipse_colorby,
                                                             cmap,
                                                             ckmin,
                                                             ckmax))
                    
                #===add the ellipse to the plot==========
                self.ax.add_artist(ellipd)
                
                
                #--------- Add induction arrows if desired --------------------
                if self.plot_tipper.find('y')==0:
                    
                    #--> plot real tipper
                    if self.plot_tipper=='yri' or self.plot_tipper=='yr':
                        txr = tmr[jj]*np.cos(tar[jj]*np.pi/180+\
                                             np.pi*self.arrow_direction)*\
                                             self.arrow_size
                        tyr = tmr[jj]*np.sin(tar[jj]*np.pi/180+\
                                             np.pi*self.arrow_direction)*\
                                             self.arrow_size
                        
                        maxlength = np.sqrt((txr/self.arrow_size)**2+\
                                            (tyr/self.arrow_size)**2)
                                            
                        if maxlength>self.arrow_threshold:
                            pass
                        else:
                            self.ax.arrow(offset*self.xstretch, 
                                          np.log10(ff)*self.ystretch, 
                                          txr,
                                          tyr,
                                          lw=alw,
                                          facecolor=self.arrow_color_real,
                                          edgecolor=self.arrow_color_real,
                                          length_includes_head=False,
                                          head_width=awidth,
                                          head_length=aheight)
                                      
                    #--> plot imaginary tipper
                    if self.plot_tipper=='yri' or self.plot_tipper=='yi':
                        txi = tmi[jj]*np.cos(tai[jj]*np.pi/180+\
                                             np.pi*self.arrow_direction)*\
                                             self.arrow_size
                        tyi = tmi[jj]*np.sin(tai[jj]*np.pi/180+\
                                             np.pi*self.arrow_direction)*\
                                             self.arrow_size
                        
                        maxlength = np.sqrt((txi/self.arrow_size)**2+\
                                            (tyi/self.arrow_size)**2)
                        if maxlength>self.arrow_threshold:
                            pass
                        else:
                            self.ax.arrow(offset*self.xstretch,
                                          np.log10(ff)*self.ystretch,
                                          txi,
                                          tyi,
                                          lw=alw,
                                          facecolor=self.arrow_color_imag,
                                          edgecolor=self.arrow_color_imag,
                                          length_includes_head=False,
                                          head_width=awidth,
                                          head_length=aheight)
        
        #--> Set plot parameters 
        self._plot_periodlst = plot_periodlst
        n = len(plot_periodlst)
        
        
        #calculate minimum period and maximum period with a stretch factor
        pmin = np.log10(plot_periodlst.min())*self.ystretch
        pmax = np.log10(plot_periodlst.max())*self.ystretch
               
        self.offsetlst = np.array(self.offsetlst)
        
        #set y-ticklabels
        if self.tscale=='period':
            yticklabels = ['{0:>4}'.format('{0: .1e}'.format(plot_periodlst[ll])) 
                            for ll in np.arange(0, n, self.ystep)]+\
                        ['{0:>4}'.format('{0: .1e}'.format(plot_periodlst[-1]))]
            
            self.ax.set_ylabel('Period (s)',
                               fontsize=self.font_size,
                               fontweight='bold')
                               
        elif self.tscale=='frequency':
            yticklabels = ['{0:>4}'.format('{0: .1e}'.format(1./plot_periodlst[ll])) 
                            for ll in np.arange(0, n, self.ystep)]+\
                            ['{0:>4}'.format('{0: .1e}'.format(1./plot_periodlst[-1]))]
            
            self.ax.set_ylabel('Frequency (Hz)',
                               fontsize=self.font_size,
                               fontweight='bold')
        #set x-axis label                       
        self.ax.set_xlabel('Station',
                           fontsize=self.font_size+2,
                           fontweight='bold')
         
        #--> set tick locations and labels
        #set y-axis major ticks
        self.ax.yaxis.set_ticks([np.log10(plot_periodlst[ll])*self.ystretch 
                             for ll in np.arange(0, n, self.ystep)])
        
        #set y-axis minor ticks                     
        self.ax.yaxis.set_ticks([np.log10(plot_periodlst[ll])*self.ystretch 
                             for ll in np.arange(0, n, 1)],minor=True)
        #set y-axis tick labels
        self.ax.set_yticklabels(yticklabels)
        
        #set x-axis ticks
        self.ax.set_xticks(self.offsetlst*self.xstretch)
        
        #set x-axis tick labels as station names
        self.ax.set_xticklabels(self.stationlst)
        
        #--> set x-limits
        if self.xlimits==None:
            self.ax.set_xlim(self.offsetlst.min()*self.xstretch-es*2,
                             self.offsetlst.max()*self.xstretch+es*2)
        else:
            self.ax.set_xlim(self.xlimits)
            
        #--> set y-limits
        if self.ylimits==None:
            self.ax.set_ylim(pmax+es*2, pmin-es*2)
        else:
            pmin = np.log10(self.ylimits[0])*self.ystretch
            pmax = np.log10(self.ylimits[1])*self.ystretch
            self.ax.set_ylim(pmax+es*2, pmin-es*2)
            
        #--> set title of the plot
        if self.title==None:
            pass
        else:
            self.ax.set_title(self.title, fontsize=self.font_size+2)
        
        #make a legend for the induction arrows
        if self.plot_tipper.find('y')==0:
            if self.plot_tipper=='yri':
                treal=self.ax.plot(np.arange(10)*.000005,
                                   np.arange(10)*.00005,
                                   color=self.arrow_color_real)
                timag=self.ax.plot(np.arange(10)*.000005,
                                   np.arange(10)*.00005,
                                   color=self.arrow_color_imag)
                self.ax.legend([treal[0],timag[0]],
                               ['Tipper_real','Tipper_imag'],
                               loc='lower right',
                               prop={'size':self.font_size-1,'weight':'bold'},
                               ncol=2,
                               markerscale=.5,
                               borderaxespad=.005,
                               borderpad=.25)
                          
            elif self.plot_tipper=='yr':
                treal = self.ax.plot(np.arange(10)*.000005,
                                     np.arange(10)*.00005,
                                     color=self.arrow_color_real)
                self.ax.legend([treal[0]],
                               ['Tipper_real'],
                               loc='lower right',
                               prop={'size':self.font_size-1,'weight':'bold'},
                               ncol=2,
                               markerscale=.5,
                               borderaxespad=.005,
                               borderpad=.25)
                          
            elif self.plot_tipper=='yi':
                timag = self.ax.plot(np.arange(10)*.000005,
                                     np.arange(10)*.00005,
                                     color=self.arrow_color_imag)
                self.ax.legend([timag[0]],
                               ['Tipper_imag'],
                               loc='lower right',
                               prop={'size':self.font_size-1,'weight':'bold'},
                               ncol=2,
                               markerscale=.5,
                               borderaxespad=.005,
                               borderpad=.25)
        
        #put a grid on the plot
        self.ax.grid(alpha=.25,which='both',color=(.25,.25,.25))
        
        #print out the min an max of the parameter plotted
        print '-'*25
        print ck+' min = {0:.2f}'.format(min(minlst))
        print ck+' max = {0:.2f}'.format(max(maxlst))
        print '-'*25

        #==> make a colorbar with appropriate colors
        if self.cb_position==None:
            self.ax2, kw = mcb.make_axes(self.ax,
                                         orientation=self.cb_orientation,
                                         shrink=.35)
        else:
            self.ax2 = self.fig.add_axes(self.cb_position)
        
        if cmap=='mt_seg_bl2wh2rd':
            #make a color list
            self.clst = [(cc,cc,1) for cc in np.arange(0,1+1./(nseg),1./(nseg))]+\
                   [(1,cc,cc) for cc in np.arange(1,-1./(nseg),-1./(nseg))]
            
            #make segmented colormap
            mt_seg_bl2wh2rd = colors.ListedColormap(self.clst)

            #make bounds so that the middle is white
            bounds = np.arange(ckmin-ckstep, ckmax+2*ckstep, ckstep)
            
            #normalize the colors
            norms = colors.BoundaryNorm(bounds, mt_seg_bl2wh2rd.N)
            
            #make the colorbar
            self.cb=mcb.ColorbarBase(self.ax2,
                                     cmap=mt_seg_bl2wh2rd,
                                     norm=norms,
                                     orientation=self.cb_orientation,
                                     ticks=bounds[1:-1])
        else:
            self.cb=mcb.ColorbarBase(self.ax2,
                                     cmap=mtcl.cmapdict[cmap],
                                     norm=colors.Normalize(vmin=ckmin,
                                                           vmax=ckmax),
                                     orientation=self.cb_orientation)

        #label the color bar accordingly
        self.cb.set_label(ckdict[ck],
                          fontdict={'size':self.font_size,'weight':'bold'})
            
        #place the label in the correct location                   
        if self.cb_orientation=='horizontal':
            self.cb.ax.xaxis.set_label_position('top')
            self.cb.ax.xaxis.set_label_coords(.5,1.3)
            
            
        elif self.cb_orientation=='vertical':
            self.cb.ax.yaxis.set_label_position('right')
            self.cb.ax.yaxis.set_label_coords(1.25,.5)
            self.cb.ax.yaxis.tick_left()
            self.cb.ax.tick_params(axis='y',direction='in')
        
        plt.show()
        
    def writeTextFiles(self, save_path=None, ptol=0.10):
        """
        This will write text files for all the phase tensor parameters
        """
        
        if save_path==None:
            svpath = os.path.dirname(self.fn_list[0])
        else:
            svpath = save_path
        
        #check to see if plot has been run if not run it
        try:
            plst=self._plot_periodlst

        except AttributeError:
            self.plot()
            plst=self._plot_periodlst
        
        if plst[0]>plst[-1]:
            plst = plst[::-1] 
            
        if self.tscale=='frequency':
            plst = 1./plst
            
        #set some empty lists to put things into
        sklst = []
        phiminlst = []
        phimaxlst = []
        elliplst = []
        azimlst = []
        tiplstr = []
        tiplsti = []
        tiplstraz = []
        tiplstiaz = []
        
        #initialize string
        stationstr = ''
        
        #match station list with filename list
        slst = [fn for ss in self.stationlst for fn in self.fn_list 
                 if os.path.basename(fn).find(ss)>=0]
        
        #first write the period or frequency as the first column
        for t1 in plst:
            sklst.append('{0:>8}  '.format('{0:.3f}'.format(t1)))
            phiminlst.append('{0:>8}  '.format('{0:.3f}'.format(t1)))
            phimaxlst.append('{0:>8}  '.format('{0:.3f}'.format(t1)))
            elliplst.append('{0:>8}  '.format('{0:.3f}'.format(t1)))
            azimlst.append('{0:>8}  '.format('{0:.3f}'.format(t1)))
            tiplstr.append('{0:>8}  '.format('{0:.3f}'.format(t1)))
            tiplstraz.append('{0:>8}  '.format('{0:.3f}'.format(t1)))
            tiplsti.append('{0:>8}  '.format('{0:.3f}'.format(t1)))
            tiplstiaz.append('{0:>8}  '.format('{0:.3f}'.format(t1)))
        
        for kk,fn in enumerate(slst):
            
            z1 = Z.Z(fn)
            pt = z1.getPhaseTensor(thetar=self.rotz)
            tip = z1.getTipper()
            if self.tscale == 'period':
                tlst = z1.period
                    
            elif self.tscale == 'frequency':
                tlst = z1.frequency
                
                 
            if kk==0:
                stationstr += '{0:>8}  '.format(self.tscale)
                
            stationstr += '{0:^8}'.format(z1.station[self.stationid[0]:\
                                                self.stationid[1]])
            for mm,t1 in enumerate(plst):
                #check to see if the periods match or are at least close in
                #case there are frequency missing
                t1_yn = False
                for ff,t2 in enumerate(tlst):
                    if t1==t2: 
                        #add on the value to the present row
                        sklst[mm]+='{0:^8}'.format('{0: .2f}'.format(pt.beta[ff]))
                        phiminlst[mm]+='{0:^8}'.format('{0: .2f}'.format(pt.phiminang[ff]))
                        phimaxlst[mm]+='{0:^8}'.format('{0: .2f}'.format(pt.phimaxang[ff]))
                        elliplst[mm]+='{0:^8}'.format('{0: .2f}'.format(pt.ellipticity[ff]))
                        azimlst[mm]+='{0:^8}'.format('{0: .2f}'.format(pt.azimuth[ff]))
                        tiplstr[mm]+='{0:>8}  '.format('{0:.3f}'.format(tip.magreal[ff]))
                        tiplstraz[mm]+='{0:>8}  '.format('{0:.3f}'.format(tip.anglereal[ff]))
                        tiplsti[mm]+='{0:>8}  '.format('{0:.3f}'.format(tip.magimag[ff]))
                        tiplstiaz[mm]+='{0:>8}  '.format('{0:.3f}'.format(tip.angleimag[ff]))
                        t1_yn = True
                        break
                        
                    elif t2>t1*(1-ptol) and t2<t1*(1+ptol):
                        #add on the value to the present row
                        sklst[mm]+='{0:^8}'.format('{0: .2f}'.format(pt.beta[ff]))
                        phiminlst[mm]+='{0:^8}'.format('{0: .2f}'.format(pt.phiminang[ff]))
                        phimaxlst[mm]+='{0:^8}'.format('{0: .2f}'.format(pt.phimaxang[ff]))
                        elliplst[mm]+='{0:^8}'.format('{0: .2f}'.format(pt.ellipticity[ff]))
                        azimlst[mm]+='{0:^8}'.format('{0: .2f}'.format(pt.azimuth[ff]))
                        tiplstr[mm]+='{0:>8}  '.format('{0:.3f}'.format(tip.magreal[ff]))
                        tiplstraz[mm]+='{0:>8}  '.format('{0:.3f}'.format(tip.anglereal[ff]))
                        tiplsti[mm]+='{0:>8}  '.format('{0:.3f}'.format(tip.magimag[ff]))
                        tiplstiaz[mm]+='{0:>8}  '.format('{0:.3f}'.format(tip.angleimag[ff]))
                        t1_yn = True                        
                        break
                    else:
                        t1_yn = False
                if t1_yn==False:
                    print 'No value for {0} at {1:.2f}'.format(z1.station,t2)
                    #add on the value to the present row
                    sklst[mm]+='{0:^8}'.format('*'*6)
                    phiminlst[mm]+='{0:^8}'.format('*'*6)
                    phimaxlst[mm]+='{0:^8}'.format('*'*6)
                    elliplst[mm]+='{0:^8}'.format('*'*6)
                    azimlst[mm]+='{0:^8}'.format('*'*6)
                    tiplstr[mm]+='{0:>8}  '.format('*'*6)
                    tiplstraz[mm]+='{0:>8}  '.format('*'*6)
                    tiplsti[mm]+='{0:>8}  '.format('*'*6)
                    tiplstiaz[mm]+='{0:>8}  '.format('*'*6)

        for mm in range(len(plst)):
            sklst[mm] += '\n'
            phiminlst[mm] += '\n'
            phimaxlst[mm] += '\n'
            elliplst[mm] += '\n'
            azimlst[mm] += '\n'
            tiplstr[mm]+='\n'
            tiplstraz[mm]+='\n'
            tiplsti[mm]+='\n'
            tiplstiaz[mm]+='\n'
                

                
            
        #write end of line for station string
        stationstr += '\n'
        
        #write files
        skfid = file(os.path.join(svpath,'PseudoSection.skew'),'w')
        skfid.write(stationstr)
        skfid.writelines(sklst)
        skfid.close()
        
        phiminfid = file(os.path.join(svpath,'PseudoSection.phimin'),'w')
        phiminfid.write(stationstr)
        phiminfid.writelines(phiminlst)
        phiminfid.close()
        
        phimaxfid = file(os.path.join(svpath,'PseudoSection.phimax'),'w')
        phimaxfid.write(stationstr)
        phimaxfid.writelines(phimaxlst)
        phimaxfid.close()
        
        ellipfid = file(os.path.join(svpath,'PseudoSection.ellipticity'),'w')
        ellipfid.write(stationstr)
        ellipfid.writelines(elliplst)
        ellipfid.close()
        
        azfid = file(os.path.join(svpath,'PseudoSection.azimuth'),'w')
        azfid.write(stationstr)
        azfid.writelines(azimlst)
        azfid.close()
        
        tprfid = file(os.path.join(svpath,'PseudoSection.tipper_mag_real'),'w')
        tprfid.write(stationstr)
        tprfid.writelines(tiplstr)
        tprfid.close()
        
        tprazfid = file(os.path.join(svpath,'PseudoSection.tipper_ang_real'),'w')
        tprazfid.write(stationstr)
        tprazfid.writelines(tiplstraz)
        tprazfid.close()
        
        tpifid = file(os.path.join(svpath,'PseudoSection.tipper_mag_imag'),'w')
        tpifid.write(stationstr)
        tpifid.writelines(tiplsti)
        tpifid.close()
        
        tpiazfid = file(os.path.join(svpath,'PseudoSection.tipper_ang_imag'),'w')
        tpiazfid.write(stationstr)
        tpiazfid.writelines(tiplstiaz)
        tpiazfid.close()
    
    def update_plot(self):
        """
        update any parameters that where changed using the built-in draw from
        canvas.  
        
        Use this if you change an of the .fig or axes properties
        
        :Example: ::
            
            >>> # to change the grid lines to be on the major ticks and gray 
            >>> pt1.ax.grid(True, which='major', color=(.5,.5,.5))
            >>> pt1.update_plot()
        
        """

        self.fig.canvas.draw()
        
    def redraw_plot(self):
        """
        use this function if you updated some attributes and want to re-plot.
        
        :Example: ::
            
            >>> # change ellipse size and color map to be segmented for skew 
            >>> pt1.ellipse_size = 5
            >>> pt1.ellipse_colorby = 'beta_seg'
            >>> pt1.ellipse_cmap = 'mt_seg_bl2wh2rd'
            >>> pt1.ellipse_range = (-9, 9, 3)
            >>> pt1.redraw_plot()
        """
        
        plt.close(self.fig)
        self.plot()
        
    def __str__(self):
        """
        rewrite the string builtin to give a useful message
        """
        
        return "Plots pseudo section of phase tensor ellipses" 
        
    def save_figure(self, save_fn, file_format='pdf', orientation='portrait', 
                  fig_dpi=None, close_plot='y'):
        """
        save_plot will save the figure to save_fn.
        
        Arguments:
        -----------
        
            **save_fn** : string
                          full path to save figure to, can be input as
                          * directory path -> the directory path to save to
                            in which the file will be saved as 
                            save_fn/station_name_ResPhase.file_format
                            
                          * full path -> file will be save to the given 
                            path.  If you use this option then the format
                            will be assumed to be provided by the path
                            
            **file_format** : [ pdf | eps | jpg | png | svg ]
                              file type of saved figure pdf,svg,eps... 
                              
            **orientation** : [ landscape | portrait ]
                              orientation in which the file will be saved
                              *default* is portrait
                              
            **fig_dpi** : int
                          The resolution in dots-per-inch the file will be
                          saved.  If None then the dpi will be that at 
                          which the figure was made.  I don't think that 
                          it can be larger than dpi of the figure.
                          
            **close_plot** : [ y | n ]
                             * 'y' will close the plot after saving.
                             * 'n' will leave plot open
                          
        :Example: ::
            >>> # save plot as a jpg
            >>> pt1.save_plot(r'/home/MT/figures', file_format='jpg')
            
        """

        if fig_dpi==None:
            fig_dpi = self.dpi
            
        if os.path.isdir(save_fn)==False:
            file_format = save_fn[-3:]
            self.fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                             orientation=orientation)
            plt.clf()
            plt.close(self.fig)
            
        else:
            save_fn = os.path.join(save_fn,'PTPseudoSection.'+
                                    file_format)
            self.fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                        orientation=orientation)
        
        if close_plot=='y':
            plt.clf()
            plt.close(self.fig)
        
        else:
            pass
        
        self.fig_fn = save_fn
        print 'Saved figure to: '+self.fig_fn
    
class PlotPhaseTensorMaps(MTArrows, MTEllipse):

    """  
    Plots phase tensor ellipses in map view from a list of edifiles with full 
    path.
    
    Arguments:
    ----------
    
        **filenamelst** : list of strings
                          full paths to .edi files to plot
                          
        **plot_frequency** : float
                             frequency to plot in Hz
                             *default* is 1
                             
        **ftol** : float
                   tolerance in frequency range to look for in each file.
                   *default* is 0.1 (10 percent)
                             
        **ellipse_dict** : dictionary
                          dictionary of parameters for the phase tensor 
                          ellipses with keys:
                              *'size' -> size of ellipse in points 
                                         *default* is 2
                              
                              *'colorby' : [ 'phimin' | 'phimax' | 'beta' | 
                                        'beta_seg' | 'phidet' | 'ellipticity' ]
                                        
                                        -'phimin' -> colors by minimum phase
                                        -'phimax' -> colors by maximum phase
                                        -'beta' -> colors by beta (skew)
                                        -'beta_seg' -> colors by beta in 
                                                       discrete segments 
                                                       defined by the range
                                        -'phidet' -> colors by determinant of
                                                     the phase tensor
                                        -'ellipticity' -> colors by ellipticity
                                        *default* is 'phimin'
                                
                              *'range' : tuple (min, max, step)
                                         Need to input at least the min and max
                                         and if using 'beta_seg' to plot
                                         discrete values input step as well
                                         *default* depends on 'colorby'
                                         
                              *'cmap' : [ 'mt_yl2rd' | 'mt_bl2yl2rd' | 
                                          'mt_wh2bl' | 'mt_rd2bl' | 
                                          'mt_bl2wh2rd' | 'mt_seg_bl2wh2rd' ]
                                          
                                       -'mt_yl2rd' -> yellow to red
                                       -'mt_bl2yl2rd' -> blue to yellow to red
                                       -'mt_wh2bl' -> white to blue
                                       -'mt_rd2bl' -> red to blue
                                       -'mt_bl2wh2rd' -> blue to white to red
                                       -'mt_bl2gr2rd' -> blue to green to red
                                       -'mt_seg_bl2wh2rd' -> discrete blue to 
                                                             white to red
                                         
        
        **cb_dict** : dictionary to control the color bar
        
                      *'orientation' : [ 'vertical' | 'horizontal' ]
                                       orientation of the color bar 
                                       *default* is vertical
                                       
                      *'position' : tuple (x,y,dx,dy)
                                    -x -> lateral position of left hand corner 
                                          of the color bar in figure between 
                                          [0,1], 0 is left side
                                          
                                    -y -> vertical position of the bottom of 
                                          the color bar in figure between 
                                          [0,1], 0 is bottom side.
                                          
                                    -dx -> width of the color bar [0,1]
                                    
                                    -dy -> height of the color bar [0,1]
                                    
        **arrow_dict** : dictionary for arrow properties
                        *'size' : float
                                  multiplier to scale the arrow. *default* is 5
                        *'head_length' : float
                                         length of the arrow head *default* is 
                                         1.5
                        *'head_width' : float
                                        width of the arrow head *default* is 
                                        1.5
                        *'lw' : float
                                line width of the arrow *default* is .5
                                
                        *'color' : tuple (real, imaginary)
                                   color of the arrows for real and imaginary
                                   
                        *'threshold': float
                                      threshold of which any arrow larger than
                                      this number will not be plotted, helps 
                                      clean up if the data is not good. 
                                      *default* is 1, note this is before 
                                      scaling by 'size'
                                      
                        *'direction : [ 0 | 1 ]
                                     -0 for arrows to point toward a conductor
                                     -1 for arrow to point away from conductor
        
        **xpad** : float
                   padding in the east-west direction of plot boundaries.  Note
                   this is by default set to lat and long units, so if you use
                   easting/northing put it the respective units. 
                   *default* is 0.2
                   
        **pad** : float
                   padding in the north-south direction of plot boundaries.  
                   Note this is by default set to lat and long units, so if you
                   use easting/northing put it the respective units.
                   *default* is 0.2
        
        **rotz** : float
                   angle in degrees to rotate the data clockwise positive.
                   *Default* is 0

        **figsize** : tuple or list (x, y) in inches
                      dimensions of the figure box in inches, this is a default
                      unit of matplotlib.  You can use this so make the plot
                      fit the figure box to minimize spaces from the plot axes
                      to the figure box.  *default* is [8, 8]
                      
        **station_dict** : dictionary
                            *'id' --> for station id index.  Ex: If you want 
                                      'S01' from 'S01dr' input as (0,3).
                                      
                            *'pad' --> pad from the center of the ellipse to 
                                       the station label
                                       
                            *'font_dict'--> dictionary of font properties
                                           font dictionary for station name. 
                                           Keys can be matplotlib.text 
                                           properties, common ones are:
                                           *'size'   -> for font size
                                           *'weight' -> for font weight
                                           *'color'  -> for color of font
                                           *'angle'  -> for angle of text
                               
        **tscale** : [ 'period' | 'frequency' ]
        
                     *'period'    -> plot vertical scale in period
                     
                     *'frequency' -> plot vertical scale in frequency
        
        **mapscale** : [ 'latlon ' | 'eastnorth' | 'eastnorthkm' ]
                       Scale of the map coordinates.
                       
                       *'latlon' --> degrees in latitude and longitude
                       
                       *'eastnorth' --> meters for easting and northing
                       
                       *'eastnorthkm' --> kilometers for easting and northing
             
        **image_dict** : dictionary of image properties
        
                         *'file' : string
                                   full path to image file name
                                   
                         *'extent' : tuple (xmin, xmax, ymin, ymax)
                                     coordinates according to mapscale. Must be
                                     input if image file is not None.
         
        **plot_yn** : [ 'y' | 'n' ]
                      *'y' to plot on creating an instance
                      
                      *'n' to not plot on creating an instance           
                       
        **fignum** : int
                     figure number.  *Default* is 1
                     
        **title** : string
                    figure title
                    
        **dpi** : int 
                  dots per inch of the resolution. *default* is 300
        
        **plot_tipper** : [ 'yri' | 'yr' | 'yi' | 'n' ]
                        *'yri' to plot induction both real and imaginary 
                           induction arrows 
                           
                        *'yr' to plot just the real induction arrows
                        
                        *'yi' to plot the imaginary induction arrows
                        
                        *'n' to not plot them
                        
                        * *Default* is 'n' 
                        
                        **Note: convention is to point towards a conductor but
                        can be changed in arrow_dict['direction']**
                         

    

                     

        **font_size** : float
                        size of the font that labels the plot, 2 will be added
                        to this number for the axis labels.
                        

        
        **station_dict** : dictionary
                           font dictionary for station name. Keys can be
                           matplotlib.text properties, common ones are:
                               *'size'   -> for font size
                               *'weight' -> for font weight
                               *'color'  -> for color of font

        **arrow_legend_dict** : dictionary of properties for legend with keys:
                               *'position' -> placement of arrow legend can be:
                                   -'upper right'
                                   -'lower right'
                                   -'upper left'
                                   -'lower left'
                               *'xborderpad'-> padding from x axis
                               *'yborderpad'-> padding from y axis
                               *'fontpad'   -> padding between arrow and 
                                               legend text
                               *'fontdict'  -> dictionary of font properties
        

        
        **reference_point** : tuple (x0,y0)
                              reference point estimate relative distance to.  
                              This point will be (0,0) on the map and 
                              everything else is referenced to this point
         
    :Example: ::
        
        >>> import mtpy.imaging.mtplottools as mtplot
        >>> import os
        >>> edipath = r"/home/EDIfiles"
        >>> edilst = [os.path.join(edipath,edi) for edi in os.listdir(edipath)
        >>> ...       if edi.find('.edi')>0]
        >>> # color by phimin with a range of 20-70 deg
        >>> ptmap = mtplot.PlotPhaseTensorMaps(edilst,freqspot=10,
        >>> ...                                ellipse_dict={'size':1,
        >>> ...                                              'range':(20,70)})
        >>> 
        >>> #----add real induction arrows----
        >>> ptmap.indarrows = 'yr'
        >>> ptmap.redraw_plot()
        >>> #
        >>> #---change the arrow properties---
        >>> ptmap.arrow_size = 1
        >>> ptmap.arrow_head_width = 0.25
        >>> ptmap.arrow_head_length = 0.25
        >>> ptmap.arrow_lw = .5
        >>> ptmap.redraw_plot()
        >>> #
        >>> #---add an image---
        >>> ptmap.image_file = r"/home/Maps/Basemap.jpg"
        >>> ptmap.image_extent = (0,10,0,10)
        >>> ptmap.redraw_plot()
        >>> #
        >>> #---Save the plot---
        >>> ptmap.save_plot(r"/home/EDIfiles",file_format='pdf')
        >>> 'Saved figure to /home/EDIfile/PTMaps/PTmap_phimin_10.0_Hz.pdf'
        
    :Example: ::
        
        >>> #change the axis label and grid color
        >>> ptmap.ax.set_xlabel('Latitude (deg)')
        >>> ptmap.ax.grid(which='major', color=(.5,1,0))
        >>> ptmap.update_plot()
        
    """
    
    def __init__(self,fn_lst=None, res_object_lst=None,
                 z_object_lst=None, tipper_object_lst=None, mt_object_lst=None,
                 plot_frequency=1, ellipse_dict={}, cb_dict={},
                 arrow_dict={}, xpad=.2, ypad=.2, rot_z=0,
                 fig_size=[8,8], station_dict=None, tscale='period',
                 mapscale='latlon', fignum=1, image_dict=None, plot_yn='y',
                 arrow_legend_dict={}, font_size=7, dpi=300, title=None,
                 reference_point=(0,0), plot_tipper='n', ftol=.1):
                                

        #----set attributes for the class-------------------------
        self.mt_lst = get_mtlst(fn_lst=fn_lst, 
                                res_object_lst=res_object_lst,
                                z_object_lst=z_object_lst, 
                                tipper_object_lst=tipper_object_lst, 
                                mt_object_lst=mt_object_lst)
        
        #set the frequency to plot
        self.plot_frequency = plot_frequency
        self.ftol = ftol
        
        #--> set the ellipse properties -------------------
        #set default size to 2
        self._ellipse_dict = ellipse_dict
        self._read_ellipse_dict()
            
        #--> set colorbar properties---------------------------------
        #set orientation to horizontal
        try:
            self.cb_orientation = cb_dict['orientation']
        except KeyError:
            self.cb_orientation = 'vertical'
        
        #set the position to middle outside the plot            
        try:
            self.cb_position = cb_dict['position']
        except KeyError:
            self.cb_position = None
            
        #--> set plot properties ------------------------------
        self.dpi = dpi
        self.font_size = font_size
        self.tscale = tscale
        self.figsize = fig_size
        self.fignum = fignum
        self.title = title
        self.xpad = xpad
        self.ypad = ypad
        self.mapscale = mapscale
        
        #if rotation angle is an int or float make an array the length of 
        #mt_lst for plotting purposes
        if type(rot_z) is float or type(rot_z) is int:
            self.rot_z = np.array([rot_z]*len(self.mt_lst))
        
        #if the rotation angle is an array for rotation of different 
        #frequency than repeat that rotation array to the len(mt_lst)
        elif type(rot_z) is np.ndarray:
            if rot_z.shape[0]!=len(self.mt_lst):
                self.rot_z = np.repeat(rot_z, len(self.mt_lst))
                
        else:
            self.rot_z = rot_z
        
        #--> set induction arrow properties -------------------------------
        self.plot_tipper = plot_tipper
        
        self._arrow_dict = arrow_dict
        self._read_arrow_dict()
            
        #--> set arrow legend properties -------------------------------
        try:
            self.arrow_legend_position = arrow_legend_dict['position']
        except KeyError:
            self.arrow_legend_position = 'lower right'
            
        #set x-border pad
        try:
            self.arrow_legend_xborderpad = arrow_legend_dict['xborderpad']
        except KeyError:
            self.arrow_legend_xborderpad = 0.2
            
        #set y-border pad
        try:
            self.arrow_legend_yborderpad = arrow_legend_dict['yborderpad']
        except KeyError:
            self.arrow_legend_yborderpad = 0.2
            
        #set font pad
        try:
            self.arrow_legend_fontpad = arrow_legend_dict['fontpad']
        except KeyError:
            self.arrow_legend_fontpad = .05
            
        #set font properties
        try:
            self.arrow_legend_fontdict = arrow_legend_dict['fontdict']
        except KeyError:
            self.arrow_legend_fontdict = {'size':self.font_size,
                                          'weight':'bold'}

        #--> set background image properties
        if image_dict!=None:
            # make sure there is a file
            try:
                self.image_file = image_dict['file']
                if not os.path.isfile(image_dict['file']):
                    raise IOError('Image file does not exist')
                    
            except KeyError:
                raise IOError('Need to include filename if plotting an image')
              
            # make sure an extent is given
            try:
                self.image_extent = image_dict['extent']
            except KeyError:
                raise NameError('Need to include the extent of the image as '+\
                                '(left, right, bottom, top)')
                                
        #--> set a central reference point
        self.plot_reference_point = reference_point
            
        #--> set station name properties
        if station_dict!=None:
            try:
                self.station_id = station_dict['id']
            except KeyError:
                self.station_id = (0,2)
            
            #set spacing of station name and ellipse
            try:
                self.station_pad = station_dict['pad']
            except KeyError:
                self.station_pad = .0005
                
            #set font properties of the station label
            try:
                self.station_font_size = station_dict['font_dict']
            except KeyError:
                self.station_font_dict = {'size':self.font_size,
                                          'weight':'bold'}
                

        #--> plot if desired ------------------------
        self.plot_yn = plot_yn
        if self.plot_yn=='y':
            self.plot()
        

    def plot(self): 
        """
        Plots the phase tensor map
        """                               
        
        #set position properties for the plot
        plt.rcParams['font.size']=self.font_size
        plt.rcParams['figure.subplot.left']=.1
        plt.rcParams['figure.subplot.right']=.98
        plt.rcParams['figure.subplot.bottom']=.1
        plt.rcParams['figure.subplot.top']=.93
        plt.rcParams['figure.subplot.wspace']=.55
        plt.rcParams['figure.subplot.hspace']=.70        
        
        #make figure instanc
        self.fig = plt.figure(self.fignum, self.figsize, dpi=self.dpi)
        
        #clear the figure if there is already one up
        plt.clf()
        
        #make an axes instance
        self.ax = self.fig.add_subplot(1,1,1,aspect='equal')
        
        #--> plot the background image if desired-----------------------
        try:
            im=plt.imread(self.image_file)
            self.ax.imshow(im, origin='lower', extent=self.image_extent, 
                      aspect='auto')
        except AttributeError:
            pass
        
        #get the reference point
        refpoint = self.plot_reference_point
            
        #set some local parameters
        es = float(self.ellipse_size)
        cmap = self.ellipse_cmap
        ckmin = float(self.ellipse_range[0])
        ckmax = float(self.ellipse_range[1])
        try:
            ckstep = float(self.ellipse_range[2])
        except IndexError:
            if cmap=='mt_seg_bl2wh2rd':
                raise ValueError('Need to input range as (min,max,step)')
            else:
                ckstep=3
        nseg = float((ckmax-ckmin)/(2*ckstep))
        ck = self.ellipse_colorby


        #--> set the bounds on the segmented colormap
        if cmap=='mt_seg_bl2wh2rd':
            bounds = np.arange(ckmin, ckmax+ckstep, ckstep) 
            
        #set tick parameters depending on the mapscale
        if self.mapscale=='latlon':
            self.tickstrfmt = '%.3f'
            
        elif self.mapscale=='eastnorth' or self.mapscale=='eastnorthkm':
            self.tickstrfmt = '%.0f'
        
        #make some empty arrays
        elliplst=[]
        latlst = np.zeros(len(self.mt_lst))
        lonlst = np.zeros(len(self.mt_lst))
        self.plot_xarr = np.zeros(len(self.mt_lst))
        self.plot_yarr = np.zeros(len(self.mt_lst))
        
        
        for ii,mt in enumerate(self.mt_lst):
            #try to find the frequency in the frequency list of each file
            freqfind = [ff for ff,f2 in enumerate(mt.frequency) 
                         if f2>self.plot_frequency*(1-self.ftol) and
                            f2<self.plot_frequency*(1+self.ftol)]
            try:
                self.jj = freqfind[0]
                jj = self.jj

                #get phase tensor
                pt = mt.get_PhaseTensor()
                pt.rotate(self.rot_z[ii])
                
                #if map scale is lat lon set parameters                
                if self.mapscale=='latlon':
                    latlst[ii] = mt.lat
                    lonlst[ii] = mt.lon
                    plotx = mt.lon-refpoint[0]
                    ploty = mt.lat-refpoint[1]
                
                #if map scale is in meters easting and northing
                elif self.mapscale=='eastnorth':
                    zone,east,north = utm2ll.LLtoUTM(23, mt.lat, mt.lon)
                    
                    #set the first point read in as a refernce other points                    
                    if ii==0:
                        zone1 = zone
                        plotx = east-refpoint[0]
                        ploty = north-refpoint[1]
                        
                    #read in all the other point
                    else:
                        #check to make sure the zone is the same this needs
                        #to be more rigorously done
                        if zone1!=zone:
                            print 'Zone change at station '+mt.station
                            if zone1[0:2]==zone[0:2]:
                                pass
                            elif int(zone1[0:2])<int(zone[0:2]):
                                east += 500000
                            else:
                                east -= -500000
                            latlst[ii] = north-refpoint[1]
                            lonlst[ii] = east-refpoint[0]
                            plotx = east-refpoint[0]
                            ploty = north-refpoint[1]
                        else:
                            latlst[ii] = north-refpoint[1]
                            lonlst[ii] = east-refpoint[0]
                            plotx = east-refpoint[0]
                            ploty = north-refpoint[1]
                
                #if mapscale is in km easting and northing
                elif self.mapscale=='eastnorthkm':
                    zone,east,north = utm2ll.LLtoUTM(23, mt.lat, mt.lon)
                    if ii==0:
                        zone1 = zone
                        plotx = (east-refpoint[0])/1000.
                        ploty = (north-refpoint[1])/1000.
                    
                    else:
                        if zone1!=zone:
                            print 'Zone change at station '+mt.station
                            if zone1[0:2]==zone[0:2]:
                                pass
                            elif int(zone1[0:2])<int(zone[0:2]):
                                east += 500000
                            else:
                                east -= 500000
                            latlst[ii] = (north-refpoint[1])/1000.
                            lonlst[ii] = (east-refpoint[0])/1000.
                            plotx = (east-refpoint[0])/1000.
                            ploty = (north-refpoint[1])/1000.
                        else:
                            latlst[ii] = (north-refpoint[1])/1000.
                            lonlst[ii] = (east-refpoint[0])/1000.
                            plotx = (east-refpoint[0])/1000.
                            ploty = (north-refpoint[1])/1000.
                else:
                    raise NameError('mapscale not recognized')
                
                #put the location of each ellipse into an array in x and y
                self.plot_xarr[ii] = plotx
                self.plot_yarr[ii] = ploty
                
                #--> set local variables
                phimin = np.nan_to_num(pt.phimin[0][jj])
                phimax = np.nan_to_num(pt.phimax[0][jj])
                eangle = np.nan_to_num(pt.azimuth[0][jj])
                
                if cmap=='mt_seg_bl2wh2rd':
                    bounds = np.arange(ckmin, ckmax+ckstep, ckstep)
                    nseg = float((ckmax-ckmin)/(2*ckstep))
        
                #get the properties to color the ellipses by
                if self.ellipse_colorby=='phiminang' or \
                   self.ellipse_colorby=='phimin':
                    colorarray = pt.phimin[0][jj]
            
                                                   
                elif self.ellipse_colorby=='phidet':
                     colorarray = np.sqrt(abs(pt.det[0][jj]))*(180/np.pi)
                     
                    
                elif self.ellipse_colorby=='skew' or\
                     self.ellipse_colorby=='skew_seg':
                    colorarray = pt.beta[0][jj]
                    
                elif self.ellipse_colorby=='ellipticity':
                    colorarray = pt.ellipticity[0][jj]
                    
                else:
                    raise NameError(self.ellipse_colorby+' is not supported')
                
                #--> get ellipse properties
                #if the ellipse size is not physically correct make it a dot
                if phimax==0 or phimax>100 or phimin==0 or phimin>100:
                    eheight=.0000001*es
                    ewidth=.0000001*es
                    print mt.station
                else:
                    scaling = es/phimax
                    eheight = phimin*scaling
                    ewidth = phimax*scaling
                
                #make an ellipse
                ellipd=patches.Ellipse((plotx,ploty),
                                       width=ewidth,
                                       height=eheight,
                                       angle=90-eangle)
                
                #get ellipse color
                if cmap.find('seg')>0:
                    ellipd.set_facecolor(mtcl.get_plot_color(colorarray,
                                                             self.ellipse_colorby,
                                                             cmap,
                                                             ckmin,
                                                             ckmax,
                                                             bounds=bounds))
                else:
                    ellipd.set_facecolor(mtcl.get_plot_color(colorarray,
                                                             self.ellipse_colorby,
                                                             cmap,
                                                             ckmin,
                                                             ckmax))
                
                #==> add ellipse to the plot
                elliplst.append(ellipd)
                self.ax.add_artist(ellipd)
                        
                #-----------Plot Induction Arrows---------------------------
                if self.plot_tipper.find('y')==0:
                    
                    #get tipper
                    tip = mt.getTipper(thetar=self.rotz)
                    
                    #make some local parameters for easier typing                    
                    ascale = self.arrow_size
                    adir = self.arrow_direction*np.pi
                    
                    #plot real tipper
                    if self.plot_tipper=='yri' or self.plot_tipper=='yr':
                        if tip.magreal[jj]<=1.0:
                            txr = tip.magreal[jj]*ascale*\
                                  np.sin((tip.anglereal[jj])*np.pi/180+adir)
                            tyr=tip.magreal[jj]*ascale*\
                                np.cos((tip.anglereal[jj])*np.pi/180+adir)
        
                            self.ax.arrow(plotx,
                                          ploty,
                                          txr,
                                          tyr,
                                          lw=self.arrow_lw,
                                          facecolor=self.arrow_color_real,
                                          edgecolor=self.arrow_color_real,
                                          length_includes_head=False,
                                          head_width=self.arrow_head_width,
                                          head_length=self.arrow_head_length)
                        else:
                            pass
                        
                    #plot imaginary tipper
                    if self.plot_tipper=='yri' or self.plot_tipper=='yi':
                        if tip.magimag[jj]<=1.0:
                            txi = tip.magimag[jj]*ascale*\
                                 np.sin((tip.angleimag[jj])*np.pi/180+adir)
                            tyi = tip.magimag[jj]*ascale*\
                                 np.cos((tip.angleimag[jj])*np.pi/180+adir)
        
                            self.ax.arrow(plotx,
                                          ploty,
                                          txi,
                                          tyi,
                                          lw=self.arrow_lw,
                                          facecolor=self.arrow_color_imag,
                                          edgecolor=self.arrow_color_imag,
                                          length_includes_head=False,
                                          head_width=self.arrow_head_width,
                                          head_length=self.arrow_head_length)
                             
                
                #------------Plot station name------------------------------
                try:
                    self.ax.text(plotx,
                            ploty+self.station_pad,
                            mt.station[self.station_id[0]:self.station_id[1]],
                            horizontalalignment='center',
                            verticalalignment='baseline',
                            fontdict=self.station_font_dict)
                except AttributeError:
                    pass
                
            #==> print a message if couldn't find the frequency
            except IndexError:
                print 'Did not find {0:.5g} Hz for station {1}'.format(
                                               self.plot_frequency,mt.station)
        
        #--> set axes properties depending on map scale------------------------
        if self.mapscale=='latlon':    
            self.ax.set_xlabel('longitude',
                               fontsize=self.font_size+2,
                               fontweight='bold')
            self.ax.set_ylabel('latitude',
                               fontsize=self.font_size+2,
                               fontweight='bold')
            
        elif self.mapscale=='eastnorth':
            self.ax.set_xlabel('Easting (m)',
                               fontsize=self.font_size+2,
                               fontweight='bold')
            self.ax.set_ylabel('Northing (m)',
                               fontsize=self.font_size+2,
                               fontweight='bold')
      
        elif self.mapscale=='eastnorthkm':
            self.ax.set_xlabel('Easting (km)',
                               fontsize=self.font_size+2,
                               fontweight='bold')
            self.ax.set_ylabel('Northing (km)',
                               fontsize=self.font_size+2,
                               fontweight='bold')

        
        #--> set plot limits
        self.ax.set_xlim(self.plot_xarr.min()-self.xpad,
                             self.plot_xarr.max()+self.xpad)
        self.ax.set_ylim(self.plot_yarr.min()-self.xpad,
                         self.plot_yarr.max()+self.xpad)
                         
        #--> set tick label format
        self.ax.xaxis.set_major_formatter(FormatStrFormatter(self.tickstrfmt))
        self.ax.yaxis.set_major_formatter(FormatStrFormatter(self.tickstrfmt))
        
        #--> set title in period or frequency
        if self.tscale=='period':
            titlefreq = '{0:.5g} (s)'.format(1./self.plot_frequency)
        else:
            titlefreq='{0:.5g} (Hz)'.format(self.plot_frequency)
        
        if not self.title:
            self.ax.set_title('Phase Tensor Map for '+titlefreq,
                              fontsize=self.font_size+2,fontweight='bold')
        else:
            self.ax.set_title(self.title+titlefreq,
                              fontsize=self.font_size+2,fontweight='bold')
                              
        #--> plot induction arrow scale bar -----------------------------------
        if self.plot_tipper.find('y')==0:
            parrx = self.ax.get_xlim()
            parry = self.ax.get_ylim()
            try:
                axpad = self.arrow_legend_xborderpad
            except AttributeError:
                axpad = self.xpad+self.arrow_size
            
            try:
                aypad = self.arrow_legend_yborderpad
            except AttributeError:
                aypad = self.ypad

            try:
                txtpad = self.arrow_legend_fontpad
            except AttributeError:
                txtpad = .25*es
                
            
            #make arrow legend postion and arrows coordinates
            if self.arrow_legend_position=='lower right':
                pax = parrx[1]-axpad
                pay = parry[0]+aypad
                ptx = self.arrow_size
                pty = 0
                txa = parrx[1]-axpad+self.arrow_size/2.
                txy = pay+txtpad
                
            elif self.arrow_legend_position=='upper right':
                pax = parrx[1]-axpad
                pay = parry[1]-aypad
                ptx = self.arrow_size
                pty = 0
                txa = parrx[1]-axpad+self.arrow_size/2.
                txy = pay+txtpad
                
            elif self.arrow_legend_position=='lower left':
                pax = parrx[0]+axpad
                pay = parry[0]+aypad
                ptx = self.arrow_size
                pty = 0
                txa = parrx[0]+axpad+self.arrow_size/2.
                txy = pay+txtpad
                
            elif self.arrow_legend_position=='upper left':
                pax = parrx[0]+axpad
                pay = parry[1]-aypad
                ptx = self.arrow_size
                pty = 0
                txa = parrx[0]+axpad+self.arrow_size/2.
                txy = pay+txtpad
            else:
                raise NameError('arrowlegend not supported.')
                
            self.ax.arrow(pax,
                          pay,
                          ptx,
                          pty,
                          lw=self.arrow_lw,
                          facecolor=self.arrow_color_real,
                          edgecolor=self.arrow_color_real,
                          length_includes_head=False,
                          head_width=self.arrow_head_width,
                          head_length=self.arrow_head_length)
            
            self.ax.text(txa,
                         txy,
                         '|T|=1',
                         horizontalalignment='center',
                         verticalalignment='baseline',
                         fontdict={'size':self.font_size,'weight':'bold'})
        
        #make a grid with gray lines
        self.ax.grid(alpha=.25)
        
        #==> make a colorbar with appropriate colors
        if self.cb_position==None:
            self.ax2, kw = mcb.make_axes(self.ax,
                                         orientation=self.cb_orientation,
                                         shrink=.35)
        else:
            self.ax2 = self.fig.add_axes(self.cb_position)
        
        if cmap=='mt_seg_bl2wh2rd':
            #make a color list
            self.clst = [(cc,cc,1) for cc in np.arange(0,1+1./(nseg),1./(nseg))]+\
                   [(1,cc,cc) for cc in np.arange(1,-1./(nseg),-1./(nseg))]
            
            #make segmented colormap
            mt_seg_bl2wh2rd = colors.ListedColormap(self.clst)

            #make bounds so that the middle is white
            bounds = np.arange(ckmin-ckstep, ckmax+2*ckstep, ckstep)
            
            #normalize the colors
            norms = colors.BoundaryNorm(bounds, mt_seg_bl2wh2rd.N)
            
            #make the colorbar
            self.cb=mcb.ColorbarBase(self.ax2,
                                     cmap=mt_seg_bl2wh2rd,
                                     norm=norms,
                                     orientation=self.cb_orientation,
                                     ticks=bounds[1:-1])
        else:
            self.cb=mcb.ColorbarBase(self.ax2,
                                     cmap=mtcl.cmapdict[cmap],
                                     norm=colors.Normalize(vmin=ckmin,
                                                           vmax=ckmax),
                                     orientation=self.cb_orientation)

        #label the color bar accordingly
        self.cb.set_label(ckdict[ck],
                          fontdict={'size':self.font_size,'weight':'bold'})
            
        #place the label in the correct location                   
        if self.cb_orientation=='horizontal':
            self.cb.ax.xaxis.set_label_position('top')
            self.cb.ax.xaxis.set_label_coords(.5,1.3)
            
            
        elif self.cb_orientation=='vertical':
            self.cb.ax.yaxis.set_label_position('right')
            self.cb.ax.yaxis.set_label_coords(1.25,.5)
            self.cb.ax.yaxis.tick_left()
            self.cb.ax.tick_params(axis='y',direction='in')
            
        plt.show()
    
        
    def save_plot(self, save_fn, file_format='pdf', 
                  orientation='portrait', fig_dpi=None, close_plot='y'):
        """
        save_plot will save the figure to save_fn.
        
        Arguments:
        -----------
        
            **save_fn** : string
                          full path to save figure to, can be input as
                          * directory path -> the directory path to save to
                            in which the file will be saved as 
                            save_fn/station_name_ResPhase.file_format
                            
                          * full path -> file will be save to the given 
                            path.  If you use this option then the format
                            will be assumed to be provided by the path
                            
            **file_format** : [ pdf | eps | jpg | png | svg ]
                              file type of saved figure pdf,svg,eps... 
                              
            **orientation** : [ landscape | portrait ]
                              orientation in which the file will be saved
                              *default* is portrait
                              
            **fig_dpi** : int
                          The resolution in dots-per-inch the file will be
                          saved.  If None then the dpi will be that at 
                          which the figure was made.  I don't think that 
                          it can be larger than dpi of the figure.
                          
            **close_plot** : [ y | n ]
                             * 'y' will close the plot after saving.
                             * 'n' will leave plot open
                          
        :Example: ::
            
            >>> # to save plot as jpg
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotPhaseTensorMaps(edilst,freqspot=10)
            >>> p1.save_plot(r'/home/MT', file_format='jpg')
            'Figure saved to /home/MT/PTMaps/PTmap_phimin_10Hz.jpg'
            
        """

        sf='_{0:.6g}'.format(np.median(self.plot_frequency_arr))
        
        if fig_dpi==None:
            fig_dpi = self.dpi
            
        if os.path.isdir(save_fn)==False:
            file_format = save_fn[-3:]
            self.fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                             orientation=orientation)
            plt.clf()
            plt.close(self.fig)
            
        else:
            if not os.path.exists(save_fn):
                os.mkdir(save_fn)
            if not os.path.exists(os.path.join(save_fn,'PTMaps')):
                os.mkdir(os.path.join(save_fn,'PTMaps'))
                save_fn = os.path.join(save_fn,'PTMaps')
                
            save_fn = os.path.join(save_fn,'PTmap_'+self.ellipse_colorby+sf+
                                    'Hz.'+file_format)
            self.fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                        orientation=orientation)
                        
        if close_plot=='y':
            plt.clf()
            plt.close(self.fig)
        
        else:
            pass
        
        self.fig_fn = save_fn
        print 'Saved figure to: '+self.fig_fn

    def update_plot(self):
        """
        update any parameters that where changed using the built-in draw from
        canvas.  
        
        Use this if you change an of the .fig or axes properties
        
        :Example: ::
            
            >>> # to change the grid lines to only be on the major ticks
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> [ax.grid(True, which='major') for ax in [p1.axr,p1.axp]]
            >>> p1.update_plot()
        
        """

        self.fig.canvas.draw()
        
    def redraw_plot(self):
        """
        use this function if you updated some attributes and want to re-plot.
        
        :Example: ::
            
            >>> # change the color and marker of the xy components
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> p1.xy_color = (.5,.5,.9)
            >>> p1.xy_marker = '*'
            >>> p1.redraw_plot()
        """
        
        plt.close(self.fig)
        self.plot()
        
    def writeTextFiles(self, save_path=None):
        """
        This will write text files for all the phase tensor parameters.
        
        Arguments:
        ----------
            **save_path** : string
                            path to save files to.  Files are saved as:
                                save_path/Map_frequency.parameter
                                
        Returns:
        --------
            **files for:**
                *phi_min
                *phi_max
                *skew
                *ellipticity
                *azimuth
                *tipper_mag_real
                *tipper_ang_real
                *tipper_mag_imag
                *tipper_ang_imag
                *station
                
            These files are in condensed map view to follow the plot.  There
            is also a file that is in table format, which might be easier
            to read.  This file has extenstion .table
                
        """
        
        #create a save path
        if save_path==None:
            svpath = os.path.join(os.path.dirname(self.fn_list[0]),'PTMaps')
        else:
            svpath = save_path
        
        #if the folder doesn't exist make it
        if not os.path.exists(svpath):
            os.mkdir(svpath)
            
        #make sure the attributes are there if not get them
        try: 
            self.plot_xarr
        except AttributeError:
            self.plot()
        
        #sort the x and y in ascending order to get placement in the file right
        xlst = np.sort(abs(self.plot_xarr))
        ylst = np.sort(abs(self.plot_yarr))
        
        #get the indicies of where the values should go in map view of the 
        #text file
        nx = self.plot_xarr.shape[0]
        xyloc = np.zeros((nx, 2))
        for jj,xx in enumerate(self.plot_xarr):
            xyloc[jj,0] = np.where(xlst==abs(xx))[0][0]
            xyloc[jj,1] = np.where(ylst==abs(self.plot_yarr[jj]))[0][0]

        #create arrays that simulate map view in a text file
        phiminmap = np.zeros((xlst.shape[0], ylst.shape[0]))
        phimaxmap = np.zeros((xlst.shape[0], ylst.shape[0]))
        azimuthmap = np.zeros((xlst.shape[0], ylst.shape[0]))
        ellipmap = np.zeros((xlst.shape[0], ylst.shape[0]))
        betamap = np.zeros((xlst.shape[0], ylst.shape[0]))
        trmap = np.zeros((xlst.shape[0], ylst.shape[0]))
        trazmap = np.zeros((xlst.shape[0], ylst.shape[0]))
        timap = np.zeros((xlst.shape[0], ylst.shape[0]))
        tiazmap = np.zeros((xlst.shape[0], ylst.shape[0]))
        stationmap = np.zeros((xlst.shape[0], ylst.shape[0]), 
                              dtype='|S8')
        
        #put the information into the zeroed arrays
        for ii in range(nx):
            z1 = Z.Z(self.fn_list[ii])

            #try to find the frequency in the frequency list of each file
            freqfind = [ff for ff,f2 in enumerate(z1.frequency) 
                         if f2>self.plot_frequency*(1-self.ftol) and
                            f2<self.plot_frequency*(1+self.ftol)]
            try:
                self.jj = freqfind[0]
                jj = self.jj            
            
                pt = z1.getPhaseTensor()
                tp = z1.getTipper()
                
                phiminmap[xyloc[ii,0],xyloc[ii,1]] = pt.phiminang[self.jj]
                phimaxmap[xyloc[ii,0],xyloc[ii,1]] = pt.phimaxang[self.jj]
                azimuthmap[xyloc[ii,0],xyloc[ii,1]] = pt.azimuth[self.jj]
                ellipmap[xyloc[ii,0],xyloc[ii,1]] = pt.ellipticity[self.jj]
                betamap[xyloc[ii,0],xyloc[ii,1]] = pt.beta[self.jj]
                trmap[xyloc[ii,0],xyloc[ii,1]] = tp.magreal[self.jj]
                trazmap[xyloc[ii,0],xyloc[ii,1]] = tp.anglereal[self.jj]
                timap[xyloc[ii,0],xyloc[ii,1]] = tp.magimag[self.jj]
                tiazmap[xyloc[ii,0],xyloc[ii,1]] = tp.angleimag[self.jj]
                try:
                    stationmap[xyloc[ii,0],xyloc[ii,1]] = \
                              z1.station[self.station_id[0]:self.station_id[1]]
                except AttributeError:
                    stationmap[xyloc[ii,0],xyloc[ii,1]] = z1.station
            except IndexError:
                print 'Did not find {0:.5g} Hz for station {1}'.format(
                                               self.plot_frequency,z1.station)

        #----------------------write files-------------------------------------
        svfn = 'Map_{0:.6g}'.format(self.plot_frequency)
        ptminfid = file(os.path.join(svpath,svfn+'.phimin'),'w')
        ptmaxfid = file(os.path.join(svpath,svfn+'.phimax'),'w')
        ptazmfid = file(os.path.join(svpath,svfn+'.azimuth'),'w')
        ptskwfid = file(os.path.join(svpath,svfn+'.skew'),'w')
        ptellfid = file(os.path.join(svpath,svfn+'.ellipticity'),'w')
        tprmgfid = file(os.path.join(svpath,svfn+'.tipper_mag_real'),'w')
        tprazfid = file(os.path.join(svpath,svfn+'.tipper_ang_real'),'w')
        tpimgfid = file(os.path.join(svpath,svfn+'.tipper_mag_imag'),'w')
        tpiazfid = file(os.path.join(svpath,svfn+'.tipper_ang_imag'),'w')
        statnfid = file(os.path.join(svpath,svfn+'.station'),'w')
        tablefid = file(os.path.join(svpath,svfn+'.table'),'w')
        
        for ly in range(ylst.shape[0]):
            for lx in range(xlst.shape[0]):
                #if there is nothing there write some spaces
                if phiminmap[lx,ly]==0.0:
                    ptminfid.write('{0:^8}'.format(' '))
                    ptmaxfid.write('{0:^8}'.format(' '))
                    ptazmfid.write('{0:^8}'.format(' '))
                    ptskwfid.write('{0:^8}'.format(' '))
                    ptellfid.write('{0:^8}'.format(' '))
                    tprmgfid.write('{0:^8}'.format(' '))
                    tprazfid.write('{0:^8}'.format(' '))
                    tpimgfid.write('{0:^8}'.format(' '))
                    tpiazfid.write('{0:^8}'.format(' '))
                    statnfid.write('{0:^8}'.format(' '))
                    
                else:
                    ptminfid.write('{0:^8}'.format(
                                          '{0: .2f}'.format(phiminmap[lx,ly])))
                    ptmaxfid.write('{0:^8}'.format(
                                          '{0: .2f}'.format(phimaxmap[lx,ly])))
                    ptazmfid.write('{0:^8}'.format(
                                          '{0: .2f}'.format(azimuthmap[lx,ly])))
                    ptskwfid.write('{0:^8}'.format(
                                          '{0: .2f}'.format(betamap[lx,ly])))
                    ptellfid.write('{0:^8}'.format(
                                          '{0: .2f}'.format(ellipmap[lx,ly])))
                    tprmgfid.write('{0:^8}'.format(
                                          '{0: .2f}'.format(trmap[lx,ly])))
                    tprazfid.write('{0:^8}'.format(
                                          '{0: .2f}'.format(trazmap[lx,ly])))
                    tpimgfid.write('{0:^8}'.format(
                                          '{0: .2f}'.format(timap[lx,ly])))
                    tpiazfid.write('{0:^8}'.format(
                                          '{0: .2f}'.format(tiazmap[lx,ly])))
                    statnfid.write('{0:^8}'.format(stationmap[lx,ly]))
            
            #make sure there is an end of line        
            ptminfid.write('\n')
            ptmaxfid.write('\n')
            ptazmfid.write('\n')
            ptskwfid.write('\n')
            ptellfid.write('\n')
            tprmgfid.write('\n')
            tprazfid.write('\n')
            tpimgfid.write('\n')
            tpiazfid.write('\n')
            statnfid.write('\n')
        
        #close the files
        ptminfid.close()
        ptmaxfid.close()
        ptazmfid.close()
        ptskwfid.close()
        ptellfid.close()
        tprmgfid.close()
        tprazfid.close()
        tpimgfid.close()
        tpiazfid.close()
        statnfid.close()
        
        #--> write the table file
        #write header
        for ss in ['station','phi_min','phi_max','skew','ellipticity',
                   'azimuth','tip_mag_re','tip_ang_re','tip_mag_im',
                   'tip_ang_im']:
            tablefid.write('{0:^12}'.format(ss))
        tablefid.write('\n')
        
        for ii in range(nx):
            xx,yy=xyloc[ii,0],xyloc[ii,1]
            tablefid.write('{0:^12}'.format(stationmap[xx,yy]))
            tablefid.write('{0:^12}'.format('{0: .2f}'.format(phiminmap[xx,yy])))
            tablefid.write('{0:^12}'.format('{0: .2f}'.format(phimaxmap[xx,yy])))
            tablefid.write('{0:^12}'.format('{0: .2f}'.format(betamap[xx,yy])))
            tablefid.write('{0:^12}'.format('{0: .2f}'.format(ellipmap[xx,yy])))
            tablefid.write('{0:^12}'.format('{0: .2f}'.format(azimuthmap[xx,yy])))
            tablefid.write('{0:^12}'.format('{0: .2f}'.format(trmap[xx,yy])))
            tablefid.write('{0:^12}'.format('{0: .2f}'.format(trazmap[xx,yy])))
            tablefid.write('{0:^12}'.format('{0: .2f}'.format(timap[xx,yy])))
            tablefid.write('{0:^12}'.format('{0: .2f}'.format(tiazmap[xx,yy])))
            tablefid.write('\n')
            
        tablefid.write('\n')
        
        print 'Wrote files to {}'.format(svpath)
            
        
    def __str__(self):
        """
        rewrite the string builtin to give a useful message
        """
        
        return "Plots phase tensor maps for one frequency"

class PlotStrike(object):
    """
    PlotStrike will plot the strike estimated from the invariants, phase tensor
    and the tipper in either a rose diagram of xy plot
    

    plots the strike angle as determined by phase tensor azimuth (Caldwell et 
    al. [2004]) and invariants of the impedance tensor (Weaver et al. [2003]).
    
    The data is split into decades where the histogram for each is plotted in 
    the form of a rose diagram with a range of 0 to 180 degrees.
    Where 0 is North and 90 is East.   The median angle of the period band is 
    set in polar diagram.  The top row is the strike estimated from
    the invariants of the impedance tensor.  The bottom row is the azimuth
    estimated from the phase tensor.  If tipper is 'y' then the 3rd row is the
    strike determined from the tipper, which is orthogonal to the induction
    arrow direction.  
    
    Arguments:
    ----------
        **edilst** : list of full paths to edifiles to be used
        
        **fignum** : int
                     figure number to be plotted. *Default* is 1
        
        **fs** : float
                 font size for labels of plotting. *Default* is 10
                 
        **dpi** : int
                  dots-per-inch resolution of figure, 300 is needed for 
                  publications. *Default* is 300
                  
        **thetar** : float
                     angle of rotation clockwise positive. *Default* is 0
                     
        **ptol** : float
                   Tolerance level to match periods from different edi files.
                   *Default* is 0.05
                   
        **text_dict** : dictionary
                  *'pad' : float
                           padding of the angle label at the bottom of each 
                           polar diagram.  *Default* is 1.65
                           
                  *'size' : float
                            font size
                   
                     
        **plot_range** : [ 'data' | (period_min,period_max) ]
                    period range to estimate the strike angle. Options are:
                        * *'data'* for estimating the strike for all periods
                            in the data.
                        * (pmin,pmax) for period min and period max, input as
                          (log10(pmin),log10(pmax))
        
        **plot_type** : [ 1 | 2 ]
                        -*1* to plot individual decades in one plot
                        -*2* to plot all period ranges into one polar diagram
                              for each strike angle estimation
        
        **plot_tipper** : [ 'y' | 'n' ]
                      -*'y'* to plot the tipper strike
                      -*'n'* to not plot tipper strike
                      
        **pt_error_floor** : float   
                    Maximum error in degrees that is allowed to estimate strike.
                    *Default* is None allowing all estimates to be used.
                    
        **fold** : [ True | False ]
                    *True to plot only from 0 to 180
                    *False to plot from 0 to 360
                

    :Example: ::
        
        >>> import os
        >>> import mtpy.imaging.mtplottools as mtplot
        >>> edipath = r"/home/EDIFiles"
        >>> edilst = [os.path.join(edipath,edi) for edi in os.listdir(edipath)
        >>> ...       if edi.find('.edi')>0]
        >>> #---plot rose plots in decades with tipper and an error floor on pt
        >>> strike = mtplot.PlotStrike(edilst, plot_type=1,pt_error_floor=5)
        >>> #---plot all decades into one rose plot for each estimation---
        >>> strike.plot_type = 2
        >>> strike.redraw_plot()
        >>> #---save the plot---
        >>> strike.save_plot(r"/home/Figures")
        'Figure saved to /home/Figures/StrikeAnalysis_.pdf'
    """
    
    def __init__(self,filenamelst,fignum=1,font_size=10,dpi=300,thetar=0,
                 period_tolerance=.05,text_dict={},plot_range='data',
                 plot_type=1,plot_tipper='n',pt_error_floor=None,
                 plot_yn='y',fold=True,bin_width=5):
        
        #------Set attributes of the class-------------------
        self.fn_list = filenamelst
        self.fignum = fignum
        self.font_size = font_size
        self.dpi = dpi
        self.thetar = thetar
        self.plot_type = plot_type
        self.plot_range = plot_range
        self.period_tolerance = period_tolerance
        self.plot_tipper = plot_tipper
        self.pt_error_floor = pt_error_floor
        self.fold = fold
        self.bin_width = bin_width
        
        try:
            self.text_pad = text_dict['pad']
        except KeyError:
            self.text_pad = 0.6
            
        try:
            self.text_size = text_dict['size']
        except KeyError:
            self.text_size = self.font_size
        
        #make a dictionary for plotting titles
        self.title_dict = {}
        self.title_dict[-5] = '10$^{-5}$--10$^{-4}$s'
        self.title_dict[-4] = '10$^{-4}$--10$^{-3}$s'
        self.title_dict[-3] = '10$^{-3}$--10$^{-2}$s'
        self.title_dict[-2] = '10$^{-2}$--10$^{-1}$s'
        self.title_dict[-1] = '10$^{-1}$--10$^{0}$s'
        self.title_dict[0] = '10$^{0}$--10$^{1}$s'
        self.title_dict[1] = '10$^{1}$--10$^{2}$s'
        self.title_dict[2] = '10$^{2}$--10$^{3}$s'
        self.title_dict[3] = '10$^{3}$--10$^{4}$s'
        self.title_dict[4] = '10$^{4}$--10$^{5}$s'
        self.title_dict[5] = '10$^{5}$--10$^{6}$s'
        
        self.plot_yn = plot_yn
        if self.plot_yn=='y':
            self.plot()
            
            
    def plot(self):
        
        plt.rcParams['font.size']=self.font_size
        plt.rcParams['figure.subplot.left']=.07
        plt.rcParams['figure.subplot.right']=.98
        plt.rcParams['figure.subplot.bottom']=.09
        plt.rcParams['figure.subplot.top']=.90
        plt.rcParams['figure.subplot.wspace']=.2
        plt.rcParams['figure.subplot.hspace']=.4   
        
        bw = self.bin_width
        
        if self.fold==True:
            histrange=(-180,180)
        elif self.fold==False:
            histrange=(0,360)
            
        #set empty lists that will hold dictionaries with keys as the period
        invlst=[]
        ptlst=[]
        tiprlst=[]
        
        #initialize some parameters
        nc=len(self.fn_list)
        nt=0
        kk=0
        
        for dd,edi in enumerate(self.fn_list):
            #read in the edi files
            z1 = Z.Z(edi)
            
            #--> set the period
            period = z1.period
        
            #get maximum length of periods
            if len(period)>nt:
                nt = len(period)
                
            #-----------get strike angle from invariants-----------------------
            zinv = z1.getInvariants(thetar=self.thetar)
            
            #add 90 degrees because invariants assume 0 is north, but plotting 
            #assumes that 90 is north and measures clockwise, thus the negative
            #because the strike angle from invariants is measured 
            #counter-clockwise
            
            zs = 90-zinv.strike
            
            #fold so the angle goes from 0 to 180
            if self.fold==True:
                #for plotting put the NW angles into the SE quadrant 
                zs[np.where(zs>90)] = zs[np.where(zs>90)]-180
                zs[np.where(zs<-90)] = zs[np.where(zs<-90)]+180
            
            #leave as the total unit circle 0 to 360
            elif self.fold==False:
                zs[np.where(zs<0)] = zs[np.where(zs<0)]+360
                #zs = 360-zs
            
            #make a dictionary of strikes with keys as period
            mdictinv = dict([(ff,jj) for ff,jj in zip(z1.period,zs)])
            invlst.append(mdictinv)
        
            #------------get strike from phase tensor strike angle---------------
            pt = z1.getPhaseTensor(thetar=self.thetar)
            az = pt.azimuth
            azerr = pt.azimuthvar
            
            #don't need to add 90 because pt assumes 90 is north and 
            #measures clockwise.
            
            #put an error max on the estimation of strike angle
            if self.pt_error_floor:
                az[np.where(azerr>self.pt_error_floor)] = 0.0
            
            #fold so the angle goes from 0 to 180
            if self.fold==True:
                az[np.where(az>90)] = az[np.where(az>90)]-180
                az[np.where(az<-90)] = az[np.where(az<-90)]+180
            
            #leave as the total unit circle 0 to 360
            elif self.fold==False:
                az[np.where(az<0)] = az[np.where(az<0)]+360
                print np.where(az>360)
            
            #make a dictionary of strikes with keys as period
            mdictpt = dict([(ff,jj) for ff,jj in zip(z1.period,az)])
            ptlst.append(mdictpt)
            
            #-----------get tipper strike------------------------------------
            tip = z1.getTipper(thetar=self.thetar)
            
            #needs to be negative because measures clockwise
            tipr = -tip.anglereal
            
            tipr[np.where(tipr==180.)] = 0.0
            
            #fold so the angle goes from 0 to 180
            if self.fold==True:
                tipr[np.where(tipr>90)] = tipr[np.where(tipr>90)]-180
                tipr[np.where(tipr<-90)] = tipr[np.where(tipr<-90)]+180
            
            #leave as the total unit circle 0 to 360
            elif self.fold==False:
                tipr[np.where(tipr<0)] = tipr[np.where(tipr<0)]+360
                tipr[np.where(tipr==360.0)] = 0.0
            
            #make a dictionary of strikes with keys as period
            tiprdict = dict([(ff,jj) for ff,jj in zip(z1.period,tipr)])
            tiprlst.append(tiprdict)

        #--> get min and max period
        maxper = np.max([np.max(mm.keys()) for mm in invlst])
        minper = np.min([np.min(mm.keys()) for mm in ptlst])
        
        #make empty arrays to put data into for easy manipulation
        medinv = np.zeros((nt,nc))
        medpt = np.zeros((nt,nc))
        medtipr = np.zeros((nt,nc))
        
        #make a list of periods from the longest period list
        plst = np.logspace(np.log10(minper),np.log10(maxper),num=nt,base=10)
        pdict = dict([(ii,jj) for jj,ii in enumerate(plst)])
        
        self._plst = plst
        
        #put data into arrays
        for ii,mm in enumerate(invlst):
            mperiod=mm.keys()
            for jj,mp in enumerate(mperiod):
                for kk in pdict.keys():
                    if mp>kk*(1-self.period_tolerance) and \
                         mp<kk*(1+self.period_tolerance):
                        ll = pdict[kk]
                        medinv[ll,ii] = invlst[ii][mp]
                        medpt[ll,ii] = ptlst[ii][mp]
                        medtipr[ll,ii] = tiprlst[ii][mp]
                    else:
                        pass

        #make the arrays local variables                    
        self._medinv = medinv
        self._medpt = medpt
        self._medtp = medtipr
            
            
        #-----Plot Histograms of the strike angles-----------------------------
        if self.plot_range=='data':
            brange=np.arange(np.floor(np.log10(minper)),
                             np.ceil(np.log10(maxper)),1)
        else:
            brange=np.arange(np.floor(self.plot_range[0]),
                             np.ceil(self.plot_range[1]),1)
                             
        self._brange = brange
        
        
        #font dictionary
        fd={'size':self.font_size,'weight':'normal'}
        
        #------------------plot indivdual decades------------------------------
        if self.plot_type==1:
            #plot specs
            plt.rcParams['figure.subplot.hspace'] = .3
            plt.rcParams['figure.subplot.wspace'] = .3
            
            self.fig = plt.figure(self.fignum, dpi=self.dpi)
            plt.clf()
            nb = len(brange)
            for jj,bb in enumerate(brange,1):
                #make subplots for invariants and phase tensor azimuths
                if self.plot_tipper=='n':
                    self.axhinv = self.fig.add_subplot(2, nb, jj, polar=True)
                    self.axhpt = self.fig.add_subplot(2, nb, jj+nb, polar=True)
                    axlst = [self.axhinv, self.axhpt]
                    
                if self.plot_tipper=='y':
                    self.axhinv = self.fig.add_subplot(3, nb, jj, polar=True)
                    self.axhpt = self.fig.add_subplot(3, nb, jj+nb, polar=True)
                    self.axhtip = self.fig.add_subplot(3, nb, jj+2*nb, polar=True)
                    axlst = [self.axhinv, self.axhpt, self.axhtip]
                
                #make a list of indicies for each decades    
                binlst=[]
                for ii,ff in enumerate(plst):
                    if ff>10**bb and ff<10**(bb+1):
                        binlst.append(ii)
                
                #extract just the subset for each decade
                hh = medinv[binlst,:]
                gg = medpt[binlst,:]
                if self.plot_tipper=='y':
                    tr = medtipr[binlst,:]
                    
                    #compute the historgram for the tipper strike
                    trhist = np.histogram(tr[np.nonzero(tr)].flatten(),
                                          bins=360/bw,
                                          range=histrange)
                    
                    #make a bar graph with each bar being width of bw degrees                               
                    bartr = self.axhtip.bar((trhist[1][:-1])*np.pi/180,
                                            trhist[0],
                                            width=bw*np.pi/180)
                    
                    #set color of the bars according to the number in that bin
                    #tipper goes from dark blue (low) to light blue (high)                        
                    for cc,bar in enumerate(bartr):
                        fc=float(trhist[0][cc])/trhist[0].max()*.9
                        bar.set_facecolor((0, 1-fc/2, fc))
                            
                
                #estimate the histogram for the decade for invariants and pt
                invhist = np.histogram(hh[np.nonzero(hh)].flatten(),
                                       bins=360/bw,
                                       range=histrange)
                pthist = np.histogram(gg[np.nonzero(gg)].flatten(),
                                      bins=360/bw,
                                      range=histrange)
                
                #plot the histograms    
                self.barinv = self.axhinv.bar((invhist[1][:-1])*np.pi/180,
                                         invhist[0],
                                         width=bw*np.pi/180)
                                         
                self.barpt = self.axhpt.bar((pthist[1][:-1])*np.pi/180,
                                       pthist[0],
                                       width=bw*np.pi/180)
                
                #set the color of the bars according to the number in that bin
                #invariants go from purple (low) to red (high)
                for cc,bar in enumerate(self.barinv):
                    fc = float(invhist[0][cc])/invhist[0].max()*.8
                    bar.set_facecolor((fc, 0, 1-fc))
                    
                #pt goes from green (low) to orange (high)
                for cc,bar in enumerate(self.barpt):
                    fc=float(pthist[0][cc])/pthist[0].max()*.8
                    bar.set_facecolor((fc,1-fc,0))
                    
                #make axis look correct with N to the top at 90.
                for aa,axh in enumerate(axlst):
                    #set multiple locator to be every 15 degrees
                    axh.xaxis.set_major_locator(MultipleLocator(30*np.pi/180))
                    
                    #set labels on the correct axis
                    axh.xaxis.set_ticklabels(['E','','',
                                              'N','','',
                                              'W','','',
                                              'S','',''])
                    #make a light grid
                    axh.grid(alpha=.25)
                    
                    #properties for the invariants
                    if aa==0:
                        #limits need to be rotate 90 counter clockwise because
                        #we already rotated by 90 degrees so the range is 
                        #from -90 to 270 with -90 being east
                        axh.set_xlim(-90*np.pi/180,270*np.pi/180)
                        
                        #label the plot with the mode value of strike
                        #need to subtract 90 again because the histogram is
                        #for ploting 0 east, 90 north measuring 
                        #counter-clockwise
                        invmode = 90-invhist[1][np.where(
                                           invhist[0]==invhist[0].max())[0][0]]
                                           
                        if invmode<0:
                            invmode += 360
                                           
                        axh.text(np.pi,axh.get_ylim()[1]*self.text_pad,
                                 '{0:.1f}$^o$'.format(invmode),
                                  horizontalalignment='center',
                                  verticalalignment='baseline',
                                  fontdict={'size':self.text_size},
                                  bbox={'facecolor':(.9,0,.1),'alpha':.25})
                        
                        #print out the statistics of the strike angles 
                        invmedian = 90-np.median(hh[np.nonzero(hh)])
                        if invmedian<0:
                            invmedian += 360
                        invmean = 90-np.mean(hh[np.nonzero(hh)])
                        if invmean<0:
                            invmean += 360
                            
                        print '-----Period Range {0:.3g} to {1:.3g} (s)-----'.format(10**bb,
                              10**(bb+1))
                             
                        print '   *Z-Invariants:  median={0:.1f} mode={1:.1f} mean={2:.1f}'.format(
                                invmedian,
                                invmode,
                                invmode) 
                                
                        #--> set title of subplot
                        axh.set_title(self.title_dict[bb],fontdict=fd,
                                      bbox={'facecolor':'white','alpha':.25})
                        
                        #--> set the title offset
                        axh.titleOffsetTrans._t=(0,.1)
            
                    #set pt axes properties
                    elif aa==1:
                        #limits go from -180 to 180 as that is how the angle
                        #is calculated
                        axh.set_xlim(-180*np.pi/180,180*np.pi/180)
                        
                        #label plot with the mode of the strike angle
                        ptmode = 90-pthist[1][np.where(
                                             pthist[0]==pthist[0].max())[0][0]]
                                             
                        if ptmode<0:
                            ptmode+=360
                            
                        ptmedian = 90-np.median(gg[np.nonzero(gg)])
                        if ptmedian<0:
                            ptmedian += 360
                            
                        ptmean = 90-np.mean(gg[np.nonzero(gg)])
                        if ptmean<0:
                            ptmean += 360
                            
                        axh.text(np.pi,axh.get_ylim()[1]*self.text_pad,
                                 '{0:.1f}$^o$'.format(ptmode),
                                  horizontalalignment='center',
                                  verticalalignment='baseline',
                                  fontdict={'size':self.text_size},
                                  bbox={'facecolor':(.9,.9,0),'alpha':.25})
                                  
                        #print out the results for the strike angles
                        
                        print '   *PT Strike:     median={0:.1f} mode={1:.1f} mean={2:.1f}'.format(
                                ptmedian,
                                ptmode,
                                ptmean)
                        
                        if self.plot_tipper!='y':
                            print '\n'
                            
                        if nb>5:
                            axh.set_title(self.title_dict[bb],fontdict=fd,
                                      bbox={'facecolor':'white','alpha':.25})
                                      
                    #set tipper axes properties
                    elif aa==2:
                        #limits go from -180 to 180
                        axh.set_xlim(-180*np.pi/180,180*np.pi/180)
                        
                        #label plot with mode
                        tpmode = 90-trhist[1][np.where(
                                             trhist[0]==trhist[0].max())[0][0]]
                        
                        if tpmode<0:
                            tpmode+=360.
                            
                        tpmedian = 90-np.median(tr[np.nonzero(tr)])
                        if tpmedian <0:
                            tpmedian += 360
                            
                        tpmean = 90-np.mean(tr[np.nonzero(tr)])
                        if tpmean<0:
                            tpmean += 360
                        
                        axh.text(np.pi,axh.get_ylim()[1]*self.text_pad,
                                 '{0:.1f}$^o$'.format(tpmode),
                                  horizontalalignment='center',
                                  verticalalignment='baseline',
                                  fontdict={'size':self.text_size},
                                  bbox={'facecolor':(0,.1,.9),'alpha':.25})
                        
                        #print out statistics for strike angle
                        print '   *Tipper Strike: median={0:.1f} mode={1:.1f} mean={2:.1f}'.format(
                                tpmedian,
                                tpmode,
                                tpmode) 
                        print '\n'
                        if nb>5: 
                            axh.set_title(self.title_dict[bb],fontdict=fd,
                                        bbox={'facecolor':'white','alpha':.25})
                    
                    #set plot labels
                    if jj==1:
                        if aa==0:
                            axh.set_ylabel('Strike (Z)',fontdict=fd,
                                           labelpad=self.font_size,
                                           bbox={'facecolor':(.9,0,.1),
                                                 'alpha':0.25})
                        elif aa==1:
                            axh.set_ylabel('PT Azimuth',fontdict=fd,
                                           labelpad=self.font_size,
                                           bbox={'facecolor':(.9,.9,0),
                                                 'alpha':.25})
                        elif aa==2:
                            axh.set_ylabel('Tipper Strike',fd,
                                           labelpad=self.font_size,
                                           bbox={'facecolor':(0,.1,.9),
                                                 'alpha':0.25})
                    
                    plt.setp(axh.yaxis.get_ticklabels(),visible=False)
                    
            print 'Note: North is assumed to be 0 and the strike angle is measured'+\
                  'clockwise positive.'
            
            plt.show()
        
        #------------------Plot strike angles for all period ranges--------------------
        elif self.plot_type==2:
            #plot specs
            plt.rcParams['figure.subplot.left']=.07
            plt.rcParams['figure.subplot.right']=.98
            plt.rcParams['figure.subplot.bottom']=.100
            plt.rcParams['figure.subplot.top']=.88
            plt.rcParams['figure.subplot.hspace']=.3
            plt.rcParams['figure.subplot.wspace']=.2
            
            self.fig = plt.figure(self.fignum,dpi=self.dpi)
            plt.clf()
            #make subplots for invariants and phase tensor azimuths
            if self.plot_tipper=='n':
                self.axhinv=self.fig.add_subplot(1,2,1,polar=True)
                self.axhpt=self.fig.add_subplot(1,2,2,polar=True)
                axlst=[self.axhinv, self.axhpt]
            else:
                self.axhinv=self.fig.add_subplot(1,3,1,polar=True)
                self.axhpt=self.fig.add_subplot(1,3,2,polar=True)
                self.axhtip=self.fig.add_subplot(1,3,3,polar=True)
                axlst=[self.axhinv, self.axhpt, self.axhtip]
            
            #make a list of indicies for each decades    
            binlst=[pdict[ff] for ff in plst 
                    if ff>10**brange.min() and ff<10**brange.max()]
            
            #extract just the subset for each decade
            hh=medinv[binlst,:]
            gg=medpt[binlst,:]
            
            #estimate the histogram for the decade for invariants and pt
            invhist=np.histogram(hh[np.nonzero(hh)].flatten(),
                                 bins=360/bw,
                                 range=histrange)
            pthist=np.histogram(gg[np.nonzero(gg)].flatten(),
                                bins=360/bw,
                                range=histrange)
            
            #plot the histograms    
            self.barinv = self.axhinv.bar((invhist[1][:-1])*np.pi/180,
                                          invhist[0],
                                          width=bw*np.pi/180)
                                          
            self.barpt = self.axhpt.bar((pthist[1][:-1])*np.pi/180,
                                        pthist[0],
                                        width=bw*np.pi/180)
            
            #set color of invariants from purple (low) to red (high count)
            for cc,bar in enumerate(self.barinv):
                fc = float(invhist[0][cc])/invhist[0].max()*.8
                bar.set_facecolor((fc,0,1-fc))
            
            #set color of pt from green (low) to orange (high count)
            for cc,bar in enumerate(self.barpt):
                fc = float(pthist[0][cc])/pthist[0].max()*.8
                bar.set_facecolor((fc,1-fc,0))
            
            #plot tipper if desired
            if self.plot_tipper=='y':
                    tr = self._medtp[binlst,:]
                    
                    trhist = np.histogram(tr[np.nonzero(tr)].flatten(),
                                          bins=360/bw,
                                          range=histrange)
                                          
                    self.bartr = self.axhtip.bar((trhist[1][:-1])*np.pi/180,
                                                 trhist[0],
                                                 width=bw*np.pi/180)
                                                 
                    #set tipper color from dark blue (low) to light blue (high)
                    for cc,bar in enumerate(self.bartr):
                        fc=float(trhist[0][cc])/trhist[0].max()*.9
                        bar.set_facecolor((0,1-fc/2,fc))
                        
            #make axis look correct with N to the top at 90.
            for aa,axh in enumerate(axlst):
                #set major ticks to be every 15 degrees
                axh.xaxis.set_major_locator(MultipleLocator(30*np.pi/180))
                
                #set a light grid                
                axh.grid(alpha=0.25)

                #set tick labels to be invisible                
                plt.setp(axh.yaxis.get_ticklabels(),visible=False)

                #place the correct label at the cardinal directions
                axh.xaxis.set_ticklabels(['E','','',
                                          'N','','',
                                          'W','','',
                                          'S','',''])
                                          
                #set invariant axes properties
                if aa==0:
                    axh.set_ylim(0,invhist[0].max())
                    
                    invmode = 90-invhist[1][np.where(
                                           invhist[0]==invhist[0].max())[0][0]]
                                           
                    if invmode<0:
                            invmode+=360
                            
                    axh.text(170*np.pi/180,axh.get_ylim()[1]*.65,
                             '{0:.1f}$^o$'.format(invmode),
                              horizontalalignment='center',
                              verticalalignment='baseline',
                              fontdict={'size':self.font_size},
                              bbox={'facecolor':(.9,0,.1),'alpha':.25})

                    #print out the statistics of the strike angles 
                    invmedian = 90-np.median(hh[np.nonzero(hh)])
                    if invmedian<0:
                        invmedian += 360
                    invmean = 90-np.mean(hh[np.nonzero(hh)])
                    if invmean<0:
                        invmean += 360
                        
                    print '-----Period Range {0:.3g} to {1:.3g} (s)-----'.format(10**brange[0],
                          10**brange[-1])
                         
                    print '   *Z-Invariants:  median={0:.1f} mode={1:.1f} mean={2:.1f}'.format(
                            invmedian,
                            invmode,
                            invmode)
                            
                    axh.set_title('Strike (Z)',fontdict=fd,
                                   bbox={'facecolor':(.9,0,.1),'alpha':0.25})
                                   
                    
        
                #set pt axes properties
                elif aa==1:
                    axh.set_ylim(0,pthist[0].max())
                    
                    ptmode = 90-pthist[1][np.where(
                                             pthist[0]==pthist[0].max())[0][0]]
                                             
                    if ptmode<0:
                            ptmode+=360
                            
                    if ptmode<0:
                            ptmode+=360
                            
                    ptmedian = 90-np.median(gg[np.nonzero(gg)])
                    if ptmedian<0:
                        ptmedian += 360
                        
                    ptmean = 90-np.mean(gg[np.nonzero(gg)])
                    if ptmean<0:
                        ptmean += 90
                            
                    axh.text(170*np.pi/180,axh.get_ylim()[1]*.65,
                             '{0:.1f}$^o$'.format(ptmode),
                              horizontalalignment='center',
                              verticalalignment='baseline',
                              fontdict={'size':self.text_size},
                              bbox={'facecolor':(.9,.9,0),'alpha':0.25})
                              
                    #print results of strike analysis for pt
                    print '   *PT Strike:     median={0:.1f} mode={1:.1f} mean={2:.1f}'.format(
                            ptmedian,
                            ptmode,
                            ptmean)
                    
                    if self.plot_tipper!='y':
                        print '\n'
                        
                    axh.set_title('PT Azimuth',fontdict=fd,
                                   bbox={'facecolor':(.9,.9,0),'alpha':0.25})
                
                #set tipper axes properties
                elif aa==2:
                    axh.set_ylim(0,trhist[0].max())
                    
                    tpmode = 90-trhist[1][np.where(
                                             trhist[0]==trhist[0].max())[0][0]]
                    
                    if tpmode<0:
                            tpmode+=360
                            
                    tpmedian = 90-np.median(tr[np.nonzero(tr)])
                    if tpmedian <0:
                        tpmedian += 360
                        
                    tpmean = 90-np.mean(tr[np.nonzero(tr)])
                    if tpmean<0:
                        tpmean += 360
                                             
                    axh.text(170*np.pi/180,axh.get_ylim()[1]*.65,
                             '{0:.1f}$^o$'.format(tpmode),
                              horizontalalignment='center',
                              verticalalignment='baseline',
                              fontdict={'size':self.text_size},
                              bbox={'facecolor':(0,.1,.9),'alpha':0.25})
                    print '   *Tipper Stike:  median={0:.1f} mode={1:.1f} mean={2:.1f}\n'.format(
                            tpmedian,
                            tpmode,
                            tpmode)
                
                    axh.set_title('Tipper Strike',fontdict=fd,
                                   bbox={'facecolor':(0,.1,.9),'alpha':0.25})
                                   
                #move title up a little to make room for labels
                axh.titleOffsetTrans._t=(0,.15)
                
            #remind the user what the assumptions of the strike angle are
            print 'Note: North is assumed to be 0 and the strike angle is '+\
                  'measured clockwise positive.'
            
            plt.show()
            
    def save_plot(self, save_fn, file_format='pdf', 
                  orientation='portrait', fig_dpi=None, close_plot='y'):
        """
        save_plot will save the figure to save_fn.
        
        Arguments:
        -----------
        
            **save_fn** : string
                          full path to save figure to, can be input as
                          * directory path -> the directory path to save to
                            in which the file will be saved as 
                            save_fn/station_name_ResPhase.file_format
                            
                          * full path -> file will be save to the given 
                            path.  If you use this option then the format
                            will be assumed to be provided by the path
                            
            **file_format** : [ pdf | eps | jpg | png | svg ]
                              file type of saved figure pdf,svg,eps... 
                              
            **orientation** : [ landscape | portrait ]
                              orientation in which the file will be saved
                              *default* is portrait
                              
            **fig_dpi** : int
                          The resolution in dots-per-inch the file will be
                          saved.  If None then the dpi will be that at 
                          which the figure was made.  I don't think that 
                          it can be larger than dpi of the figure.
                          
            **close_plot** : [ y | n ]
                             * 'y' will close the plot after saving.
                             * 'n' will leave plot open
                          
        :Example: ::
            
            >>> # to save plot as jpg
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotPhaseTensorMaps(edilst,freqspot=10)
            >>> p1.save_plot(r'/home/MT', file_format='jpg')
            'Figure saved to /home/MT/PTMaps/PTmap_phimin_10Hz.jpg'
            
        """
        
        if fig_dpi==None:
            fig_dpi = self.dpi
            
        if os.path.isdir(save_fn)==False:
            file_format = save_fn[-3:]
            self.fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                             orientation=orientation)
            plt.clf()
            plt.close(self.fig)
            
        else:
            if not os.path.exists(save_fn):
                os.mkdir(save_fn)
                
            save_fn = os.path.join(save_fn,'StrikeAnalysis_'+file_format)
            self.fig.savefig(save_fn, dpi=fig_dpi, format=file_format,
                        orientation=orientation)
                        
        if close_plot=='y':
            plt.clf()
            plt.close(self.fig)
        
        else:
            pass
        
        self.fig_fn = save_fn
        print 'Saved figure to: '+self.fig_fn

    def update_plot(self):
        """
        update any parameters that where changed using the built-in draw from
        canvas.  
        
        Use this if you change an of the .fig or axes properties
        
        :Example: ::
            
            >>> # to change the grid lines to only be on the major ticks
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> [ax.grid(True, which='major') for ax in [p1.axr,p1.axp]]
            >>> p1.update_plot()
        
        """

        self.fig.canvas.draw()
        
    def redraw_plot(self):
        """
        use this function if you updated some attributes and want to re-plot.
        
        :Example: ::
            
            >>> # change the color and marker of the xy components
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> p1.xy_color = (.5,.5,.9)
            >>> p1.xy_marker = '*'
            >>> p1.redraw_plot()
        """
        
        plt.close(self.fig)
        self.plot()
        
    def __str__(self):
        """
        rewrite the string builtin to give a useful message
        """
        
        return "Plots phase tensor maps for one frequency"
        
    def writeTextFiles(self, save_path=None):
        """
        Saves the strike information as a text file.
        """
        
        #check to see if the strikes have been calculated
        try:
            self.bin_width
        except AttributeError:
            self.plot()
        
        #get the path to save the file to
        if save_path==None:
            svpath = os.path.dirname(self.fn_list[0])
        
        else:
            svpath = save_path
        
        #set 
        if self.fold==True:
            histrange=(-180,180)
            
        elif self.fold==False:
            histrange=(0,360)
            
        #set the bin width
        bw = self.bin_width

        slstinv = [['station']]            
        slstpt = [['station']]            
        slsttip = [['station']]            
            
        #calculate the strikes for the different period bands
        for jj,bb in enumerate(self._brange):
            tstr = self.title_dict[bb].replace('$','')
            tstr = tstr.replace('{','').replace('}','').replace('^','e')
            tstr = tstr.replace('s', '(s)')
            slstinv[0].append(tstr)
            slstpt[0].append(tstr)
            slsttip[0].append(tstr)
            
            #calculate the strike for the different period bands per station
            for kk,fn in enumerate(self.fn_list,1):
                z1 = Z.Z(fn)
                
                if jj==0:
                    slstinv.append([z1.station])
                    slstpt.append([z1.station])
                    slsttip.append([z1.station])
                
                zinv = z1.getInvariants()
                pt = z1.getPhaseTensor()
                tp = z1.getTipper()
                
                bnlst = []
                for nn,per in enumerate(z1.period):
                    if per>10**bb and per<10**(bb+1):
                        bnlst.append(nn)
                
                #---> strike from invariants
                zs = 90-zinv.strike[bnlst]
                #fold so the angle goes from 0 to 180
                if self.fold==True:
                    #for plotting put the NW angles into the SE quadrant 
                    zs[np.where(zs>90)] = zs[np.where(zs>90)]-180
                    zs[np.where(zs<-90)] = zs[np.where(zs<-90)]+180
                
                #leave as the total unit circle 0 to 360
                elif self.fold==False:
                    pass
                
                zshist = np.histogram(zs[np.nonzero(zs)].flatten(),
                                          bins=360/bw,
                                          range=histrange)
                
                #==============================================================
                # For putting the values into a useful text file
                # need to subtract 90 from the values to put them into 
                # coordinates where north is 0 and east is 90, which is 
                # different from plotting where east in the plotting function
                # is equal to 0 and north is 90, measuring counter-clockwise
                #==============================================================
                
                #==> compute mean
                invmean=90-zs.mean()
                if invmean<0: invmean+=360
                invmed=90-np.median(zs)
                
                #==> compute median
                if invmed<0: invmed+=360
                
                #==> compute mode
                invmode=90-zshist[1][np.where(
                                           zshist[0]==zshist[0].max())[0][0]]
                if invmode<0: invmode+=360
                          
                #==> append to list
                slstinv[kk].append((invmean,
                                    invmed,
                                    invmode))
                
                #---> strike from phase tensor
                az = pt.azimuth[bnlst]
                #fold so the angle goes from 0 to 180
                if self.fold==True:
                    az[np.where(az>90)] = az[np.where(az>90)]-180
                    az[np.where(az<-90)] = az[np.where(az<-90)]+180
                
                #leave as the total unit circle 0 to 360
                elif self.fold==False:
                    az[np.where(az<0)] = az[np.where(az<0)]+360
                
                #==> compute mean
                ptmean1 = 90-az.mean()
                if ptmean1<0: ptmean1 += 360
                
                #==> compute median
                ptmed1 = 90-np.median(az)
                if ptmed1<0: ptmed1 += 360
                    
                #==> compute mode
                azhist = np.histogram(az[np.nonzero(az)].flatten(),
                                          bins=360/bw,
                                          range=histrange)
                ptmode1 = 90-azhist[1][np.where(
                                           azhist[0]==azhist[0].max())[0][0]]
                if ptmode1<0: ptmode1 += 360              
                                
                slstpt[kk].append((ptmean1,
                                   ptmed1,
                                   ptmode1))

                #---> strike from tipper
                #needs to be negative because measures clockwise
                tipr = -tp.anglereal[bnlst]
                
                #fold so the angle goes from 0 to 180
                if self.fold==True:
                    tipr[np.where(tipr>90)] = tipr[np.where(tipr>90)]-180
                    tipr[np.where(tipr<-90)] = tipr[np.where(tipr<-90)]+180
                
                #leave as the total unit circle 0 to 360
                elif self.fold==False:
                    tipr[np.where(tipr<0)] = tipr[np.where(tipr<0)]+360
                    
                tphist = np.histogram(tipr[np.nonzero(tipr)].flatten(),
                                          bins=360/bw,
                                          range=histrange)
                                          
                #==> compute mean
                tpmean1 = 90-tipr.mean()
                if tpmean1<0: tpmean1 += 360
                
                #==> compute median
                tpmed1 = 90-np.median(tipr)
                if tpmed1<0: tpmed1 += 360
                
                #==> compute mode
                tpmode1 = 90-tphist[1][np.where(
                                           tphist[0]==tphist[0].max())[0][0]]
                if tpmode1<0: tpmode1 += 360                                           
                                          
                #--> append statistics to list 
                slsttip[kk].append((tpmean1,
                                    tpmed1,
                                    tpmode1))
 
            #make a list of indicies for each decades    
            binlst=[]
            for ii,ff in enumerate(self._plst):
                if ff>10**bb and ff<10**(bb+1):
                    binlst.append(ii)
            
            #extract just the subset for each decade
            hh = self._medinv[binlst,:]
            gg = self._medpt[binlst,:]
            tr = self._medtp[binlst,:]

            #estimate the histogram for the decade for invariants and pt
            invhist = np.histogram(hh[np.nonzero(hh)].flatten(),
                                   bins=360/bw,
                                   range=histrange)
            pthist = np.histogram(gg[np.nonzero(gg)].flatten(),
                                  bins=360/bw,
                                  range=histrange)
                                  
            trhist = np.histogram(tr[np.nonzero(tr)].flatten(),
                                  bins=360/bw,
                                  range=histrange)
            
            #--> include the row for mean, median and mode for each parameter
            if jj==0:                      
                slstinv.append(['mean'])
                slstinv.append(['median'])
                slstinv.append(['mode'])
                
                slstpt.append(['mean'])
                slstpt.append(['median'])
                slstpt.append(['mode'])
                
                slsttip.append(['mean'])
                slsttip.append(['median'])
                slsttip.append(['mode'])

            #--> compute mean, median and mode for invariants
            #==> mean
            imean = 90-np.mean(hh[np.nonzero(hh)])
            if imean<0: imean += 360
            
            #==> median
            imed = 90-np.median(hh[np.nonzero(hh)])
            if imed<0: imed +=360
            
            #==> mode
            imode = 90-invhist[1][np.where(
                                invhist[0]==invhist[0].max())[0][0]]
            if imode<0: imode +=360
                     
            #--> add them to the list of estimates
            slstinv[kk+1].append(imean)
            slstinv[kk+2].append(imed)
            slstinv[kk+3].append(imode)
            
            #--> compute pt statistics
            #==> mean
            ptmean = 90-np.mean(gg[np.nonzero(gg)])
            if ptmean<0: ptmean=np.mean(gg[np.nonzero(gg)])
            
            #==> median
            ptmed = 90-np.median(gg[np.nonzero(gg)])
            if ptmed<0: ptmed +=360
            
            #==> mode
            ptmode = 90-pthist[1][np.where(
                                pthist[0]==pthist[0].max())[0][0]]
            if ptmode<0: ptmode +=360
                                
            #--> add the statistics to the parameter list
            slstpt[kk+1].append(ptmean)
            slstpt[kk+2].append(ptmed)
            slstpt[kk+3].append(ptmode)
            
            #--> compute tipper statistics
            #==> mean            
            tpmean = 90-np.mean(tipr[np.nonzero(tipr)])
            if tpmean<0: tpmean += 360
            
            #==> median
            tpmed = 90-np.median(tipr[np.nonzero(tipr)])
            if tpmed<0: tpmed +=360
            
            #==> mode
            tpmode = 90-trhist[1][np.where(
                                trhist[0]==trhist[0].max())[0][0]]
            if tpmode<0: tpmode +=360
                            
            #--> add the statistics to parameter list
            slsttip[kk+1].append(tpmean)
            slsttip[kk+2].append(tpmed)
            slsttip[kk+3].append(tpmode)
                                            
        invfid = file(os.path.join(svpath,'Strike.invariants'),'w')        
        ptfid = file(os.path.join(svpath,'Strike.pt'),'w')  
        tpfid = file(os.path.join(svpath,'Strike.tipper'),'w')
        
        #---> write strike from the invariants
        #==> mean
        invfid.write('-'*20+'MEAN'+'-'*20+'\n')
        for ii,l1 in enumerate(slstinv):
            for jj,l2 in enumerate(l1):
                if ii==0:
                    invfid.write('{0:^16}'.format(l2))
                else:
                    if jj==0:
                        invfid.write('{0:>16}'.format(l2+' '*6))
                    else:
                        try:
                            invfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2[0])))
                        except IndexError:
                            invfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2)))
            invfid.write('\n')
        
        #==> median
        invfid.write('-'*20+'MEDIAN'+'-'*20+'\n')
        for ii,l1 in enumerate(slstinv):
            for jj,l2 in enumerate(l1):
                if ii==0:
                    invfid.write('{0:^16}'.format(l2))
                else:
                    if jj==0:
                        invfid.write('{0:>16}'.format(l2+' '*6))
                    else:
                        try:
                            invfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2[1])))
                        except IndexError:
                            invfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2)))
            invfid.write('\n')
        
        #==> mode
        invfid.write('-'*20+'MODE'+'-'*20+'\n')
        for ii,l1 in enumerate(slstinv):
            for jj,l2 in enumerate(l1):
                if ii==0:
                    invfid.write('{0:^16}'.format(l2))
                else:
                    if jj==0:
                        invfid.write('{0:>16}'.format(l2+' '*6))
                    else:
                        try:
                            invfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2[2])))
                        except IndexError:
                            invfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2)))
            invfid.write('\n')
        invfid.close()
        
        
        #---> write the phase tensor text files
        ptfid.write('-'*20+'MEAN'+'-'*20+'\n')
        for ii,l1 in enumerate(slstpt):
            for jj,l2 in enumerate(l1):
                if ii==0:
                    ptfid.write('{0:^16}'.format(l2))
                else:
                    if jj==0:
                        ptfid.write('{0:>16}'.format(l2+' '*6))
                    else:
                        try:
                            ptfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2[0])))
                        except IndexError:
                            ptfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2)))
            ptfid.write('\n')
            
        ptfid.write('-'*20+'MEDIAN'+'-'*20+'\n')
        for ii,l1 in enumerate(slstpt):
            for jj,l2 in enumerate(l1):
                if ii==0:
                    ptfid.write('{0:^16}'.format(l2))
                else:
                    if jj==0:
                        ptfid.write('{0:>16}'.format(l2+' '*6))
                    else:
                        try:
                            ptfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2[1])))
                        except IndexError:
                            ptfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2)))
            ptfid.write('\n')
            
        ptfid.write('-'*20+'MODE'+'-'*20+'\n')
        for ii,l1 in enumerate(slstpt):
            for jj,l2 in enumerate(l1):
                if ii==0:
                    ptfid.write('{0:^16}'.format(l2))
                else:
                    if jj==0:
                        ptfid.write('{0:>16}'.format(l2+' '*6))
                    else:
                        try:
                            ptfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2[2])))
                        except IndexError:
                            ptfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2)))
            ptfid.write('\n')
        ptfid.close()
        
        
        #---> write the tipper text files
        tpfid.write('-'*20+'MEAN'+'-'*20+'\n')
        for ii,l1 in enumerate(slsttip):
            for jj,l2 in enumerate(l1):
                if ii==0:
                    tpfid.write('{0:^16}'.format(l2))
                else:
                    if jj==0:
                        tpfid.write('{0:>16}'.format(l2+' '*6))
                    else:
                        try:
                            tpfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2[0])))
                        except IndexError:
                            tpfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2)))
            tpfid.write('\n')
            
        tpfid.write('-'*20+'MEDIAN'+'-'*20+'\n')
        for ii,l1 in enumerate(slsttip):
            for jj,l2 in enumerate(l1):
                if ii==0:
                    tpfid.write('{0:^16}'.format(l2))
                else:
                    if jj==0:
                        tpfid.write('{0:>16}'.format(l2+' '*6))
                    else:
                        try:
                            tpfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2[1])))
                        except IndexError:
                            tpfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2)))
            tpfid.write('\n')
            
        tpfid.write('-'*20+'MODE'+'-'*20+'\n')
        for ii,l1 in enumerate(slsttip):
            for jj,l2 in enumerate(l1):
                if ii==0:
                    tpfid.write('{0:^16}'.format(l2))
                else:
                    if jj==0:
                        tpfid.write('{0:>16}'.format(l2+' '*6))
                    else:
                        try:
                            tpfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2[2])))
                        except IndexError:
                            tpfid.write('{0:^16}'.format(
                                         '{0: .2f}'.format(l2)))
            tpfid.write('\n')
        tpfid.close()

class PlotTimeSeries(object):
    """
    plot the time series
    """
  


#
#def plotRTpseudoSection(filenamelst,colorkey='rhodet',esize=2,
#                        stretch=.005,colorkeymm=[0,90],stationid=[0,4],
#                        title=None,cbshrink=.8,linedir='ns',fignum=1,rotz=0,
#                        yscale='period',pxy=[8,8],dpi=300):
#    
#    """
#    plotRTpseudoSection(filenamelst,colorkey='beta',esize=2,stretch=
#    .005) will plot a pseudo section of resistivity tensor ellipses given a list of 
#    full path filenames. (Weckmann et al. 2002)
#    
#    **filenamelst** : list of strings
#                          full paths to .edi files to plot
#        
#        **colorkey** : [ 'rhodet' ]
#                       fill color of the ellipses and can be:
#                       * 'rhodet'      -> minimum phase
#                       * more to come
#                       * *Default* is 'rhodet'
#                       
#        **colorkeymm** : tuple (min,max)
#                        min and max of colorkey to which colorbar is normalized
#                        to.  In log10 resistivity
#                        
#        **esize** : float
#                    size of ellipse in map units 
#        
#        **stretch** : float
#                            is a factor that scales the distance from one 
#                            station to the next to make the plot readable.
#                            *Default* is 0.005
#        **linedir** : [ 'ns' | 'ew' ]
#                      predominant direction of profile line
#                      * 'ns' -> North-South Line
#                      * 'ew' -> East-West line
#                      * *Default* is 'ns'
#        
#        **stationid** : tuple or list 
#                        start and stop of station name indicies.  
#                        ex: for MT01dr stationid=(0,4) will be MT01
#        
#        **rotz** : float
#                   angle in degrees to rotate the data clockwise positive.
#                   *Default* is 0
#        
#        **title** : string
#                    figure title added to Phase Tensor + title
#                    
#        **cbshrink** : float
#                       percent to shrink the color bar to fit the image better
#                       *Default* is 0.8 -> 80 percent
#                       
#        **fignum** : int
#                     figure number.  *Default* is 1
#                      
#        **yscale** : [ 'period' | 'frequency' ]
#                     * 'period'    -> plot vertical scale in period
#                     * 'frequency' -> plot vertical scale in frequency
#                     
#    :Example: ::
#        
#        >>> import mtpy.imaging.mtplottools as mtplot
#        >>> import os
#        >>> edipath = r"/home/EDIfiles"
#        >>> edilst = [os.path.join(edipath,edi) for edi in os.listdir(edipath)
#        >>> ...       if edi.find('.edi')]
#        >>> # color by rhodet with a range of 0-4 log10 resistivity
#        >>> mtplot.plotRTpseudoSection(edilst,colorkeymm=(0,4))
#    
#    """
#    
#    fs=int(dpi/30.)
#    plt.rcParams['font.size']=fs
#    plt.rcParams['figure.subplot.left']=.08
#    plt.rcParams['figure.subplot.right']=.98
#    plt.rcParams['figure.subplot.bottom']=.06
#    plt.rcParams['figure.subplot.top']=.96
#    plt.rcParams['figure.subplot.wspace']=.55
#    plt.rcParams['figure.subplot.hspace']=.70
#    #plt.rcParams['font.family']='helvetica'
#    
#    
#    #create a plot instance
#    fig=plt.figure(fignum,pxy,dpi=dpi)
#    ax=fig.add_subplot(1,1,1,aspect='equal')
#    stationlst=[]
#    offsetlst=[]
#    minlst=[]
#    maxlst=[]
#    #plot phase tensor ellipses
#    for ii,fn in enumerate(filenamelst):
#        imp=Z.Z(fn)
#        stationlst.append(mt.station[stationid[0]:stationid[1]])
#        zone,east,north=utm2ll.LLtoUTM(23,mt.lat,mt.lon)
#        
#        if ii==0:
#            east0=east
#            north0=north
#            offset=0.0
#        else:
#            if linedir=='ew': 
#                if east0<east:
#                    offset=np.sqrt((east0-east)**2+(north0-north)**2)
#                elif east0>east:
#                    offset=-1*np.sqrt((east0-east)**2+(north0-north)**2)
#                else:
#                    offset=0
#            elif linedir=='ns':
#                if north0<north:
#                    offset=np.sqrt((east0-east)**2+(north0-north)**2)
#                elif north0>north:
#                    offset=-1*np.sqrt((east0-east)**2+(north0-north)**2)
#                else:
#                    offset=0
#        offsetlst.append(offset)
#        #get phase tensor elements and flip so the top is small periods/high 
#        #frequency
#        rt=imp.getResTensor(thetar=rotz)
#        periodlst=imp.period[::-1]
#        phimax=rt.rhomax[::-1]
#        phimin=rt.rhomin[::-1]
#        azimuth=rt.rhoazimuth[::-1]
#        if colorkey=='rhomin':
#            colorarray=phimin
#        elif colorkey=='rhomax':
#            colorarray=phimax
#        elif colorkey=='rhobeta':
#            colorarray=rt.rhobeta[::-1]
#        elif colorkey=='rhodet':
#            colorarray=rt.rhodet[::-1]
#        n=len(periodlst)
#        minlst.append(min(colorarray))
#        maxlst.append(max(colorarray))
#
#        for jj in range(n):
#            #make sure the ellipses will be visable
#            eheight=phimax[jj]/phimax[jj]*esize
#            ewidth=phimin[jj]/phimax[jj]*esize
#        
#            #create an ellipse scaled by phimin and phimax and oriented along
#            #the azimuth 
#            
#            emax=10*esize
#            if eheight>emax or ewidth>emax:
#                pass
#            else:
#                ellip=Ellipse((offset*stretch,3*jj),width=ewidth,
#                              height=eheight,
#                              angle=azimuth[jj])
#                #color the ellipse as red high conductivity, blue low
#                cvars=abs(np.log10(colorarray[jj]))/colorkeymm[1]
#                if cvars>1:
#                    ellip.set_facecolor((0,0,1))
#                elif cvars<float(colorkeymm[0])/colorkeymm[1] or cvars<0:
#                    ellip.set_facecolor((1,0,0))
#                else:
#                    ellip.set_facecolor((1-cvars,0,cvars))
#                ax.add_artist(ellip)
#            
#    offsetlst=np.array(offsetlst)
#    ax.set_xlim(min(offsetlst)*stretch-4,max(offsetlst)*stretch+4)
#    ax.set_ylim(-5,n*3+5)
#    if yscale=='period':
#        yticklabels=['{0:.3g}'.format(periodlst[ii]) for ii in np.arange(start=0,stop=n,
#                     step=2)]
#        ax.set_ylabel('Period (s)',fontsize=fs+5,fontweight='bold')
#    elif yscale=='frequency':
#        yticklabels=['{0:.4g}'.format(1./periodlst[ii]) for ii in np.arange(start=0,stop=n,
#                     step=2)]
#        ax.set_ylabel('Frequency (Hz)',fontsize=fs+5,fontweight='bold')
#    ax.set_xlabel('Station',fontsize=fs+5,fontweight='bold')
#    
#    if title==None:
#        pass
##        plt.title('Phase Tensor Pseudo Section '+title,fontsize=16)
#    else:
#        ax.set_title(title,fontsize=fs+4)
#    plt.yticks(np.arange(start=0,stop=3*n,step=6),yticklabels)
#    plt.xticks(np.array(offsetlst)*stretch,stationlst)
#    
#    ax.grid(alpha=.25,which='both')
#    
#    print 'Colorkey min = ',min(minlst)
#    print 'Colorkey max = ',max(maxlst)
#    
#    #make colorbar
#    ax2=make_axes(ax,shrink=cbshrink)
#    cb=ColorbarBase(ax2[0],cmap=rtcmap,norm=Normalize(vmin=colorkeymm[0],
#                        vmax=colorkeymm[1]))
#    cb.set_label(colorkey,fontdict={'size':14,'weight':'bold'})
#    
#    plt.show()
#
#def plotPTMaps(edifilelst,freqspot=10,esize=2.0,colorkey='phimin',xpad=.2,
#               ypad=.2,tickstrfmt='%2.2f',cborientation='vertical',
#               colorkeymm=[0,90.],figsave='y',fmt=['png'],rotz=0,pxy=[10,12],
#               galpha=.25,stationid=None,stationpad=.0005,
#               sfdict={'size':12,'weight':'bold'},indarrows='n',
#               cmap='ptcmap',tscale='period',mapscale='latlon',fignum=1,
#               imagefile=None,image_extent=None,refpoint=(0,0),cbshrink=.8,
#               arrowprop={'headheight':0.25,'headwidth':0.25,'linewidth':0.5,
#                          'arrowscale':1},
#               arrowlegend={'placement':'lower right','xborderpad':.2,
#                            'yborderpad':.2,'fontpad':.05,
#                            'fontdict':{'size':10,'weight':'bold'}}):
#    """  
#    Plots phase tensor ellipses in map view from a list of edifiles with full 
#    path.
#    
#    Arguments:
#    ----------
#        **edilst** : list of strings
#                          full paths to .edi files to plot
#                          
#        **freqspot** : position in frequency list for plotting, an integer
#        
#        **esize** : float
#                    size of ellipse in map units 
#        
#        **colorkey** : [ 'phimin' | 'beta' | 'ellipticity' | 'phidet' ]
#                       fill color of the ellipses and can be:
#                       * 'phimin'      -> minimum phase
#                       * 'beta'        -> phase tensor skew angle
#                       * 'ellipticity' -> phase tensor ellipticity
#                       * 'phidet'      -> determinant of the phase tensor
#                       * *Default* is 'phimin'
#                       
#        **colorkeymm** : tuple (min,max)
#                        min and max of colorkey to which colorbar is normalized
#                        to.  In degrees except for ellipticity which is already
#                        normalized.
#                    
#        **xpad** : float
#                   padding in x-direction in map units from furthest ellipses
#        
#        **ypad** : float
#                   padding in y-direction in map units from furthest ellipses
#        
#        **tickstrfmt** : string
#                        format of tick strings needs to be a string format.
#                        ex: '%.2f' for 2 decimal place in floating number
#        
#        **cborientation** : [ 'horizontal' | 'vertical' ]
#                            colorbar orientation horizontal or vertical
#        
#        **figsave** :  [ 'y' | 'n' ]
#                        * 'y' will save figure to edifilelist path in a folder 
#                           called PTfigures.  The figure will also close once
#                           saved.
#                        * 'n' will not save the figure
#                
#        **fmt** : list of formats 
#                 can be pdf,eps or any other formats supported by matplotlib. 
#                 Can be a list of multiple formats.
#                 **Note: that pdf and eps sometimes do not work properly.
#            
#        **rotz** : float
#                   angle in degrees to rotate the data clockwise positive.
#                   *Default* is 0
#        
#        **pxy** : tuple (width,height)
#                  dimensions of the figure in inches.  *Default* is (10,12)
#        
#        **galpha** : float [0:1]
#                     opacity of the grid.  0 for transparent, 1 for opaque
#                     *Default* is 0.25
#        
#        **stationid** : tuple or list 
#                        start and stop of station name indicies.  
#                        ex: for MT01dr stationid=(0,4) will be MT01.
#                        *Default* is None
#                    
#        **stationpad** : float
#                         padding for station name in the y-direction in map
#                         units
#        
#        **sfdict** : dictionary
#                     font dictionary for station name. Keys can be
#                     matplotlib.text properties, common ones are:
#                         * 'size'   -> for font size
#                         * 'weight' -> for font weight
#                         * 'color'  -> for color of font
#                                     
#        **indarrow** : [ 'yri' | 'yr' | 'yi' | 'n' ]
#                        * 'yri' to plot induction both real and imaginary 
#                           induction arrows 
#                        * 'yr' to plot just the real induction arrows
#                        * 'yi' to plot the imaginary induction arrows
#                        * 'n' to not plot them
#                        * *Default* is 'n'                        
#                        **Note: convention is to point towards a conductor **
#       
#       **arrowprop** : dictionary of arrow properties with keys:
#                        * 'linewidth'  -> width of the arrow line
#                        * 'headheight' -> height of arrow head
#                        * 'headwidth'  -> width of the arrow head
#                        * 'arrowscale' -> scale size of the arrow
#        
#        
#        **arrowlegend** : dictionary of properties for legend with keys:
#                        * 'placement -> placement of arrow legend can be:
#                            - 'upper right'
#                            - 'lower right'
#                            - 'upper left'
#                            - 'lower left'
#                        * 'xborderpad' -> padding from x axis
#                        * yborderpad'  -> padding from y axis
#                        * fontpad'     -> padding between arrow and legend text
#                        * fontdict'    -> dictionary of font properties
#        
#        **cmap** :[ 'ptcmap' | 'ptcmap3' | 'skcmap' | 'skcmap2' | 'rtcmap' ]
#                  color map of ellipse facecolor.  So far the colormaps are:
#                      * 'ptcmap'  -> yellow (low phase) to red (high phase)
#                      * 'ptcmap3' -> white (low numbers) to blue (high numbers)
#                      * 'skcmap'  -> blue to yellow to red
#                      * 'skcmap2' -> blue to white to red
#                      * 'rtcmap'  -> blue to purple to red
#            
#        **tscale** : [ 'period' | 'frequency' ]
#                     * 'period'    -> plot vertical scale in period
#                     * 'frequency' -> plot vertical scale in frequency
#        
#        **mapscale** : [ 'latlon' | 'eastnorth' | 'eastnorthkm' ]
#                      scale of map
#                          * 'latlon'     -> lats and longs
#                          * 'eastnorth'  -> for easting and northing, this is 
#                             recomended if you want to plot tipper data for 
#                             small surveys.
#                          * 'eastnorthkm' -> for kilometer scaling
#                          ** Note: if the ellipses are plotting in the wrong 
#                          spot in east-north scale, check to see if your survey
#                          crosses UTM grids.  Currently there is no way of 
#                          dealing with this.
#                   
#        **imagefile** : string
#                        path to an image file jpg or png or svg
#        
#        **image_extent** : tuple (xmin,xmax,ymin,ymax)
#                           coordinates according to mapscale. Must be input if
#                           image file is not None.
#        
#        **refpoint** : tuple (x,y)
#                       reference point estimate relative distance to.  This 
#                       point will be (0,0) on the map and everything else is 
#                       referenced to this point
#         
#    :Example: ::
#        
#        >>> import mtpy.imaging.mtplottools as mtplot
#        >>> import os
#        >>> edipath = r"/home/EDIfiles"
#        >>> edilst = [os.path.join(edipath,edi) for edi in os.listdir(edipath)
#        >>> ...       if edi.find('.edi')]
#        >>> # color by phimin with a range of 20-70 deg in meter scale
#        >>> mtplot.plotPTMaps(edilst,colorkeymm=(20,70),mapscale='eastnorth')
#        >>> 
#        >>> # add induction arrows to skew angle with range (-5,5)
#        >>> mtplot.plotPTMaps(edilst,colorkey='beta',
#        >>> ...               colorkeymm=(-5,5),indarrows='yri')
#        >>>
#        >>> # put an underlying image as a basemap in km scale
#        >>> mtplot.plotPTMaps(edilst,imagefile=r"/home/Maps/Basemap.jpg",
#        >>> ...               image_extent=(0,20,0,20),mapscale='eastnorthkm')
#
#
#    """
#    jj=freqspot
#    fig=plt.figure(fignum,pxy,dpi=200)
#    plt.clf()
#    ax=fig.add_subplot(1,1,1,aspect='equal')
#    
#    if imagefile!=None:
#        if image_extent==None:
#            raise ValueError('Need to put in image extent')
#        im=plt.imread(imagefile)
#        ax.imshow(im,origin='lower',extent=image_extent,aspect='auto')
#        
#    elliplst=[]
#    latlst=[]
#    lonlst=[]
#    if not esize is float:
#        esize=float(esize)
#    
#    if mapscale=='latlon':
#        tickstrfmt='%.3f'
#    elif mapscale=='eastnorth' or mapscale=='eastnorthkm':
#        tickstrfmt='%.0f'
#    
#    ckmin=colorkeymm[0]
#    ckmax=colorkeymm[1]
#    
#    plt.rcParams['font.size']=8
#    plt.rcParams['figure.subplot.left']=.1
#    plt.rcParams['figure.subplot.right']=.98
#    plt.rcParams['figure.subplot.bottom']=.1
#    plt.rcParams['figure.subplot.top']=.93
#    plt.rcParams['figure.subplot.wspace']=.55
#    plt.rcParams['figure.subplot.hspace']=.70
#    #plt.rcParams['font.family']='helvetica'
#    
#    for ii,filename in enumerate(edifilelst):
#        #get phase tensor info
#        imp=Z.Z(filename)
#        #get phase tensor
#        pt=imp.getPhaseTensor(thetar=rotz)
#        pt.phimax=np.nan_to_num(pt.phimax)
#        pt.phimin=np.nan_to_num(pt.phimin)
#        #check to see if the period is there
#        try:
#            freq=1./imp.period[jj]
#            if mapscale=='latlon':
#                latlst.append(imp.lat)
#                lonlst.append(imp.lon)
#                plotx=imp.lon-refpoint[0]
#                ploty=imp.lat-refpoint[1]
#            elif mapscale=='eastnorth':
#                zone,east,north=utm2ll.LLtoUTM(23,imp.lat,imp.lon)
#                if ii==0:
#                    zone1=zone
#                    plotx=east-refpoint[0]
#                    ploty=north-refpoint[1]
#                else:
#                    if zone1!=zone:
#                        if zone1[0:2]==zone[0:2]:
#                            pass
#                        elif int(zone1[0:2])<int(zone[0:2]):
#                            east=east+500000
#                        else:
#                            east=east-500000
#                        latlst.append(north-refpoint[1])
#                        lonlst.append(east-refpoint[0])
#                        plotx=east-refpoint[0]
#                        ploty=north-refpoint[1]
#                    else:
#                        latlst.append(north-refpoint[1])
#                        lonlst.append(east-refpoint[0])
#                        plotx=east-refpoint[0]
#                        ploty=north-refpoint[1]
#            elif mapscale=='eastnorthkm':
#                zone,east,north=utm2ll.LLtoUTM(23,imp.lat,imp.lon)
#                if ii==0:
#                    zone1=zone
#                    plotx=(east-refpoint[0])/1000.
#                    ploty=(north-refpoint[1])/1000.
#                else:
#                    if zone1!=zone:
#                        if zone1[0:2]==zone[0:2]:
#                            pass
#                        elif int(zone1[0:2])<int(zone[0:2]):
#                            east=east+500000
#                        else:
#                            east=east-500000
#                        latlst.append((north-refpoint[1])/1000.)
#                        lonlst.append((east-refpoint[0])/1000.)
#                        plotx=(east-refpoint[0])/1000.
#                        ploty=(north-refpoint[1])/1000.
#                    else:
#                        latlst.append((north-refpoint[1])/1000.)
#                        lonlst.append((east-refpoint[0])/1000.)
#                        plotx=(east-refpoint[0])/1000.
#                        ploty=(north-refpoint[1])/1000.
#            else:
#                raise NameError('mapscale not recognized')
#                    
#            
#            phimin=pt.phimin[jj]
#            phimax=pt.phimax[jj]
#            eangle=pt.azimuth[jj]
#            #create an ellipse object
#            if phimax==0 or phimax>100 or phimin==0 or pt.phiminang[jj]<0 or \
#                pt.phiminang[jj]>100:
#                eheight=.0000001*esize
#                ewidth=.0000001*esize
#            else:
#                scaling=esize/phimax
#                eheight=phimin*scaling
#                ewidth=phimax*scaling
#            ellipd=Ellipse((plotx,ploty),width=ewidth,height=eheight,
#                          angle=eangle)
#            #print imp.lon,imp.lat,scaling,ewidth,eheight,phimin,phimax
#            elliplst.append(ellipd)
#            ax.add_artist(ellipd)
#            
#            #get face color info
#            if colorkey=='phiminang' or  colorkey=='phimin':
#                cvar=(pt.phiminang[jj]-ckmin)/(ckmax-ckmin)
#            elif colorkey=='phidet':
#                cvar=(pt.phidet[jj]-ckmin)/(ckmax-ckmin)
#            elif colorkey=='beta':
#                cvar=(pt.beta[jj]-abs(ckmin))/(ckmax-ckmin)
#            elif colorkey=='ellipticity':
#                cvar=(pt.ellipticity[jj]-ckmin)/(ckmax-ckmin)
#            else:
#                raise NameError('color key '+colorkey+' not supported')
#            
#            #set facecolor depending on the colormap
#            #yellow to red
#            if cmap=='ptcmap':
#                if abs(cvar)>1:
#                    ellipd.set_facecolor((1,0,0))
#                elif cvar<0:
#                    ellipd.set_facecolor((1-abs(cvar),1,abs(cvar)))
#                else:
#                    ellipd.set_facecolor((1,1-abs(cvar),.1))
#            #white to blue
#            elif cmap=='ptcmap3':
#                if abs(cvar)>1:
#                    ellipd.set_facecolor((0,0,0))
#                else:
#                    ellipd.set_facecolor((1-abs(cvar),1-abs(cvar),1))
#            #blue to yellow to red
#            elif cmap=='skcmap2':
#                if cvar<0 and cvar>-1:
#                    ellipd.set_facecolor((1-abs(cvar),1-abs(cvar),1))
#                elif cvar<-1:
#                    ellipd.set_facecolor((0,0,1))
#                elif cvar>0 and cvar<1:
#                    ellipd.set_facecolor((1,1-abs(cvar),1-abs(cvar)))
#                elif cvar>1:
#                    ellipd.set_facecolor((1,0,0))
#            #blue to white to red
#            elif cmap=='skcmap':
#                if cvar<0 and cvar>-1:
#                    ellipd.set_facecolor((abs(cvar),abs(cvar),1-abs(cvar)))
#                elif cvar<-1:
#                    ellipd.set_facecolor((0,0,1))
#                elif cvar>0 and cvar<1:
#                    ellipd.set_facecolor((1,1-abs(cvar),.01))
#                elif cvar>1:
#                    ellipd.set_facecolor((1,0,0))
#                    
#            #-----------Plot Induction Arrows---------------------------
#            if indarrows.find('y')==0:
##                if mapscale=='latlon':
##                    print 'Might try mapscale=latlon for better scale of arrows'
#                    
#                tip=imp.getTipper(thetar=rotz)
#                aheight=arrowprop['headheight']
#                awidth=arrowprop['headwidth']
#                ascale=arrowprop['arrowscale']
#                #plot real tipper
#                if indarrows=='yri' or indarrows=='yr':
#                    if tip.magreal[jj]<=1.0:
#                        txr=tip.magreal[jj]*ascale*\
#                            np.sin((tip.anglereal[jj])*np.pi/180)
#                        tyr=tip.magreal[jj]*ascale*\
#                            np.cos((tip.anglereal[jj])*np.pi/180)
#    
#                        ax.arrow(plotx,ploty,txr,tyr,lw=arrowprop['linewidth'],
#                             facecolor='k',edgecolor='k',
#                             length_includes_head=False,
#                             head_width=awidth,head_length=aheight)
#                    else:
#                        pass
#                #plot imaginary tipper
#                if indarrows=='yri' or indarrows=='yi':
#                    if tip.magimag[jj]<=1.0:
#                        txi=tip.magimag[jj]*\
#                            np.sin((tip.angleimag[jj])*np.pi/180)*scaling
#                        tyi=tip.magimag[jj]*\
#                            np.cos((tip.angleimag[jj])*np.pi/180)*scaling
#    
#                        ax.arrow(plotx,ploty,txi,tyi,lw=arrowprop['linewidth'],
#                                 facecolor='b',edgecolor='b',
#                                 length_includes_head=False,
#                                 head_width=awidth,head_length=aheight)
#                         
#            
#            #------------Plot station name------------------------------
#            if stationid!=None:
#                ax.text(plotx,ploty+stationpad,
#                        imp.station[stationid[0]:stationid[1]],
#                        horizontalalignment='center',
#                        verticalalignment='baseline',
#                        fontdict=sfdict)
#                
#        #if the period is not there 
#        except IndexError:
#            print 'Did not find index for station'.format(jj)+imp.station
#    
#    if mapscale=='latlon':    
#        ax.set_xlabel('longitude',fontsize=10,fontweight='bold')
#        ax.set_ylabel('latitude',fontsize=10,fontweight='bold')
#        ax.set_xlim(min(lonlst)-xpad,max(lonlst)+xpad)
#        ax.xaxis.set_major_formatter(FormatStrFormatter(tickstrfmt))
#        ax.set_ylim(min(latlst)-xpad,max(latlst)+xpad)
#        ax.yaxis.set_major_formatter(FormatStrFormatter(tickstrfmt))
#    elif mapscale=='eastnorth':
#        ax.set_xlabel('Easting (m)',fontsize=10,fontweight='bold')
#        ax.set_ylabel('Northing (m)',fontsize=10,fontweight='bold')
#        ax.set_xlim(min(lonlst)-xpad,max(lonlst)+xpad)
#        ax.xaxis.set_major_formatter(FormatStrFormatter(tickstrfmt))
#        ax.set_ylim(min(latlst)-xpad,max(latlst)+xpad)
#        ax.yaxis.set_major_formatter(FormatStrFormatter(tickstrfmt))
#    elif mapscale=='eastnorthkm':
#        ax.set_xlabel('Easting (km)',fontsize=10,fontweight='bold')
#        ax.set_ylabel('Northing (km)',fontsize=10,fontweight='bold')
#        ax.set_xlim(min(lonlst)-xpad,max(lonlst)+xpad)
#        ax.xaxis.set_major_formatter(FormatStrFormatter(tickstrfmt))
#        ax.set_ylim(min(latlst)-xpad,max(latlst)+xpad)
#        ax.yaxis.set_major_formatter(FormatStrFormatter(tickstrfmt))
#    if tscale=='period':
#        titlefreq='{0:.5g} (s)'.format(1./freq)
#    else:
#        titlefreq='{0:.5g} (Hz)'.format(freq)
#    ax.set_title('Phase Tensor Map for '+titlefreq,
#                 fontsize=10,fontweight='bold')
#    #plot induction arrow scale bar
#    if indarrows.find('y')==0:
#        parrx=ax.get_xlim()
#        parry=ax.get_ylim()
#        try:
#            axpad=arrowlegend['xborderpad']
#        except KeyError:
#            axpad=xpad+arrowprop['arrowscale']
#        try:
#            aypad=arrowlegend['yborderpad']
#        except KeyError:
#            aypad=ypad
#        try:
#            txtpad=arrowlegend['fontpad']
#        except KeyError:
#            txtpad=.25*esize
#            
#        
#        if arrowlegend['placement']=='lower right':
#            pax=parrx[1]-axpad
#            pay=parry[0]+aypad
#            ptx=arrowprop['arrowscale']
#            pty=0
#            txa=parrx[1]-axpad+arrowprop['arrowscale']/2.
#            txy=pay+txtpad
#        elif arrowlegend['placement']=='upper right':
#            pax=parrx[1]-axpad
#            pay=parry[1]-aypad
#            ptx=arrowprop['arrowscale']
#            pty=0
#            txa=parrx[1]-axpad+arrowprop['arrowscale']/2.
#            txy=pay+txtpad
#        elif arrowlegend['placement']=='lower left':
#            pax=parrx[0]+axpad
#            pay=parry[0]+aypad
#            ptx=arrowprop['arrowscale']
#            pty=0
#            txa=parrx[0]+axpad+arrowprop['arrowscale']/2.
#            txy=pay+txtpad
#        elif arrowlegend['placement']=='upper left':
#            pax=parrx[0]+axpad
#            pay=parry[1]-aypad
#            ptx=arrowprop['arrowscale']
#            pty=0
#            txa=parrx[0]+axpad+arrowprop['arrowscale']/2.
#            txy=pay+txtpad
#        else:
#            raise NameError('arrowlegend not supported.')
#            
#        ax.arrow(pax,pay,ptx,pty,lw=arrowprop['linewidth'],
#                             facecolor='k',edgecolor='k',
#                             length_includes_head=False,
#                             head_width=arrowprop['headwidth'],
#                             head_length=arrowprop['headheight'])
#        
#        ax.text(txa,txy,'|T|=1',
#                horizontalalignment='center',
#                verticalalignment='baseline',
#                fontdict={'size':10,'weight':'bold'})
#                
#    ax.grid(alpha=galpha)
#    
##    if indarrows.find('y')==0:
##        if indarrows=='yri':
##            treal=ax.plot(np.arange(10)*.000005,np.arange(10)*.00005,'k')
##            timag=ax.plot(np.arange(10)*.000005,np.arange(10)*.00005,'b')
##            ax.legend([treal[0],timag[0]],['Tipper_real','Tipper_imag'],
##                      loc='upper center',
##                      prop={'size':10,'weight':'bold'},
##                      ncol=2,markerscale=.5,borderaxespad=.005,
##                      borderpad=.25)
##        elif indarrows=='yr':
##            treal=ax.plot(np.arange(10)*.000005,np.arange(10)*.00005,'k')
##            ax.legend([treal[0]],['Tipper_real'],
##                      loc='upper center',
##                      prop={'size':10,'weight':'bold'},
##                      ncol=2,markerscale=.5,borderaxespad=.005,
##                      borderpad=.25)
##        elif indarrows=='yi':
##            timag=ax.plot(np.arange(10)*.000005,np.arange(10)*.00005,'b')
##            ax.legend([timag[0]],['Tipper_imag'],
##                      loc='upper center',
##                      prop={'size':10,'weight':'bold'},
##                      ncol=2,markerscale=.5,borderaxespad=.005,
##                      borderpad=.25)
#    
#    
#    
#    #make a colorbar with appropriate colors             
#    ax2=make_axes(ax,shrink=cbshrink)
#    if cmap=='ptcmap': 
#        cb=ColorbarBase(ax2[0],cmap=ptcmap,norm=Normalize(vmin=ckmin,vmax=ckmax))
#        cb.set_label(colorkey+' (deg)')
#    elif cmap=='ptcmap3': 
#        cb=ColorbarBase(ax2[0],cmap=ptcmap3,norm=Normalize(vmin=ckmin,vmax=ckmax))
#        cb.set_label(colorkey+' (deg)')
#    elif cmap=='skcmap': 
#        cb=ColorbarBase(ax2[0],cmap=skcmap,norm=Normalize(vmin=ckmin,vmax=ckmax))
#        cb.set_label(colorkey+' (deg)')
#    elif cmap=='skcmap2': 
#        cb=ColorbarBase(ax2[0],cmap=skcmap2,norm=Normalize(vmin=ckmin,vmax=ckmax))
#        cb.set_label(colorkey+' (deg)')
#    elif cmap=='rtcmap': 
#        cb=ColorbarBase(ax2[0],cmap=rtcmap,norm=Normalize(vmin=ckmin,vmax=ckmax))
#
#    #label the color bar accordingly
#    if colorkey=='phimin' or colorkey=='phiminang':
#        cb.set_label('$\Phi_{min}$ (deg)',fontdict={'size':10,'weight':'bold'})
#    elif colorkey=='beta':
#        cb.set_label('Skew (deg)',fontdict={'size':10,'weight':'bold'})
#    elif colorkey=='phidet':
#        cb.set_label('Det{$\Phi$} (deg)',fontdict={'size':10,'weight':'bold'})
#    elif colorkey=='ellipticity':
#        cb.set_label('Ellipticity',fontdict={'size':10,'weight':'bold'})
#        
#    plt.show()
#    
#    #save the figure if desired
#    if figsave=='y':
#        sf='_{0:.5g}'.format(freq)
#        savepath=os.path.join(os.path.dirname(edifilelst[0]),'PTfigures')
#        if not os.path.exists(savepath):
#            os.mkdir(savepath)
#            print 'Made directory: '+savepath
#        else:
#            pass
#        for f in fmt:
#            fig.savefig(os.path.join(savepath,
#                                 'PTmap_'+colorkey+sf+'Hz.'+f),
#                                 format=f)
#            print 'Saved file figures to: '+ os.path.join(savepath, \
#                                     'PTmap_'+colorkey+sf+'Hz.'+f)
#        plt.close()
#        
#
#def plotResPhasePseudoSection(edifilelst,stationid=[0,4],ffactor=1,
#                              maxperiod=60,aspect=4,cmap='jet_r',xtickspace=2,
#                              linedir='ns',rotz=0,dpi=300):
#    """
#    plotResPhasePseudoSection(edifilelst,stationid=4,ffactor=10E3,df=100.,
#                              maxperiod=24,aspect=4,cmap='jet_r') plots a 
#    pseudo section from a list of edifiles with full path with descending 
#    frequency or ascending period on the y axis and relative position on the x. 
#    keyword arguments can be:
#        stationid = start and finish of station string for plotting
#        ffactor = fudge factor to make sure resistivities plot correctly
#        df = sampling frequency (Hz)
#        maxperiod = maximum period to plot
#        aspect = horizontal to vertical ratio of plot
#        cmap = colormap of image
#    """
#    
#    fs=int(dpi/40)
#    plt.rcParams['font.size']=fs
#    plt.rcParams['figure.subplot.left']=.07
#    plt.rcParams['figure.subplot.right']=.98
#    plt.rcParams['figure.subplot.bottom']=.06
#    plt.rcParams['figure.subplot.top']=.94
#    plt.rcParams['figure.subplot.wspace']=.01
#    plt.rcParams['figure.subplot.hspace']=.20
#    #plt.rcParams['font.family']='helvetica'
#    
#    
#    #create a plot instance
##    ax1=fig.add_subplot(2,2,1)
##    ax2=fig.add_subplot(2,2,2,sharex=ax1)
##    ax3=fig.add_subplot(2,2,3,sharex=ax1)
##    ax4=fig.add_subplot(2,2,4,sharex=ax1)
#    
#    #create empty lists to put things into
#    stationlst=[]
#    offsetlst=[]
#    minperiodlst=[]
#    maxperiodlst=[]
#    periodlst=[]
#    nlst=[]
#    
#    #create empty arrays to put data into
#    n=len(edifilelst)
#    resxx=np.zeros((maxperiod,n))
#    resxy=np.zeros((maxperiod,n))
#    resyx=np.zeros((maxperiod,n))
#    resyy=np.zeros((maxperiod,n))
#    
#    phasexx=np.zeros((maxperiod,n))
#    phasexy=np.zeros((maxperiod,n))
#    phaseyx=np.zeros((maxperiod,n))
#    phaseyy=np.zeros((maxperiod,n))
#    
#    #get data into arrays
#    for ii,fn in enumerate(edifilelst):
#        #get offsets between stations
#        imp=Z.Z(fn)
#        stationlst.append(imp.station[stationid[0]:stationid[1]])
#        zone,east,north=utm2ll.LLtoUTM(23,imp.lat,imp.lon)
#        
#        if ii==0:
#            east0=east
#            north0=north
#            offset=0.0
#        else:
#            if linedir=='ew': 
#                if east0<east:
#                    offset=np.sqrt((east0-east)**2+(north0-north)**2)
#                elif east0>east:
#                    offset=-1*np.sqrt((east0-east)**2+(north0-north)**2)
#                else:
#                    offset=0
#            elif linedir=='ns':
#                if north0<north:
#                    offset=np.sqrt((east0-east)**2+(north0-north)**2)
#                elif north0>north:
#                    offset=-1*np.sqrt((east0-east)**2+(north0-north)**2)
#                else:
#                    offset=0
#        offsetlst.append(offset)
#        #get resisitivity and phase in a dictionary and append to a list
#        rp=imp.getResPhase(ffactor=ffactor,thetar=rotz)
#        m=len(imp.period)
#        resxx[0:m,ii]=np.log10(rp.resxx)#[::-1]
#        resxy[0:m,ii]=np.log10(rp.resxy)#[::-1]
#        resyx[0:m,ii]=np.log10(rp.resyx)#[::-1]
#        resyy[0:m,ii]=np.log10(rp.resyy)#[::-1]
#        
#        phasexx[0:m,ii]=rp.phasexx#[::-1]
#        phasexy[0:m,ii]=rp.phasexy#[::-1]
#        phaseyx[0:m,ii]=rp.phaseyx+180#[::-1]
#        phaseyy[0:m,ii]=rp.phaseyy#[::-1]
#        
#        #get min and max of the period, just in case some edi files have 
#        #different period information
#        minperiodlst.append(min(imp.period))
#        maxperiodlst.append(max(imp.period))
#        nlst.append(len(imp.period))
#        periodlst.append(imp.period)
#        
#    nperiod=max(nlst)
#    for pp in range(len(periodlst)):
#        if nlst[pp]==nperiod:
#            period=np.log10(periodlst[pp])#[::-1]
#
#    #plot data
#    fig=plt.figure(1,[12,4],dpi=150)
#    extent=(0,n,period[-1],period[0])
#    aspect=aspect
#    cmap=cmap
#    pad=.2
#    kwargs={'aspect':aspect,'cmap':cmap,'extent':extent}
#    cbarkwargs={'shrink':.7,'orientation':'horizontal','pad':pad}
#
#    
#    ax2=plt.subplot(2,4,2)
#    plt.imshow(resxy[0:nperiod,:],**kwargs)
#    plt.colorbar(**cbarkwargs)
#    plt.xticks(np.arange(0,n,xtickspace),
#               [stationlst[st] for st in range(0,n,xtickspace)])
##    plt.ylabel('Log$_{10}$ Period',fontsize=10,fontweight='bold')
#    plt.xlabel('Station',fontsize=fs+4,fontweight='bold')
#    plt.title('Log$_{10}\mathbf{(1/\sigma_{xy})}$',fontsize=fs+4,fontweight='bold')
#    ax2.yaxis.set_minor_locator(MultipleLocator(.2))
#    plt.grid()
#    
#    ax3=plt.subplot(2,4,3)
#    plt.imshow(resyx[0:nperiod,:],**kwargs)
#    plt.colorbar(**cbarkwargs)
#    plt.xticks(np.arange(0,n,xtickspace),
#               [stationlst[st] for st in range(0,n,xtickspace)])
##    plt.ylabel('Log$_{10}$ Period',fontsize=fs+4,fontweight='bold')
#    plt.xlabel('Station',fontsize=fs+4,fontweight='bold')
#    plt.title('Log$_{10}\mathbf{(1/\sigma_{yx})}$',fontsize=fs+4,fontweight='bold')
#    ax3.yaxis.set_minor_locator(MultipleLocator(.2))
#    plt.grid()
#    
#    ax6=plt.subplot(2,4,6)
#    plt.imshow(phasexy[0:nperiod,:],vmin=0,vmax=90,**kwargs)
#    plt.colorbar(**cbarkwargs)
#    plt.xticks(np.arange(0,n,xtickspace),
#               [stationlst[st] for st in range(0,n,xtickspace)])
##    plt.ylabel('Log$_{10}$ Period',fontsize=fs+4,fontweight='bold')
#    plt.xlabel('Station',fontsize=fs+4,fontweight='bold')
#    plt.title('$\mathbf{\phi_{xy}}$',fontsize=fs+4)
#    ax6.yaxis.set_minor_locator(MultipleLocator(.2))
#    plt.grid()
#    
#    ax7=plt.subplot(2,4,7)
#    plt.imshow(phaseyx[0:nperiod,:],vmin=0,vmax=90,**kwargs)
#    plt.colorbar(**cbarkwargs)
#    plt.xticks(np.arange(0,n,xtickspace),
#               [stationlst[st] for st in range(0,n,xtickspace)])
##    plt.ylabel('Log$_{10}$ Period',fontsize=fs+4,fontweight='bold')
#    plt.xlabel('Station',fontsize=fs+4,fontweight='bold')
#    plt.title('$\mathbf{\phi_{yx}}$',fontsize=fs+4)
#    ax7.yaxis.set_minor_locator(MultipleLocator(.2))
#    plt.grid()
#    
##    fig2=plt.figure(2,dpi=150)    
#
#    ax1=plt.subplot(2,4,1)
#    plt.imshow(resxx[0:nperiod,:],**kwargs)
#    plt.colorbar(**cbarkwargs)
#    plt.xticks(np.arange(0,n,xtickspace),
#               [stationlst[st] for st in range(0,n,xtickspace)])
#    plt.ylabel('Log$_{10}$ Period',fontsize=fs+4,fontweight='bold')
#    plt.xlabel('Station',fontsize=fs+4,fontweight='bold')
#    plt.title('Log$_{10}\mathbf{(1/\sigma_{xx})}$',fontsize=fs+4,fontweight='bold')
#    ax1.yaxis.set_minor_locator(MultipleLocator(.2))
#    plt.grid()
#    
#    ax4=plt.subplot(2,4,4)
#    plt.imshow(resyy[0:nperiod,:],**kwargs)
#    plt.colorbar(**cbarkwargs)
#    plt.xticks(np.arange(0,n,xtickspace),
#               [stationlst[st] for st in range(0,n,xtickspace)])
##    plt.ylabel('Log$_{10}$ Period',fontsize=fs+4,fontweight='bold')
#    plt.xlabel('Station',fontsize=fs+4,fontweight='bold')
#    plt.title('Log$_{10}\mathbf{(1/\sigma_{yy})}$',fontsize=fs+4,fontweight='bold')
#    ax4.yaxis.set_minor_locator(MultipleLocator(.2))
#    plt.grid()
#    
#    ax5=plt.subplot(2,4,5)
#    plt.imshow(phasexx[0:nperiod,:],**kwargs)
#    plt.colorbar(**cbarkwargs)
#    plt.xticks(np.arange(0,n,xtickspace),
#               [stationlst[st] for st in range(0,n,xtickspace)])
#    plt.ylabel('Log$_{10}$ Period',fontsize=fs+4,fontweight='bold')
#    plt.xlabel('Station',fontsize=fs+4,fontweight='bold')
#    plt.title('$\mathbf{\phi_{xx}}$',fontsize=fs+4)
#    ax5.yaxis.set_minor_locator(MultipleLocator(.2))
#    plt.grid()
#    
#    ax8=plt.subplot(2,4,8)
#    plt.imshow(phaseyy[0:nperiod,:],**kwargs)
#    plt.colorbar(**cbarkwargs)
#    plt.xticks(np.arange(0,n,xtickspace),
#               [stationlst[st] for st in range(0,n,xtickspace)])
##    plt.ylabel('Log$_{10}$ Period',fontsize=fs+4,fontweight='bold')
#    plt.xlabel('Station',fontsize=fs+4,fontweight='bold')
#    plt.title('$\mathbf{\phi_{yy}}$',fontsize=fs+4)
#    ax8.yaxis.set_minor_locator(MultipleLocator(.2))
#    plt.grid()
#    plt.show()
#    
#def plotRTMaps(edifilelst,freqspot=10,esize=2.0,colorkey='rhodet',xpad=.2,
#               ypad=.2,tickstrfmt='%2.4f',cborientation='vertical',
#               colorkeymm=[0,4],figsave='y',fmt=['png'],rotz=0,pxy=[10,12],
#                galpha=.25):
#    """ 
#    plotPTMaps(edifilelst,freqspot=10,esize=2.0,colorkey='phimin',xpad=.2,
#               ypad=.2,tickstrfmt='%2.4f',cborientation='vertical',
#               colorkeymax=90.,figsave='y',fmt=['png']) 
#    plots phase tensor ellipses in map view from a list of edifiles with full 
#    path.  Parameters are:
#        
#        freqspot = position in frequency list for plotting, an integer
#        esize = size of ellipse, float
#        colorkey =  the fill color of the ellipses and can be any of the 
#        dictionary keys returned by Z.getPhaseTensor(), note skew is beta:
#        'phimin','phi', 'phiminvar', 'azimuthvar', 'azimuth', 'betavar', 
#        'phivar', 'alphavar', 'beta', 'ellipticityvar', 'phiminangvar', 
#        'ellipticity', 'phimaxangvar', 'alpha', 'phiminang', 'phimaxvar', 
#        'phimaxang', 'phimax'
#        colorkeymm = [min,max] min and max of colorkey to which colorbar is
#                    normalized to.
#        xpad = pad from xmin and xmax on plot
#        ypad = pad from ymin and ymax on plot
#        tickstrfmt = format of tick strings needs to be a string format
#        cborientation = colorbar orientation horizontal or vertical
#        figsave = y or n, if yes figure will be saved to edifilelist path in 
#                a folder called PTfigures.
#        fmt = ['png'] is format of save figure can be pdf,eps or any other 
#            formats supported by matplotlib. Can be a list of multiple formats.
#            Note that pdf and eps do not properly yet.
#        
#    """
#    jj=freqspot
#    fig=plt.figure(1,pxy,dpi=150)
#    ax=fig.add_subplot(1,1,1,aspect='equal')
#    elliplst=[]
#    latlst=[]
#    lonlst=[]
#    if not esize is float:
#        esize=float(esize)
#    
#    ckmin=colorkeymm[0]
#    ckmax=colorkeymm[1]
#    
#    plt.rcParams['font.size']=8
#    plt.rcParams['figure.subplot.left']=.1
#    plt.rcParams['figure.subplot.right']=.98
#    plt.rcParams['figure.subplot.bottom']=.1
#    plt.rcParams['figure.subplot.top']=.93
#    plt.rcParams['figure.subplot.wspace']=.55
#    plt.rcParams['figure.subplot.hspace']=.70
#    #plt.rcParams['font.family']='helvetica'
#    
#    for ii,filename in enumerate(edifilelst):
#        #get phase tensor info
#        imp=Z.Z(filename)
#        try:
#            freq=1./imp.period[jj]
#            latlst.append(imp.lat)
#            lonlst.append(imp.lon)
#            rt=imp.getResTensor(thetar=rotz)
#            phimax=rt.rhomax[jj]
#            phimin=rt.rhomin[jj]
#            eangle=rt.rhoazimuth[jj]
#            if colorkey=='rhomin':
#                colorarray=phimin
#            elif colorkey=='rhomax':
#                colorarray=phimax
#            elif colorkey=='rhobeta':
#                colorarray=rt.rhobeta[jj]
#            elif colorkey=='rhodet':
#                colorarray=rt.rhodet[jj]
#            eangle=rt.rhoazimuth[jj]
#            #create an ellipse object
#            scaling=esize/phimax
#            eheight=phimin*scaling
#            ewidth=phimax*scaling
#            
##            ellipd=Ellipse((imp.lon,imp.lat),width=ewidth,height=eheight,
##                          angle=eangle)
##            #print imp.lon,imp.lat,scaling,ewidth,eheight,phimin,phimax
##            elliplst.append(ellipd)
##            ax.add_artist(ellipd)
##            #get face color info
#        
#            #create an ellipse scaled by phimin and phimax and oriented along
#            #the azimuth 
#            emax=10*esize
##            print eheight,ewidth,emax
#            if eheight>emax or ewidth>emax:
#                pass
#            else:
#                ellip=Ellipse((imp.lon,imp.lat),width=ewidth,
#                              height=eheight,
#                              angle=eangle)
#                #color the ellipse as red high conductivity, blue low
#                cvars=(np.log10(abs(colorarray))-ckmin)/(ckmax-ckmin)
#                #print cvars
#                if cvars>1:
#                    ellip.set_facecolor((0,0,1))
#                elif cvars<float(ckmin)/ckmax or cvars<0:
#                    ellip.set_facecolor((1,0,0))
#                else:
#                    ellip.set_facecolor((1-cvars,0,cvars))
#                ax.add_artist(ellip)            
#            
#        except IndexError:
#            pass
#        
#    ax.set_xlabel('longitude',fontsize=10,fontweight='bold')
#    ax.set_ylabel('latitude',fontsize=10,fontweight='bold')
#    ax.set_xlim(min(lonlst)-xpad,max(lonlst)+xpad)
#    ax.xaxis.set_major_formatter(FormatStrFormatter(tickstrfmt))
#    ax.set_ylim(min(latlst)-xpad,max(latlst)+xpad)
#    ax.yaxis.set_major_formatter(FormatStrFormatter(tickstrfmt))
#    titlefreq='%2.3f' % (1/freq)
#    ax.set_title('Resistivity Tensor for '+titlefreq+'(s)',
#                 fontsize=10,fontweight='bold')
#    ax.grid(alpha=galpha)
#                 
#    ax2=make_axes(ax,shrink=.8)
#    if colorkey=='rhodet' or colorkey=='phidet':
#        cb=ColorbarBase(ax2[0],cmap=rtcmap,norm=Normalize(vmin=ckmin,vmax=ckmax))
#        cb.set_label('Log$_{10}$ '+colorkey+' ($\Omega \cdot$m)')
#    elif colorkey=='beta' or colorkey=='ellipticity':
#        cb=ColorbarBase(ax2[0],cmap=ptcmap3,norm=Normalize(vmin=ckmin,vmax=ckmax))
#        cb.set_label(colorkey+' (deg)')
#    plt.show()
#    
#    if figsave=='y':
#        sf='%2.3g' % freq
#        savepath=os.path.join(os.path.dirname(edifilelst[0]),'RTfigures')
#        if not os.path.exists(savepath):
#            os.mkdir(savepath)
#            print 'Made directory: '+savepath
#        else:
#            pass
#        for f in fmt:
#            fig.savefig(os.path.join(savepath,
#                                 'RTmap'+sf+'Hz.'+f),
#                                 format=f)
#            print 'Saved file figures to: '+ os.path.join(savepath, \
#                                     'RTmap'+sf+'Hz.'+f)
#        plt.close()
#    
