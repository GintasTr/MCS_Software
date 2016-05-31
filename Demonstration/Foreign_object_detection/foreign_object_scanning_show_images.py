# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".
import math
import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
import cv2

disp = Display((1024, 768))  #((1024, 768))   640,480                           # Create a display

IMAGE640 = Image("640Background.jpg")
IMAGE1024 = Image("BlackBackground.gif")
BACKGROUND_IMAGE = IMAGE1024

# Start of scanning
def start_scanning_image():
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(70)
    img.dl().text(
        "Foreign object detection",
        (220,img.height/3),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Press Enter",
        (370,img.height - 150),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                           # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if left click was used on display
            disp.done = True                          # Turn off Display
        img.show()                                    # Show the image on Display

    disp.done = False
    img.clearLayers()                                       # Clear old drawings

    #disp.quit()                                       # Exit the display so it does not go to "Not responding"

# Inform about reading from file
def reading_from_file_image(object_coords_stored, object_name_stored, object_area_stored,
                  object_rect_distance_stored, object_aspect_ratio_stored,
                  object_average_hue, object_average_sat, object_std_sat):
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(70)
    img.dl().text(
        "Reading calibration data",
        (210,50),
        color=Color.WHITE)

    img.dl().setFontSize(50)
    # img.dl().text("%f" % round(angle_average,2))[0:2]
    # "%04i" % found_object_x
    text_temp = "Object coordinates: X - %04i, Y - %04i" % (object_coords_stored[0],object_coords_stored[1])
    img.dl().text(
        text_temp,
        (150,200),
        color=Color.WHITE)
    text_temp = "Object name: %s" % object_name_stored
    img.dl().text(
        text_temp,
        (150,250),
        color=Color.WHITE)
    text_temp = "Object geometry: area - %i, aspect ratio - %.2f" % \
                (object_area_stored,round(object_aspect_ratio_stored,2))
    img.dl().text(
        text_temp,
        (150,300),
        color=Color.WHITE)
    text_temp = "Average colour data: Hue - %.1f, Sat - %.1f" % (round(object_average_hue,2),round(object_average_sat,2))
    img.dl().text(
        text_temp,
        (150,350),
        color=Color.WHITE)

    img.dl().setFontSize(70)
    img.dl().text(
        "Press Enter",
        (370,img.height - 150),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                           # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if left click was used on display
            disp.done = True                          # Turn off Display
        img.show()                                    # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings

# Image taken
def detection_image_taken(img):
    img.dl().setFontSize(70)
    img.dl().text(
        "Detection image taken",
        (230, 30),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                      # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if y was pressed
            disp.done = True
        img.show()                                    # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings


# If object is not found during scanning
def scanning_object_not_found(img):
    img.dl().setFontSize(50)
    img.dl().text(
        "Specified foreign object was not found",
        (200, 200),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Press Enter",
        (400,img.height - 120),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                      # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if y was pressed
            disp.done = True
        img.show()                                    # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings


# If object is found, show found blobs
def show_filtered_image(img, all_blobs, foreign_object):

    img.dl().setFontSize(70)
    img.dl().text(
        "Possible detected objects",
        (200, 60),
        # (img.width, img.width),
        color=Color.WHITE)

    img.dl().setFontSize(40)
    img.dl().text(
        "Similar foreign object was detected at: X - %i, Y - %i" %
        (foreign_object.coordinates()[0],foreign_object.coordinates()[1]),
        (120, 600),
        # (img.width, img.width),
        color=Color.WHITE)


    for b in all_blobs:
        b.draw(color = Color.RED, width=3, layer = img.dl())
    foreign_object.draw(color = Color.GREEN,width=3, layer = img.dl())

    img.save(disp)

    while disp.isNotDone():                      # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if y was pressed
            disp.done = True
        img.show()                                    # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings

# Before starting multiple scanning
def start_multiple_scanning():
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(70)
    img.dl().text(
        "Confirmation scanning in progress",
        (100,img.height/3),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Please wait",
        (360,img.height - 150),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                           # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if left click was used on display
            disp.done = True                          # Turn off Display
        img.show()                                    # Show the image on Display

    disp.done = False
    img.clearLayers()                                       # Clear old drawings

# After multiple scanning - final one
def end_multiple_scanning_results(final_result, object_coord_x, object_coord_y):
    img = BACKGROUND_IMAGE
    if final_result == "Not found":
        text_colour = Color.GREEN
        object_presence = "Not found"
    else:
        text_colour = Color.RED
        img.dl().setFontSize(40)
        object_presence = "Present"
        img.dl().text(
        ("Object coordinates are: X - %i, Y - %i" % (object_coord_x,object_coord_y)),
        (125,350),
        # (img.width, img.width),
        color=text_colour)

    img.dl().setFontSize(70)
    img.dl().text(
    "End of scanning",
    (310,50),
    color=Color.WHITE)

    img.dl().setFontSize(40)
    img.dl().text(
        ("Object is: %s" %
         (object_presence)),
        (125,300),
        # (img.width, img.width),
        color=text_colour)

    img.dl().setFontSize(50)
    img.dl().text(
        "Finished scanning routine",
        (290,img.height - 150),
        # (img.width, img.width),
        color=Color.WHITE)
    img.save(disp)

    while disp.isNotDone():                           # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_RETURN] == 1):                # Check if left click was used on display
            disp.done = True                          # Turn off Display
        img.show()                                    # Show the image on Display

    disp.done = False
    img.clearLayers()                                       # Clear old drawings


if __name__ == '__main__':
    while True:
        img = IMAGE1024
        detection_image_taken(img)
        # closed_coords_stored_x = 1203
        # closed_coords_stored_y = 542
        # closed_angle_stored = 12.3542
        # open_angle_stored = 48.65942
        # closed_average_hue = 253.4321315
        # closed_average_sat = 12.15412354
        # closed_std_sat = 0
        # reading_from_file_image(closed_coords_stored_x,
        #                         closed_coords_stored_y,
        #                         closed_angle_stored,open_angle_stored,
        #                         closed_average_hue,closed_average_sat)
        # raw_input()
