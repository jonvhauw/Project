import TDMS as tdms                             #test
import TDMSDataProcessing as tdmsData
import TDMSPlotTraces as tdmsPlot
import TDMSAnimateTraces as tdmsAnimate
import TDMSDataAnalysis as tdmsAnalysis
import TDMSEKModel as tdmsEKModel
import TDMSSaveData as tdmsSave
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
#from numba import jit

if (__name__ == "__main__"):
    comsolFieldFactor =  (23e3)*(6.5e-3)/10 # Conversion factor based on comsol simulation V/m/m/V
    electrodeSpacing = 6.5e-3 # Spacing between electrodes in m
    AODSpacialFactor = 8.2e-6/10  # AOD voltage to distance in focal plane m/V
    FPGAClockPeriod = 25e-9
    electrodePolarity = "Negative"  # Positive voltage means E-Field is in the opposite direction of positive displacement
    
    z = 0e-06
    
    """ 
    Scripting Parameters
    """    
    # Time Parameters
    timeSegment =  [43.1,43.85]
    #timeSegment = [0, 0.6]
    tdmsData.offsetExtFieldTime =0.001581849
    tdmsData.offsetSPCMTime =0.00073128 -2.220855e-6
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
    tdmsPlot.plotAOD = True
    tdmsPlot.plotPixelNumber = False
    tdmsPlot.plotAODSync = plotSync
    tdmsPlot.plotDiscont = False
    
    # SPCM Parameters
    tdmsPlot.plotSPCM = True
    tdmsPlot.plotSPCMSync = plotSync
    tdmsPlot.plotSPCMSampleRatio = 1
    tdmsData.filterSPCM = False
    tdmsData.windowSize = 50
    tdmsAnimate.darkCount = 2
    compensateOutliers=True
    
    
    # Ext Parameters
    tdmsPlot.plotExtField = True
    tdmsPlot.plotExtFieldKymo = False
    
    # Fit Parameters
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
    tdmsAnimate.fps = 60
    tdmsAnimate.dpi = 110
    
    rollImage = False
    rollPixels = 0
    rollAxis = 0

    
    
    
    """ 
    Raw Data from TDMS
    """
    print("### Reading data from:\n")
    tdmsPathList,tdmsFolderPath,experimentName = tdms.get_tdms_file_path(rootPath="C:\\Users\\Lucas\\Documents\\Phd\\Experiments\\Scanning laser electrophoresis\\Experimental Data\\POC experiments")
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
    
    uEO = 0.00011 * tdmsHierarchyDict["Experiment Parameters"]['Amplitude (V)'][0]
    
    tdmsEKModel.init_dependent_variables()
    
    
    
    """ 
    Edit and generate data from TDMS
    """  
      
    print("### Generating signals and segmenting \n")
    pixelNumberArray, AODTimeArray, AODSyncTimeArray, AODSyncDataArray, SPCMDataArray, SPCMTimeArray, SPCMSyncTimeArray, SPCMSyncDataArray,eFieldDataArray, eFieldTimeArray = tdmsData.return_arrays_from_tdms_hierarchy(pixelNumberArray=pixelNumberArray, AODLoopTicksArray=AODLoopTicksArray, SPCMDataArray=SPCMDataArray,
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
    eFieldStrengthDataArray = tdmsAnalysis.scale_eField_data_to_eField_strength(eFieldDataArray=eFieldDataArray,eFieldAmp=eFieldAmp,electrodePolarity=electrodePolarity)
    
    """ 
    Plot Data from TDMS
    """      
    
    print("### Plotting signals \n")
    tdmsPlot.plot_trace_segment(AODTimeArray=AODTimeArray,AOD1DataArray=AOD1DataArray,AOD2DataArray=AOD2DataArray,
                      pixelNumberArray=pixelNumberArray,SPCMTimeArray=SPCMTimeArray,SPCMDataArray=SPCMDataArray,
                      eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldDataArray,discontTimeArray=discontTimeArray,discontDataArray=discontDataArray,AODSyncTimeArray=AODSyncTimeArray,AODSyncDataArray=AODSyncDataArray,
                      SPCMSyncDataArray=SPCMSyncDataArray,SPCMSyncTimeArray=SPCMSyncTimeArray)   
    
    input("Press enter to continue...")
    #tdmsPlot.cnt=0
    tdmsAnimate.generate_picture_from_segment(pixelNumberArray=pixelNumberArray,AODTimeArray=AODTimeArray,AOD1DataArray=AOD1DataArray,
                                        AOD2DataArray=AOD2DataArray,SPCMTimeArray=SPCMTimeArray,SPCMDataArray=SPCMDataArray,eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray,
                                        rollImage=rollImage,rollAxis=rollAxis,rollPixels=rollPixels,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName, time=43.15)
    
    offsetExtFieldTimeAuto, offsetSPCMTimeAuto, Period = tdmsData.find_auto_offset(AODSyncTimeArray=AODSyncTimeArray, AODSyncDataArray=AODSyncDataArray, SPCMSyncTimeArray=SPCMSyncTimeArray, 
                                    SPCMSyncDataArray=SPCMDataArray, eFieldTimeArray=eFieldTimeArray, eFieldDataArray=eFieldDataArray)
    
    
    input("Press enter to continue...")



    """ 
    Extracting Information from Data
    """     
     
    print("###  Processing Data \n")
    
    if(readSavedData):
        frameTimeStampArray,frameSumWidthCentroidArray,frameSumHeightCentroidArray,frameSumWidthArrayList,frameSumHeightArrayList = tdmsSave.read_data_from_txt(savedDataPath=txtDataFilePath)
    else:
        frameTimeStampArrayList,frameArrayListList,frameSumWidthArrayListList, frameSumHeightArrayListList,frameSumWidthCentroidArrayList,frameSumHeightCentroidArrayList = tdmsAnimate.generate_video_from_segment(pixelNumberArray=pixelNumberArray,AODTimeArray=AODTimeArray,AOD1DataArray=AOD1DataArray,
                                        AOD2DataArray=AOD2DataArray,SPCMTimeArray=SPCMTimeArray,SPCMDataArray=SPCMDataArray,eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray,
                                        rollImage=rollImage,rollAxis=rollAxis,rollPixels=rollPixels,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName)
        
        frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList,frameSumWidthCentroidArray,frameSumHeightCentroidArray = tdmsData.flatten_fragments_to_segment(frameTimeStampArrayList=frameTimeStampArrayList, frameSumWidthArrayListList=frameSumWidthArrayListList, frameSumHeightArrayListList=frameSumHeightArrayListList,
                                                                                                                                                                          frameSumWidthCentroidArrayList=frameSumWidthCentroidArrayList,frameSumHeightCentroidArrayList=frameSumHeightCentroidArrayList)        
        
    
        
    
    """ 
    Analyse Data from TDMS
    """      
    
    widthPositionArray, heightPositionArray = tdmsAnalysis.scale_to_dimensions(frameSumWidthCentroidArray=frameSumWidthCentroidArray,frameSumHeightCentroidArray=frameSumHeightCentroidArray,pitchX=pitchX,pitchY=pitchY)
    positionTimeArray, filteredHeightPositionArray = tdmsAnalysis.low_pass_filter(timeArray=frameTimeStampArray, dataArray=heightPositionArray,eFieldFreq=eFieldFreq,compensateOutliers=compensateOutliers)
    positionTimeArray, filteredWidthPositionArray = tdmsAnalysis.low_pass_filter(timeArray=frameTimeStampArray, dataArray=widthPositionArray,eFieldFreq=eFieldFreq,compensateOutliers=compensateOutliers)
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
    
    if(saveData):
        savedDataPath = tdmsSave.write_data_to_txt(frameTimeStampArray=frameTimeStampArray, frameSumWidthCentroidArray=frameSumWidthCentroidArray, frameSumHeightCentroidArray=frameSumHeightCentroidArray, 
                                                   frameSumHeightArrayList=frameSumHeightArrayList, frameSumWidthArrayList=frameSumWidthArrayList, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName)     
        
        tdmsSave.write_scaled_position_to_txt(frameTimeStampArray=frameTimeStampArray,frameTimeStampArrayList=frameTimeStampArrayList,widthPositionArrayList=widthPositionArrayList,heightPositionArrayList=heightPositionArrayList,
                                     tdmsFolderPath=tdmsFolderPath, experimentName=experimentName)
        
        tdmsSave.write_scaled_filtered_position_to_txt(frameTimeStampArray=frameTimeStampArray,positionTimeArrayList=positionTimeArrayList,filteredWidthPositionArrayList=filteredHeightPositionArrayList,
                                                       filteredHeightPositionArrayList=filteredHeightPositionArrayList,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName)
        
        tdmsSave.write_scaled_velocity_to_txt(frameTimeStampArray=frameTimeStampArray,velocityTimeArrayList=velocityTimeArrayList,velocityArrayList=heightVelocityArrayList,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName)       
    
    
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
        tdmsPlot.plot_fitted_velocity_scatter_plot(fittedVelocityList=fittedVelocityList,fittedCovVelocityList=fittedCovVelocityList)
    
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
        
        tdmsPlot.plot_fitted_velocity_fixed_uEO(fitteduEPArray=fitteduEPArray,uEO=uEO)
        
        tdmsSave.save_fixed_uEO_and_uEP_to_file(frameTimeStampArray=frameTimeStampArray, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName, fitteduEPArray=fitteduEPArray,uEO=uEO,velocityTimeArrayList=velocityTimeArrayList)        
    
    
    tdmsPlot.plot_position_and_velocity_trace(frameTimeStampArray=frameTimeStampArray,heightPositionArray=heightPositionArray,
                                         positionTimeArray=positionTimeArray,filteredHeightPositionArray=filteredHeightPositionArray,
                                         velocityTimeArray=velocityTimeArray,heightVelocityArray=heightVelocityArray,
                                         eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray)  
    
    
    
    
    tdmsPlot.plot_overlapping_periods(timeArrayList=velocityTimeArrayList,dataArrayList=heightVelocityArrayList,averageVelocityTimeArray=np.linspace(0.0,1.0,100),averageVelocityArray=averageVelocityArray,eFieldFreq=eFieldFreq)
    
    
    
    
    """
    tdmsPlot.plot_kymograph(yDataArrayList=frameSumHeightArrayList,frameTimeStampArray=frameTimeStampArray,eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray, 
                            positionTimeArray=positionTimeArray,frameSumHeightCentroidArray=filteredHeightPositionArray,pitchX=pitchX,pitchY=pitchY)
    
    """
    tdmsPlot.plot_kymograph(xDataArrayList=frameSumWidthArrayList,yDataArrayList=frameSumHeightArrayList,frameTimeStampArray=frameTimeStampArray,eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray, 
                            positionTimeArray=positionTimeArray,frameSumHeightCentroidArray=filteredHeightPositionArray,frameSumWidthCentroidArray=filteredWidthPositionArray,pitchX=pitchX,pitchY=pitchY)    
    
    print("Done")
    