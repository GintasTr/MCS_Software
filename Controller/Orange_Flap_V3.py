# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
from os.path import exists

cam = None
# prepares, selects the camera
def setup():
    global cam
    if cam == None:
        cam = Camera(0, {"width": 1024, "height": 768})    # Only for RPI 2592x1944. For calibration - 1024x768
    #cam = Camera                                          # Only for laptop
    time.sleep(1)


# for image acquisition from camera (and flipping)
def GetImage():
    img = cam.getImage()
    #img = cam.getImage()        ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipVertical()
    return img


# Function to apply colour distance filter
def apply_filter(Calibration_values, img):
    #min_value = 30                                                  # If needed - minimal illumination of the object
    minsaturation = 40  #(Calibration_values["AvSat"]/2)
    img = img.toHSV()
    Filtered = img.hueDistance(color = Calibration_values["AvHue"],
                               minsaturation = minsaturation
                               #minvalue = min_value
                               )
    Filtered = Filtered.invert()
    Filtered = Filtered.erode(1)
    Filtered = Filtered.dilate(2)
    return Filtered


# Function to read calibration file
# Reminder: calibration_data = {"max_light": max_light, "min_light:": min_light,"m_led_coords": m_led_coords,
# "m_led_data": m_led_data, "dist_led": dist_led,"seq_time": seq_time}
def read_calibration_data(STORAGE_FILE):

    with open(STORAGE_FILE, "r") as storage:
        mouseX = int(storage.readline().split()[1])
        mouseY = int(storage.readline().split()[1])
        AvHue = float(storage.readline().split()[1])
        AvSat = float(storage.readline().split()[1])
        FlatWHRatio = float(storage.readline().split()[1])
        SlopeWHRatio = float(storage.readline().split()[1])

    # SCALE COORDINATES DUE TO RESOLUTION DIFFERENCE BETWEEN CALIBRATION (1024x768) and scanning (2592x1944)
    #mouseX = mouseX * 2592/1024
    #mouseY = mouseY * 1944/768


    calibration_data = {"mouseX": mouseX,
                        "mouseY": mouseY,
                        "AvHue": AvHue,
                        "AvSat": AvSat,
                        "FlatWHRatio": FlatWHRatio,
                        "SlopeWHRatio": SlopeWHRatio,
                        }
    print calibration_data
    return calibration_data


# Function to calculate average of the results and return the final one
def calculate_average(results):
    Possibilities = {                       # Get the dictionary with all the options
    "Error - No flaps found": 0,                    # Initialise variable for "No flaps found"
    "Slope position": 0,                    # Initialise variable for "Slope position"
    "Flat position": 0,                     # Initialise variable for "Flat position"
    }
    for variable in results:                # Increment each time the specific result is acquired
        if variable[0] == "E":
            Possibilities["Error - No flaps found"] += 1
        elif variable[0] == "S":
            Possibilities["Slope position"] += 1
        elif variable[0] == "F":
            Possibilities["Flat position"] += 1
        else:
            print "Something strange happened." # If none of the results fit (Not possible)

    Final_result = max(Possibilities, key=Possibilities.get)
    if Possibilities[Final_result] == 2:
        Final_result = "Error - No flaps found"

                                                # Get the max value of the dictionary
    return Final_result



# Main function:
def do_Orange_Flap_scanning(): ## DEBUGING TESTING
    STORAGE_FILE = "Orange_flap_calibration_data.txt"
    blobs_threshold_main = 240           # 170 on laptop.
                                         # thresholds for calibration blob detection and main process blob detection
    blobs_min_size_main = 1000          # 1000 On laptop
    NUMBER_OF_ITERATIONS = 5
    results = range(NUMBER_OF_ITERATIONS)                  # Initialise results list

    setup()

    #ONLY USED FOR WINDOWS
    #calibration_data_location = os.path.join(os.path.dirname(__file__), 'Calibration_files\\', STORAGE_FILE)
    calibration_data_location = os.path.join(os.path.dirname(__file__), 'Calibration_files', STORAGE_FILE)
    print "Reading from: " + calibration_data_location

    if not exists(calibration_data_location):
        print ("Calibration data for flap position detection has not been found. "
               "Please do the calibration first and store its data to "
               "Calibration_files folder before running the scan")
        return "Error"                                                    # If error occurs

    flat_data = read_calibration_data(calibration_data_location)          # Extract calibration data
    slope_data = flat_data.pop("SlopeWHRatio")
    threshold_ratio = (flat_data["FlatWHRatio"]+ slope_data) / 2
    print "threshold ratio is:", threshold_ratio
    ## Main loop:
    for i in range(0, len(results)):
        Img = GetImage()
        Img = Img.toHSV()
        filtered = apply_filter(flat_data, Img)
        possible_flaps = filtered.findBlobs(threshval = blobs_threshold_main, minsize=blobs_min_size_main)
        if possible_flaps > 1:
            possible_flaps = possible_flaps.sortDistance(point = (flat_data["mouseX"], flat_data["mouseY"]))
        elif possible_flaps < 1:
            results[i] = "Error - No flaps found"
            continue
        possible_flaps.draw(width=3)
        #filtered.show()                                                # Too slow for RPI
        flap = possible_flaps[0]
        #Img.dl().rectangle2pts(flap.topLeftCorner(), flap.bottomRightCorner(),Color.RED, width = 5) #FOR FEEDBACK ONLY
        #Img.show()  #FOR FEEDBACK ONLY
        detectedRatio = float(flap.width())/float(flap.height())
        print "Detected ratio is:", detectedRatio
        if detectedRatio > threshold_ratio:
            results[i] = "Slope position"
            print "Flap is in slope position"
        elif detectedRatio <= threshold_ratio:
            results[i] = "Flat position"
            print "Flap is in flat position"
        else:
            results[i] = "Error - not finished correctly"
            print "Error - Detected incorrectly"
    print "Result list: ", results
    final_result = calculate_average(results)
    return final_result

# If called by itself:
if __name__ == '__main__':
    print do_Orange_Flap_scanning()