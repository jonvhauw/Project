# test

import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QFileDialog
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QThreadPool

import TDMS as tdms
import TDMSDataProcessing as tdmsData
import TDMSPlotTraces as tdmsPlot
import TDMSAnimateTraces as tdmsAnimate
import TDMSDataAnalysis as tdmsAnalysis
import TDMSEKModel as tdmsEKModel
import TDMSSaveData as tdmsSave
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread

tdmsPlot.plotExtField = True
tdmsPlot.plotSPCM = True
tdmsPlot.plotSPCMSync = True
tdmsPlot.plotAOD = True
tdmsPlot.plotAODSync = True



class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi("vopguiscrollable.ui", self)

        self.checkAODX.stateChanged.connect(self.refreshDataProcessingPlotAOD)
        self.checkAODY.stateChanged.connect(self.refreshDataProcessingPlotAOD)
        self.checkAODSync.stateChanged.connect(self.refreshDataProcessingPlotAODSync)
        self.checkSPCM.stateChanged.connect(self.refreshDataProcessingPlotSPCM)
        self.checkEField.stateChanged.connect(self.refreshDataProcessingPlotEField)
        self.checkSPCMSync.stateChanged.connect(self.refreshDataProcessingPlotSPCMSync)
        self.updateFrames.stateChanged.connect(self.plot_existing_frames)


        self.checkVelocityFitting_3.stateChanged.connect(self.refreshDataAnalysisOverlap)
        self.checkEEmaxFitting_3.stateChanged.connect(self.refreshDataAnalysisOverlap)
        self.checkAverageFitting_3.stateChanged.connect(self.refreshDataAnalysisOverlap)

        self.checkEEmaxPosition_3.stateChanged.connect(self.refreshDataAnalysisPositionVelocity)
        self.checkEEmaxVelocity_3.stateChanged.connect(self.refreshDataAnalysisPositionVelocity)
        self.checkYPositionFilter_3.stateChanged.connect(self.refreshDataAnalysisPositionVelocity)
        self.checkYVelocity_3.stateChanged.connect(self.refreshDataAnalysisPositionVelocity)
        self.checkYPosition_3.stateChanged.connect(self.refreshDataAnalysisPositionVelocity)





        self.comboColorAODX.currentIndexChanged.connect(self.plot)
        self.comboColorAODY.currentIndexChanged.connect(self.plot)
        self.comboColorAODSync.currentIndexChanged.connect(self.plot)
        self.comboColorSPCM.currentIndexChanged.connect(self.plot)
        self.comboColorEField.currentIndexChanged.connect(self.plot)
        self.comboColorSPCMSync.currentIndexChanged.connect(self.plot)

        self.comboColorVelocityFitting_3.currentIndexChanged.connect(self.plot_overlapping_periods)
        self.comboColorAverageFitting_3.currentIndexChanged.connect(self.plot_overlapping_periods)
        self.comboColorEEmaxFitting_3.currentIndexChanged.connect(self.plot_overlapping_periods)

        self.comboStyleVelocityFitting_3.currentIndexChanged.connect(self.plot_overlapping_periods)
        self.comboStyleAverageFitting_3.currentIndexChanged.connect(self.plot_overlapping_periods)
        self.comboStyleEEmaxFitting_3.currentIndexChanged.connect(self.plot_overlapping_periods)

        self.comboColorEEmaxTrace_3.currentIndexChanged.connect(self.plot_position_and_velocity_trace)
        self.comboColorYTrace_3.currentIndexChanged.connect(self.plot_position_and_velocity_trace)
        self.comboColorYPosition_3.currentIndexChanged.connect(self.plot_position_and_velocity_trace)

        self.comboStyleEEmaxTrace_3.currentIndexChanged.connect(self.plot_position_and_velocity_trace)
        self.comboStyleYTrace_3.currentIndexChanged.connect(self.plot_position_and_velocity_trace)

        self.actionimport_files.triggered.connect(self.getfiles)
        #self.actionimport_saved_files.triggered.connect(self.get_saved_files)

        self.spinBoxStart.valueChanged.connect(self.show_startTime)
        self.spinBoxStop.valueChanged.connect(self.show_stopTime)

        self.buttonUpdate.clicked.connect(self.update)
        self.autoOffset.clicked.connect(self.calculate_offset)
        self.generateFrames.clicked.connect(self.generate_frames)
        self.processData.clicked.connect(self.process_data)
        self.plotKymo.clicked.connect(self.kymo_matplot)
        self.saveData.clicked.connect(self.save_data)

        self.comboStyleAODX.currentIndexChanged.connect(self.plot)
        self.comboStyleAODY.currentIndexChanged.connect(self.plot)
        self.comboStyleAODSync.currentIndexChanged.connect(self.plot)
        self.comboStyleSPCM.currentIndexChanged.connect(self.plot)
        self.comboStyleEField.currentIndexChanged.connect(self.plot)
        self.comboStyleSPCMSync.currentIndexChanged.connect(self.plot)


        self.spinBoxeFieldSync.setMinimum(-1)
        self.spinBoxSPCMSync.setMinimum(-1)

        self.spinBoxStart.setValue(43.1)
        self.spinBoxStop.setValue(43.85)
        self.spinBoxeFieldSync.setValue(0.0028518545866624834)
        self.spinBoxSPCMSync.setValue(0.0017841314182235968)

        self.imageSlider.sliderMoved.connect(self.move_slider)
        #self.imageSlider.sliderReleased.connect(self.move_slider)

        
    def refreshDataProcessingPlot(self):
        self.scene = QGraphicsScene()
        self.graphicsTimeTraces.setScene(self.scene)

        self.plotWdgt = pg.PlotWidget(self.scene)
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        plot_item = self.plotWdgt.plot(data)

        proxy_widget = self.scene.addWidget(self.plotWdgt)
        self.graphicsTimeTraces.fitInView(self.scene.sceneRect())
        print("check button changed")



    def resizeEvent(self, event: QResizeEvent):
        self.graphicsTimeTraces.fitInView(self.scene.sceneRect())
        self.graphicsFrames.fitInView(self.scene.sceneRect())
        self.graphicsOverlappingPeriods.fitInView(self.scene.sceneRect())
        self.graphicsVelocity_2.fitInView(self.scene.sceneRect())
        self.graphicsParticlePositionTrace.fitInView(self.scene.sceneRect())
        self.graphicsParticleVelocityTrace.fitInView(self.scene.sceneRect())
        self.graphicsKymoX.fitInView(self.scene.sceneRect())
        self.graphicsKymoY.fitInView(self.scene.sceneRect())

    def getfiles(self):
        dlg = QFileDialog()
        dlg.setDirectory("C:\\Users\\jonas\\OneDrive\\Documenten\\Bach3\\Project\\Data")
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFileMode(QFileDialog.ExistingFiles)
        #filenames = QStringList()
            
        if dlg.exec_():
            self.filenames = dlg.selectedFiles()

        self.update()

    def get_saved_files(self):
        dlg = QFileDialog()
        dlg.setDirectory("C:\\Users\\jonas\\OneDrive\\Documenten\\Bach3\\Project\\Data")
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFileMode(QFileDialog.ExistingFiles)
        #filenames = QStringList()
            
        if dlg.exec_():
            self.savedFilenames = dlg.selectedFiles()

        self.read_saved_data()

    def read_saved_data(self):
        global frameTimeStampArray,frameSumWidthCentroidArray,frameSumHeightCentroidArray,frameSumWidthArrayList,frameSumHeightArrayList
        global compensateOutliers
        compensateOutliers=True
        tdmsPathList = self.savedFilenames
        tdmsPathList,tdmsFolderPath,experimentName = tdms.get_tdms_file_path2(tdmsPathList)
        tdmsFileList,txtDataFilePath = tdms.read_tdms_file_list(tdmsFilePathList=tdmsPathList)
        frameTimeStampArray,frameSumWidthCentroidArray,frameSumHeightCentroidArray,frameSumWidthArrayList,frameSumHeightArrayList = tdmsSave.read_data_from_txt(savedDataPath=txtDataFilePath)
        #self.plot_existing_frames()
        self.processData.setEnabled(True)

    #functions to show certain parameters at a current time 
    def show_startTime(self):
        # getting current value
        value = self.spinBoxStart.value()
        print('Starttime: ', value)

    def show_stopTime(self):
        # getting current value
        value = self.spinBoxStop.value()
        print('Stoptime: ', value)

    def showoffsetExtFieldTime(self):
        value = self.spinBoxAODXSync.value()
        print('Offset external field: ', value)

    def showoffsetSPCMTime(self):
        value = self.spinBoxSPCMSync.value()
        print('Offset SPCM: ', value)

    def calculate_offset(self):
        global AODSyncTimeArray, AODSyncDataArray, SPCMSyncDataArray, SPCMSyncTimeArray
        global eFieldTimeArray, eFieldDataArray

        self.autoOffset.setEnabled(False)

        offsetExtFieldTimeAuto, offsetSPCMTimeAuto, Period = tdmsData.find_auto_offset(AODSyncTimeArray=AODSyncTimeArray, AODSyncDataArray=AODSyncDataArray, SPCMSyncTimeArray=SPCMSyncTimeArray, 
                                    SPCMSyncDataArray=SPCMDataArray, eFieldTimeArray=eFieldTimeArray, eFieldDataArray=eFieldDataArray)   

        self.spinBoxeFieldSync.setMinimum(-1)
        self.spinBoxSPCMSync.setMinimum(-1)
        self.spinBoxeFieldSync.setValue(offsetExtFieldTimeAuto)
        self.spinBoxSPCMSync.setValue(offsetSPCMTimeAuto)
        self.autoOffset.setEnabled(True)

    def update(self):
        print('start')
        threadCount = QThreadPool.globalInstance().maxThreadCount()
        print(threadCount)
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = update_start()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report)
        # Step 6: Start the thread
        self.thread.start()
        # Final resets
        self.buttonUpdate.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.buttonUpdate.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.buttonUpdate.setText("Update")
        )
        self.thread.finished.connect(self.plot)
        self.thread.finished.connect(lambda: self.generateFrames.setEnabled(True))
        self.thread.finished.connect(lambda: self.updateFrames.setEnabled(True))

    def plot(self):
        global AODTimeArray, AOD1DataArray, AOD2DataArray
        global pixelNumberArray, SPCMTimeArray, SPCMDataArray
        global eFieldTimeArray, eFieldDataArray
        global discontTimeArray, discontDataArray
        global AODSyncTimeArray, AODSyncDataArray, SPCMSyncDataArray, SPCMSyncTimeArray
        self.scene = QGraphicsScene()
        self.graphicsTimeTraces.setScene(self.scene)

        plotje= tdmsPlot.plot_trace2(self.scene, AODTimeArray=AODTimeArray,AOD1DataArray=AOD1DataArray,AOD2DataArray=AOD2DataArray,
                             pixelNumberArray=pixelNumberArray,SPCMTimeArray=SPCMTimeArray,SPCMDataArray=SPCMDataArray,
                             eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldDataArray,discontTimeArray=discontTimeArray,discontDataArray=discontDataArray,AODSyncTimeArray=AODSyncTimeArray,AODSyncDataArray=AODSyncDataArray,
                             SPCMSyncDataArray=SPCMSyncDataArray,SPCMSyncTimeArray=SPCMSyncTimeArray,  AOD1_c=self.comboColorAODX.currentText(), AOD2_c = self.comboColorAODY.currentText(), SPCM_c = self.comboColorSPCM.currentText(),EF_c = self.comboColorEField.currentText(), SPCM_sync_c = self.comboColorSPCMSync.currentText(), AOD_sync_c = self.comboColorAODSync.currentText(), AOD1_s=self.comboStyleAODX.currentText(), AOD2_s = self.comboStyleAODY.currentText(), SPCM_s = self.comboStyleSPCM.currentText(), EF_s = self.comboStyleEField.currentText(), SPCM_sync_s = self.comboStyleSPCMSync.currentText(), AOD_sync_s = self.comboStyleAODSync.currentText())



        proxy_widget = self.scene.addWidget(plotje)
        self.graphicsTimeTraces.fitInView(self.scene.sceneRect())

    def report(self, string=""):
        self.buttonUpdate.setText(string)
        

    def refreshDataProcessingPlotAOD(self):
        tdmsPlot.plotAODY = self.checkAODY.isChecked() 
        tdmsPlot.plotAODX = self.checkAODX.isChecked()

        self.update2()

    def refreshDataProcessingPlotAODSync(self):

        tdmsPlot.plotAODSync = self.checkAODSync.isChecked()

        self.update2()

    def refreshDataProcessingPlotSPCM(self):

        tdmsPlot.plotSPCM = self.checkSPCM.isChecked()

        self.update2()

    def refreshDataProcessingPlotSPCMSync(self):
  
        tdmsPlot.plotSPCMSync = self.checkSPCMSync.isChecked()

        self.update2()

    def refreshDataProcessingPlotEField(self):
        tdmsPlot.plotExtField = self.checkEField.isChecked()

        self.update2()

    def refreshDataAnalysisOverlap(self):
        tdmsPlot.plotExtField = self.checkEEmaxFitting_3.isChecked()
        tdmsPlot.plotAverage = self.checkAverageFitting_3.isChecked()
        tdmsPlot.plotVelocity = self.checkVelocityFitting_3.isChecked()
        
        self.plot_overlapping_periods()

    def refreshDataAnalysisPositionVelocity(self):
        tdmsPlot.plotExtField1 = self.checkEEmaxPosition_3.isChecked()
        tdmsPlot.plotExtField2 = self.checkEEmaxVelocity_3.isChecked()
        tdmsPlot.plotYPosition = self.checkYPosition_3.isChecked()
        tdmsPlot.plotYPositionFilter = self.checkYPositionFilter_3.isChecked()
        tdmsPlot.plotYVelocity = self.checkYVelocity_3.isChecked()

        self.plot_position_and_velocity_trace()

    def update2(self):
        global AODTimeArray, AOD1DataArray, AOD2DataArray
        global pixelNumberArray, SPCMTimeArray, SPCMDataArray
        global eFieldTimeArray, eFieldDataArray
        global discontTimeArray, discontDataArray
        global AODSyncTimeArray, AODSyncDataArray, SPCMSyncDataArray, SPCMSyncTimeArray
        global offsetExtField0, offsetSPCM0 

        AOD1_s_value = self.comboStyleAODX.currentText()
        print('AOD1 waarde is: ', AOD1_s_value)


        offsetExtFieldTime = window.spinBoxeFieldSync.value()
        offsetSPCMTime = window.spinBoxSPCMSync.value()



        eFieldTimeArray += (offsetExtFieldTime-offsetExtField0)
        SPCMTimeArray += (offsetSPCMTime-offsetSPCM0)

        offsetExtField0 = offsetExtFieldTime
        offsetSPCM0 = offsetSPCMTime



        self.scene = QGraphicsScene()
        self.graphicsTimeTraces.setScene(self.scene)

        plotje= tdmsPlot.plot_trace2(self.scene, AODTimeArray=AODTimeArray,AOD1DataArray=AOD1DataArray,AOD2DataArray=AOD2DataArray,
                             pixelNumberArray=pixelNumberArray,SPCMTimeArray=SPCMTimeArray,SPCMDataArray=SPCMDataArray,
                             eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldDataArray,discontTimeArray=discontTimeArray,discontDataArray=discontDataArray,AODSyncTimeArray=AODSyncTimeArray,AODSyncDataArray=AODSyncDataArray,
                             SPCMSyncDataArray=SPCMSyncDataArray,SPCMSyncTimeArray=SPCMSyncTimeArray,  AOD1_c=self.comboColorAODX.currentText(), AOD2_c = self.comboColorAODY.currentText(), SPCM_c = self.comboColorSPCM.currentText(),EF_c = self.comboColorEField.currentText(), SPCM_sync_c = self.comboColorSPCMSync.currentText(), AOD_sync_c = self.comboColorAODSync.currentText(), AOD1_s=self.comboStyleAODX.currentText(), AOD2_s = self.comboStyleAODY.currentText(), SPCM_s = self.comboStyleSPCM.currentText(), EF_s = self.comboStyleEField.currentText(), SPCM_sync_s = self.comboStyleSPCMSync.currentText(), AOD_sync_s = self.comboStyleAODSync.currentText())



        proxy_widget = self.scene.addWidget(plotje)
        #self.graphicsTimeTraces.resizeScene()
        self.graphicsTimeTraces.fitInView(self.scene.sceneRect())
    
    def generate_frames(self):
        print('start')

        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = generate_frames()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.plot_existing_frames)
        # Step 6: Start the thread
        self.thread.start()
        # Final resets
        self.generateFrames.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.generateFrames.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.generateFrames.setText("generate frames")
        )
        self.thread.finished.connect(self.plot_existing_frames)
        self.thread.finished.connect(lambda: self.generateFrames.setEnabled(True))
        self.thread.finished.connect(lambda: self.processData.setEnabled(True))

    
    def plot_existing_frames(self):
        #x = np.random.rand(4, 30, 30, 500)

        global frameTimeStampArrayList,frameArrayListList
        global frameArrayList2, frameTimeStampArray2
        frameTimeStampArray2 = tdmsData.ravel_list_of_arrays(arrayList=frameTimeStampArrayList)
        frameArrayList2 = tdmsData.ravel_list_of_lists(listList=frameArrayListList)
        #self.imageSlider.setRange(frameTimeStampArray2[0], frameTimeStampArray2[-1])
        self.imageSlider.setRange(0, len(frameTimeStampArray2)-1)
        if self.updateFrames.isChecked():
                self.scene = QGraphicsScene()
                self.graphicsFrames.setScene(self.scene)
                imv = tdmsPlot.plot_frame_video_and_sums_slider(scene=self.scene, i=self.imageSlider.value(), frameArray=np.array(frameArrayList2),pitchX=tdmsAnimate.pitchX,pitchY=tdmsAnimate.pitchY, timeArray=frameTimeStampArray2)
                #imv = tdmsPlot.plot_frame_video_and_sums2(scene=self.scene, frameArray=x,pitchX=1,pitchY=1, timeArray=np.array([i for i in range(500)]))
                #proxy_widget = self.scene.addWidget(pw)
                proxy_widget2 = self.scene.addWidget(imv)
                #self.graphicsFrames.resizeScene()
                self.graphicsFrames.fitInView(self.scene.sceneRect())
    
    def move_slider(self):
        global frameArrayList2, frameTimeStampArray2
        i = self.imageSlider.value()
        self.scene = QGraphicsScene()
        self.graphicsFrames.setScene(self.scene)
        imv = tdmsPlot.plot_frame_video_and_sums_slider(scene=self.scene, i=i, frameArray=np.array(frameArrayList2),pitchX=tdmsAnimate.pitchX,pitchY=tdmsAnimate.pitchY, timeArray=frameTimeStampArray2)
        #imv = tdmsPlot.plot_frame_video_and_sums2(scene=self.scene, frameArray=x,pitchX=1,pitchY=1, timeArray=np.array([i for i in range(500)]))
        proxy_widget = self.scene.addWidget(imv)
        self.graphicsFrames.fitInView(self.scene.sceneRect())
    
    def process_data(self):
        print('start')
        self.tabWidget.setCurrentIndex(1)
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = process_data()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.fitted_velocity1.connect(self.plot_fitted_velocity1)
        self.worker.fitted_velocity2.connect(self.plot_fitted_velocity2)
        self.worker.position_and_velocity_trace.connect(self.plot_position_and_velocity_trace)
        self.worker.overlapping_periods.connect(self.plot_overlapping_periods)
        self.worker.kymograph.connect(self.plot_kymograph)
        # Step 6: Start the thread
        self.thread.start()
        # Final resets
        self.processData.setEnabled(False)
        self.generateFrames.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.processData.setEnabled(True)
        )
        
        self.thread.finished.connect(lambda: self.generateFrames.setEnabled(True))
        self.thread.finished.connect(lambda: self.saveData.setEnabled(True))
    
    def plot_fitted_velocity1(self):
        print("plotting")
        global fitteduEPArray, uEO 

        self.scene = QGraphicsScene()
        self.graphicsVelocity_2.setScene(self.scene)
        plot, ueo, uep = tdmsPlot.plot_fitted_velocity_fixed_uEO_gui(scene=self.scene, fitteduEPArray=fitteduEPArray,uEO=uEO)
        proxy_widget = self.scene.addWidget(plot)

        

        #self.graphicsVelocity_2.resizeScene()
        self.graphicsVelocity_2.fitInView(self.scene.sceneRect())
        self.label_7.setText(str(ueo) + ' mm/s')
        self.label_8.setText(str(uep) + ' mm/s')

    def plot_fitted_velocity2(self):
        print("plotting")
        global fittedVelocityList, fittedCovVelocityList

        self.scene = QGraphicsScene()
        self.graphicsVelocity_2.setScene(self.scene)
        plot = tdmsPlot.plot_fitted_velocity_scatter_plot_gui(fittedVelocityList=fittedVelocityList,fittedCovVelocityList=fittedCovVelocityList)
        proxy_widget = self.scene.addWidget(plot)
        #self.graphicsVelocity_2.resizeScene()
        self.graphicsVelocity_2.fitInView(self.scene.sceneRect())

    def plot_position_and_velocity_trace(self):
        global frameTimeStampArray, eFieldTimeArray, eFieldStrengthDataArray
        global heightPositionArray, positionTimeArray, filteredHeightPositionArray, velocityTimeArray, heightVelocityArray

        self.scenePosition = QGraphicsScene()
        self.graphicsParticlePositionTrace.setScene(self.scenePosition)
        self.sceneVelocity = QGraphicsScene()
        self.graphicsParticleVelocityTrace.setScene(self.sceneVelocity)
        pos2, pos1, vel2, vel1, pw1, pw2 = tdmsPlot.plot_position_and_velocity_trace_gui(self.scenePosition, self.sceneVelocity, frameTimeStampArray=frameTimeStampArray,heightPositionArray=heightPositionArray,
                                         positionTimeArray=positionTimeArray,filteredHeightPositionArray=filteredHeightPositionArray,
                                         velocityTimeArray=velocityTimeArray,heightVelocityArray=heightVelocityArray,
                                         eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray, EEmaxTrace_c = self.comboColorEEmaxTrace_3.currentText(), YTrace_c = self.comboColorYTrace_3.currentText(), YPosition_c = self.comboColorYPosition_3.currentText(), EEmaxTrace_s = self.comboStyleEEmaxTrace_3.currentText(), YTrace_s = self.comboStyleYTrace_3.currentText()) 
        #proxy_widget1 = self.scenePosition.addWidget(pos1) 
        #proxy_widget2 = self.sceneVelocity.addWidget(vel1)
        #proxy_widget3 = self.scenePosition.addWidget(pos2) 
        #proxy_widget4 = self.sceneVelocity.addWidget(vel2)
        proxy_widget5 = self.scenePosition.addWidget(pw1) 
        proxy_widget6 = self.sceneVelocity.addWidget(pw2)
        #self.graphicsParticlePositionTrace.resizeScene()
        #self.graphicsParticleVelocityTrace.resizeScene()
        self.graphicsParticlePositionTrace.fitInView(self.scene.sceneRect())
        self.graphicsParticleVelocityTrace.fitInView(self.scene.sceneRect())
    
    def plot_overlapping_periods(self):
        global velocityTimeArrayList, heightVelocityArrayList, averageVelocityArray

        self.scene = QGraphicsScene()
        self.graphicsOverlappingPeriods.setScene(self.scene)
        pw, plotPeriod, ploteField = tdmsPlot.plot_overlapping_periods_gui(self.scene, timeArrayList=velocityTimeArrayList,dataArrayList=heightVelocityArrayList,averageVelocityTimeArray=np.linspace(0.0,1.0,100),averageVelocityArray=averageVelocityArray,eFieldFreq=tdmsEKModel.f, velocity_c = self.comboColorVelocityFitting_3.currentText(), average_c = self.comboColorAverageFitting_3.currentText() , EEmax_c = self.comboColorEEmaxFitting_3.currentText(), velocity_s = self.comboStyleVelocityFitting_3.currentText(), average_s = self.comboStyleAverageFitting_3.currentText(), EEmax_s = self.comboStyleEEmaxFitting_3.currentText())
        proxy_widget = self.scene.addWidget(pw)
        #self.graphicsOverlappingPeriods.resizeScene()
        self.graphicsOverlappingPeriods.fitInView(self.scene.sceneRect())

    def plot_kymograph(self):
        global frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList,frameSumWidthCentroidArray,frameSumHeightCentroidArray, filteredWidthPositionArray, filteredHeightPositionArray, eFieldTimeArray, eFieldStrengthDataArray
        global positionTimeArray

        self.scene1 = QGraphicsScene()
        self.scene2 = QGraphicsScene()

        self.graphicsKymoX.setScene(self.scene1)
        self.graphicsKymoY.setScene(self.scene2)

        pw1, pw2, kymox1, kymox2, kymoy1, kymoy2 = tdmsPlot.plot_double_kymograph_gui(self.scene1, self.scene2, xDataArrayList=frameSumWidthArrayList,yDataArrayList=frameSumHeightArrayList,frameTimeStampArray=frameTimeStampArray,eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray, 
                            positionTimeArray=positionTimeArray,frameSumHeightCentroidArray=filteredHeightPositionArray,frameSumWidthCentroidArray=filteredWidthPositionArray,pitchX=tdmsAnimate.pitchX,pitchY=tdmsAnimate.pitchY)    

        proxy_widget1 = self.scene1.addWidget(pw1)
        proxy_widget2 = self.scene2.addWidget(pw2)
        self.plotKymo.setEnabled(True)
        self.graphicsKymoX.fitInView(self.scene.sceneRect())
        self.graphicsKymoY.fitInView(self.scene.sceneRect())
    '''
    def kymo_matplot(self):
        thread = Thread(target =self.kymo_matplot2)
        thread.start()
        thread.join()
        print("thread finished...exiting")
    '''
    def kymo_matplot(self):
        global frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList,frameSumWidthCentroidArray,frameSumHeightCentroidArray, filteredWidthPositionArray, filteredHeightPositionArray, eFieldTimeArray, eFieldStrengthDataArray
        global positionTimeArray
        tdmsPlot.plot_kymograph(xDataArrayList=frameSumWidthArrayList,yDataArrayList=frameSumHeightArrayList,frameTimeStampArray=frameTimeStampArray,eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray, 
                            positionTimeArray=positionTimeArray,frameSumHeightCentroidArray=filteredHeightPositionArray,frameSumWidthCentroidArray=filteredWidthPositionArray,pitchX=tdmsAnimate.pitchX,pitchY=tdmsAnimate.pitchY)  
        '''
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = kymoMatplot()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        # Final resets
        self.plotKymo.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.plotKymo.setEnabled(True)
        )
        '''
    def save_data(self):
        self.saveData.setEnabled(False)
        global frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList,frameSumWidthCentroidArray,frameSumHeightCentroidArray, filteredWidthPositionArray, filteredHeightPositionArray
        global heightPositionArray, positionTimeArray, velocityTimeArray, heightVelocityArray 
        global widthPositionArrayList, heightPositionArrayList, positionTimeArrayList, filteredHeightPositionArrayList
        global velocityTimeArrayList, heightVelocityArrayList, averageVelocityArray, fitteduEPArray
        global tdmsFolderPath, experimentName
        global uEO, fixeduEO, fittedCovVelocityList, fittedVelocityList
     
        savedDataPath = tdmsSave.write_data_to_txt(frameTimeStampArray=frameTimeStampArray, frameSumWidthCentroidArray=frameSumWidthCentroidArray, frameSumHeightCentroidArray=frameSumHeightCentroidArray, 
                                                   frameSumHeightArrayList=frameSumHeightArrayList, frameSumWidthArrayList=frameSumWidthArrayList, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName)     
        
        tdmsSave.write_scaled_position_to_txt(frameTimeStampArray=frameTimeStampArray,frameTimeStampArrayList=frameTimeStampArrayList,widthPositionArrayList=widthPositionArrayList,heightPositionArrayList=heightPositionArrayList,
                                     tdmsFolderPath=tdmsFolderPath, experimentName=experimentName)
        
        tdmsSave.write_scaled_filtered_position_to_txt(frameTimeStampArray=frameTimeStampArray,positionTimeArrayList=positionTimeArrayList,filteredWidthPositionArrayList=filteredHeightPositionArrayList,
                                                       filteredHeightPositionArrayList=filteredHeightPositionArrayList,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName)
        
        tdmsSave.write_scaled_velocity_to_txt(frameTimeStampArray=frameTimeStampArray,velocityTimeArrayList=velocityTimeArrayList,velocityArrayList=heightVelocityArrayList,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName)
        if fixeduEO == True:
            tdmsSave.save_fixed_uEO_and_uEP_to_file(frameTimeStampArray=frameTimeStampArray, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName, fitteduEPArray=fitteduEPArray,uEO=uEO,velocityTimeArrayList=velocityTimeArrayList)
        else:
            tdmsSave.save_uEO_and_uEP_to_file(frameTimeStampArray=frameTimeStampArray, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName, fittedVelocityList=fittedVelocityList, fittedCovVelocityList=fittedCovVelocityList,velocityTimeArrayList=velocityTimeArrayList)
        self.saveData.setEnabled(True)       






