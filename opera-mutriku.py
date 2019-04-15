#~##############################################################################
##
# bokeh serve --allow-websocket-origin=* opera-mutriku.py
##  
#~##############################################################################

import numpy as np
import itertools, os, h5py

from bokeh.models import Button, ColumnDataSource, Select, HoverTool
from bokeh.models.widgets import DataTable, TableColumn, Tabs, Panel, Div
from bokeh import layouts
from bokeh.io import curdoc
from bokeh.plotting import figure

#~##############################################################################
# create a color table
# http://tools.medialab.sciences-po.fr/iwanthue/
colors = [ "#ffb160", "#6297ff", "#8dc722", "#e12eaa", "#000000", "#f01958",
           "#ffb318", "#8bd892", "#6f3a95", "#c99cff", "#1c6000", "#ff82a9",
           "#01a9a7", "#c66100", "#978700", "#A05A2C", "#01a04f" ]

VP_default_width  = 770
VP_default_height = 600

TS_default_width  = 1550
TS_default_height = 300

#~##############################################################################
'''
get filenames from working folder
'''
def get_h5_filenames( folder, inclusions, exclusions ):

  h5_files = []

  fld_files = []
  for root, dir, files in os.walk( folder ):
      for file in files:
        fld_files.append( os.path.join( root, file ) )
  fld_files = sorted( fld_files )

  for filename in fld_files:
    ext = os.path.splitext( filename )[1]

    if ext in ['.h5']:
      if any( sub in filename for sub in inclusions ):
        if not any( sub in filename for sub in exclusions ):
          h5_files.append( filename )
  
  return h5_files

