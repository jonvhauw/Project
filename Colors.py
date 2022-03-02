import pyqtgraph as pg
import PyQt5 as qt

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

def make_pen(color= 're', style='solid'):
    global color_dict
    if style == 'dashed':
        pen = pg.mkPen(color_dict[color], style=qt.QtCore.Qt.DashLine)
    else:
        pen = pg.mkPen(color_dict[color])
    return pen
