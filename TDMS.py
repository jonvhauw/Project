import numpy as np
import os
import easygui
from nptdms import TdmsFile

# Opens a file selection window using easygui

# Input: default opening file

# Output: - tdmsPathList: List of the tdms file paths
#         - tdmsFolderPath: the folder path of the selected files 
#         - experimentName: string with the EPxx 

def get_tdms_file_path(rootPath="C:\\Users\\Lucas\\Documents\\Phd"):
    tdmsPathList =  easygui.fileopenbox(default=rootPath, filetypes=["*.tdms"], multiple=True)
    
    
    splitList = tdmsPathList[0].split("_")
    experimentName = splitList[-1].split(".")[0]
    
    tdmsFolderPath = os.path.dirname(tdmsPathList[0])
    
    print("Folder:{}".format(tdmsFolderPath))
    print("Experiment:{}".format(experimentName))
    
    return tdmsPathList,tdmsFolderPath,experimentName

# Opens a tdms file

# Input: path of the tdms file to open

# Output: - tdmsFile: a tdms file object 

def read_tdms_file(tdmsFilePath=""):
    tdmsFile = TdmsFile.read(tdmsFilePath)
    
    return tdmsFile

# Opens a tdms files in tdmsFilePathList

# Input: - tdmsPathList: List of the tdms file paths, can also contain .txt file 
#                        in case preprocessed data will be used (in main: readSavedData = True)

# Output: - tdmsFileList: List of Tdms file objets
#         - txtDataFilePath: .txt file path of file containing preprocessed data

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

# Return a dictionary with all data and experiment within a .tdms file

# Input: - tdmsFile: a tdms file object

# Output: - tdmsHierarchyDict: a dictionary with 3 layers tdmsHierarchyDict[group name][channel name][data array]

def return_tdms_hierarchy(tdmsFile=None):
    tdmsHierarchyDict = {}
    for group in tdmsFile.groups():
        channelDict = {}
        for channel in group.channels():
            channelDict[channel.name] = channel.data
        tdmsHierarchyDict[group.name] = channelDict
    
    return tdmsHierarchyDict

# Return a list of dictionaries with all data and experiment within all .tdms file

# Input: - tdmsFileList: list of tdms file objects

# Output: - tdmsHierarchyDictList: list of dictionaries returned from return_tdms_hierarchy()

def return_tdms_hierarchy_list(tdmsFileList=[]):
    tdmsHierarchyDictList = []
    for tdmsFile in tdmsFileList:
        tdmsHierarchyDict = return_tdms_hierarchy(tdmsFile=tdmsFile)
        tdmsHierarchyDictList.append(tdmsHierarchyDict)
        
    return tdmsHierarchyDictList

# Combines all dictionaries on the group level in single dictionary with all data

# Input: - tdmsHierarchyDictList: list of tdms dictionaries given by return_tdms_hierarchy_list()

# Output: - combinedHierarchyDict: combine dictionary of all .tdms data, 3 layers tdmsHierarchyDict[group name][channel name][data array]

def combine_tdms_hierarchy_list(tdmsHierarchyDictList=[]):
    combinedHierarchyDict = {}
    for tdmsHierarchyDict in tdmsHierarchyDictList:
        for groupName in tdmsHierarchyDict.keys():
            combinedHierarchyDict[groupName] = tdmsHierarchyDict[groupName]
            
    return combinedHierarchyDict

# Returns all raw data arrays contained within the combined tdmsHierarchyDict

# Input: - tdmsHierarchyDict: the combined hierarchy dict from combine_tdms_hierarchy_list()

# Output: - pixelNumberArray: Array containing the index of the pixel which represents a x and y value for AOD Voltages
#         - AODLoopTicksArray: Array containing the amount of ticks which elapsed for obtaining respective pixel index
#         - SPCMDataArray: Array containing the amount of photons captured in current bin
#         - SPCMLoopTicksArray: Array containing the amount of ticks which elapsed for obtaining photons in respective bin
#         - eFieldDataArray: Array containing the external voltage value 
#         - eFieldLoopTicksArray: Array containing the amount of ticks which elapsed for respective external voltage

def return_raw_arrays_from_tdms_hierarchy(tdmsHierarchyDict={}):
    pixelNumberArray = tdmsHierarchyDict["AOD Analog Out"]["Pixel Number"]
    AODLoopTicksArray = tdmsHierarchyDict["AOD Analog Out"]["Loop Ticks AOD"].astype(np.int16)
    
    SPCMDataArray = tdmsHierarchyDict["SPCM Digital Input"]["SPCM"]
    SPCMLoopTicksArray = tdmsHierarchyDict["SPCM Digital Input"]["Loop Ticks SPCM"].astype(np.int16)
    
    eFieldDataArray = tdmsHierarchyDict["Ext Field Analog Out"]["AO2 Value"].astype(np.int16)
    eFieldLoopTicksArray =tdmsHierarchyDict["Ext Field Analog Out"]["Loop Ticks Ext Field"]
    
    return pixelNumberArray, AODLoopTicksArray, SPCMDataArray, SPCMLoopTicksArray, eFieldDataArray, eFieldLoopTicksArray
    
# Returns the experiment parameters from the tdms hierarchy dictionary

# Input: - tdmsHierarchyDict: the combined hierarchy dict from combine_tdms_hierarchy_list()
#         - comsolFieldFactor: A ratio calculated with comsol to know the E-Field intensity as a function of external field voltage
#         - electrodeSpacing: Spacing of the gold plated electrodes in the sample
#         - AODSpacialFactor: A conversion factor of AOD voltage to position 

# Output: - eFieldAmp: Amplitude of the external field applied to the microfluidic channel center
#         - eFieldFreq: Frequency of the external field 
#         - pitchX: Voltage distance between every pixel along the x direction 
#         - pitchY: Voltage distance between every pixel along the y direction
#         - binSize: Integration time of SPCM 
#         - dotsPerLine: Amount of pixels per line in the AOD scanning pattern
#         - numberOfLines: Amount of lines in the AOD scanning pattern

def return_parameters_from_tdms_hierarchy(tdmsHierarchyDict={},comsolFieldFactor=10.0,electrodeSpacing=1e-3,AODSpacialFactor=10):
    eFieldAmp = tdmsHierarchyDict["Experiment Parameters"]["Amplitude (V)"][0] * comsolFieldFactor/electrodeSpacing
    eFieldFreq = tdmsHierarchyDict["Experiment Parameters"]["Freq (Hz)"][0]
    pitchX = tdmsHierarchyDict["Experiment Parameters"]["xPitch (V)"] [0] * AODSpacialFactor
    pitchY = tdmsHierarchyDict["Experiment Parameters"]["yPitch (V)"][0] * AODSpacialFactor
    binSize = tdmsHierarchyDict["Experiment Parameters"]["Bin (us)"][0]     
    dotsPerLine = tdmsHierarchyDict["Experiment Parameters"]["Dots per Line"][0]
    numberOfLines = tdmsHierarchyDict["Experiment Parameters"]["Number of Lines"][0]
    
    return eFieldAmp, eFieldFreq, pitchX, pitchY, binSize, dotsPerLine, numberOfLines

# Printing function for displaying contents of tdms hierarchy dictionary

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
    