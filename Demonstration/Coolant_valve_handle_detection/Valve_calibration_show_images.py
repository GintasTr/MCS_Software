# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
import cv2

IMAGE640 = Image("640Background.jpg")
IMAGE1024 = Image("BlackBackground.gif")
BACKGROUND_IMAGE = IMAGE1024

disp = Display((1024, 768))  #((1024, 768))                              # Create a display
# Start of calibration
def calibration_start_image():
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(70)
    img.dl().text(
        "Coolant valve handle calibration",
        (img.width/7,img.height/3),
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


# Function to ask for closed position image
def request_of_closed_position():
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(40)
    img.dl().text(
        "Place the camera as it would be during coolant valve inspection",
        (70,img.height/3),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().setFontSize(50)
    img.dl().text(
        "Put the valve handle to CLOSED position",
        (180,img.height/3 + 50),
        # (img.width, img.width),
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
    #disp.quit()                                       # Exit the display so it does not go to "Not responding"


# Request of OPEN position
def request_of_open_position():
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(40)
    img.dl().text(
        "Place the camera as it would be during coolant valve inspection",
        (70,img.height/3),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().setFontSize(50)
    img.dl().text(
        "Put the valve handle to OPEN position",
        (180,img.height/3 + 50),
        # (img.width, img.width),
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


# Function to ask if valve handle is clearly seen
def clearly_seen_confirmation(img):
    result = False
    img.dl().setFontSize(70)
    img.dl().text(
        "Is valve handle clearly visible?",
        (img.width/7, 30),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Press y/n",
        (400,img.height - 120),
        # (img.width, img.width),
        color=Color.WHITE)

    img.save(disp)

    while disp.isNotDone():                      # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_y] == 1):                # Check if y was pressed
            disp.done = True
            result = True
        elif(pressed[pg.K_n] == 1):              # Check if n was pressed
            disp.done = True
            result = False
        img.show()                                    # Show the image on Display
    disp.done = False

    img.clearLayers()                                       # Clear old drawings
    return result


def get_valve_handle_coordinates_image(img):
    SQUARE_DIMENSIONS = 8
    mouse_coords = None

    while disp.isNotDone():                                     # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()

        img.clearLayers()                                       # Clear old drawings

        img.dl().setFontSize(70)
        img.dl().text(
            "Left click on valve handle",
            (220, 30),
            # (img.width, img.width),
            color=Color.WHITE)
        img.dl().text(
            "Press Enter",
            (370,img.height - 120),
            # (img.width, img.width),
            color=Color.WHITE)


        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = "X:" + str(mouse_coords[0]) + " Y:" + str(mouse_coords[1])
            img.dl().setFontSize(20)

            img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED,
                                       dimensions = [SQUARE_DIMENSIONS,SQUARE_DIMENSIONS])
        if (pressed[pg.K_RETURN] == 1):                         # If enter pressed
            if mouse_coords != None:
                disp.done = True                                # Turn off Display
            else:
                print "Pressed Enter before clicking on image"
        img.save(disp)                                          # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings
    #Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]


# If handle was not found
def handle_not_found(img):
    img.dl().setFontSize(70)
    img.dl().text(
        "Handle was not found",
        (245, 30),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Press Enter",
        (370,img.height - 120),
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


# Confirm that handle was correctly foun
def correct_blob_confirmation_image(handle_found, img):
    img.clearLayers()                                       # Clear old drawings
    result = False
    test_img = img

    handle_found.drawMinRect(layer=test_img.dl(), color = Color.RED, width = 3, alpha=255)

    test_img.dl().setFontSize(45)
    test_img.dl().text(
        "Is valve handle with a red square around it?",
        (175, 30),
        # (img.width, img.width),
        color=Color.WHITE)
    test_img.dl().setFontSize(70)

    test_img.dl().text(
        "Press y/n",
        (400,test_img.height - 120),
        # (img.width, img.width),
        color=Color.WHITE)

    test_img.save(disp)

    while disp.isNotDone():                      # Loop until display is not needed anymore
        pressed = pg.key.get_pressed()
        if(pressed[pg.K_y] == 1):                # Check if y was pressed
            disp.done = True
            result = True
        elif(pressed[pg.K_n] == 1):              # Check if n was pressed
            disp.done = True
            result = False
        test_img.show()                          # Show the image on Display
    disp.done = False
    img.clearLayers()                                       # Clear old drawings
    return result


def store_results_image(closed_coords_stored, closed_angle_stored, open_angle_stored,
                  closed_average_hue, closed_average_sat, closed_std_sat):
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(70)
    img.dl().text(
        "Data is recorded and stored",
        (180,50),
        color=Color.WHITE)

    img.dl().setFontSize(50)
    # img.dl().text("%f" % round(angle_average,2))[0:2]
    # "%04i" % found_object_x
    text_temp = "Handle coordinates: X - %04i, Y - %04i" % (closed_coords_stored[0],closed_coords_stored[1])
    img.dl().text(
        text_temp,
        (150,250),
        color=Color.WHITE)
    text_temp = "Calibration angles: Closed - %.1f, Open - %.1f" % (round(closed_angle_stored,2),round(open_angle_stored,2))
    img.dl().text(
        text_temp,
        (150,300),
        color=Color.WHITE)
    text_temp = "Average colour data: Hue - %.1f, Sat - %.1f" % (round(closed_average_hue,2),round(closed_average_sat,2))
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

    #disp.quit()                                       # Exit the display so it does not go to "Not responding"



if __name__ == '__main__':
    while True:
        closed_coords_stored = [1203, 542]
        closed_angle_stored = 12.3542
        open_angle_stored = 48.65942
        closed_average_hue = 253.4321315
        closed_average_sat = 12.15412354
        closed_std_sat = 0
        store_results_image(closed_coords_stored,closed_angle_stored,open_angle_stored,
                            closed_average_hue,closed_average_sat,closed_std_sat)
        raw_input()
