import numpy as np
import scipy.signal as ss
import os

# Helper function to recognize whether a string is convertable to a float

# Input: - string

# Output: - Boolean which represents if the string is convertable to a float

def is_float(string=""):
    try:
        value = float(string)
        return True
    except:
        return False
        

# Writes all necessary processed data to a txt file

# Input:  - frameTimeStampArray: Array containing the timestamps of every frame
#         - frameSumWidthCentroidArray: Centroid pixel along the width from respective frame 
#         - frameSumHeightCentroidArray: Centroid pixel along the height from respective frame 
#         - frameSumHeightArrayList: Sum profile of frame along the height direcation from respective frame
#         - frameSumWidthArrayList: Sum profile of frame along the width direcation from respective frame
#         - tdmsFolderPath: Path of the folder which contains the respective tdms files
#         - experimentName: Name of the experiment aka EPxx

# Output: - savedDataPath: Path of the saved file

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

# Writes all necessary processed scaled position data to a txt file

# Input:  - frameTimeStampArray: Array containing the timestamps of every frame 
#         - frameTimeStampArrayList: List containing arrays of timestamps from respective periods
#         - widthPositionArrayList: List containing arrays of scaled width positions in units of m from respective periods
#         - heightPositionArrayList: List containing arrays of scaled height positions in units of m from respective periods
#         - tdmsFolderPath: Path of the folder which contains the respective tdms files
#         - experimentName: Name of the experiment aka EPxx

# Output: - savedDataPath: Path of the saved file

# writes to file "position Timestamp(s);width position (m);height position (m);period number \n"

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

# Writes all necessary processed scaled and filtered position data to a txt file

# Input:  - frameTimeStampArray: Array containing the timestamps of every frame 
#         - positionTimeArrayList: List containing arrays of timestamps from respective periods
#         - filteredWidthPositionArrayList: List containing arrays of scaled and filtered width positions in units of m from respective periods
#         - filteredHeightPositionArrayList: List containing arrays of scaled and filtered height positions in units of m from respective periods
#         - tdmsFolderPath: Path of the folder which contains the respective tdms files
#         - experimentName: Name of the experiment aka EPxx

# Output: - savedDataPath: Path of the saved file

# writes to file "position Timestamp(s);filtered widht position (m);filtered height position (m);period number \n"

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

# Writes all necessary processed data to a txt file

# Input:  - frameTimeStampArray: Array containing the timestamps of every frame
#         - velocityTimeArrayList: List containing arrays of timestamps from respective periods
#         - velocityArrayList: List containing arrays of velocities along oscillating direction in units of m/s from respective periods
#         - tdmsFolderPath: Path of the folder which contains the respective tdms files
#         - experimentName: Name of the experiment aka EPxx

# Output: - savedDataPath: Path of the saved file

# writes to file "velocity Timestamp(s);velocity(mm/s);period number \n"

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
    
# Returns a path for save file based on start and stop time and experiment

# Input:  - frameTimeStampArray: Array containing the timestamps of every frame
#         - tdmsFolderPath: Path of the folder which contains the respective tdms files
#         - experimentName: Name of the experiment aka EPxx
#         - extension: file type like ".txt"
#         - addText: text to add to path such as "scaled_position"

# Output: - savedDataPath: Path of the saved file, file name has the form "EPxx_start-stop_addText.extension" example "EP12_1.35-1.85_scaled_position.txt"
    
def generate_file_path(frameTimeStampArray=np.array([]),tdmsFolderPath="",experimentName="",extension="txt",addText=""):
    timeStampString = "_{:2.4f}-{:2.4f}".format(frameTimeStampArray[0],frameTimeStampArray[-1])
    
    savedDataPath = tdmsFolderPath
    savedDataPath = os.path.join(savedDataPath,experimentName)
    savedDataPath = savedDataPath + timeStampString + addText + "." + extension
    
    return savedDataPath

# Returns an array from a string of an array in a saved file

# Input:  - stringArray: string of an array: "[1 2 3 4 5]"

