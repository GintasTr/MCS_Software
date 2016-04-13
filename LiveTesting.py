from SimpleCV import *
import cv2


# prepares, selects the camera
def setup():
    global cam
    cam = Camera()
    time.sleep(1)


# Function to get the image from camera
def GetImage():
    img = cam.getImage()                                            # Get image from camera
    img = cam.getImage()                                            # ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    img = img.flipHorizontal()                                      # Flip image (has to be tested on PI)
    return img



# Function for getting ValveCoords:
def GetValveCoords(img, RequestText):
    print RequestText                                           # Ask user to click on display
    disp = Display()                                            # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = "X:" + str(mouse_coords[0]) + " Y:" + str(mouse_coords[1])
            img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED, dimensions = [20,20])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        img.save(disp)                                          # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]


# Function to detect the main LED:
def ValveDetection(img, coords, data):
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
    # filtered = filtered.dilate(1) #TO BE TESTED               # Possible morphOps OPEN??
    # Filtered = filtered.erode(1)
    global debugging
    all_blobs = filtered.findBlobs(threshval = blobs_threshold, minsize=blobs_min_size)
    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
    elif all_blobs < 1:                                         # If none blobs found
        # print "No blobs found"                                  # Print and return that no blobs were found. Not needed
        return "No blobs found"
    debugging = filtered
    m_led = all_blobs[-1]                                       # m_led is the closes blob to the click
    return m_led


# Function to get the colour data of small area around certain point
def GetColourData(img, coords):
    crop_size = 10                                              # Area around the point to be evaluated (square width)
    cropped = img.crop(coords[0],                               # Adjust cropping area (x,y,w,h)
                       coords[1], crop_size,
                       crop_size, centered= True)
    cropped.save("cropped.jpg")
    cropped = cropped.getNumpyCv2()                             # Convert image to numpy array compatible with openCV
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)          # Convert image to HSV colour scheme with openCV
    meanHue = np.mean(cropped[:,:,0])                           # Slice the NumPy array to get the mean Hue
    meanSat = np.mean(cropped[:,:,1])                           # Slice the NumPy array to get the mean Sat
    stdSat = np.std(cropped[:,:,1])                             # Slice the NumPy array to get the std Sat
    minSat = np.min(cropped[:,:,1])                             # Slice the NumPy array to get the min Sat
    meanValue = np.mean(cropped[:,:,2])                         # Slice the NumPy array to get the mean Brightness
    # print meanHue, "- mean Hue"                                 # Print the obtained values for debugging
    # print meanSat, "- mean Sat"
    # print stdSat, "- std Sat"
    # print minSat, "- min Sat"
    # print meanValue, " - min Val"
    # raw_input("check results")                                  # FOR DEBUGGING

    hsv_data = {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    return hsv_data                                             # Return the obtained values


# Main software:
# Initialisation:

setup()                                                         # Perform camera setup
# TODO: Check for calibration data. If found, ask whether do calibration again. If not, go to calibration.

img = GetImage()
coords = GetValveCoords(img, "Click on the Handle")
colour_data = GetColourData(img, coords)
disp = Display()
while disp.isNotDone():
    img = GetImage()
    handle = ValveDetection(img, coords, colour_data)
    if handle == "No blobs found":
        img.dl().text(handle, (10, 10), color=Color.RED)
        img.show()
        continue
    handle.drawMinRect(layer=img.dl(), color = Color.RED, width = 3)
    Width_by_Height = str(handle.minRectWidth()/handle.minRectHeight())
    Minimum_Width = str(handle.minRectWidth())
    Minimum_Height = str(handle.minRectHeight())
    Aspect_ratio = str(handle.aspectRatio())

    img.dl().text(("Width_by_Height" + Width_by_Height), [10,10], color=Color.RED)
    img.dl().text(("Minimum_Width" + Minimum_Width), [10,30], color=Color.RED)
    img.dl().text(("Minimum_Height" + Minimum_Height), [10,60], color=Color.RED)
    img.dl().text(("Aspect_ratio" + Aspect_ratio), [10,80], color=Color.RED)

    img.show()                                          # Show the image on Display
disp.quit()
