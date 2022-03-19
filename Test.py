
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui
import Colors
import matplotlib.cm as cm
import matplotlib as mpl
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QFileDialog
'''
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
'''

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
def twin_plot():
    plotWidget1 = pg.plot(title="Three plot curves")
    plotWidget2 = pg.plot(title="Three plot curves")
    plotWidget1.setXLink(plotWidget2)
    x = [0, 1, 2, 3, 4]
    y1 = [0, 1, 2, 3, 4]
    y2 = np.array(y1)*10

    plot1 = plotWidget1.plot(x, y1)
    plot2 = plotWidget2.plot(x, y2)

    #plot2.plot(x, y2)

def set_plot_in_box(view):
    app = pg.QtGui.QApplication([])
    x = [1, 2, 3, 4, 5, 6, 7 ,8 ,9, 10]
    y = [0, 1, 2,3, 4 ,5, 6, 7, 8, 9]
    scene = QGraphicsScene()
    view.setScene(scene)
    ploti = pg.PlotItem()
    ploti.plot(x, y)
    scene.addItem(ploti)


def set_image_in_box(view):
    x = np.random.rand(50,50)
    scene = QGraphicsScene()
    view.setScene(scene)
    img = pg.ImageItem(x)
    scene.addItem(img)
'''
twin_plot()
## Start Qt event loop.
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1 or not hasattr(pg.QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.exec_()
'''

pg.mkQApp()
 
pw = pg.PlotWidget()
pw.show()
#pw.setWindowsTitle('pyqtgraph example: MultiplePlotAxes')
p1 = pw.plotItem
p1.setLabels(left='axis 1')
 
## create a new ViewBox, link the right axis to its coordinate system
p2 = pg.ViewBox()
p1.showAxis('right')
p1.scene().addItem(p2)
p1.getAxis('right').linkToView(p2)
p2.setXLink(p1)
p1.getAxis('right').setLabel('axis2', color='#0000ff')
 
## create third ViewBox. 
## this time we need to create a new axis as well.

 
 
## Handle view resizing 
def updateViews():
    ## view has resized; update auxiliary views to match
    global p1, p2, p3
    p2.setGeometry(p1.vb.sceneBoundingRect())
    p3.setGeometry(p1.vb.sceneBoundingRect())
     
    ## need to re-update linked axes since this was called
    ## incorrectly while views had different shapes.
    ## (probably this should be handled in ViewBox.resizeEvent)
    p2.linkedViewChanged(p1.vb, p2.XAxis)
    p3.linkedViewChanged(p1.vb, p3.XAxis)
 
updateViews()
p1.vb.sigResized.connect(updateViews)
 
 
p1.plot([1,2,4,8,16,32])
p2.addItem(pg.PlotCurveItem([10,20,40,80,40,20], pen='b'))
p3.addItem(pg.PlotCurveItem([3200,1600,800,400,200,100], pen='r'))
 
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()