#~##############################################################################
class ValData:

  #~============================================================================
  def __init__( self ):
    self.selector_callback_list = []
    self.max_selection = -1

  #~============================================================================
  def register_select_callback( self, func ):
    self.selector_callback_list.append( func )

  #~============================================================================
  def select_callback( self, attr, old, new ):

    if self.max_selection > 0 and len( new ) > self.max_selection:
      new = new[-self.max_selection:]
    self.status_bar.text = "Number of selected tests: %i" % len( new ) 
    self.Table_source.selected.indices = new
    for func in self.selector_callback_list:
      func( new )

  #~============================================================================
  def select_all_callback( self ):
    lst = list( range( Values.num_tests ) )
    self.status_bar.text = "Number of selected tests: %i" % len( lst ) 
    self.Table_source.selected.indices = lst
    for func in self.selector_callback_list:
      func( lst )

  #~============================================================================
  def select_all_button( self ):
    self.button_widget = Button( label = 'Select all rows', 
                                 button_type='success', width=180 )
    self.button_widget.on_click( self.select_all_callback )
    return self.button_widget

  #~============================================================================
  def CreateValuesTab( self ):

    TimeStamp = []
    CL = []
    CL_color = []
    CL_name = []

    RMS_p = []
    RMS_Q = []
    RMS_Omega = []
    RMS_Psi = []
    RMS_Phi = []
    RMS_Pi = []

    Omega_Mean = []
    Pi_Mean = []
    Eta_Mean = []

    Ppneu_Mean = []
    Pturb_Mean = []
    Pdrive_Mean = []
    Pgrid_Mean = []

    folder = os.path.join( os.getcwd(), 'data' )
    h5_files = get_h5_filenames( folder, ['OPERA_PP_'], [] )

    fcount = 0
    ncount = len(h5_files)

    for filename in h5_files:

      fcount += 1
      if fcount % 50 == 0:
        print( "Reading file %i of %i" % ( fcount, ncount ) )     

      hf = h5py.File( filename, 'r')

      grp_name = 'Values'

      TimeStamp.append( str( hf[ grp_name + '/TimeStamp' ][()] )[0:19] )
      CLi = int( hf[ grp_name + '/CL' ][()] )
      CL.append( CLi )
      CL_color.append( colors[ CLi ] )
      CL_name.append( 'CL ' + str( CLi ) )

      RMS_p.append( float( hf[ grp_name + '/RMS_p' ][()] ) )
      RMS_Q.append( float( hf[ grp_name + '/RMS_Q' ][()] ) )
      RMS_Omega.append( float( hf[ grp_name + '/RMS_Omega' ][()] ) )
      RMS_Psi.append( float( hf[ grp_name + '/RMS_Psi' ][()] ) )
      RMS_Phi.append( float( hf[ grp_name + '/RMS_Phi' ][()] ) )
      RMS_Pi.append( float( hf[ grp_name + '/RMS_Pi' ][()] ) )

      Omega_Mean.append( float( hf[ grp_name + '/Omega_Mean' ][()] ) )
      Pi_Mean.append( float( hf[ grp_name + '/Pi_Mean' ][()] ) )
      Eta_Mean.append( float( hf[ grp_name + '/Eta_Mean' ][()] ) )

      Ppneu_Mean.append( float( hf[ grp_name + '/Ppneu_Mean' ][()] ) )
      Pturb_Mean.append( float( hf[ grp_name + '/Pturb_Mean' ][()] ) )
      Pdrive_Mean.append( float( hf[ grp_name + '/Pdrive_Mean' ][()] ) )
      Pgrid_Mean.append( float( hf[ grp_name + '/Pgrid_Mean' ][()] ) )

      hf.close()

    self.num_tests = len( TimeStamp )

    self.array_dic = {
      'TimeStamp' : TimeStamp,
      'CL' : CL,
      'CL_color': CL_color,
      'CL_name': CL_name,
      'Eta_Mean' : Eta_Mean,
      'Pi_Mean' : Pi_Mean,
      'Omega_Mean' : Omega_Mean,
      'Ppneu_Mean' : Ppneu_Mean,
      'Pturb_Mean' : Pturb_Mean,
      'Pdrive_Mean' : Pdrive_Mean,
      'Pgrid_Mean' : Pgrid_Mean,
      'RMS_p' : RMS_p,
      'RMS_Q' : RMS_Q,
      'RMS_Omega' : RMS_Omega,
      'RMS_Psi' : RMS_Psi,
      'RMS_Phi' : RMS_Phi,
      'RMS_Pi' : RMS_Pi,
    }

    self.Table_cols_name = [
        TableColumn( field='TimeStamp', title='TimeStamp' ),
        TableColumn( field='CL_name', title='Ctrl Law'),
        TableColumn( field='Eta_Mean', title='Eta_Mean'),
        TableColumn( field='RMS_p', title='RMS_p'),
        TableColumn( field='RMS_Q', title='RMS_Q'),
        TableColumn( field='Omega_Mean', title='Omega_Mean'),
        TableColumn( field='RMS_Omega', title='RMS_Omega'),
        TableColumn( field='Ppneu_Mean', title='Ppneu_Mean'),
        TableColumn( field='Pturb_Mean', title='Pturb_Mean'),
        TableColumn( field='Pdrive_Mean', title='Pdrive_Mean'),
        TableColumn( field='Pgrid_Mean', title='Pgrid_Mean'),
        TableColumn( field='RMS_Psi', title='RMS_Psi'),
        TableColumn( field='RMS_Phi', title='RMS_Phi'),
        TableColumn( field='Pi_Mean', title='Pi_Mean'),
        TableColumn( field='RMS_Pi', title='RMS_Pi'),
    ]

    self.Table_source = ColumnDataSource( self.array_dic )

    self.Table_source.selected.indices = list( range( self.num_tests ) ) 

    self.data_table = DataTable( selectable = True, 
                                 source=self.Table_source, 
                                 columns=self.Table_cols_name, width=1600, 
                                 height=380)

    self.Table_source.selected.on_change( 'indices', self.select_callback )

    self.axis_options = [ 'RMS_Psi', 'Eta_Mean', 'CL', 'Pi_Mean', 'Omega_Mean', 
                          'Ppneu_Mean', 'Pturb_Mean', 'Pdrive_Mean', 
                          'Pgrid_Mean', 'RMS_p', 'RMS_Q', 'RMS_Omega', 
                          'RMS_Phi', 'RMS_Pi' ]
    
    self.status_bar = Div(  text="Number of selected tests: %i" % self.num_tests, width = VP_default_width )

    return self.data_table, self.status_bar

  #~============================================================================
  def CreateTimeSeriesTab( self ):

    self.CreateValuesTab()  

    self.TimeStamp_dic = {}
    time = []
    Delta_p = []
    Eta = []
    HSSV = []
    Omega = []
    Pdrive = []
    Pgrid = []
    Phi = []
    Pi = []
    Ppneu = []
    Psi = []
    Pturb = []
    Q = []
    damper = []
  
    folder = os.path.join( os.getcwd(), 'data' )
    h5_files = get_h5_filenames( folder, ['OPERA_PP_'], [] )

    counter = 0

    for filename in h5_files:
      
      hf = h5py.File( filename, 'r')

      grp_name = 'Values'

      TS = str( hf[ grp_name + '/TimeStamp' ][()] )[0:19]
      self.TimeStamp_dic[ counter ] = TS
      counter += 1

      grp_name = 'TimeSeries'

      time.append( np.array( hf[ grp_name + '/time' ] ) )
      damper.append( np.array( hf[ grp_name + '/damper' ] ) )
      Delta_p.append( np.array( hf[ grp_name + '/Delta_p' ] ) )
      Q.append( np.array( hf[ grp_name + '/Q' ] ) )
      Eta.append( np.array( hf[ grp_name + '/Eta' ] ) )
      HSSV.append( np.array( hf[ grp_name + '/HSSV' ] ) )
      Omega.append( np.array( hf[ grp_name + '/Omega' ] ) )
      Ppneu.append( np.array( hf[ grp_name + '/Ppneu' ] ) )
      Pturb.append( np.array( hf[ grp_name + '/Pturb' ] ) )
      Pdrive.append( np.array( hf[ grp_name + '/Pdrive' ] ) )
      Pgrid.append( np.array( hf[ grp_name + '/Pgrid' ] ) )
      Phi.append( np.array( hf[ grp_name + '/Phi' ] ) )
      Pi.append( np.array( hf[ grp_name + '/Pi' ] ) )
      Psi.append( np.array( hf[ grp_name + '/Psi' ] ) )

      hf.close()

    self.TS_array_dic = {
      'time' : time,
      'damper' : damper,
      'Delta_p' : Delta_p,
      'Q' : Q,
      'Eta' : Eta,
      'HSSV' : HSSV,
      'Omega' : Omega,
      'Ppneu' : Ppneu,
      'Pturb' : Pturb,
      'Pdrive' : Pdrive,
      'Pgrid' : Pgrid,
      'Phi' : Phi,
      'Pi' : Pi,
      'Psi' : Psi
    }

    self.TS_Table_source = ColumnDataSource( self.TS_array_dic )

    self.TS_axis_options = [ 'Eta', 'damper', 'Delta_p', 'Q', 
                             'HSSV', 'Omega', 'Ppneu', 'Pturb', 'Pdrive',
                             'Pgrid', 'Phi', 'Pi', 'Psi' ]

    return self.data_table, self.status_bar

