
import numpy as np
import sys

import sys          #test


import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QFileDialog
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QThreadPool
from PyQt5 import uic
import Test
from time import sleep

#add plot directly in main class 
'''
def initUI(self):
    self.x = np.array([1,2,3,4])
    self.y = np.array([1,4,9,16])
    self.plt = pg.PlotWidget()
    self.plot = self.plt.plot(self.x, self.y)
    [...]

name_plot and datax, datay comes from progress.emit(str, array, array)
def addDataToPlot(self, name_plot, datax, datay):
    [...]
    self.x = np.append(self.x, data['x'])
    self.y =np.append(self.y, data['y'])
    self.plot.setData(self.x, self.y)
'''

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, np.ndarray)

    def run(self):
        """Long-running task."""
        for i in range(5):
            sleep(1)
            self.progress.emit(i + 1, np.array([1, 2]))
        self.finished.emit()
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi("vopguiscrollable.ui", self)

        self.checkAODX.stateChanged.connect(self.runLongTask)
        self.checkAODY.stateChanged.connect(self.refreshDataProcessingPlot)
        self.checkAODSync.stateChanged.connect(self.refreshDataProcessingPlot)
        self.checkSPCM.stateChanged.connect(self.refreshDataProcessingPlot)
        self.checkEField.stateChanged.connect(self.refreshDataProcessingPlot)
        self.checkSPCMSync.stateChanged.connect(self.refreshDataProcessingPlot)

        self.comboColorAODX.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboColorAODY.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboColorAODSync.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboColorSPCM.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboColorEField.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboColorSPCMSync.currentIndexChanged.connect(self.refreshDataProcessingPlot)

        self.comboStyleAODX.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboStyleAODY.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboStyleAODSync.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboStyleSPCM.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboStyleEField.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboStyleSPCMSync.currentIndexChanged.connect(self.refreshDataProcessingPlot)

        self.actionimport_files.triggered.connect(self.getfiles)

        self.test()

    def refreshDataProcessingPlot(self):
        self.scene = QGraphicsScene()
        self.graphicsTimeTraces.setScene(self.scene)

        self.plotWdgt = pg.PlotWidget(self.scene)
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        plot_item = self.plotWdgt.plot(data)

        proxy_widget = self.scene.addWidget(self.plotWdgt)
        self.graphicsTimeTraces.fitInView(self.scene.sceneRect())
        print("check button changed")

    def getfiles(self):
      dlg = QFileDialog()
      dlg.setFileMode(QFileDialog.AnyFile)
      dlg.setFileMode(QFileDialog.ExistingFiles)
      #filenames = QStringList()
		
      if dlg.exec_():
         self.filenames = dlg.selectedFiles()

         print(self.filenames)
    
    def resizeEvent(self, event: QResizeEvent):
        self.graphicsTimeTraces.fitInView(self.scene.sceneRect())
    
    def test(self):
        Test.set_image_in_box(self.graphicsTimeTraces)
    
    def runLongTask(self):
        print('start')
        threadCount = QThreadPool.globalInstance().maxThreadCount()
        print(threadCount)
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()
        # Final resets
        self.checkAODX.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.checkAODX.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.checkAODX.setText("done")
        )
    def reportProgress(self, n, ar):
        self.checkAODX.setText(f"Long-Running Step: {n}" + str(ar))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()