# Output: - array: np.array([1,2,3,4,5])

def cast_stringarray_to_string(stringArray=""):
    array = np.array([])
    
    stringArray = stringArray.replace("[","")
    stringArray = stringArray.replace("]","")
    stringArrayList = stringArray.split(" ")
    
    for value in stringArrayList:
        if(is_float(string=value)):
            array = np.append(array, float(value))
    
    return array

# Reads and returns data from saved files generated in the function above

# Input: - savedDataPath: Path of the saved file

# Output: - frameTimeStampArray: Array containing the timestamps of every frame
#         - frameSumWidthCentroidArray: Centroid pixel along the width from respective frame 
#         - frameSumHeightCentroidArray: Centroid pixel along the height from respective frame 
#         - frameSumHeightArrayList: Sum profile of frame along the height direcation from respective frame
#         - frameSumWidthArrayList: Sum profile of frame along the width direcation from respective frame

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
    
# Saves the fitted uEO and uEP 

# Input:  - frameTimeStampArray: Array containing the timestamps of every frame
#         - tdmsFolderPath: Path of the folder which contains the respective tdms files
#         - experimentName: Name of the experiment aka EPxx 
#         - extension: file type like ".txt"
#         - fittedVelocityList: List of arrays with two fitted values, the uEP and uEO for every respective period
#         - fittedCovVelocityList: List of arrays with the covariance matrix of the uEP and uEO fits for every respective period
#         - velocityTimeArrayList: List of time arrays of the velocity

# writes to file "periodStartTime(s);periodStopTime(s);uEP(mm/s);uEO(mm/s) \n"
    
def save_uEO_and_uEP_to_file(frameTimeStampArray=np.array([]),tdmsFolderPath="",experimentName="",extension="csv",fittedVelocityList=[],fittedCovVelocityList=[],velocityTimeArrayList=[]):
    filePath = generate_file_path(frameTimeStampArray=frameTimeStampArray, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName, extension=extension)
    file = open(filePath,'w')
    file.write("periodStartTime(s);periodStopTime(s);uEP(mm/s);uEO(mm/s) \n")
    
    for i in range(len(fittedVelocityList)):
        dataLineString = "{};{};{};{}\n".format(velocityTimeArrayList[i][0],velocityTimeArrayList[i][-1],fittedVelocityList[i][0],fittedVelocityList[i][1])
        dataLineString = dataLineString.replace(".", ",")
        
        file.write(dataLineString)
    
    file.close()
    
# Saves the fitted uEP given the uEO 

# Input:  - frameTimeStampArray: Array containing the timestamps of every frame
#         - tdmsFolderPath: Path of the folder which contains the respective tdms files
#         - experimentName: Name of the experiment aka EPxx 
#         - extension: file type like ".txt"
#         - fitteduEPArray: Array with fitted uEP value for every respective period
#         - velocityTimeArrayList: List of time arrays of the velocity
#         - uEO: Estimated uEO value

# writes to file "periodStartTime(s);periodStopTime(s);uEP(mm/s);uEO(mm/s) \n"

def save_fixed_uEO_and_uEP_to_file(frameTimeStampArray=np.array([]),tdmsFolderPath="",experimentName="",extension="csv",fitteduEPArray=np.array([]),velocityTimeArrayList=[],uEO=0.001):
    filePath = generate_file_path(frameTimeStampArray=frameTimeStampArray, tdmsFolderPath=tdmsFolderPath, experimentName=experimentName, extension=extension)
    file = open(filePath,'w')
    file.write("periodStartTime(s);periodStopTime(s);uEP(mm/s);uEO(mm/s) \n")
    
    for i in range(len(fitteduEPArray)):
        dataLineString = "{};{};{};{}\n".format(velocityTimeArrayList[i][0],velocityTimeArrayList[i][-1],fitteduEPArray[i],uEO)
        dataLineString = dataLineString.replace(".", ",")
        
        file.write(dataLineString)
    
    file.close()
   
    
    
