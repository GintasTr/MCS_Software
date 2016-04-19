from SimpleCV import *
import numpy as np
import cv2
from pylepton import Lepton


# Function to get raw values from thermal camera
def get_raw_values():
    with Lepton() as l:
        a,_ = l.capture()
    return a


# Function to get the image from the thermal camera
def GetImage(raw_values):
    STORED_IMAGE_NAME = "CalibrationImage.jpg"
    #img = get_raw_values()                                  # Get raw image values
    cv2.normalize(raw_values, raw_values, 0, 65535, cv2.NORM_MINMAX)      # Normalize image
    np.right_shift(raw_values,8,raw_values)                               # Shift to 8 bit array
    cv2.imwrite(STORED_IMAGE_NAME, np.uint8(raw_values))           # Write the image to file
    simplecv_img = Image(STORED_IMAGE_NAME)                 # Take the image from file as SIMPLECV image
    return simplecv_img





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


# Function for getting the correct image
def RequestConfirmedImage(RequestText, ConfirmationText1, ConfirmationText2):
    confirmation = False                                        # Initialise the confimation loop
    while not confirmation:                                     # Loop until confirmation = True
        raw_input(RequestText)                                  # Show the request to put camera nicely.
        raw_values_new = get_raw_values()
        img = GetImage(raw_values_new)                                        # Get image from camera
        print ConfirmationText1                                 # Ask to close the image and then answer
        img_scaled = img.scale(5)
        show_image_until_pressed(img_scaled)                    # Show the image
        confirmation = GetConfirmation(ConfirmationText2)       # Ask whether object was clearly visible and confirm.
    return img


# Function for getting object coordinates:
def GetCoords(img, RequestText, CROP_SIZE):
    CROP_SIZE = CROP_SIZE * 2
    print RequestText                                           # Ask user to click on display
    disp = Display()                                            # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = "X:" + str(mouse_coords[0]) + " Y:" + str(mouse_coords[1])
            img.dl().setFontSize(14)                            # Set small font size for text on small image
            img.dl().text(text, (mouse_coords[0] + 1, mouse_coords[1] + 1), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]],
                                       color = Color.RED, dimensions = [CROP_SIZE,CROP_SIZE])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        img.save(disp)                                          # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]



# Function to get the raw value average of small area around specified coordinates
def get_average_cropped(coords, raw_values, CROP_SIZE):
    np.set_printoptions(threshold=np.nan)                       # Configuration so that full aray is stored in text file
    CROP_SIZE = CROP_SIZE                                       # Area around the point to be evaluated (square width)
    #STORED_VALUES_NAME = "CalibrationValues.txt"
    #with open(STORED_VALUES_NAME, "w") as f:                    # Store raw data to file for debugging
    #    f.write(str(raw_values))

    coord_x = coords[0]                                         # Define X coordinates
    coord_y = coords[1]                                         # Define Y coordinates
    cropped = raw_values[(coord_y - CROP_SIZE) : (coord_y + CROP_SIZE), (coord_x - CROP_SIZE) : (coord_x + CROP_SIZE)]
                                                                # Get the cropped array
    average_value = np.mean(cropped)                                  # Get the mean value of the cropped array

    return average_value

# Function to write calibration results to file
def store_results(calibration_results, ambient_temperature):
    INFORMATION_STORED = "Calibration is done, values are stored in Ambient_%s.txt, values recorded:\n"
    with open("Ambient_%s.txt" % ambient_temperature, "w") as storage:
        for i in range(0, len(calibration_results)):
            storage.write(str(calibration_results[i])+"\n")
    print INFORMATION_STORED % ambient_temperature
    for i in range(0, len(calibration_results)):
        print str(calibration_results[i])


# Function to get the position of calibration object in the image
def getObjectPosition(CROP_SIZE):
    CROP_SIZE = CROP_SIZE
    FIRST_REQUEST_TEXT = "Please put the camera so that the calibration object is clearly visible in the image"
    TEXT_WHILE_IMAGE_SHOWN = "Check the image whether calibration object is clearly visible and close it with esc " \
                             "or left click"
    CONFIRMATION_QUESTION = "Is the calibration object clearly visible in the image? Y/N"
    COORDINATES_REQUEST = "Please left click on the calibration object, so that the whole red square is within " \
                          "object limits. Then close the image with esc or right mouse click."

    # Get the image confirmed by user
    image = RequestConfirmedImage(FIRST_REQUEST_TEXT, TEXT_WHILE_IMAGE_SHOWN, CONFIRMATION_QUESTION)

    # Get the coordinates of the object
    coords = GetCoords(image, COORDINATES_REQUEST, CROP_SIZE)

    return coords

