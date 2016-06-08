# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
from os.path import exists
from foreign_object_scanning_show_images import *
cam = None
# prepares, selects the camera
def setup(cam_local):
    global cam
    cam = cam_local
    # if cam == None:
    #     cam = Camera(0, {"width": 1024, "height": 768})    # Only for RPI 2592x1944. For calibration - 1024x768
    # #cam = Camera                                          # Only for laptop
    # time.sleep(1)


# for image acquisition from camera (and flipping)
def GetImage():
    # img = cam.getImage()
    img = cam.getImage()        ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS? ###COMMENT OUT
    #img = img.flipVertical()        ###COMMENT IN
    img = img.flipHorizontal()
    return img


# Function to detect foreign object:
def ObjectDetection(img, coords, data, object_area):
    #Std_constant = 5                                            # Describes how many std dev of value to include
    min_value = 30                                              # Minimal illumination threshold
                                                                # Derive minimum saturation. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    min_area = object_area/4                                    # Derive minimum and maximum area objects can take
    max_area = object_area*4
    minsaturation = int(2*data["avg_sat"]/3)         #(data["avg_sat"]- Std_constant * data["std_sat"])
    img = img.toHSV()                                           # Convert image to HSV colour space
    blobs_threshold = 240 #170 on laptop                        # Specify blobs colour distance threshold
                                                                # Apply filters to the image
    filtered = img.hueDistance(color = data["avg_hue"],
                               minsaturation = minsaturation,
                               minvalue = min_value)
    filtered = filtered.invert()                                # Invert black and white (to have LED as white)

    # filtered = filtered.morphClose()                            # Perform morphOps


    filtered = filtered.erode(iterations= 2)
    filtered = filtered.dilate(iterations= 2)

    all_blobs = filtered.findBlobs(threshval = blobs_threshold,
                                   minsize= min_area,
                                   maxsize = max_area )
    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs = all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
    elif all_blobs < 1:
        return "No blobs found"
    foreign_object = all_blobs[0]                               # foreign_object is the closes blob to the click

    return foreign_object


def object_detection_show(img, coords, data, object_area):
    min_value = 30                                              # Minimal illumination threshold
                                                                # Derive minimum saturation. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    min_area = object_area/4                                    # Derive minimum and maximum area objects can take
    max_area = object_area*4
    minsaturation = int(2*data["avg_sat"]/3)                    #(data["avg_sat"]- Std_constant * data["std_sat"])
    img = img.toHSV()                                           # Convert image to HSV colour space
    blobs_threshold = 240 #170 on laptop                        # Specify blobs colour distance threshold
                                                                # Apply filters to the image TODO: calibrate or change the filtering
    filtered = img.hueDistance(color = data["avg_hue"],
                               minsaturation = minsaturation,
                               minvalue = min_value)
    filtered = filtered.invert()                                # Invert black and white (to have LED as white)


    # filtered = filtered.morphClose()                            # Perform morphOps TODO: look for better options

    filtered = filtered.erode(iterations= 2)
    filtered = filtered.dilate(iterations= 2)


    all_blobs = filtered.findBlobs(threshval = blobs_threshold,
                                   minsize= min_area,
                                   maxsize = max_area )
    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs = all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
    elif all_blobs < 1:
        return scanning_object_not_found(img)
    foreign_object = all_blobs[0]                               # foreign_object is the closes blob to the click

    return show_filtered_image(img, all_blobs, foreign_object)

# READ THE DATA STORED IN CALIBRATION FILE
def read_calibration_data(NAME_OF_CALIBRATION_FILE):

    with open(NAME_OF_CALIBRATION_FILE, "r") as storage:
        object_coord_x = float(storage.readline().split()[1])
        object_coord_y = float(storage.readline().split()[1])
        object_name_stored = (storage.readline().split()[1:])
        object_area_stored = float(storage.readline().split()[1])
        object_rect_distance_stored = float(storage.readline().split()[1])
        object_aspect_ratio_stored = float(storage.readline().split()[1])
        object_average_hue = float(storage.readline().split()[1])
        object_average_sat = float(storage.readline().split()[1])
        object_std_sat = float(storage.readline().split()[1])

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

