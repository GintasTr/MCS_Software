# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI


from SimpleCV import *
from object_calibration_show_images import *
import cv2

# prepares, selects the camera
def setup(cam_received):
    global cam
    cam = cam_received

    # cam = Camera(0, {"width": 1024, "height": 768})        # Only for RPI 2592x1944. For calibration - 1024x768
    #cam = Camera()
    # time.sleep(1)

# for image acquisition from camera (and flipping)
def GetImage():
    #img = cam.getImage() ###COMMENT OUT
    img = cam.getImage()                                    ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipVertical()
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


# Function to get the user confirmation about the image
def GetConfirmation(ConfirmationText):
    while True:                                                     # Loop until valid response
        print ConfirmationText                                      # Ask for confirmation
        try:                                                        # Catch Index error in case of too fast response
            userInput = raw_input()                                 # Check user input
            userInput = userInput.lower()                           # Make it lower case
            if userInput[0] == "y":                                 # Check if it is y, n, or something else
                return True                                         # Return respective values
            elif userInput[0] == "n":
                return False
        except(IndexError):                                         # In case of Index error (too fast response)
            print "Something is wrong, try again."
        else:
            print "Incorrect value entered."


# Function to ask inform the user of something
def inform_user(informationText):
    raw_input(informationText)


# Function for getting the correct image
def RequestConfirmedImage(RequestText, ConfirmationText1, ConfirmationText2):
    confirmation = False                                        # Initialise the confimation loop
    while not confirmation:                                     # Loop until confirmation = True
        request_of_confirmed_image()
        # raw_input(RequestText)                                  # Show the request to put camera nicely.
        img = GetImage()                                        # Get image from camera
        # print ConfirmationText1                                 # Ask to close the image and then answer
        # disp = Display()                                        # Create a display
        # while disp.isNotDone():                                 # Loop until display is not needed anymore
        #     if disp.mouseLeft:                                  # Check if left click was used on display
        #         disp.done = True                                # Turn off Display
        #     img.show()                                          # Show the image on Display
        # Display().quit()                                        # Exit the display so it does not go to "Not responding"
        # confirmation = GetConfirmation(ConfirmationText2)       # Ask whether LED was clearly visible and confirm.
        confirmation = object_clearly_seen(img)
    return img


# Function for getting objectCoords:
def getObjectCoords(img, RequestText):
    CROP_DIMENSIONS = 10
    print RequestText                                           # Ask user to click on display
    disp = Display(img.size())                                  # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = "X:" + str(mouse_coords[0]) + " Y:" + str(mouse_coords[1])
            img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]],
                                       color = Color.RED,
                                       dimensions = [CROP_DIMENSIONS,CROP_DIMENSIONS])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        img.save(disp)                                          # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]


# Function to ensure that correct blob was found
def correct_blob_confirmation(handle, img):
    TEXT_WHILE_IMAGE = "Look at the image and close it with mouse click or escape"
    QUESTION_TO_ASK = "Does the foreign object have red square around it in the picture? Y/N"
    test_img = img                                               # Show the image
    handle.drawMinRect(layer=test_img.dl(), color = Color.RED, width = 3)
                                                                 # Draw a rectangle around the found blob
    print TEXT_WHILE_IMAGE                                       # Print a message
    show_image_until_pressed(test_img)                           # Show image until pressed
    correct_blob = GetConfirmation(QUESTION_TO_ASK)              # Ask for confirmation
    return correct_blob


# Function to detect the foreign object for the first time:
def InitialObjectDetection(img, coords, data):
    #Std_constant = 5                                           # Describes how many std dev of value to include
    min_value = 30                                              # Minimal illumination threshold
                                                                # Derive minimum saturation. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    minsaturation = int(2*data["avg_sat"]/3) #(data["avg_sat"]- Std_constant * data["std_sat"])
    img = img.toHSV()                                           # Convert image to HSV colour space
    blobs_threshold = 230  #170 on laptop                       # Specify blobs colour distance threshold
    blobs_min_size =  10                                        # Specify minimum blobs size
                                                                # Apply filters to the image TODO: calibrate or change the filtering
    filtered = img.hueDistance(color = data["avg_hue"],
                               minsaturation = minsaturation,
                               minvalue = min_value)
    filtered = filtered.invert()                                # Invert black and white (to have object as white)
    filtered = filtered.morphClose()                            # Perform morphOps TODO: look for better options
    all_blobs = filtered.findBlobs(threshval = blobs_threshold, minsize=blobs_min_size)
    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs = all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
    elif all_blobs < 1:
        return "No blobs found"
    m_valve = all_blobs[0]                                     # m_valve is the closes blob to the click
    return m_valve


