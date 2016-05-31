# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".
# import math
from SimpleCV import *
# LENGTH = 30             # Pixels
# closed_angle = 30
#
#
# closed_angle_radians = math.radians(closed_angle)
# x_offset = int(round(LENGTH * math.sin(closed_angle_radians)))
# print x_offset
disp = Display((1024,768))
IMAGE1024 = Image("BlackBackground.gif")
BACKGROUND_IMAGE = IMAGE1024

def request_of_closed_position():
    img = BACKGROUND_IMAGE
    final_result = "Not found"

    img = BACKGROUND_IMAGE
    if final_result == "Not found":
        text_colour = Color.GREEN
        object_presence = "Not found"
    else:
        text_colour = Color.RED
        object_presence = "Present"
        img.dl().setFontSize(40)
        img.dl().text(
        ("Object coordinates are: X - %04i, Y - %04i" % (231,45)),
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
    request_of_closed_position()