def scanning_procedure_show(object_coords, colour_data, object_area):
    img = GetImage()                                                   # Get the image

    result = object_detection_show(img, object_coords, colour_data, object_area)
    return result                                              # Return the result


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
            return "Error"
    Final_result = max(Possibilities, key=Possibilities.get)
                                                # Get the max value of the dictionary
    return Final_result


### MAIN SOFTWARE:
def detect_foreign_object(cam_local, calibration_name):
    setup(cam_local)
    start_scanning_image()
    NAME_OF_FOREIGN_OBJECT = calibration_name               # NAME OF THE FOREIGN OBJECT WHICH IS DETECTED.
                                                            # ALSO NAME OF THE FILE WITH CALIBRATION DATA
    #ONLY USED FOR WINDOWS
    #fn = os.path.join(os.path.dirname(__file__), 'Calibration_files\\', NAME_OF_FOREIGN_OBJECT)
    fn = os.path.join(os.path.dirname(__file__), NAME_OF_FOREIGN_OBJECT)

    NAME_OF_CALIBRATION_FILE = fn + ".txt"


    print "Scanning for " + NAME_OF_CALIBRATION_FILE        # Prompt the user which object is being detected
    n = 5                                                   # NUMBER OF SAMPLE IMAGES
    results = range(n)                                      # Create a list of results

    if not exists(NAME_OF_CALIBRATION_FILE):
        print ("Calibration data for this object has not been found. "
               "Please do the calibration first and store its data to "
               "Calibration_files folder before running the scan")
        return "Error"                                      # If error occurs - only used when called by other software



    # Read and store the calibration data
    calibration_data = read_calibration_data(NAME_OF_CALIBRATION_FILE)

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


    # SCALE COORDINATES DUE TO RESOLUTION DIFFERENCE BETWEEN CALIBRATION (1024x768) and scanning (2592x1944)
    #m_led_coord_x = m_led_coord_x * 2592/1024
    #m_led_coord_y = m_led_coord_y * 1944/768
    #object_area = object_area * 6

    object_coords = (object_coord_x, object_coord_y)
    colour_data = {"avg_hue": object_average_hue,
                   "avg_sat": object_average_sat,
                   "std_sat": object_std_sat}

    reading_from_file_image(object_coords, object_name, object_area,
                  object_rect_distance, object_aspect_ratio,
                  object_average_hue, object_average_sat, object_std_sat)

    show_demo = True
    while show_demo:
        show_demo = scanning_procedure_show(object_coords, colour_data, object_area)

    start_multiple_scanning()
    for i in range(0, len(results)):

        # Try to detect foreign object TODO: Implement aspect ratio and sqare distance measurements, modify the filtering values
        foreign_object_present = scanning_procedure(object_coords,colour_data, object_area)

        processed_result = process_a_result(foreign_object_present)
        results[i] = processed_result

        if results[i] == "Object is present":                       # If object was found
            found_object_x = foreign_object_present.coordinates()[0]
            found_object_y = foreign_object_present.coordinates()[1]
            print "Object is present at x - %i and y - %i" % (found_object_x,found_object_y)
        else:
            print "Not found"


        #print results[i]                                           # Used for debugging

    final_result = calculate_average(results)

    if final_result == "Not found":
        found_object_x = 0000
        found_object_y = 0000

    found_object_x = "%04i" % found_object_x
    found_object_y = "%04i" % found_object_y

    print "%s is:" %NAME_OF_FOREIGN_OBJECT, final_result, " with coordinates of:", found_object_x, found_object_y

    end_multiple_scanning_results(final_result, object_coord_x, object_coord_y)

    fault_detection_output = {"fault_detection_feedback": final_result,
                          "object_coord_x": found_object_x,
                          "object_coord_y": found_object_y}


    return fault_detection_output

# If called by itself, just so that it does not show error when something is returned
if __name__ == '__main__':
    cam = Camera(0, {"width": 960, "height": 720})    # Only for RPI 2592x1944. For calibration - 1024x768
    result = detect_foreign_object(cam, "1")
    print "Result returned from the module: ", result