import pyqtgraph as pg
import PyQt5 as qt
import numpy as np
import matplotlib.pyplot as plt
from math import fmod
color_dict = {}
#color_dict['lg'] = (144,238,144)
color_dict['light green'] = (144,238,144)
color_dict['dark green'] = (144,238,144)
color_dict['dark blue'] = (0,0,139)
color_dict['turquoise'] = (48, 213, 200)
color_dict['red'] = (255, 0, 0)
color_dict['dark red'] = (139, 0, 0)
color_dict['blue'] = (0, 0, 255)
color_dict['gold'] = (255,215,0)


def make_pen(color= 're', style='solid', width=1):
    global color_dict
    if style == 'dashed':
        pen = pg.mkPen(color_dict[color], style=qt.QtCore.Qt.DashLine, width=width)
    else:
        pen = pg.mkPen(color_dict[color], width=width)
    return pen

