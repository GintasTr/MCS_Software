from SimpleCV import *
import cv2
from Setup import *
from User_Interface_Commands import *
from Calibration import *
from Camera_Wrapper import *
from Image_Processing import *
from Calibration import *

# Function to detect the main LED:
def ValveDetection(img, coords, data):
    Std_constant = 5                                            # Describes how many std dev of value to include
    min_value = 30                                              # Minimal illumination threshold
                                                                # Derive minimum saturation. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    minsaturation = (data["avg_sat"]- Std_constant * data["std_sat"])
    img = img.toHSV()                                           # Convert image to HSV colour space
    blobs_threshold = 100                                       # Specify blobs colour distance threshold
    blobs_min_size =  1000                                       # Specify minimum blobs size
                                                                # Apply filters to the image TODO: calibrate or change the filtering
    filtered = img.hueDistance(color = data["avg_hue"],
                               minsaturation = minsaturation,
                               minvalue = min_value)
    filtered = filtered.invert()                                # Invert black and white (to have LED as white)
    filtered = filtered.morphClose()                             # Perform morphOps TODO: look for better options
    all_blobs = filtered.findBlobs(threshval = blobs_threshold, minsize=blobs_min_size)
    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
        return "No blobs found"
    m_valve = all_blobs[-1]                                       # m_valve is the closes blob to the click
    return m_valve


# Function to get the colour data of small area around certain point
def GetColourData(img, coords):
    CROP_SIZE = 10                                              # Area around the point to be evaluated (square width)

    cropped = img.crop(coords[0],                               # Adjust cropping area (x,y,w,h)
                       coords[1], CROP_SIZE,
                       CROP_SIZE, centered= True)
    cropped = cropped.getNumpyCv2()                             # Convert image to numpy array compatible with openCV
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)          # Convert image to HSV colour scheme with openCV
    meanHue = np.mean(cropped[:,:,0])                           # Slice the NumPy array to get the mean Hue
    meanSat = np.mean(cropped[:,:,1])                           # Slice the NumPy array to get the mean Sat
    stdSat = np.std(cropped[:,:,1])                             # Slice the NumPy array to get the std Sat
    minSat = np.min(cropped[:,:,1])                             # Slice the NumPy array to get the min Sat
    meanValue = np.mean(cropped[:,:,2])                         # Slice the NumPy array to get the mean Brightness
    # print meanHue, "- mean Hue"                                 # Print the obtained values for debugging
    # print meanSat, "- mean Sat"
    # print stdSat, "- std Sat"
    # print minSat, "- min Sat"
    # print meanValue, " - min Val"
    # raw_input("check results")                                  # FOR DEBUGGING

    hsv_data = {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    return hsv_data