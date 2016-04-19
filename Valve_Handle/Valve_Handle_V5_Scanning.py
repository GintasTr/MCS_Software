from SimpleCV import *
import cv2
from os.path import exists

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
def HandleDetection(img, coords, data):
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
    elif all_blobs < 1:
        return "No blobs found"
    m_Handle = all_blobs[-1]                                       # m_Handle is the closes blob to the click
    return m_Handle


# READ THE DATA STORED IN CALIBRATION FILE
def read_calibration_data():
    storage = open("valve_handle_data.txt")
    Handle_coord_x = float(storage.readline().split()[1])
    Handle_coord_y = float(storage.readline().split()[1])
    closed_angle_stored = float(storage.readline().split()[1])
    open_angle_stored = float(storage.readline().split()[1])
    closed_average_hue = float(storage.readline().split()[1])
    closed_average_sat = float(storage.readline().split()[1])
    closed_std_sat = float(storage.readline().split()[1])
    storage.close()

    calibration_data = {"Handle_coord_x": Handle_coord_x,
                        "Handle_coord_y": Handle_coord_y,
                        "closed_angle_stored": closed_angle_stored,
                        "open_angle_stored": open_angle_stored,
                        "closed_average_hue": closed_average_hue,
                        "closed_average_sat": closed_average_sat,
                        "closed_std_sat": closed_std_sat
                        }
    return calibration_data


# Function to scan the image
def scanning_procedure(Handle_coords, colour_data):
    img = GetImage()                                           # Get the image
    Handle = HandleDetection(img, Handle_coords, colour_data)  # Try to detect the handle
    return Handle                                              # Return the result


# Function to process the results from images
def process_a_result(handle, closed_angle, open_angle):
    middle_angle = abs(closed_angle-open_angle)/2           # Find the middle distance between two angles
    if handle == "No blobs found":                          # If no blobs were found
        return "No blobs found"
    if abs(handle.angle() - closed_angle) > middle_angle:   # Check if handle is open or closed
        return "Open"
    else:
        return "Closed"


# Function to calculate average of the results and return the final one
def calculate_average(results):
    Possibilities = {                 # Get the dictionary with all the options
    "Not_found": 0,                    # Initialise variable for "No blobs found"
    "Open": 0,                        # Initialise variable for "Open"
    "Closed" : 0                      # Initialise variable for "Closed"
    }
    for variable in results:                    # Increment each time the specific result is acquired
        if variable[0] == "N":
            Possibilities["Not_found"] += 1
        elif variable[0] == "O":
            Possibilities["Open"] += 1
        elif variable[0] == "C":
            Possibilities["Closed"] += 1
        else:
            print "Something strange happened." # If none of the results fit (Not possible)
    Final_result = max(Possibilities, key=Possibilities.get)
                                                # Get the max value of the dictionary
    return Final_result

# MAIN SOFTWARE:

setup()

n = 10                              # NUMBER OF SAMPLE IMAGES
results = range(n)                  # Create a list of results


# Perform camera setup
if not exists("valve_handle_data.txt"):
    raw_input("Calibration has not been done. Please do the calibration first before running the scan")
    #return "error"             FOR LATER

# Read and store the calibration data
calibration_data = read_calibration_data()

# RENAMING FOR EASIER ACCESS:
Handle_coord_x = calibration_data['Handle_coord_x']
Handle_coord_y = calibration_data['Handle_coord_y']
closed_angle_stored = calibration_data['closed_angle_stored']
open_angle_stored = calibration_data['open_angle_stored']
closed_average_hue = calibration_data['closed_average_hue']
closed_average_sat = calibration_data['closed_average_sat']
closed_std_sat = calibration_data['closed_std_sat']

Handle_coords = (Handle_coord_x, Handle_coord_y)
colour_data = {"avg_hue": closed_average_hue,
               "avg_sat": closed_average_sat,
               "std_sat": closed_std_sat}


for i in range(0, len(results)):
    result = scanning_procedure(Handle_coords,colour_data)
    processed_result = process_a_result(result, closed_angle_stored, open_angle_stored)
    results[i] = processed_result
    print results[i]

final_result = calculate_average(results)

print "Coolant valve handle position is:", final_result
