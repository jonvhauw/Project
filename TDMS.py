import numpy as np
import os
import easygui
from nptdms import TdmsFile


def get_tdms_file_path(rootPath="C:\\Users\\Lucas\\Documents\\Phd"):
    tdmsPathList =  easygui.fileopenbox(default=rootPath, filetypes=["*.tdms"], multiple=True)
    
    
    splitList = tdmsPathList[0].split("_")
    experimentName = splitList[-1].split(".")[0]
    
    tdmsFolderPath = os.path.dirname(tdmsPathList[0])
    
    print("Folder:{}".format(tdmsFolderPath))
    print("Experiment:{}".format(experimentName))
    
    return tdmsPathList,tdmsFolderPath,experimentName

def read_tdms_file(tdmsFilePath=""):
    tdmsFile = TdmsFile.read(tdmsFilePath)
    
    return tdmsFile

def read_tdms_file_list(tdmsFilePathList=[]):
    tdmsFileList = []
    txtDataFilePath = ""
    for tdmsFilePath in tdmsFilePathList:
        if(".txt" in tdmsFilePath):
            txtDataFilePath = tdmsFilePath
        else:
            tdmsFile = TdmsFile.read(tdmsFilePath)
            tdmsFileList.append(tdmsFile)
        
    return tdmsFileList,txtDataFilePath
    
def return_tdms_hierarchy(tdmsFile=None):
    tdmsHierarchyDict = {}
    for group in tdmsFile.groups():
        channelDict = {}
        for channel in group.channels():
            channelDict[channel.name] = channel.data
        tdmsHierarchyDict[group.name] = channelDict
    
    return tdmsHierarchyDict

def return_tdms_hierarchy_list(tdmsFileList=[]):
    tdmsHierarchyDictList = []
    for tdmsFile in tdmsFileList:
        tdmsHierarchyDict = return_tdms_hierarchy(tdmsFile=tdmsFile)
        tdmsHierarchyDictList.append(tdmsHierarchyDict)
        
    return tdmsHierarchyDictList

def combine_tdms_hierarchy_list(tdmsHierarchyDictList=[]):
    combinedHierarchyDict = {}
    for tdmsHierarchyDict in tdmsHierarchyDictList:
        for groupName in tdmsHierarchyDict.keys():
            combinedHierarchyDict[groupName] = tdmsHierarchyDict[groupName]
            
    return combinedHierarchyDict

def return_raw_arrays_from_tdms_hierarchy(tdmsHierarchyDict={}):
    pixelNumberArray = tdmsHierarchyDict["AOD Analog Out"]["Pixel Number"]
    AODLoopTicksArray = tdmsHierarchyDict["AOD Analog Out"]["Loop Ticks AOD"].astype(np.int16)
    
    SPCMDataArray = tdmsHierarchyDict["SPCM Digital Input"]["SPCM"]
    SPCMLoopTicksArray = tdmsHierarchyDict["SPCM Digital Input"]["Loop Ticks SPCM"].astype(np.int16)
    
    eFieldDataArray = tdmsHierarchyDict["Ext Field Analog Out"]["AO2 Value"].astype(np.int16)
    eFieldLoopTicksArray =tdmsHierarchyDict["Ext Field Analog Out"]["Loop Ticks Ext Field"]
    
    return pixelNumberArray, AODLoopTicksArray, SPCMDataArray, SPCMLoopTicksArray, eFieldDataArray, eFieldLoopTicksArray
    
def return_parameters_from_tdms_hierarchy(tdmsHierarchyDict={},comsolFieldFactor=10.0,electrodeSpacing=1e-3,AODSpacialFactor=10):
    eFieldAmp = tdmsHierarchyDict["Experiment Parameters"]["Amplitude (V)"][0] * comsolFieldFactor/electrodeSpacing
    eFieldFreq = tdmsHierarchyDict["Experiment Parameters"]["Freq (Hz)"][0]
    pitchX = tdmsHierarchyDict["Experiment Parameters"]["xPitch (V)"] [0] * AODSpacialFactor
    pitchY = tdmsHierarchyDict["Experiment Parameters"]["yPitch (V)"][0] * AODSpacialFactor
    binSize = tdmsHierarchyDict["Experiment Parameters"]["Bin (us)"][0]     
    dotsPerLine = tdmsHierarchyDict["Experiment Parameters"]["Dots per Line"][0]
    numberOfLines = tdmsHierarchyDict["Experiment Parameters"]["Number of Lines"][0]
    
    return eFieldAmp, eFieldFreq, pitchX, pitchY, binSize, dotsPerLine, numberOfLines


def print_tdms_hierarchy(tdmsHierarchyDict):
    counter1 = 0
    
    for key in tdmsHierarchyDict.keys():
        print("Group {}: {}".format(counter1,key))
        counter2 = 0
        for channelKey in tdmsHierarchyDict[key].keys():
            printString = "---- Channel {}: {} ====".format(counter2, channelKey)
            if(len(tdmsHierarchyDict[key][channelKey])> 10 ):
                printString = printString + " Array with {} elements".format(len(tdmsHierarchyDict[key][channelKey]))
            else:
                printString = printString + " {}".format(tdmsHierarchyDict[key][channelKey])
            
            print(printString)
            
            counter2 = counter2 + 1
        counter1 = counter1 + 1
    