class update_start(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def run(self):
        global pixelNumberArray, AODTimeArray, AODSyncTimeArray, AODSyncDataArray, SPCMDataArray, SPCMTimeArray, SPCMSyncTimeArray, SPCMSyncDataArray,eFieldDataArray, eFieldTimeArray
        global discontIndexArray
        global discontTimeArray,discontDataArray
        global discontTimeArray,discontDataArray
        global AOD1DataArray, AOD2DataArray
        global AOD1DataArray, AOD2DataArray
        global AODTimeArray,AOD1DataArray,AOD2DataArray,pixelNumberArray,SPCMTimeArray,SPCMDataArray,eFieldTimeArray,eFieldDataArray,discontTimeArray,discontDataArray,AODSyncTimeArray,AODSyncDataArray,SPCMSyncTimeArray,SPCMSyncDataArray
        global eFieldStrengthDataArray
        global offsetSPCM0, offsetExtField0



        timeSegment = [window.spinBoxStart.value(), window.spinBoxStop.value()]
        offsetExtFieldTime = window.spinBoxeFieldSync.value()
        offsetSPCMTime = window.spinBoxSPCMSync.value()

        comsolFieldFactor =  (23e3)*(6.5e-3)/10 # Conversion factor based on comsol simulation V/m/m/V
        electrodeSpacing = 6.5e-3 # Spacing between electrodes in m
        AODSpacialFactor = 8.2e-6/10  # AOD voltage to distance in focal plane m/V
        FPGAClockPeriod = 25e-9
        electrodePolarity = "Negative"  # Positive voltage means E-Field is in the opposite direction of positive displacement
        
        global z
        z = 0e-06
        
        """ 
        Scripting Parameters
        """    
        # Time Parameters
        #timeSegment =  [43.1,43.85]
        offsetExtField0 = offsetExtFieldTime
        offsetSPCM0 = offsetSPCMTime
        tdmsData.offsetExtFieldTime =offsetExtFieldTime
        tdmsData.offsetSPCMTime =offsetSPCMTime
        tdmsData.offsetOn = True
        
        
        plotSync = True
        
        
        # General Parameters
        tdmsPlot.plotTrace = True
        tdmsPlot.normalize = True
        tdmsPlot.plotKymo = True
        tdmsPlot.plotCentroidKymo = True
        
        tdmsAnimate.centroidCalculation = "gaussian fit"
        
        saveData = True
        readSavedData = False
        
        # AOD Parameters
        scanPattern = str(window.scanPattern.currentText())
        #tdmsPlot.plotAOD = True
        tdmsPlot.plotPixelNumber = False
        #tdmsPlot.plotAODSync = plotSync
        tdmsPlot.plotDiscont = False
        
        # SPCM Parameters
        #tdmsPlot.plotSPCM = True
        #tdmsPlot.plotSPCMSync = plotSync
        tdmsPlot.plotSPCMSampleRatio = 1
        tdmsData.filterSPCM = False
        tdmsData.windowSize = 50
        tdmsAnimate.darkCount = 2
        global compensateOutliers
        compensateOutliers=True
        
        
        # Ext Parameters
        #tdmsPlot.plotExtField = True
        tdmsPlot.plotExtFieldKymo = False
        
        # Fit Parameters
        global fixeduEO
        fixeduEO = True
        
        
        # Animation Parameters
        tdmsAnimate.animate = False
        tdmsAnimate.onlyImage = False
        tdmsAnimate.singleAxisSum = False
        tdmsAnimate.addCentroidLine = False
        tdmsAnimate.liveAnimation = False
        tdmsAnimate.displayTimeStamp = True    
        tdmsAnimate.saveVideo = False
        tdmsAnimate.combineVideos = True
        tdmsAnimate.maxFramesPerFragment = 300
        tdmsAnimate.pixelsPerFrame = 16*16
        tdmsAnimate.fps = 60
        tdmsAnimate.dpi = 110
        
        rollImage = False
        rollPixels = 0
        rollAxis = 0

        """ 
        Raw Data from TDMS
        """
        print("### Reading data from:\n")
        global tdmsFolderPath, experimentName
        tdmsPathList = window.filenames
        tdmsPathList,tdmsFolderPath,experimentName = tdms.get_tdms_file_path2(tdmsPathList)
        tdmsFileList,txtDataFilePath = tdms.read_tdms_file_list(tdmsFilePathList=tdmsPathList)
        tdmsHierarchyDictList = tdms.return_tdms_hierarchy_list(tdmsFileList=tdmsFileList)
        tdmsHierarchyDict = tdms.combine_tdms_hierarchy_list(tdmsHierarchyDictList=tdmsHierarchyDictList)
        tdms.print_tdms_hierarchy(tdmsHierarchyDict)
        pixelNumberArray, AODLoopTicksArray, SPCMDataArray, SPCMLoopTicksArray, eFieldDataArray, eFieldLoopTicksArray=tdms.return_raw_arrays_from_tdms_hierarchy(tdmsHierarchyDict=tdmsHierarchyDict)
        eFieldAmp,eFieldFreq,pitchX,pitchY,binSize,dotsPerLine, numberOfLines=tdms.return_parameters_from_tdms_hierarchy(tdmsHierarchyDict=tdmsHierarchyDict,comsolFieldFactor=comsolFieldFactor,electrodeSpacing=electrodeSpacing,AODSpacialFactor=AODSpacialFactor)
        
        tdmsAnalysis.filterCutoff = int(1.5*eFieldFreq)
        tdmsAnimate.pitchX = pitchX
        tdmsAnimate.pitchY = pitchY
        tdmsAnimate.pixelsPerFrame = max(pixelNumberArray)
        tdmsEKModel.f = eFieldFreq
        tdmsEKModel.E = eFieldAmp
        
        global uEO
        uEO = 0.00011 * tdmsHierarchyDict["Experiment Parameters"]['Amplitude (V)'][0]
        
        tdmsEKModel.init_dependent_variables()
        
        
        
        """ 
        Edit and generate data from TDMS
        """    
        print("### Generating signals and segmenting \n")
        self.progress.emit("Generating signals")
        pixelNumberArray, AODTimeArray, AODSyncTimeArray, AODSyncDataArray, SPCMDataArray, SPCMTimeArray, SPCMSyncTimeArray, SPCMSyncDataArray,eFieldDataArray, eFieldTimeArray = tdmsData.return_arrays_from_tdms_hierarchy2(pixelNumberArray=pixelNumberArray, AODLoopTicksArray=AODLoopTicksArray, SPCMDataArray=SPCMDataArray,
                                                                                                                                                                                                                            SPCMLoopTicksArray=SPCMLoopTicksArray, eFieldDataArray=eFieldDataArray, eFieldLoopTicksArray=eFieldLoopTicksArray,
                                                                                                                                                                                                                            FPGAClockPeriod=FPGAClockPeriod,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName)
        discontIndexArray = tdmsData.locate_AOD_discontinuities(pixelNumberArray=pixelNumberArray)
        discontTimeArray,discontDataArray = tdmsData.discont_index_to_time_and_data_array(discontIndexArray=discontIndexArray, AODTimeArray=AODTimeArray)
        AOD1DataArray, AOD2DataArray   = tdmsData.pixel_number_array_to_AOD_grid_index_arrays(pixelNumberArray=pixelNumberArray,amountOfLines=int(numberOfLines),pixelsPerLine=int(dotsPerLine),lineAxis=0,scanningPattern=scanPattern)
        AODTimeArray,AOD1DataArray,AOD2DataArray,pixelNumberArray,SPCMTimeArray,SPCMDataArray,eFieldTimeArray,eFieldDataArray,discontTimeArray,discontDataArray,AODSyncTimeArray,AODSyncDataArray,SPCMSyncTimeArray,SPCMSyncDataArray= tdmsData.data_to_segment(timeSegment=timeSegment,AOD1DataArray=AOD1DataArray,AOD2DataArray=AOD2DataArray,
                                                                                                                                                                                                                        AODTimeArray=AODTimeArray,SPCMTimeArray=SPCMTimeArray,SPCMDataArray=SPCMDataArray,
                                                                                                                                                                                                                        eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldDataArray,pixelNumberArray=pixelNumberArray,
                                                                                                                                                                                                                        discontTimeArray=discontTimeArray,discontDataArray=discontDataArray,AODSyncTimeArray=AODSyncTimeArray,
                                                                                                                                                                                                                        AODSyncDataArray=AODSyncDataArray,SPCMSyncDataArray=SPCMSyncDataArray,SPCMSyncTimeArray=SPCMSyncTimeArray) 
        self.progress.emit("Data ready")   
        eFieldStrengthDataArray = tdmsAnalysis.scale_eField_data_to_eField_strength(eFieldDataArray=eFieldDataArray,eFieldAmp=eFieldAmp,electrodePolarity=electrodePolarity)
        print('Offset external field: ', offsetExtFieldTime)

        print("### Plotting signals \n")
        print(len(AODTimeArray), len(SPCMTimeArray))
        self.finished.emit()




    #functions to adapt plotting parameters

class generate_frames(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal()

    def run(self):
        global pixelNumberArray, AODTimeArray, SPCMDataArray, SPCMTimeArray, eFieldDataArray, eFieldTimeArray
        global discontIndexArray
 
        global frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList,frameSumWidthCentroidArray,frameSumHeightCentroidArray
        global AODTimeArray,AOD1DataArray,AOD2DataArray,pixelNumberArray,SPCMTimeArray,SPCMDataArray,eFieldTimeArray,eFieldDataArray,discontTimeArray,discontDataArray,AODSyncTimeArray,AODSyncDataArray,SPCMSyncTimeArray,SPCMSyncDataArray
        global eFieldStrengthDataArray
        #global SPCMTimeFragmentArrayList, SPCMDataFragmentArrayList, AODTimeFragmentArrayList, AOD1DataFragmentArrayList, AOD2DataFragmentArrayList,pixelNumberFragmentArrayList
        global frameTimeStampArrayList,frameArrayListList,frameSumWidthArrayListList,frameSumHeightArrayListList, frameSumWidthCentroidArrayList, frameSumHeightCentroidArrayList


        SPCMTimeFragmentArrayList, SPCMDataFragmentArrayList, AODTimeFragmentArrayList, AOD1DataFragmentArrayList, AOD2DataFragmentArrayList,pixelNumberFragmentArrayList = tdmsAnimate.split_segment_into_fragments(pixelNumberArray=pixelNumberArray,AODTimeArray=AODTimeArray,
                                 AOD1DataArray=AOD1DataArray,AOD2DataArray=AOD2DataArray,SPCMTimeArray=SPCMTimeArray,SPCMDataArray=SPCMDataArray)
        frameArrayListList = []
        frameTimeStampArrayList = []
        frameSumHeightArrayListList = []
        frameSumWidthArrayListList = []
        frameSumHeightCentroidArrayList = []
        frameSumWidthCentroidArrayList = []
        globalEfieldArray = np.array([])
        print("Frag length" + str(len(SPCMTimeFragmentArrayList)))
        print(len(SPCMTimeFragmentArrayList))
        for i in range(len(SPCMTimeFragmentArrayList)):

            
            AODTimeFragmentArray = AODTimeFragmentArrayList[i]
            AOD1DataFragmentArray = AOD1DataFragmentArrayList[i]
            AOD2DataFragmentArray = AOD2DataFragmentArrayList[i]
            SPCMTimeFragmentArray = SPCMTimeFragmentArrayList[i]
            SPCMDataFragmentArray = SPCMDataFragmentArrayList[i]
            pixelNumberFragmentArray = pixelNumberFragmentArrayList[i]
        
        
            frameArrayList, frameSumWidthArrayList, frameSumHeightArrayList, frameSumWidthCentroidArray ,frameSumHeightCentroidArray, frameTimeStampArray,frameSumHeightAmplitudeArray,frameSumHeightSigmaArray,frameSumWidthAmplitudeArray,frameSumWidthSigmaArray  = tdmsAnimate.generate_frame_list_from_fragment(AODTimeArray=AODTimeFragmentArray,AOD1DataArray=AOD1DataFragmentArray,
                                                            AOD2DataArray=AOD2DataFragmentArray,pixelNumberArray=pixelNumberFragmentArray,SPCMTimeArray=SPCMTimeFragmentArray,SPCMDataArray=SPCMDataFragmentArray,
                                                            rollImage=False,rollAxis=0,rollPixels=0)
            
            eFieldFrameTimeArray = np.array([])
            globalEfieldArray = np.array([])
            eFieldAmp = max(eFieldDataArray)
            for frameTimeStamp in frameTimeStampArray:
                timeIndex = int(len(np.where(eFieldTimeArray < frameTimeStamp)[0]))
                value = eFieldDataArray[timeIndex]/eFieldAmp
                eFieldFrameTimeArray = np.append(eFieldFrameTimeArray,eFieldTimeArray[timeIndex])
                globalEfieldArray = np.append(globalEfieldArray,value)
                
            
            
            
            
            globalArrayList1 = frameSumHeightArrayList
            globalArrayList2 = frameSumWidthArrayList
            globalArrayList3 = frameArrayList
            globalFrameTimeStampArray = frameTimeStampArray
            
            globalAmplitudeArray = frameSumHeightAmplitudeArray
            globalSigmaArray = frameSumHeightSigmaArray
            globalCentroidArray = frameSumHeightCentroidArray
            
        
            frameTimeStampArrayList.append(frameTimeStampArray)
            frameArrayListList.append(frameArrayList)
            frameSumWidthCentroidArrayList.append(frameSumWidthCentroidArray)
            frameSumWidthArrayListList.append(frameSumWidthArrayList)
            frameSumHeightCentroidArrayList.append(frameSumHeightCentroidArray)
            frameSumHeightArrayListList.append(frameSumHeightArrayList)

            self.progress.emit()
        frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList,frameSumWidthCentroidArray,frameSumHeightCentroidArray = tdmsData.flatten_fragments_to_segment(frameTimeStampArrayList=frameTimeStampArrayList, frameSumWidthArrayListList=frameSumWidthArrayListList, frameSumHeightArrayListList=frameSumHeightArrayListList,
                                                                                                                                                                          frameSumWidthCentroidArrayList=frameSumWidthCentroidArrayList,frameSumHeightCentroidArrayList=frameSumHeightCentroidArrayList)   

        self.finished.emit()



class process_data(QObject):
    finished = pyqtSignal()
    fitted_velocity1 = pyqtSignal()
    fitted_velocity2 = pyqtSignal()
    position_and_velocity_trace = pyqtSignal()
    overlapping_periods = pyqtSignal()
    kymograph = pyqtSignal()
    finished = pyqtSignal()

    def run(self):
        print("starting")
        global AODTimeArray,AOD1DataArray,AOD2DataArray,pixelNumberArray,SPCMTimeArray,SPCMDataArray,eFieldTimeArray,eFieldDataArray,discontTimeArray,discontDataArray,AODSyncTimeArray,AODSyncDataArray,SPCMSyncTimeArray,SPCMSyncDataArray
        global eFieldStrengthDataArray

        global compensateOutliers, uEO, z, experimentName, tdmsFolderPath
        global fittedCovVelocityList, fittedVelocityList  
        global fitteduEPArray, fixeduEO
        global frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList,frameSumWidthCentroidArray,frameSumHeightCentroidArray, filteredWidthPositionArray, filteredHeightPositionArray
        global heightPositionArray, positionTimeArray, velocityTimeArray, heightVelocityArray
        global velocityTimeArrayList, heightVelocityArrayList, averageVelocityArray
        global widthPositionArrayList, heightPositionArrayList, positionTimeArrayList, filteredHeightPositionArrayList
        
        widthPositionArray, heightPositionArray = tdmsAnalysis.scale_to_dimensions(frameSumWidthCentroidArray=frameSumWidthCentroidArray,frameSumHeightCentroidArray=frameSumHeightCentroidArray,pitchX=tdmsAnimate.pitchX,pitchY=tdmsAnimate.pitchY)
        positionTimeArray, filteredHeightPositionArray = tdmsAnalysis.low_pass_filter(timeArray=frameTimeStampArray, dataArray=heightPositionArray,eFieldFreq=tdmsEKModel.f,compensateOutliers=compensateOutliers)
        positionTimeArray, filteredWidthPositionArray = tdmsAnalysis.low_pass_filter(timeArray=frameTimeStampArray, dataArray=widthPositionArray,eFieldFreq=tdmsEKModel.f,compensateOutliers=compensateOutliers)
        heightVelocityArray, velocityTimeArray = tdmsAnalysis.differentiate_signal(dataArray=filteredHeightPositionArray,timeArray=positionTimeArray)
        

        positionTimeArrayList, filteredHeightPositionArrayList = tdmsAnalysis.split_trace_per_efield_period(eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray,dataArray=filteredHeightPositionArray,timeArray=positionTimeArray)
        positionTimeArrayList, filteredWidthPositionArrayList = tdmsAnalysis.split_trace_per_efield_period(eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray,dataArray=filteredWidthPositionArray,timeArray=positionTimeArray)
        frameTimeStampArrayList, heightPositionArrayList = tdmsAnalysis.split_trace_per_efield_period(eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray,dataArray=heightPositionArray,timeArray=frameTimeStampArray)
        frameTimeStampArrayList, widthPositionArrayList = tdmsAnalysis.split_trace_per_efield_period(eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray,dataArray=widthPositionArray,timeArray=frameTimeStampArray)    
        velocityTimeArrayList, heightVelocityArrayList = tdmsAnalysis.split_trace_per_efield_period(eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray,dataArray=heightVelocityArray,timeArray=velocityTimeArray,compensateAverage=True)
        
        positionTimeArrayList = positionTimeArrayList[1:]
        filteredHeightPositionArrayList = filteredHeightPositionArrayList[1:]
        filteredWidthPositionArrayList = filteredWidthPositionArrayList[1:]
        heightPositionArrayList = heightPositionArrayList[1:]
        widthPositionArrayList = widthPositionArrayList[1:]
        frameTimeStampArrayList = frameTimeStampArrayList[1:]
        velocityTimeArrayList = velocityTimeArrayList[1:]
        heightVelocityArrayList = heightVelocityArrayList[1:]

        self.position_and_velocity_trace.emit()
        self.overlapping_periods.emit()

        if(fixeduEO == False):
            global fittedVelocityList, fittedCovVelocityList
            initialGuess, fittedVelocityList, fittedCovVelocityList, velocityFitArrayList = tdmsEKModel.fit_model_to_segment(timeArrayList=velocityTimeArrayList,velocityArrayList=heightVelocityArrayList,y=0,z=z)
            
            fitteduEPArray = np.array([])
            fitteduEOArray = np.array([])
            for i in range(len(fittedCovVelocityList)):
                fitteduEPArray = np.append(fitteduEPArray,fittedVelocityList[i][0])
                fitteduEOArray = np.append(fitteduEOArray,fittedVelocityList[i][1])
                
            averageuEO = np.average(fitteduEOArray) 
            averageuEP = np.average(fitteduEPArray) 
            
            averageVelocityArray = tdmsEKModel.calc_period_from_uEO_and_uEP(normalizedTimeArray=np.linspace(0.0,1.0,100), uEO=averageuEO, uEP=averageuEP, order=100,y=0,z=z)
            
            tdmsSave.save_uEO_and_uEP_to_file(frameTimeStampArray=frameTimeStampArray, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName, fittedVelocityList=fittedVelocityList, fittedCovVelocityList=fittedCovVelocityList,velocityTimeArrayList=velocityTimeArrayList)
  
            #tdmsPlot.plot_fitted_velocity_scatter_plot(fittedVelocityList=fittedVelocityList,fittedCovVelocityList=fittedCovVelocityList)
            self.fitted_velocity2.emit()
        
        else:
            initialGuess, fittedVelocityList, fittedCovVelocityList, velocityFitArrayList = tdmsEKModel.fit_model_to_segment_fixed_uEO(timeArrayList=velocityTimeArrayList,velocityArrayList=heightVelocityArrayList,uEO=uEO,y=0,z=z)
            
            fitteduEPArray = np.array([])
            fitteduEOArray = np.array([])
            for i in range(len(fittedCovVelocityList)):
                fitteduEPArray = np.append(fitteduEPArray,fittedVelocityList[i][0])
                fitteduEOArray = np.append(fitteduEOArray,uEO)
                
            averageuEO = np.average(fitteduEOArray) 
            averageuEP = np.average(fitteduEPArray) 
            
            averageVelocityArray = tdmsEKModel.calc_period_from_uEO_and_uEP(normalizedTimeArray=np.linspace(0.0,1.0,100), uEO=averageuEO, uEP=averageuEP, order=100,y=0,z=z)
            
            #tdmsPlot.plot_fitted_velocity_fixed_uEO(fitteduEPArray=fitteduEPArray,uEO=uEO)
            self.fitted_velocity1.emit()
            tdmsSave.save_fixed_uEO_and_uEP_to_file(frameTimeStampArray=frameTimeStampArray, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName, fitteduEPArray=fitteduEPArray,uEO=uEO,velocityTimeArrayList=velocityTimeArrayList) 
        self.kymograph.emit()
        self.finished.emit()

class kymoMatplot(QObject):
    finished = pyqtSignal()

    def run(self):
        global frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList,frameSumWidthCentroidArray,frameSumHeightCentroidArray, filteredWidthPositionArray, filteredHeightPositionArray, eFieldTimeArray, eFieldStrengthDataArray
        global positionTimeArray
        tdmsPlot.plot_kymograph(xDataArrayList=frameSumWidthArrayList,yDataArrayList=frameSumHeightArrayList,frameTimeStampArray=frameTimeStampArray,eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray, 
                            positionTimeArray=positionTimeArray,frameSumHeightCentroidArray=filteredHeightPositionArray,frameSumWidthCentroidArray=filteredWidthPositionArray,pitchX=tdmsAnimate.pitchX,pitchY=tdmsAnimate.pitchY)    
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()