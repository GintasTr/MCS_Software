# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
import cv2
import Orange_Flap_V5_Demo
from Orange_flap_calibration_images import orange_calibration_images
demo_images = orange_calibration_images()

# prepares, selects the camera
def setup(cam_received):
    global cam
    cam = cam_received
    # cam = Camera(0, {"width": 1024, "height": 768})        # Only for RPI 2592x1944. For calibration - 1024x768
    # #cam = Camera()
    # time.sleep(1)


# for image acquisition from camera (and flipping)
def GetImage():
    img = cam.getImage()
    img = cam.getImage()                                    ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    #img = img.flipVertical()
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


# Function only for DEMO - to combine some redundant functions
def get_image_and_coords(CROP_LENGTH):
    flat_image_done = False
    while (not flat_image_done):  # Repeat until flat flap image is acquired correctly
        demo_images.ask_for_flat_position()
        flat_image = GetImage()  # Get image of the flat flap

        result = demo_images.ask_for_mouse_coords(flat_image,CROP_LENGTH)
        if result == False:
            continue
        else:
            coords = result
            flat_image_done = True

    return {"coords": coords, "image": flat_image}


# Function to find average values of colour (hue, sat, val)
def ColorAveraging(flat_image, Calibration_coords, CROP_LENGTH):
    cropped = flat_image.crop(Calibration_coords[0],
                              Calibration_coords[1], CROP_LENGTH,
                              CROP_LENGTH, centered= True)
    cropped_num = cropped.getNumpyCv2()
    cropped_num = cv2.cvtColor(cropped_num, cv2.COLOR_BGR2HSV)
    meanHue = np.mean(cropped_num[:,:,0])
    meanSat = np.mean(cropped_num[:,:,1])
    stdSat = np.std(cropped_num[:,:,1])
    minSat = np.min(cropped_num[:,:,1])
    meanValue = np.mean(cropped_num[:,:,2])
    print meanHue, "- mean Hue"
    print meanSat, "- mean Sat"
    print stdSat, "- std Sat"
    print minSat, "- min Sat"
    #raw_input("check results")   --FOR DEBUGGING

    hue_hist = np.histogram(cropped.toHSV().getNumpy()[:,:,2], range = (0.0, 255.0), bins = 255)[0]  # Check if histogram rolls over (object is red.)

    if ((hue_hist[0] != 0) and (hue_hist[1] != 0) and (hue_hist[-1] != 0) and (hue_hist[-2] != 0)):
        max_index = hue_hist.argmax()                               # If red, then get maximum hue histogram location
        print "Object is red, then average hue is: ", max_index     # Report issue
        meanHue = max_index                                         # Re-write Hue value

    values = {"AvHue": meanHue, "AvSat": meanSat, "StdSat": stdSat}
    return values


# Calibration procedure
def Flat_Calibration():
    blobs_threshold_flat = 240 #170 on laptop
    blobs_min_size_flat = 1000
    CROP_LENGTH = 20
    flat_calibration_done = False
    while (not flat_calibration_done):  # Repeat until flat flap calibration is performed correctly

        image_and_coords = get_image_and_coords(CROP_LENGTH)

        flat_image = image_and_coords["image"]
        Calibration_coords = image_and_coords["coords"]
        # flat_image = AcquireFlatImage()
        # Calibration_coords = get_calibration_coordinates(flat_image)

        print "Approximate coordinates of flap: ", Calibration_coords
        Calibration_values = ColorAveraging(flat_image, Calibration_coords, CROP_LENGTH)

        filteredImage = Orange_Flap_V5_Demo.apply_filter(Calibration_values, flat_image)
        possible_flaps = filteredImage.findBlobs(threshval = blobs_threshold_flat, minsize=blobs_min_size_flat)
        if possible_flaps > 1:
            possible_flaps = possible_flaps.sortDistance(point =(Calibration_coords[0], Calibration_coords[1]))
            # for i in range(0, len(possible_flaps)):
            #     filteredImage.dl().rectangle2pts(possible_flaps[i].topLeftCorner(),
            #                                      possible_flaps[i].bottomRightCorner(),Color.GREEN, width = 5)
            #     filteredImage.dl().text("%s" %i, (possible_flaps[i].topLeftCorner()), color=Color.RED)
        elif possible_flaps < 1:
            print "No possible flaps were found, starting calibration again"
            demo_images.no_flaps_found(flat_image)
            continue
        flap = possible_flaps[0]

        FlapWHRatio = round(float(flap.width()) / float(flap.height()), 4)
        result = demo_images.show_detected_orange_flap(flat_image,flap,FlapWHRatio, "Flat")
        if result == True:
            flat_calibration_done = True
            continue
        else:
            continue

    FlapWHRatio = round(float(flap.width()) / float(flap.height()), 4)
    values = {"AvHue": Calibration_values["AvHue"], "AvSat": Calibration_values["AvSat"],
              "StdSat": Calibration_values["StdSat"], "FlatWHRatio": FlapWHRatio,
              "mouseX": Calibration_coords[0], "mouseY": Calibration_coords[1]}
    return values