#~##############################################################################
class ValuesPlot:

  #~============================================================================
  def x_axis_sel_callback( self, attr, old, new ):
    self.x_axis = new
    self.plot_source.data['x'] = self.Table_source.data[ self.x_axis ]
    self.figure.xaxis.axis_label = self.x_axis
    self.hover.tooltips = [ (self.x_axis, "@x"), (self.y_axis, "@y") ]

  #~============================================================================
  def y_axis_sel_callback( self, attr, old, new ):
    self.y_axis = new
    self.plot_source.data['y'] = self.Table_source.data[ self.y_axis ]
    self.figure.yaxis.axis_label = self.y_axis
    self.hover.tooltips = [ (self.x_axis, "@x"), (self.y_axis, "@y") ]

  #~============================================================================
  def select_callback( self, lst ):
    self.plot_source.selected.indices = lst

  #~============================================================================
  def Create( self, plot_name, vals ):
   
    self.Table_source = vals.Table_source
    self.plot_source = ColumnDataSource( data = dict( x=[], y=[] ) )
    
    vals.register_select_callback( self.select_callback )

    self.plot_name = plot_name
    self.x_axis = vals.axis_options[0]
    self.y_axis = vals.axis_options[1]

    x = self.Table_source.data[ self.x_axis ]
    y = self.Table_source.data[ self.y_axis ]
    c = self.Table_source.data[ 'CL_color' ]
    n = self.Table_source.data[ 'CL_name' ]
    
    self.plot_source.data.update( { 'x' : x, 'y' : y, 'CL_color' : c, 'CL_name' : n } )

    self.x_sel_widget = Select( options=vals.axis_options, value=self.x_axis, 
                              title=self.plot_name + ' - x axis', width=150 )
    self.x_sel_widget.on_change( 'value', self.x_axis_sel_callback )

    self.y_sel_widget = Select( options=vals.axis_options, value = self.y_axis, 
                              title = self.plot_name + ' - y axis', width=150 )
    self.y_sel_widget.on_change( 'value', self.y_axis_sel_callback )

    self.figure = figure( title=self.plot_name, 
                          plot_width=VP_default_width, 
                          plot_height=VP_default_height,
                          output_backend="webgl",
                          tools="pan,box_zoom,wheel_zoom,reset,save" )
    
    self.circles = self.figure.circle( x='x', y='y', source=self.plot_source, 
                                       color='CL_color', legend='CL_name' )

    self.hover = HoverTool( tooltips = [ (self.x_axis, "@x"), (self.y_axis, "@y") ] )
    self.figure.add_tools( self.hover )

    self.figure.xaxis.axis_label = self.x_axis
    self.figure.yaxis.axis_label = self.y_axis
    self.figure.yaxis.axis_label_standoff = 5

    self.figure.toolbar.logo = None

