from SimpleCV import *
import cv2
import time
import colorsys

# for image acquisition from camera (and flipping)
def GetImage():
    img = cam.getImage()
    img = cam.getImage()
    flipped = img.flipHorizontal()
    return flipped

# prepares, selects the camera
def setup():
    global cam
    cam = Camera()
    time.sleep(1)


def GetClickCoords(img, RequestText):
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
    return mouse_coords


def GetCalibrationData(img, coords):
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
    return hsv_data



def MainLedDetection(img, coords, data):
    Std_constant = 3                                            # Describes how many std dev of value to include
    min_value = 30                                              # Minimal illumination threshold
                                                                # Derive minimum saturation. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    minsaturation = (data["avg_sat"]- Std_constant * data["std_sat"])
    img = img.toHSV()                                           # Convert image to HSV colour space
    blobs_threshold = 220                                       # Specify blobs colour distance threshold
    blobs_min_size =  200                                       # Specify minimum blobs size
                                                                # Apply filters to the image TODO: calibrate or change the filtering
    filtered = img.hueDistance(color = data["avg_hue"],
                               minsaturation = minsaturation,
                               minvalue = min_value)
    filtered = filtered.invert()                                # Invert black and white (to have LED as white)
    filtered = filtered.morphClose()                            # Perform morphOps TODO: look for better options
    # filtered = filtered.dilate(1) #TO BE TESTED               # Possible morphOps options
    # Filtered = filtered.erode(1)
                                                                # Look for blobs
    all_blobs = filtered.findBlobs(threshval = blobs_threshold, minsize=blobs_min_size)
    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
        for i in range(0, len(all_blobs)):                      # For every found blob draw a rect on filtered image
                                                                # Only for debugging.
            filtered.dl().rectangle2pts(all_blobs[i].topLeftCorner(),
                                        all_blobs[i].bottomRightCorner(),Color.GREEN, width = 5)
            filtered.dl().text("%s" %i, (all_blobs[i].bottomRightCorner()), color=Color.RED)
    elif all_blobs < 1:                                         # If none blobs found
        print "No blobs found"                                  # Print and return that no blobs were found
        return "No blobs found"
    m_led = all_blobs[-1]                                       # m_led is the closes blob to the click
    return m_led



def GetLight(img, coords, hsv_data, dist):
    dist_scalar = 1.2                                           # Margin of distance to include both LEDs
    crop_length = int(round(dist_scalar*dist))
    main_blob = MainLedDetection(img,coords,hsv_data)           # Get main led blob. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    if main_blob == "No blobs found":
        return "No blobs found"
    blob_coordinates = main_blob.coordinates()
    cropped = img.crop(blob_coordinates[0],
                        blob_coordinates[1], crop_length,
                        crop_length, centered=True)
    cropped = cropped.toGray()
    light_value = cropped.meanColor()
    print light_value                                           # For debugging
    return light_value


#MAIN

setup()
raw_input("take image")
img = GetImage()
coords = GetClickCoords(img, "Please select main LED")
cal_data = GetCalibrationData(img, coords)
main_blob = MainLedDetection(img, coords, cal_data)
if main_blob == "No blobs found":
    print "No blobs found"

raw_input("done")

disp = Display()
while disp.isNotDone():                                     # Loop until display is not needed anymore
    img = GetImage()
    main_blob = MainLedDetection(img, coords, cal_data)
    if main_blob == "No blobs found":
        img.save(disp)
        print "No blobs found"
        continue
    img.dl().rectangle2pts(main_blob.topLeftCorner(),
                    main_blob.bottomRightCorner(),Color.GREEN, width = 5)
    if disp.mouseRight:                                     # If right clicked
        disp.done = True                                    # Turn off Display



    blob_coordinates = main_blob.coordinates()
    cropped = img.crop(blob_coordinates[0],
                        blob_coordinates[1], 200,
                        200, centered=True)
    cropped = cropped.toGray()
    img.dl().sprite(cropped, scale = 1.0)
    cropped = cropped.getGrayNumpy()
    light_value = np.mean(cropped)
    print light_value                                           # For debugging


    img.save(disp)







"""
#CORRECT AND LOOKS AWESOME :D

cam = Camera()
crop_size = 30                                              # Area around the point to be evaluated (square width)

while True:
    img = GetImage()
    disp = Display()                                            # Create a display
    start = time.clock()
    elapsed_old = 0
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img = GetImage()
        filtered = img
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            cropped1 = img.crop(mouse_coords[0],                               # Adjust cropping area (x,y,w,h)
                       mouse_coords[1], crop_size,
                       crop_size, centered= True)
            cropped = cropped1.getNumpyCv2()                             # Convert image to numpy array compatible with openCV
            cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)          # Convert image to HSV colour scheme with openCV
            meanHue = int(np.mean(cropped[:,:,0]))                           # Slice the NumPy array to get the mean Hue
            meanSat = int(np.mean(cropped[:,:,1]))                           # Slice the NumPy array to get the mean Sat
            meanValue = int(np.mean(cropped[:,:,2]))                         # Slice the NumPy array to get the mean Brightness
            hsvNumpy = np.uint8([[[meanHue,meanSat,meanValue]]])
            rgbColor = cv2.cvtColor(hsvNumpy, cv2.COLOR_HSV2RGB)
            rgbColor2 = (rgbColor[0,0,0],rgbColor[0,0,1],rgbColor[0,0,2])
            red = int(rgbColor2[0])
            green = int(rgbColor2[1])
            blue = int(rgbColor2[2])
            filtered = img.hueDistance(color = meanHue, minsaturation = (meanSat - meanSat/2), minvalue= (meanValue - meanValue/2))
            filtered.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED, dimensions = [30,30])
            filtered.dl().sprite(cropped1, scale = 5.0)
            filtered.dl().rectangle(topLeft = (150,0),dimensions = (50,150),
                               color = (red, green, blue), filled = True, alpha = -1)


        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        filtered.save(disp)                                          # Show the image on Display
        elapsed = (time.clock() - start)
        delta_t = elapsed - elapsed_old
        elapsed_old = elapsed
        print elapsed, "Total time"
        print delta_t, "Delta T"
    Display().quit()

while True:
    None

"""

"""
# img = Image("Cropped.jpg")
# hsv = img.toHSV()

    hsv = img.getNumpyCv2()
    hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)

    print hsv.shape
    print hsv

    # print hsv[:,:,0], "HUE"
    # print hsv[:,:,1], "SAT"
    # print hsv[:,:,2], "VAL"

    avgHue = np.mean(hsv[:,:,0])
    print avgHue, "AVG Hue"

    avgSat = np.mean(hsv[:,:,1])
    stdSat = np.std(hsv[:,:,1])
    minSat = np.min(hsv[:,:,1])
    avgVal = np.mean(hsv[:,:,2])
    print avgSat, "avgSat"
    # print stdSat, "stdSat"
    # print minSat, "minSat"
    print avgVal, "avgVal"

    """