
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui
import Colors
import matplotlib.cm as cm
import matplotlib as mpl

app = pg.QtGui.QApplication([])

x = np.random.rand(500,50,50)

pg.setConfigOptions(antialias=True)

# main graphics window
view = pg.GraphicsView()

# show the window
#view.show()

# add a plotItem
imv = pg.ImageView()
imv.show()
# add the plotItem to the graphicsWindow and set it as central
#view.setCentralItem(p)

# create an image object
img = pg.ImageItem(border='w', levels=(x.min(),x.max()))

tr = QtGui.QTransform()  # prepare ImageItem transformation:
tr.scale(0.4, 10)
# add the imageItem to the plotItem
img.setTransform(tr)
colors = [
            (0, 0, 0),
            (4, 5, 61),
            (84, 42, 55),
            (15, 87, 60),
            (208, 17, 141),
            (255, 255, 255)
        ]

norm = mpl.colors.Normalize(vmin=0, vmax=x.max())
cmap = cm.jet
m = cm.ScalarMappable(norm=norm, cmap=cmap)

# color map
#cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)
#cmap = Colors.generatePgColormap('plasma')
#print(cmap)
# setting color map to the image view
#imv.setColorMap(cmap)

imv.setImage(x)
app.exec_()
# hide axis and set title


# data generator
'''
cnt=0
def animLoop():
    global cnt
    if cnt < x.shape[0]:
        imv.setImage(m.to_rgba(x[cnt]))
    cnt+=1

slider = QtGui.QSlider()
slider.setOrientation(QtCore.Qt.Horizontal)
slider.setMinimum(0)
# max is the last index of the image list
slider.setMaximum(x.shape[0])
imv.addWidget(slider)

slider.sliderMoved.connect(animLoop)



#timer2 = QtCore.QTimer()
#timer2.setInterval(100)
#timer2.timeout.connect(animloop2)

timer = QtCore.QTimer()
timer.setInterval(1000)
timer.timeout.connect(animLoop)
timer.start(2000)

app.exec_()
'''