#~##############################################################################
class TimeSeriesPlot:

  #~============================================================================
  def TS_select_callback( self, lst ):

    if len( lst ) > self.max_selection:
      n = self.max_selection
      lst = lst[-n:]

    n = len( lst )
    self.Table_source.selected.indices = lst
    self.selection_lst = lst
    
    for i in range( self.max_selection ):
      if i < n:
        k = lst[i]
        x = self.TS_Table_source.data[ self.x_axis ][k]
        y = self.TS_Table_source.data[ self.y_axis ][k]
        self.lines_src[i].data.update( { 'x': x, 'y': y } )      
        self.lines_glyph[i].visible = True
      else:
        self.lines_src[i].data.update( { 'x': [], 'y': [] } )      
        self.lines_glyph[i].visible = False

  #~============================================================================
  def y_axis_sel_callback( self, attr, old, new ):
    self.y_axis = new
    self.figure.yaxis.axis_label = self.y_axis
    self.TS_select_callback( self.selection_lst )
    self.hover.tooltips = [ (self.x_axis, "@x"), (self.y_axis, "@y") ]

  #~============================================================================
  def Create( self, plot_name, vals ):
  
    self.max_selection = 4
    self.vals = vals
    self.Table_source = vals.Table_source
    
    self.selection_lst = [2,3,4]

    self.TS_Table_source = vals.TS_Table_source

    self.plot_name = plot_name
    self.x_axis = 'time'
    self.y_axis = vals.TS_axis_options[0]

    self.Table_source.selected.indices = self.selection_lst

    self.y_sel_widget = Select( options = vals.TS_axis_options, 
                                value = self.y_axis, 
                                title = self.plot_name+' - y axis', 
                                width=250 )
    self.y_sel_widget.on_change( 'value', self.y_axis_sel_callback )

    self.figure = figure( title=self.plot_name, 
                          plot_width=TS_default_width, 
                          plot_height=TS_default_height,
                          output_backend="webgl",
                          tools="pan,box_zoom,wheel_zoom,reset,save" )

    self.lines_glyph = []
    self.line_name = []
    self.lines_src = []
    for i in range( self.max_selection ):      
      self.line_name.append( 'line' + str(i) )
      self.lines_src.append( ColumnDataSource( { 'x' : [], 'y': [] } ) )
      self.lines_glyph.append( self.figure.line( x='x', y='y', 
                                                 source=self.lines_src[i],
                                                 name=self.line_name[i], 
                                                 color=colors[i], 
                                                 visible = False ) )

    for (i, k) in enumerate( self.selection_lst ):
      x = self.TS_Table_source.data[ self.x_axis ][k]
      y = self.TS_Table_source.data[ self.y_axis ][k]
      self.lines_src[i].data.update( { 'x': x, 'y': y } )      
      self.lines_glyph[i].visible = True

    self.hover = HoverTool( tooltips = [ (self.x_axis, "@x"), (self.y_axis, "@y") ] )
    self.figure.add_tools( self.hover )

    self.figure.xaxis.axis_label = self.x_axis
    self.figure.yaxis.axis_label = self.y_axis
    self.figure.yaxis.axis_label_standoff = 5

    self.figure.toolbar.logo = None
  
    vals.register_select_callback( self.TS_select_callback )

