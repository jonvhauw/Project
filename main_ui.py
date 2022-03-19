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

        self.comboColorAODX.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboColorAODY.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboColorAODSync.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboColorSPCM.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboColorEField.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboColorSPCMSync.currentIndexChanged.connect(self.refreshDataProcessingPlot)

        self.actionimport_files.triggered.connect(self.getfiles)

        self.spinBoxStart.valueChanged.connect(self.show_startTime)
        self.spinBoxStop.valueChanged.connect(self.show_stopTime)

        self.buttonUpdate.clicked.connect(self.plot_existing_frames)
        self.autoOffset.clicked.connect(self.calculate_offset)
        self.generateFrames.clicked.connect(self.generate_frames)
        self.processData.clicked.connect(self.process_data)

        self.comboStyleAODX.currentIndexChanged.connect(self.update2)
        self.comboStyleAODY.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboStyleAODSync.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboStyleSPCM.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboStyleEField.currentIndexChanged.connect(self.refreshDataProcessingPlot)
        self.comboStyleSPCMSync.currentIndexChanged.connect(self.refreshDataProcessingPlot)

        self.spinBoxeFieldSync.setMinimum(-1)
        self.spinBoxSPCMSync.setMinimum(-1)

        self.spinBoxStart.setValue(43.1)
        self.spinBoxStop.setValue(43.85)




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

    def getfiles(self):
        dlg = QFileDialog()
        dlg.setDirectory("C:\\Users\\jonas\\OneDrive\\Documenten\\Bach3\\Project\\Data")
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFileMode(QFileDialog.ExistingFiles)
        #filenames = QStringList()
            
        if dlg.exec_():
            self.filenames = dlg.selectedFiles()

        self.update()


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
                             SPCMSyncDataArray=SPCMSyncDataArray,SPCMSyncTimeArray=SPCMSyncTimeArray)
        


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
                             SPCMSyncDataArray=SPCMSyncDataArray,SPCMSyncTimeArray=SPCMSyncTimeArray, AOD1_s = AOD1_s_value)
        


        proxy_widget = self.scene.addWidget(plotje)
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

        frameTimeStampArray2 = tdmsData.ravel_list_of_arrays(arrayList=frameTimeStampArrayList)
        frameArrayList2 = tdmsData.ravel_list_of_lists(listList=frameArrayListList)

        if self.updateFrames.isChecked():
                self.scene = QGraphicsScene()
                self.graphicsFrames.setScene(self.scene)
                imv = tdmsPlot.plot_frame_video_and_sums2(scene=self.scene, frameArray=np.array(frameArrayList2),pitchX=tdmsAnimate.pitchX,pitchY=tdmsAnimate.pitchY, timeArray=frameTimeStampArray2)
                #imv = tdmsPlot.plot_frame_video_and_sums2(scene=self.scene, frameArray=x,pitchX=1,pitchY=1, timeArray=np.array([i for i in range(500)]))
                proxy_widget = self.scene.addWidget(imv)
                self.graphicsFrames.fitInView(self.scene.sceneRect())
    
    def process_data(self):
        print('start')
        threadCount = QThreadPool.globalInstance().maxThreadCount()
        print(threadCount)
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
        
        self.worker.fitted_velocity.connect(self.plot_fitted_velocity)
        self.worker.position_and_velocity_trace.connect(self.plot_position_and_velocity_trace)
        self.worker.overlapping_periods.connect(self.plot_overlapping_periods)
        # Step 6: Start the thread
        self.thread.start()
        # Final resets
        self.processData.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.processData.setEnabled(True)
        )
        
        self.thread.finished.connect(lambda: self.generateFrames.setEnabled(True))
    
    def plot_fitted_velocity(self):
        print("plotting")
        global fitteduEPArray, uEO 
        self.scene = QGraphicsScene()
        self.graphicsVelocity_2.setScene(self.scene)
        plot = tdmsPlot.plot_fitted_velocity_fixed_uEO_gui(scene=self.scene, fitteduEPArray=fitteduEPArray,uEO=uEO)
        proxy_widget = self.scene.addWidget(plot)
        #self.graphicsVelocity_2.fitInView(self.scene.sceneRect())

    def plot_position_and_velocity_trace(self):
        global frameTimeStampArray, eFieldTimeArray, eFieldStrengthDataArray
        global heightPositionArray, positionTimeArray, filteredHeightPositionArray, velocityTimeArray, heightVelocityArray

        self.scenePosition = QGraphicsScene()
        self.graphicsParticlePositionTrace.setScene(self.scenePosition)
        self.sceneVelocity = QGraphicsScene()
        self.graphicsParticleVelocityTrace.setScene(self.sceneVelocity)
        pos2, pos1, vel2, vel1, pw1 = tdmsPlot.plot_position_and_velocity_trace_gui(self.scenePosition, self.sceneVelocity, frameTimeStampArray=frameTimeStampArray,heightPositionArray=heightPositionArray,
                                         positionTimeArray=positionTimeArray,filteredHeightPositionArray=filteredHeightPositionArray,
                                         velocityTimeArray=velocityTimeArray,heightVelocityArray=heightVelocityArray,
                                         eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray) 
        #proxy_widget1 = self.scenePosition.addWidget(pos1) 
        porxy_widget2 = self.sceneVelocity.addWidget(vel1)
        #proxy_widget3 = self.scenePosition.addWidget(pos2) 
        porxy_widget4 = self.sceneVelocity.addWidget(vel2)
        proxy_widget5 = self.scenePosition.addWidget(pw1) 
        #self.graphicsParticlePositionTrace.fitInView(self.scene.sceneRect())
        #self.graphicsParticleVelocityTrace.fitInView(self.scene.sceneRect())
    
    def plot_overlapping_periods(self):
        return None
    







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
        scanPattern = "S-shape"
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
        self.finished.emit()



