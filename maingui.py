import sys          #test

import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QFileDialog
from PyQt5.QtGui import QResizeEvent
from PyQt5 import uic
import Test

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi("vopguiscrollable.ui", self)

        self.checkAODX.stateChanged.connect(self.refreshDataProcessingPlot)
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
        Test.set_plot_in_box(self.graphicsTimeTraces)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()