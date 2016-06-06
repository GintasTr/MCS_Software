# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".
#from Valve_Handle_V6_Calibration_Demo import do_Calibration_procedure
from Valve_calibration_show_images import *
import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')
from Valve_scanning_show_images import *
from SimpleCV import *
from os.path import exists

# cam = None
# prepares, selects the camera
def setup(cam_received):
    global cam
    cam = cam_received
    # if cam == None:
    #     cam = Camera(0, {"width": 1024, "height": 768})    # Only for RPI 2592x1944. For calibration - 1024x768
    #cam = Camera                                          # Only for laptop
    # time.sleep(1)


# for image acquisition from camera (and flipping)
def GetImage():
    # img = cam.getImage()
    img = cam.getImage()        ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS? ###COMMENT OUT
    #img = img.flipVertical()        ###COMMENT IN
    img = img.flipHorizontal()
    return img

# Shows the image until the button is pressed
def show_image_until_pressed(img):
    disp = Display()                                        # Create a display
    while disp.isNotDone():                                 # Loop until display is not needed anymore
        if disp.mouseLeft:                                  # Check if left click was used on display
            disp.done = True                                # Turn off Display
        img.show()                                          # Show the image on Display
    Display().quit()                                        # Exit the display so it does not go to "Not responding"

# Briefly flashes the image
def show_image_briefly(img):
    img.show()                                              # Show the image on Display


# Function to detect valve Handle:
def HandleDetection(img, coords, data):
    #Std_constant = 4                                            # Describes how many std dev of value to include
    min_value = 30                                              # Minimal illumination threshold
                                                                # Derive minimum saturation. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    minsaturation = int(2*data["avg_sat"]/3)       #(data["avg_sat"]- Std_constant * data["std_sat"])
    img = img.toHSV()                                           # Convert image to HSV colour space
    blobs_threshold = 245                                       # Specify blobs colour distance threshold
    blobs_min_size = 500                                       # Specify minimum blobs size
                                                                # Apply filters to the image
    filtered = img.hueDistance(color = data["avg_hue"],
                               minsaturation = minsaturation,
                               minvalue = min_value)
    filtered = filtered.invert()                                # Invert black and white (to have LED as white)
    #filtered = filtered.morphClose()                            # Perform morphOps
    filtered = filtered.erode(1)    # ADDED TESTING
    filtered = filtered.dilate(1)    # ADDED TESTING
    all_blobs = filtered.findBlobs(threshval = blobs_threshold, minsize=blobs_min_size)

    # all_blobs.draw(width = 5)     #TESTING
    # show_image_until_pressed(filtered)

    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs = all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
    elif all_blobs < 1:
        return "No blobs found"
    m_Handle = all_blobs[0]                                       # m_Handle is the closes blob to the click
    return m_Handle


# READ THE DATA STORED IN CALIBRATION FILE
def read_calibration_data(STORAGE_LOCATION):

    with open(STORAGE_LOCATION, "r") as storage:
        Handle_coord_x = float(storage.readline().split()[1])
        Handle_coord_y = float(storage.readline().split()[1])
        closed_angle_stored = float(storage.readline().split()[1])
        open_angle_stored = float(storage.readline().split()[1])
        closed_average_hue = float(storage.readline().split()[1])
        closed_average_sat = float(storage.readline().split()[1])
        closed_std_sat = float(storage.readline().split()[1])

    calibration_data = {"Handle_coord_x": Handle_coord_x,
                        "Handle_coord_y": Handle_coord_y,
                        "closed_angle_stored": closed_angle_stored,
                        "open_angle_stored": open_angle_stored,
                        "closed_average_hue": closed_average_hue,
                        "closed_average_sat": closed_average_sat,
                        "closed_std_sat": closed_std_sat
                        }
    print calibration_data
    return calibration_data


def scanning_procedure_shown(Handle_coords,colour_data):

    img = GetImage()                                           # Get the image
    Handle = HandleDetection(img, Handle_coords, colour_data)  # Try to detect the handle
    return {"Handle": Handle, "img":img}                       # Return the result


# Function to process the results from images.
# Returns dictionary of: results = {"position": "Closed" or "Open", "angle_info": angle from position
def process_a_result(handle, closed_angle, open_angle):

    if handle == "No blobs found":                          # If no blobs were found
        angle_info = 99
        angle_results = {"position": "Error - No blobs found",
                         "angle_info": angle_info}
        return angle_results
    current_angle = handle.angle()
    inverse_to_distance_from_closed = abs((current_angle-closed_angle)%180 - 90)
    inverse_to_distance_from_open = abs((current_angle-open_angle)%180 - 90)
    if inverse_to_distance_from_closed > inverse_to_distance_from_open:
        angle_info = 90 - inverse_to_distance_from_closed
        angle_results = {"position": "Closed",
                         "angle_info": angle_info}
        return angle_results
    else:
        angle_info = 90 - inverse_to_distance_from_open
        angle_results = {"position": "Open",
                         "angle_info": angle_info}
        return angle_results


# Returns dictionary of: results = {"position": "Closed" or "Open", "angle_info": angle from position
def process_a_result_shown(handle, closed_angle, open_angle, img):

    if handle == "No blobs found":                          # If no blobs were found
        angle_info = 99
        angle_results = {"position": "Error - No blobs found",
                         "angle_info": angle_info}
        keep_scanning = scanning_handle_not_found(img)
        return keep_scanning

    current_angle = handle.angle()

    inverse_to_distance_from_closed = abs((current_angle-closed_angle)%180 - 90)
    inverse_to_distance_from_open = abs((current_angle-open_angle)%180 - 90)
    if inverse_to_distance_from_closed > inverse_to_distance_from_open:
        angle_info = 90 - inverse_to_distance_from_closed
        angle_results = {"position": "Closed",
                         "angle_info": angle_info}

    else:
        angle_info = 90 - inverse_to_distance_from_open
        angle_results = {"position": "Open",
                         "angle_info": angle_info}

    keep_scanning = angle_comparison_image(current_angle, closed_angle, open_angle, img, handle,
                                           angle_results["position"], angle_results["angle_info"])
    return keep_scanning



