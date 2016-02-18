from SimpleCV import *
import cv2
import colorsys

# for image acquisition from camera (and flipping)
def GetImage():
    img = cam.getImage()
    flipped = img.flipHorizontal()
    return flipped



"""
b = np.arange((4*4*3))
b = b.reshape(4,4,3)
print b

avg = np.mean(b[:,:,0])
print avg, "AVG"
d = np.std(b[:,:,0])
print d, "STD"
"""

"""
img = Image("Cropped.jpg")
#hsv = img.toHSV()

hsv = img.getNumpyCv2()
hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)

hsvmean = np.mean(hsv, axis = 0)

print hsv.shape


hsvStd = np.std(hsvmean, axis = 0)
hsvmean = np.mean(hsvmean, axis = 0)
print hsvStd, "STD"
print hsvmean, "mean" #correct

meanHue = hsvmean[0]
meanSat = hsvmean[1]
stdSat = hsvStd[1]

print meanHue
print meanSat
print stdSat

"""

#CORRECT AND LOOKS AWESOME :D

cam = Camera()
crop_size = 30                                              # Area around the point to be evaluated (square width)

while True:
    img = GetImage()
    disp = Display()                                            # Create a display
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
    Display().quit()

while True:
    None



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