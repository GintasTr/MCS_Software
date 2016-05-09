from SimpleCV import *
import cv2
from os.path import exists


# prepares, selects the camera
def setup():
    global cam
    cam = Camera()
    time.sleep(1)


# for image acquisition from camera (and flipping)
def GetImage():
    img = cam.getImage()
    img = cam.getImage()        ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipHorizontal()
    return img


# Function to apply colour distance filter
def apply_filter(Calibration_values, img):
    #min_value = 30                                                  # If needed - minimal illumination of the object
    minsaturation = (Calibration_values["AvSat"]/2)
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
def do_Orange_Flap_scanning():
    STORAGE_FILE = "Orange_flap_calibration_data.txt"
    blobs_threshold_main = 180          #thresholds for calibration blob detection and main process blob detection
    blobs_min_size_main = 1000
    NUMBER_OF_ITERATIONS = 5
    results = range(NUMBER_OF_ITERATIONS)                  # Initialise results list
    setup()


    calibration_data_location = os.path.join(os.path.dirname(__file__), 'Calibration_files\\', STORAGE_FILE)
    print "Reading from: " + calibration_data_location

    if not exists(calibration_data_location):
        print ("Calibration data for flap position detection has not been found. "
               "Please do the calibration first and store its data to "
               "Calibration_files folder before running the scan")
        return "Error"                                                    # If error occurs

    flat_data = read_calibration_data(calibration_data_location)          # Extract calibration data
    slope_data = flat_data.pop("SlopeWHRatio")

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
        filtered.show()
        flap = possible_flaps[0]
        #Img.dl().rectangle2pts(flap.topLeftCorner(), flap.bottomRightCorner(),Color.RED, width = 5) #FOR FEEDBACK ONLY
        #Img.show()  #FOR FEEDBACK ONLY
        detectedRatio = flap.width()/flap.height()
        if detectedRatio > (flat_data["FlatWHRatio"]+ slope_data) / 2:
            results[i] = "Slope position"
            print "Flap is in slope position"
        elif detectedRatio <= (flat_data["FlatWHRatio"]+ slope_data) / 2:
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