# Function to request user of ambient temperature. Can be changed to ambient temperature sensor if needed
def getAmbientTemperature():
    REQUEST_TEXT = "Please enter the measured ambient temperature in degrees celsius (from 0 to 80):\n>>>"
    VALUE_ERROR_TEXT = "Please enter a number (for float numbers use .)"
    CONFIRMATION_QUESTION = "The ambient temperature is %s degrees celsius, is that correct? Y/N\n>>>"
    INCORRECT_VALUE_ENTERED = "Incorrect value entered (please enter value between 0 to 80 degrees celsius)"

    while True:
        usr_input = raw_input(REQUEST_TEXT)                         # Get the user input
        try:                                                        # Check if it is possible to convert it to float
            usr_input = float(usr_input)                            # Try to convrt it to float
        except(ValueError):                                         # Catch it error is shown
            print VALUE_ERROR_TEXT                                  # Print the error text
            continue                                                # Loop again

        if ((type(usr_input) == float) and (usr_input > 0) and (usr_input < 80)):
                                                                    # Check whether value is valid (float and >0, <80)
            print CONFIRMATION_QUESTION % usr_input,
            try:                                                    # Catch Index error in case of too fast response
                userInput = raw_input()                             # Check user input
                userInput = userInput.lower()                       # Make it lower case
                if userInput[0] == "y":                             # Check if it is y, n, or something else
                    return usr_input                                # Return time stated
                elif userInput[0] == "n":
                    continue
            except(IndexError):                                     # In case of Index error (too fast response)
                    print "Something is wrong, try again."
        else:
            print INCORRECT_VALUE_ENTERED


# Function to check if variable can be converted to float or not
def check_if_input_float(usr_input):
    try:                                                        # Check if it is possible to convert it to float
        usr_input = float(usr_input)                            # Try to convert it to float
        usr_input_float = True                                  # If successful - mark it as float
    except(ValueError):                                         # Catch if error is shown
        usr_input_float = False                                 # Mark input as letter
    return usr_input_float


# Function to show calibration image to ensure calibration item is within cropping limits
def show_image_to_check(raw_values, coords, CROP_SIZE):
    INFORMATION_TEXT = "Check whether red rectangle is fully within calibration object. " \
                       "Right click or esc to turn image off"
    image = GetImage(raw_values)
    CROP_SIZE = CROP_SIZE * 2
    print INFORMATION_TEXT                                      # Ask user to click on display
    disp = Display()                                            # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        image.dl().centeredRectangle(center = [coords[0], coords[1]],
                                color = Color.RED, dimensions = [CROP_SIZE,CROP_SIZE])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        image.save(disp)                                         # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"


# Function to perform calibration procedure
def calibration_procedure(coords, CROP_SIZE):
    INITIAL_INFORMATION = "Calibration procedure is starting. Please do not move camera or object."
    TEMPERATURE_REQUEST = "Please input the measured object temperature in degrees Celsius to record a raw value. " \
                          "To stop calibration input: S. To re-calibrate last measurement input: R\n>>>"
    LETTER_RECEIVED = "Input was not a number."
    SINGLE_RESULT = "Temperature of %.1f is equal to raw value of: %i"
    TERMINATION_INFORMTION = "Calibration end was requested"
    LAST_ENTRY_REMOVED = "Last entry of temperature calibration was deleted"
    UNKNOWN_LETTER_ENTERED = "Wrong letter entered, please enter temperature, S to stop or R to remove last entry"
    CALIBRAION_DONE = "Calibration values were obtained"

    raw_input(INITIAL_INFORMATION)                                 # Notify the user that calibration is starting
    calibration_done = False
    results = ["Temperature(C) Raw_value"]
    while (not calibration_done):
        usr_input = raw_input(TEMPERATURE_REQUEST)                  # Get the user input
        usr_input_float = check_if_input_float(usr_input)           # Check if input can be converted to float
        if usr_input_float == True:                                 # If temperature was entered
            usr_input = float(usr_input)
            raw_values = get_raw_values()                           # Get raw thermal imager output
            cropped_average = get_average_cropped(coords, raw_values, CROP_SIZE)
                                                                    # Get the average value in cropped region
            show_image_to_check(raw_values, coords, CROP_SIZE)
            print SINGLE_RESULT % (usr_input, cropped_average)      # Print single result
            results.append(("%.1f %i") % (usr_input, cropped_average))
                                                                    # Add the result to results array
            continue                                                # Loop again
        else:                                                       # If number is not float
            print LETTER_RECEIVED                                   # Notify user
            if usr_input == ("s" or "S"):                           # Check which letter
                calibration_done = True                             # Stop the loop
                print TERMINATION_INFORMTION                        # Warn the user about finish
                continue                                            # Loop again
            elif usr_input == ("r" or "R"):                         # If letter R is first
                del results[-1]                                     # Delete last entry from results
                print LAST_ENTRY_REMOVED                            # Warn user about deletion
                continue                                            # Loop again
            else:                                                   # If some other letter is pressed
                print UNKNOWN_LETTER_ENTERED                        # Show the error
                continue                                            # Loop again
    print CALIBRAION_DONE                                           # Warn user about finish
    return results                                                  # Return calibration results


# Function to perform calibration
def perform_calibration():
    CROP_SIZE = 2
    FINISHED_PROMPT = "Procedure is done, end of calibration"

    # Get the coordinates of the Object to be calibrated to
    coords = getObjectPosition(CROP_SIZE)

    # Get the ambient temperature
    ambient_temperature = getAmbientTemperature()

    # Perform the calibration procedure
    calibration_results = calibration_procedure(coords, CROP_SIZE)

    store_results(calibration_results, ambient_temperature)
    raw_input(FINISHED_PROMPT)

# MAIN SOFTWARE:
# Initialisation:
# Nothing to initialise.

### CALIBRATION PART
perform_calibration()