#~##############################################################################
Values = ValData()

ValuesTable, VP_status_bar = Values.CreateValuesTab()
ValuesSelAllButton = Values.select_all_button()

Values_Tab_layout = layouts.column( ValuesSelAllButton, ValuesTable, VP_status_bar )
tab1 = Panel( child = Values_Tab_layout, title = 'Values table' )

VP_Plot1 = ValuesPlot()
VP_Plot1.Create( 'Values Plot 1', Values )

VP_Plot2 = ValuesPlot()
VP_Plot2.Create( 'Values Plot 2', Values )

VP_layout = layouts.Column( layouts.row( VP_Plot1.x_sel_widget, 
                                         VP_Plot1.y_sel_widget, 
                                         VP_Plot2.x_sel_widget, 
                                         VP_Plot2.y_sel_widget ), 
                            layouts.row( VP_Plot1.figure, 
                                         VP_Plot2.figure ) )
tab2 = Panel( child = VP_layout, title = 'Values plots' )

TSeries = ValData()

TSeries_Tab_layout, TS_status_bar = TSeries.CreateTimeSeriesTab()
TS_Tab3_layout = layouts.column( TSeries_Tab_layout, TS_status_bar )

tab3 = Panel( child = TS_Tab3_layout, title = 'TimeSeries table')

TS_Plot1 = TimeSeriesPlot()
TS_Plot1.Create( 'TimeSeries Plot 1', TSeries )

TS_Plot2 = TimeSeriesPlot()
TS_Plot2.Create( 'TimeSeries Plot 2', TSeries )

TS_Plot2.figure.x_range = TS_Plot1.figure.x_range

TS_layout = layouts.Column( layouts.row( TS_Plot1.y_sel_widget, 
                                         TS_Plot2.y_sel_widget ), 
                            layouts.column( TS_Plot1.figure, 
                                            TS_Plot2.figure ) )
tab4 = Panel( child = TS_layout, title = 'TimeSeries plots' )

tabs_object = Tabs( tabs = [ tab1, tab2, tab3, tab4 ] )

curdoc().title = "OPERA - Mutriku Post-process V0.17"
curdoc().add_root( tabs_object )