# Function to calculate average of the results and return the final one
def calculate_average(results):
    Possibilities = {                 # Get the dictionary with all the options
    "Error - Not_found": 0,           # Initialise variable for "No blobs found"
    "Open": 0,                        # Initialise variable for "Open"
    "Closed" : 0                      # Initialise variable for "Closed"
    }
    for variable in results:                    # Increment each time the specific result is acquired
        if variable[0] == "E":
            Possibilities["Error - Not_found"] += 1
        elif variable[0] == "O":
            Possibilities["Open"] += 1
        elif variable[0] == "C":
            Possibilities["Closed"] += 1
        else:
            print "Something strange happened." # If none of the results fit (Not possible)
    Final_result = max(Possibilities, key=Possibilities.get)
                                                # Get the max value of the dictionary
    return Final_result


# MAIN SOFTWARE FUNCTION:
def do_Valve_Handle_scanning(cam_received):
    # MAIN SOFTWARE:
    start_scanning_image()

    STORAGE_FILE = "valve_handle_data.txt"

    setup(cam_received)                                                 # Perform camera setup

    #ONLY USED FOR WINDOWS
    #calibration_data_location = os.path.join(os.path.dirname(__file__), 'Calibration_files\\', STORAGE_FILE)
    calibration_data_location = os.path.join(os.path.dirname(__file__), STORAGE_FILE)


    print "Reading from: " + calibration_data_location

    if not exists(calibration_data_location):
        print ("Calibration data for this object has not been found. "
               "Please do the calibration first and store its data to "
               "Calibration_files folder before running the scan")
        return "Error"                                      # If error occurs - only used when called by other software

    n = 5                                                   # NUMBER OF SAMPLE IMAGES
    results = range(n)                                      # Create a list of results


    # Read and store the calibration data
    calibration_data = read_calibration_data(calibration_data_location)

    # RENAMING FOR EASIER ACCESS:
    Handle_coord_x = calibration_data['Handle_coord_x']
    Handle_coord_y = calibration_data['Handle_coord_y']
    closed_angle_stored = calibration_data['closed_angle_stored']
    open_angle_stored = calibration_data['open_angle_stored']
    closed_average_hue = calibration_data['closed_average_hue']
    closed_average_sat = calibration_data['closed_average_sat']
    closed_std_sat = calibration_data['closed_std_sat']


    reading_from_file_image(Handle_coord_x,Handle_coord_y, closed_angle_stored,
                            open_angle_stored,closed_average_hue,closed_average_sat)
    # SCALE COORDINATES DUE TO RESOLUTION DIFFERENCE BETWEEN CALIBRATION (1024x768) and scanning (2592x1944)
    #Handle_coord_x = Handle_coord_x * 2592/1024
    #Handle_coord_y = Handle_coord_y * 1944/768

    Handle_coords = (Handle_coord_x, Handle_coord_y)
    colour_data = {"avg_hue": closed_average_hue,
                   "avg_sat": closed_average_sat,
                   "std_sat": closed_std_sat}

    # Initialise variables
    open_angle_detected_average, closed_angle_detected_average, open_angle_numbers, closed_angle_numbers = 0, 0, 0, 0
    show_scanning = True
    while show_scanning:
        result_dictionary_shown = scanning_procedure_shown(Handle_coords,colour_data)
        result_shown = result_dictionary_shown["Handle"]
        show_scanning = process_a_result_shown(result_shown, closed_angle_stored,
                                                        open_angle_stored,result_dictionary_shown["img"])

    start_multiple_scanning()
    for i in range(0, len(results)):
        result_dictionary_shown = scanning_procedure_shown(Handle_coords,colour_data)
        result = result_dictionary_shown["Handle"]
        processed_result = process_a_result(result, closed_angle_stored, open_angle_stored)
                                                                # Returns dictionary {"position", "angle_info"}
        results[i] = processed_result["position"]

        print "Single result is:", processed_result

        if processed_result["position"] == "Open":
            open_angle_detected_average = open_angle_detected_average + processed_result["angle_info"]
            open_angle_numbers += 1

        if processed_result["position"] == "Closed":
            closed_angle_detected_average = closed_angle_detected_average + processed_result["angle_info"]
            closed_angle_numbers += 1

        #print results[i]        # TESTING

    final_result = calculate_average(results)

    if final_result == "Open":                                          # Calculate and select correct average angle
        angle_average = open_angle_detected_average/open_angle_numbers
    elif final_result == "Closed":
        angle_average = closed_angle_detected_average/closed_angle_numbers
    else:
        angle_average = 99

    angle_average = ("%.2f" % round(angle_average,2))                # Convert to the required format
    end_multiple_scanning_results(final_result, angle_average)
    fault_detection_output = {"angle_information": angle_average,
                              "fault_detection_feedback": final_result
                             }
    print "Coolant valve handle position is:", fault_detection_output["fault_detection_feedback"],\
        "and angle information is:", fault_detection_output["angle_information"]
    return fault_detection_output


# If called by itself:
if __name__ == '__main__':
    cam = Camera(0, {"width": 960, "height": 720})
    output = do_Valve_Handle_scanning(cam)
    print output