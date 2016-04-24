from SimpleCV import *
import cv2
from Controller import LED_Sequence_Controlled_V5


# prepares, selects the camera
def setup():
    global cam
    cam = Camera()
    time.sleep(0.2)


# Function to get the image from camera
def GetImage():
    img = cam.getImage()                                            # Get image from camera
    img = cam.getImage()                                            # ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipHorizontal()                                      # Flip image (has to be tested on PI)
    return img


# Briefly flashes the image
def show_image_briefly(img):
    img.show()                                              # Show the image on Display


# Shows the image until the button is pressed
def show_image_until_pressed(img):
    disp = Display()                                        # Create a display
    while disp.isNotDone():                                 # Loop until display is not needed anymore
        if disp.mouseLeft:                                  # Check if left click was used on display
            disp.done = True                                # Turn off Display
        img.show()                                          # Show the image on Display
    Display().quit()                                        # Exit the display so it does not go to "Not responding"


# Debugging function: Shows the pixel value when clicked on the screen:
def debug_pixel_value(img):
    disp = Display()                                            # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = str(img.getGrayPixel(mouse_coords[0],mouse_coords[1]))
            img.dl().text(text, (mouse_coords[0], mouse_coords[1]), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED, dimensions = [2,2])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        img.save(disp)                                          # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]



setup()
while True:
    img = Image("CROPPED1.jpg")
    show_image_until_pressed(img)

    img_num = img.getNumpyCv2()                             # Convert image to numpy array compatible with openCV
    img_num = cv2.cvtColor(img_num, cv2.COLOR_BGR2HSV)          # Convert image to HSV colour scheme with openCV
    meanHue = np.mean(img_num[:,:,0])                           # Slice the NumPy array to get the mean Hue
    meanSat = np.mean(img_num[:,:,1])                           # Slice the NumPy array to get the mean Sat
    stdSat = np.std(img_num[:,:,1])                             # Slice the NumPy array to get the std Sat
    minSat = np.min(img_num[:,:,1])                             # Slice the NumPy array to get the min Sat
    meanValue = np.mean(img_num[:,:,2])                         # Slice the NumPy array to get the mean Brightness

    print meanHue, "- mean Hue"                             # Print the obtained values for debugging
    print meanSat, "- mean Sat"
    print meanValue, " - min Val"

    hue_hist = img.hueHistogram()
    print hue_hist, "one", hue_hist[0], "two", hue_hist[1],"last", hue_hist[-1],"before last", hue_hist[-2]

    if hue_hist[0] and hue_hist[1] and hue_hist[2] and hue_hist[-1] and hue_hist[-2] and hue_hist[-3] != 0:
        max_index = hue_hist.argmax()
        print "AvgHue is then: ", max_index
        meanHue = max_index

    img2 = img.hueDistance(color = meanHue, minsaturation = 2, minvalue = 20)
    img2 = img2.invert()
    debug_pixel_value(img2)