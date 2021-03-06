from SimpleCV import *
import cv2
from os.path import exists
from sys import argv

# prepares, selects the camera
def setup():
    global cam
    cam = Camera()
    time.sleep(1)


# Function to get the image from the camera
def GetImage():
    img = cam.getImage()                                            # Get image from camera
    img = cam.getImage()                                            # ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipHorizontal()                                      # Flip image (has to be tested on PI)
    return img


# Function to detect valve Handle:
def ObjectDetection(img, coords, data, object_area):
    Std_constant = 5                                            # Describes how many std dev of value to include
    min_value = 30                                              # Minimal illumination threshold
                                                                # Derive minimum saturation. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    min_area = object_area/4                                    # Derive minimum and maximum area objects can take
    max_area = object_area*4
    minsaturation = (data["avg_sat"]- Std_constant * data["std_sat"])
    img = img.toHSV()                                           # Convert image to HSV colour space
    blobs_threshold = 100                                       # Specify blobs colour distance threshold
                                                                # Apply filters to the image TODO: calibrate or change the filtering
    filtered = img.hueDistance(color = data["avg_hue"],
                               minsaturation = minsaturation,
                               minvalue = min_value)
    filtered = filtered.invert()                                # Invert black and white (to have LED as white)
    filtered = filtered.morphClose()                             # Perform morphOps TODO: look for better options
    all_blobs = filtered.findBlobs(threshval = blobs_threshold, minsize= min_area, maxsize = max_area )
    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
    elif all_blobs < 1:
        return "No blobs found"
    foreign_object = all_blobs[-1]                                       # foreign_object is the closes blob to the click
    return foreign_object


# READ THE DATA STORED IN CALIBRATION FILE
def read_calibration_data():
    storage = open(NAME_OF_CALIBRATION_FILE)
    object_coord_x = float(storage.readline().split()[1])
    object_coord_y = float(storage.readline().split()[1])
    object_name_stored = (storage.readline().split()[1:])
    object_area_stored = float(storage.readline().split()[1])
    object_rect_distance_stored = float(storage.readline().split()[1])
    object_aspect_ratio_stored = float(storage.readline().split()[1])
    object_average_hue = float(storage.readline().split()[1])
    object_average_sat = float(storage.readline().split()[1])
    object_std_sat = float(storage.readline().split()[1])
    storage.close()

    calibration_data = {"object_coord_x": object_coord_x,
                        "object_coord_y": object_coord_y,
                        "object_name_stored": object_name_stored,
                        "object_area_stored": object_area_stored,
                        "object_rect_distance_stored": object_rect_distance_stored,
                        "object_aspect_ratio_stored": object_aspect_ratio_stored,
                        "object_average_hue": object_average_hue,
                        "object_average_sat": object_average_sat,
                        "object_std_sat": object_std_sat
                        }
    print calibration_data
    return calibration_data


# Function to scan the image
def scanning_procedure(object_coords, colour_data, object_area):
    img = GetImage()                                                   # Get the image
    foreign_object = ObjectDetection(img, object_coords, colour_data, object_area)
                                                                       # Try to detect the object
    return foreign_object                                              # Return the result


# Function to process the results from images
def process_a_result(foreign_object):
    if foreign_object == "No blobs found":                          # If no blobs were found
        return "No blobs found"
    return "Object is present"                                      # If specific blob was found


# Function to calculate average of the results and return the final one
def calculate_average(results):
    Possibilities = {                 # Get the dictionary with all the options
    "Not found": 0,                    # Initialise variable for "No blobs found"
    "Object is present": 0,                        # Initialise variable for "Open"
    }
    for variable in results:                    # Increment each time the specific result is acquired
        if variable[0] == "N":
            Possibilities["Not found"] += 1
        elif variable[0] == "O":
            Possibilities["Object is present"] += 1
        else:
            print "Something strange happened." # If none of the results fit (Not possible)
    Final_result = max(Possibilities, key=Possibilities.get)
                                                # Get the max value of the dictionary
    return Final_result


### MAIN SOFTWARE:

setup()

NAME_OF_FOREIGN_OBJECT = str(argv[1])                   # NAME OF THE FOREIGN OBJECT WHICH IS DETECTED.
                                                        # ALSO NAME OF THE FILE WITH CALIBRATION DATA
NAME_OF_CALIBRATION_FILE = NAME_OF_FOREIGN_OBJECT + ".txt"
print "Scanning for" + NAME_OF_CALIBRATION_FILE         # Prompt the user which object is being detected
n = 10                                                  # NUMBER OF SAMPLE IMAGES
results = range(n)                                      # Create a list of results


# Perform camera setup
if not exists(NAME_OF_CALIBRATION_FILE):
    raw_input("Calibration for this object has not been done. Please do the calibration first before running the scan")
    #return "error"             FOR LATER

# Read and store the calibration data
calibration_data = read_calibration_data()

# RENAMING FOR EASIER ACCESS:
object_coord_x = calibration_data['object_coord_x']
object_coord_y = calibration_data['object_coord_y']
object_name = calibration_data['object_name_stored']
object_area = calibration_data['object_area_stored']
object_rect_distance = calibration_data['object_rect_distance_stored']
object_aspect_ratio = calibration_data['object_aspect_ratio_stored']
object_average_hue = calibration_data['object_average_hue']
object_average_sat = calibration_data['object_average_sat']
object_std_sat = calibration_data['object_std_sat']

object_coords = (object_coord_x, object_coord_y)
colour_data = {"avg_hue": object_average_hue,
               "avg_sat": object_average_sat,
               "std_sat": object_std_sat}


for i in range(0, len(results)):

    # Try to detect foreign object TODO: Implement aspect ratio and sqare distance measurements, modify the filtering values
    foreign_object_present = scanning_procedure(object_coords,colour_data, object_area)

    processed_result = process_a_result(foreign_object_present)
    results[i] = processed_result
    print results[i]

final_result = calculate_average(results)

print "%s is:" %NAME_OF_FOREIGN_OBJECT, final_result
