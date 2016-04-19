from SimpleCV import *
import numpy as np
import cv2


# prepares, selects the camera
def setup():
    global cam
    cam = Camera()
    time.sleep(1)


# Function to get the image from the camera
def GetImage():
    img = cam.getImage()                                    # Get image from camera
    img = cam.getImage()                                    # ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipHorizontal()                              # Flip image (has to be tested on PI)
    img = img.getNumpyCv2()                                 # Convert image to numpy array compatible with openCV
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)             # THAT IS THE THING THERMAL CAMERA RETURNS

    #cv2.imshow("Image", img)
    #cv2.waitKey(10000)

    img_SimpleCV = Image(img)
    img_SimpleCV.show()


    return img

# Shows the image until the button is pressed
def show_image_until_pressed(img):
    disp = Display()                                        # Create a display
    while disp.isNotDone():                                 # Loop until display is not needed anymore
        if disp.mouseLeft:                                  # Check if left click was used on display
            disp.done = True                                # Turn off Display
        img.show()                                          # Show the image on Display
    Display().quit()                                        # Exit the display so it does not go to "Not responding"


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


def RequestConfirmedImage(RequestText, ConfirmationText1, ConfirmationText2):
    confirmation = False                                        # Initialise the confimation loop
    while not confirmation:                                     # Loop until confirmation = True
        raw_input(RequestText)                                  # Show the request to put camera nicely.
        img = GetImage()                                        # Get image from camera
        print ConfirmationText1                                 # Ask to close the image and then answer
        show_image_until_pressed(img)                           # Show the image
        confirmation = GetConfirmation(ConfirmationText2)       # Ask whether object was clearly visible and confirm.
    return img


# Function for getting object coordinates:
def GetCoords(img, RequestText, CROP_SIZE):
    CROP_SIZE = CROP_SIZE
    print RequestText                                           # Ask user to click on display
    disp = Display()                                            # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = "X:" + str(mouse_coords[0]) + " Y:" + str(mouse_coords[1])
            img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]],
                                       color = Color.RED, dimensions = [CROP_SIZE,CROP_SIZE])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        img.save(disp)                                          # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]




setup()



CROP_SIZE = 5
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