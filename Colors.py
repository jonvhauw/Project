from matplotlib import style
import pyqtgraph as pg
import PyQt5 as qt
import numpy as np
import matplotlib.pyplot as plt
from math import fmod
color_dict = {}
color_dict['lg'] = (144,238,144)
color_dict['lg'] = (144,238,144)
color_dict['dg'] = (144,238,144)
color_dict['db'] = (0,0,139)
color_dict['tu'] = (48, 213, 200)
color_dict['re'] = (255, 0, 0)
color_dict['dr'] = (139, 0, 0)
color_dict['bl'] = (0, 0, 255)
color_dict['go'] = (255,215,0)

style_dict = {}
style_dict['solid'] = qt.QtCore.Qt.SolidLine
style_dict['dashed'] = qt.QtCore.Qt.DashLine
style_dict['dotted'] = qt.QtCore.Qt.DotLine
style_dict['dashed/dotted'] = qt.QtCore.Qt.DashDotLine

def make_pen(color= 're', style='solid', width=1):
    global color_dict
    
    pen = pg.mkPen(color_dict[color], style=style_dict[style], width=width)
    
    return pen