# Function to get the colour data of small area around certain point
def GetColourData(img, coords):
    CROP_SIZE = 10    #10 on laptop                             # Area around the point to be evaluated (square width)

    cropped = img.crop(coords[0],                               # Adjust cropping area (x,y,w,h)
                       coords[1], CROP_SIZE,
                       CROP_SIZE, centered= True)
    cropped_num = cropped.getNumpyCv2()                             # Convert image to numpy array compatible with openCV
    cropped_num = cv2.cvtColor(cropped_num, cv2.COLOR_BGR2HSV)          # Convert image to HSV colour scheme with openCV
    meanHue = np.mean(cropped_num[:,:,0])                           # Slice the NumPy array to get the mean Hue
    meanSat = np.mean(cropped_num[:,:,1])                           # Slice the NumPy array to get the mean Sat
    stdSat = np.std(cropped_num[:,:,1])                             # Slice the NumPy array to get the std Sat
    minSat = np.min(cropped_num[:,:,1])                             # Slice the NumPy array to get the min Sat
    meanValue = np.mean(cropped_num[:,:,2])                         # Slice the NumPy array to get the mean Brightness

    hue_hist = cropped.hueHistogram()                               # Check if histogram rolls over (object is red.)
    if (hue_hist[1] != 0) and (hue_hist[0] != 0) and (hue_hist[-1] != 0) and (hue_hist[-2] != 0):
        print hue_hist
        max_index = hue_hist.argmax()                               # If red, then get maximum hue histogram location
        print "Object is red, then average hue is: ", max_index     # Report issue
        meanHue = max_index


    hsv_data = {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    return hsv_data

# Function to name the object type
def object_type():
    QUESTION_TO_ASK ="Type in the name of the object type (no spaces):"
    CONFIRMATION_TEXT = "Object name is %s. And it is one word. Y/N?"
    SINGLE_WORD_WARNING = "Please, enter only single word (or use _ to seperate words)"
    correct_name = False                            # Initialise naming loop

    object_type_image()

    while not correct_name:                         # Start looping
        object_type_name = raw_input(QUESTION_TO_ASK + "\n>>>")
        if len(object_type_name.split()) > 1:
            print SINGLE_WORD_WARNING
            continue
        if GetConfirmation(CONFIRMATION_TEXT%object_type_name) == False:
            continue                                # If incorrect name, loop again
        correct_name = True                         # If correct name, return it
        return object_type_name


# Function to write calibration results to file
def store_results(object_coords_stored, object_name_stored, object_area_stored,
                  object_rect_distance_stored, object_aspect_ratio_stored,
                  object_average_hue, object_average_sat, object_std_sat):

    FILE_NAME = object_name_stored + ".txt"
    storage = open(FILE_NAME, "w")
    storage.write("""object_coord_x: %s
object_coord_y: %s
object_name_stored: %s
object_area_stored: %s
object_rect_distance_stored: %s
object_aspect_ratio_stored: %s
object_average_hue: %s
object_average_sat: %s
object_std_sat: %s""" %(object_coords_stored[0],object_coords_stored[1], object_name_stored, object_area_stored,
                  object_rect_distance_stored, object_aspect_ratio_stored,
                  object_average_hue, object_average_sat, object_std_sat))
    storage.close()
    print """object_coord_x: %s
object_coord_y: %s
object_name_stored: %s
object_area_stored: %s
object_rect_distance_stored: %s
object_aspect_ratio_stored: %s
object_average_hue: %s
object_average_sat: %s
object_std_sat: %s""" %(object_coords_stored[0],object_coords_stored[1], object_name_stored, object_area_stored,
                  object_rect_distance_stored, object_aspect_ratio_stored,
                  object_average_hue, object_average_sat, object_std_sat)
    return FILE_NAME

# Function to get the required foreign object data
def get_object_data():
    USER_REQUEST = "Please put the camera so that it could detect the example foreign object."
    REQUEST_WHILE_IMAGE_SHOWN = "This is the image taken. Close the image by right clicking on it or pressing escape"
    CONFIRMATION_QUESTION = "Was the foreign object example handle clearly seen in the image? Y/N"
    COORDINATES_REQUEST = "Pease right click on the foreign object example to calibrate its coordinates"

    calibration_data_not_acquired = True                             # Initialise object detection loop
    while calibration_data_not_acquired:                             # Start the loop
        # Get the example foreign object image
        img_object = RequestConfirmedImage(USER_REQUEST, REQUEST_WHILE_IMAGE_SHOWN,CONFIRMATION_QUESTION)

        # Get the coordinates of example object
        #object_coords = getObjectCoords(img_object,COORDINATES_REQUEST)
        object_coords = get_object_coords_image(img_object)
        # Get the average colour data around the selected part
        object_colour_data = GetColourData(img_object, object_coords)
        #In format of: hsv_data = {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}

        # Try to detect the object
        object_found = InitialObjectDetection(img_object, object_coords, object_colour_data)
        # If no objects were found: Start again TODO: ADD aditonal user calibration?
        if object_found == "No blobs found":
            object_not_found_image(img_object)
            print "No objects were found, please continue the calibration again"
            continue

        # Check if foreign object was correctly found:
        if correct_object_confirmation_image(object_found, img_object) == False:
        #if correct_blob_confirmation(object_found, img_object) == False:
            continue

        # Ask for the type of foreign object:
        object_type_name = object_type()

        # Record foreign object data TODO: Possible additional data to record
        object_area = object_found.area()
        object_rect_distance = object_found.rectangleDistance()
        object_aspect_ratio = object_found.aspectRatio()

        # Return foreign object calibration data
        total_object_data = {"colour_data": object_colour_data,
                             "object_coords": object_coords,
                             "object_type_name": object_type_name,
                             "object_area": object_area,
                             "object_rect_distance": object_rect_distance,
                             "object_aspect_ratio": object_aspect_ratio,
                             }
        return total_object_data



# Function to perform calibration
def perform_calibration():

    calibration_start_image()
    # Function to get the foreign object data (avg hue, avg sat, std sat,
    # click coords, object_type_name, object_area, object_rect_distance, object_aspect_ratio)
    object_data = get_object_data()

    #Results to store
    object_coords_stored = object_data["object_coords"]
    object_name_stored = object_data["object_type_name"]
    object_area_stored = object_data["object_area"]
    object_rect_distance_stored = object_data["object_rect_distance"]
    object_aspect_ratio_stored = object_data["object_aspect_ratio"]
    object_average_hue = object_data["colour_data"]["avg_hue"]
    object_average_sat = object_data["colour_data"]["avg_sat"]
    object_std_sat = object_data["colour_data"]["std_sat"]

    FILE_NAME = store_results(object_coords_stored, object_name_stored, object_area_stored,
                  object_rect_distance_stored, object_aspect_ratio_stored,
                  object_average_hue, object_average_sat, object_std_sat)
    store_calibration_data_image(object_coords_stored, object_name_stored, object_area_stored,
                  object_rect_distance_stored, object_aspect_ratio_stored,
                  object_average_hue, object_average_sat, object_std_sat)

    return object_name_stored



# MAIN SOFTWARE:
def do_calibration_procedure(cam_received):
    setup(cam_received)                                             # Perform camera setup

    object_name_stored = perform_calibration()
    return object_name_stored
    # raw_input("Calibration Done. Saved as " + FILE_NAME)


# If called by itself, perform calibration
if __name__ == '__main__':
    cam = Camera(0, {"width": 1024, "height": 768})        # Only for RPI 2592x1944. For calibration - 1024x768
    file_name = do_calibration_procedure(cam)