def Slope_Calibration(AvHue,AvSat,StdSat,mouseX,mouseY):
    blobs_threshold_slope = 240 #170 on laptop
    blobs_min_size_slope = 1000
    slope_calibration_done = False
    while (not slope_calibration_done):

        demo_images.ask_for_slope_position()

        slope_image = GetImage()

        # slope_image = AcquireSlopeImage()

        filtered_image = Orange_Flap_V5_Demo.apply_filter({"AvHue": AvHue, "AvSat": AvSat, "StdSat": StdSat}, slope_image)
        possible_flaps = filtered_image.findBlobs(threshval = blobs_threshold_slope, minsize=blobs_min_size_slope)   #CAN ADD SIZES AND STUFF

        if possible_flaps > 1:
            possible_flaps = possible_flaps.sortDistance(point =(mouseX, mouseY))
            # for i in range(0, len(possible_flaps)):
            #     filtered_image.dl().rectangle2pts(possible_flaps[i].topLeftCorner(),
            #                                      possible_flaps[i].bottomRightCorner(),Color.GREEN, width = 5)
            #     filtered_image.dl().text("%s" %i, (possible_flaps[i].bottomRightCorner()), color=Color.RED)
        elif possible_flaps < 1:
            print "No flap was found, please take another picture"
            demo_images.no_flaps_found(slope_image)
            continue
        flap = possible_flaps[0]

        SlopeWHRatio = round(float(flap.width()) / float(flap.height()), 4)
        result = demo_images.show_detected_orange_flap(slope_image,flap,SlopeWHRatio, "Slope")
        if result == True:
            slope_calibration_done = True
            continue
        else:
            continue

    SlopeWHRatio = round(float(flap.width()) / float(flap.height()), 4)
    return SlopeWHRatio

# Function to write calibration results to file
def store_results(flat_data, slope_data):
    FILE_NAME = "Orange_flap_calibration_data.txt"
    with open(FILE_NAME, "w") as storage:
        storage.write(
"""mouseX: %s
mouseY: %s
AvHue: %s
AvSat: %s
FlatWHRatio: %s
SlopeWHRatio: %s"""
                  % (flat_data["mouseX"],
                    flat_data["mouseY"],
                    flat_data["AvHue"],
                    flat_data["AvSat"],
                    flat_data["FlatWHRatio"],
                    slope_data))
    print (
"""coord_x: %s
coord_y: %s
avg_hue: %s
avg_sat: %s
FlatWHRatio: %s
SlopeWHRatio: %s"""
                  % (flat_data["mouseX"],
                    flat_data["mouseY"],
                    flat_data["AvHue"],
                    flat_data["AvSat"],
                    flat_data["FlatWHRatio"],
                    slope_data))
    demo_images.data_stored_image(flat_data["mouseX"],flat_data["mouseY"],
                                  flat_data["FlatWHRatio"], slope_data,
                                  flat_data["AvHue"], flat_data["AvSat"])

#MAIN SOFTWARE FUNCTION
def perform_calibration_procedure(cam_received):
    setup(cam_received)
    demo_images.calibration_start()

    # To get the location and size of QR code
    # qr_data = qr_code_calibration()

    flat_data = Flat_Calibration()

    slope_data = Slope_Calibration(flat_data["AvHue"], flat_data["AvSat"], flat_data["StdSat"],
                                flat_data["mouseX"], flat_data["mouseY"])
    store_results(flat_data, slope_data)


# If called by itself:
if __name__ == '__main__':
    cam = Camera(0, {"width": 960, "height": 720})
    time.sleep(1)
    perform_calibration_procedure(cam)


