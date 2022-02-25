import numpy as np
import scipy.signal as ss
import os


def is_float(string=""):
    try:
        value = float(string)
        return True
    except:
        return False
        


def write_data_to_txt(frameTimeStampArray=np.array([]),frameSumWidthCentroidArray=np.array([]),frameSumHeightCentroidArray=np.array([]),frameSumHeightArrayList=[],frameSumWidthArrayList=[],tdmsFolderPath="",experimentName=""):
    savedDataPath = generate_file_path(frameTimeStampArray=frameTimeStampArray,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName)
    file = open(savedDataPath,'w')
    
    for i in range(len(frameTimeStampArray)):
        arrayString1 = "{}".format(frameSumWidthArrayList[i]).replace('\n','')
        arrayString2 = "{}".format(frameSumHeightArrayList[i]).replace('\n','')
        dataLine = "{};{};{};{};{}\n".format(frameTimeStampArray[i],frameSumWidthCentroidArray[i],frameSumHeightCentroidArray[i],arrayString1,arrayString2)
        file.write(dataLine)
        
    file.close()
    
    print("Data saved: \n")
    print(savedDataPath)
    
    return savedDataPath


def write_scaled_position_to_txt(frameTimeStampArray=np.array([]),frameTimeStampArrayList=[],widthPositionArrayList=[],heightPositionArrayList=[],tdmsFolderPath="",experimentName=""):
    savedDataPath = generate_file_path(frameTimeStampArray=frameTimeStampArray,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName,addText="_scaled_position")
    file = open(savedDataPath,'w')
    
    for i in range(len(frameTimeStampArrayList)):
        for j in range(len(frameTimeStampArrayList[i])):
            dataLine = "{};{};{};{}\n".format(frameTimeStampArrayList[i][j],widthPositionArrayList[i][j],heightPositionArrayList[i][j],i)
            file.write(dataLine)
        
    file.close()
    
    print("Scaled Position Data saved: \n")
    print(savedDataPath)
    
    return savedDataPath

def write_scaled_filtered_position_to_txt(frameTimeStampArray=np.array([]),positionTimeArrayList=[],filteredWidthPositionArrayList=[],filteredHeightPositionArrayList=[],tdmsFolderPath="",experimentName=""):
    savedDataPath = generate_file_path(frameTimeStampArray=frameTimeStampArray,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName,addText="_scaled_filtered_position")
    file = open(savedDataPath,'w')
    
    for i in range(len(positionTimeArrayList)):
        for j in range(len(positionTimeArrayList[i])):
            dataLine = "{};{};{};{}\n".format(positionTimeArrayList[i][j],filteredWidthPositionArrayList[i][j],filteredHeightPositionArrayList[i][j],i)
            file.write(dataLine)
        
    file.close()
    
    print("Scaled Position Data saved: \n")
    print(savedDataPath)
    
    return savedDataPath

def write_scaled_velocity_to_txt(frameTimeStampArray=np.array([]),velocityTimeArrayList=[],velocityArrayList=[],tdmsFolderPath="",experimentName=""):
    savedDataPath = generate_file_path(frameTimeStampArray=frameTimeStampArray,tdmsFolderPath=tdmsFolderPath,experimentName=experimentName,addText="_scaled_velocity")
    file = open(savedDataPath,'w')
    
    for i in range(len(velocityTimeArrayList)):
        for j in range(len(velocityTimeArrayList[i])):
            dataLine = "{};{};{}\n".format(velocityTimeArrayList[i][j],velocityArrayList[i][j],i)
            file.write(dataLine)
        
    file.close()
    
    print("Scaled Position Data saved: \n")
    print(savedDataPath)
    
    return savedDataPath
    
    
def generate_file_path(frameTimeStampArray=np.array([]),tdmsFolderPath="",experimentName="",extension="txt",addText=""):
    timeStampString = "_{:2.4f}-{:2.4f}".format(frameTimeStampArray[0],frameTimeStampArray[-1])
    
    savedDataPath = tdmsFolderPath
    savedDataPath = os.path.join(savedDataPath,experimentName)
    savedDataPath = savedDataPath + timeStampString + addText + "." + extension
    
    return savedDataPath


def cast_stringarray_to_string(stringArray=""):
    array = np.array([])
    
    stringArray = stringArray.replace("[","")
    stringArray = stringArray.replace("]","")
    stringArrayList = stringArray.split(" ")
    
    for value in stringArrayList:
        if(is_float(string=value)):
            array = np.append(array, float(value))
    
    return array

def read_data_from_txt(savedDataPath=""):
    frameTimeStampArray = np.array([])
    frameSumWidthCentroidArray = np.array([])
    frameSumHeightCentroidArray = np.array([])
    frameSumHeightArrayList = []
    frameSumWidthArrayList = []
    
    file = open(savedDataPath,'r')
    lines = file.readlines()
    
    for line in lines:
        lineList = line.split(';')
        frameTimeStampArray = np.append(frameTimeStampArray,float(lineList[0]))
        frameSumWidthCentroidArray = np.append(frameSumWidthCentroidArray,float(lineList[1]))
        frameSumHeightCentroidArray = np.append(frameSumHeightCentroidArray,float(lineList[2]))
        array = cast_stringarray_to_string(stringArray = lineList[3])
        frameSumWidthArrayList.append(array)
        array = cast_stringarray_to_string(stringArray = lineList[4])
        frameSumHeightArrayList.append(array)
        
        
    
    return frameTimeStampArray,frameSumWidthCentroidArray,frameSumHeightCentroidArray,frameSumWidthArrayList,frameSumHeightArrayList
    
    
def save_uEO_and_uEP_to_file(frameTimeStampArray=np.array([]),tdmsFolderPath="",experimentName="",extension="csv",fittedVelocityList=[],fittedCovVelocityList=[],velocityTimeArrayList=[]):
    filePath = generate_file_path(frameTimeStampArray=frameTimeStampArray, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName, extension=extension)
    file = open(filePath,'w')
    file.write("periodStartTime(s);periodStopTime(s);uEP(mm/s);uEO(mm/s) \n")
    
    for i in range(len(fittedVelocityList)):
        dataLineString = "{};{};{};{}\n".format(velocityTimeArrayList[i][0],velocityTimeArrayList[i][-1],fittedVelocityList[i][0],fittedVelocityList[i][1])
        dataLineString = dataLineString.replace(".", ",")
        
        file.write(dataLineString)
    
    file.close()
    

def save_fixed_uEO_and_uEP_to_file(frameTimeStampArray=np.array([]),tdmsFolderPath="",experimentName="",extension="csv",fitteduEPArray=np.array([]),velocityTimeArrayList=[],uEO=0.001):
    filePath = generate_file_path(frameTimeStampArray=frameTimeStampArray, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName, extension=extension)
    file = open(filePath,'w')
    file.write("periodStartTime(s);periodStopTime(s);uEP(mm/s);uEO(mm/s) \n")
    
    for i in range(len(fitteduEPArray)):
        dataLineString = "{};{};{};{}\n".format(velocityTimeArrayList[i][0],velocityTimeArrayList[i][-1],fitteduEPArray[i],uEO)
        dataLineString = dataLineString.replace(".", ",")
        
        file.write(dataLineString)
    
    file.close()
   
    
    