class process_data(QObject):
    finished = pyqtSignal()
    fitted_velocity = pyqtSignal()
    position_and_velocity_trace = pyqtSignal()
    overlapping_periods = pyqtSignal()

    def run(self):
        print("starting")
        global AODTimeArray,AOD1DataArray,AOD2DataArray,pixelNumberArray,SPCMTimeArray,SPCMDataArray,eFieldTimeArray,eFieldDataArray,discontTimeArray,discontDataArray,AODSyncTimeArray,AODSyncDataArray,SPCMSyncTimeArray,SPCMSyncDataArray
        global eFieldStrengthDataArray
        global frameTimeStampArrayList,frameArrayListList,frameSumWidthArrayListList,frameSumHeightArrayListList, frameSumWidthCentroidArrayList, frameSumHeightCentroidArrayList
        global compensateOutliers, uEO, z, experimentName, tdmsFolderPath
        global fittedCovVelocityList, fittedVelocityList  
        global fitteduEPArray
        global frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList,frameSumWidthCentroidArray,frameSumHeightCentroidArray
        global heightPositionArray, positionTimeArray, filteredHeightPositionArray, velocityTimeArray, heightVelocityArray
  
        frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList,frameSumWidthCentroidArray,frameSumHeightCentroidArray = tdmsData.flatten_fragments_to_segment(frameTimeStampArrayList=frameTimeStampArrayList, frameSumWidthArrayListList=frameSumWidthArrayListList, frameSumHeightArrayListList=frameSumHeightArrayListList,
                                                                                                                                                                          frameSumWidthCentroidArrayList=frameSumWidthCentroidArrayList,frameSumHeightCentroidArrayList=frameSumHeightCentroidArrayList)   

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

        if(fixeduEO == False):
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
            self.fitted_velocity.emit()
        
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
            self.fitted_velocity.emit()
            tdmsSave.save_fixed_uEO_and_uEP_to_file(frameTimeStampArray=frameTimeStampArray, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName, fitteduEPArray=fitteduEPArray,uEO=uEO,velocityTimeArrayList=velocityTimeArrayList) 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()