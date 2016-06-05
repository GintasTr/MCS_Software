# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".
import math
import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
from Demonstration.show_images import Show_images


screen = Show_images()
# disp = Display((960, 720))  #((1024, 768))   640,480                           # Create a display

IMAGE640 = Image("640Background.jpg")
IMAGE1024 = Image("BlackBackground.gif")
IMAGE960 = Image("960x720.jpg")
BACKGROUND_IMAGE = IMAGE960

# Start of calibration
def start_scanning_image():
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(70)
    img.dl().text(
        "Coolant valve handle detection",
        (110,img.height/3),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Press Enter",
        (340,img.height - 150),
        # (img.width, img.width),
        color=Color.WHITE)

    screen.show_till_press_enter(img)

    #disp.quit()                                       # Exit the display so it does not go to "Not responding"

# Inform about reading from file
def reading_from_file_image(Handle_coord_x,Handle_coord_y, closed_angle_stored,
                            open_angle_stored,closed_average_hue,closed_average_sat):
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(70)
    img.dl().text(
        "Reading calibration data",
        (210,50),
        color=Color.WHITE)

    img.dl().setFontSize(50)
    # img.dl().text("%f" % round(angle_average,2))[0:2]
    # "%04i" % found_object_x
    text_temp = "Handle coordinates: X - %04i, Y - %04i" % (Handle_coord_x,Handle_coord_y)
    img.dl().text(
        text_temp,
        (110,250),
        color=Color.WHITE)
    text_temp = "Calibration angles: Closed - %.1f, Open - %.1f" % (round(closed_angle_stored,2),round(open_angle_stored,2))
    img.dl().text(
        text_temp,
        (110,300),
        color=Color.WHITE)
    text_temp = "Average colour data: Hue - %.1f, Sat - %.1f" % (round(closed_average_hue,2),round(closed_average_sat,2))
    img.dl().text(
        text_temp,
        (110,350),
        color=Color.WHITE)

    img.dl().setFontSize(70)
    img.dl().text(
        "Press Enter",
        (340,img.height - 150),
        # (img.width, img.width),
        color=Color.WHITE)

    screen.show_till_press_enter(img)


# If handle is not found during scanning
def scanning_handle_not_found(img):
    img.dl().setFontSize(70)
    img.dl().text(
        "Handle was not found",
        (245, 30),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Press Enter",
        (340,img.height - 120),
        # (img.width, img.width),
        color=Color.WHITE)

    return screen.show_briefly_till_n(img)


# Show lines with angles to represent comparison
def angle_comparison_image(current_angle, closed_angle, open_angle, img, handle,
                           current_position, angle_inverse):
    LENGTH = 150             # Pixels


    if current_position == "Closed":
        text_colour = Color.RED
    elif current_position == "Open":
        text_colour = Color.YELLOW
    else:
        text_colour = Color.BLUE
        handle_position = "Not found"

    img.dl().setFontSize(50)
    img.dl().text(
        ("Detected angle is closer to %s angle" % current_position),
        (165, 30),
        color=text_colour)

    img.dl().setFontSize(40)
    img.dl().text(
        ("Detected angle: %.2f" % current_angle),
        (20, 480),
        # (img.width, img.width),
        color=Color.BLUE)
    img.dl().text(
        ("Open angle: %.2f" % open_angle),
        (20, 520),
        # (img.width, img.width),
        color=Color.YELLOW)
    img.dl().text(
        ("Closed angle: %.2f" % closed_angle),
        (20, 560),
        # (img.width, img.width),
        color=Color.RED)
    img.dl().text(
        ("Distance to %s angle: %.1f" % (current_position, round(angle_inverse,2))),
        (255, img.height - 100),
        color= text_colour,
        alpha = 255)


    # Draw CLOSED LINES (RED)
    closed_angle_radians = math.radians(closed_angle)
    y_offset = int(round(LENGTH * math.sin(closed_angle_radians)))
    x_offset = int(round(LENGTH * math.cos(closed_angle_radians)))

    img.dl().line(start=handle.bottomLeftCorner(),
                  stop=((handle.bottomLeftCorner()[0] + x_offset),(handle.bottomLeftCorner()[1] + y_offset)),
                  color = Color.RED, width = 3)
    img.dl().line(start=handle.bottomLeftCorner(),
                  stop=((handle.bottomLeftCorner()[0] - x_offset),(handle.bottomLeftCorner()[1] - y_offset)),
                  color = Color.RED, width = 3)

    # Draw OPEN LINES (GREEN)
    open_angle_radians = math.radians(open_angle)
    y_offset = int(round(LENGTH * math.sin(open_angle_radians)))
    x_offset = int(round(LENGTH * math.cos(open_angle_radians)))

    img.dl().line(start=handle.bottomLeftCorner(),
                  stop=((handle.bottomLeftCorner()[0] + x_offset),(handle.bottomLeftCorner()[1] + y_offset)),
                  color = Color.YELLOW, width = 3)
    img.dl().line(start=handle.bottomLeftCorner(),
                  stop=((handle.bottomLeftCorner()[0] - x_offset),(handle.bottomLeftCorner()[1] - y_offset)),
                  color = Color.YELLOW, width = 3)

    # Draw CURRENT LINES (BLUE)
    current_angle_radians = math.radians(current_angle)
    y_offset = int(round(LENGTH * math.sin(current_angle_radians)))
    x_offset = int(round(LENGTH * math.cos(current_angle_radians)))

    img.dl().line(start=handle.bottomLeftCorner(),
                  stop=((handle.bottomLeftCorner()[0] + x_offset),(handle.bottomLeftCorner()[1] + y_offset)),
                  color = Color.BLUE, width = 3)
    img.dl().line(start=handle.bottomLeftCorner(),
                  stop=((handle.bottomLeftCorner()[0] - x_offset),(handle.bottomLeftCorner()[1] - y_offset)),
                  color = Color.BLUE, width = 3)


    return screen.show_briefly_till_n(img)


# Before starting multiple scanning
def start_multiple_scanning():
    img = BACKGROUND_IMAGE

    img.dl().setFontSize(70)
    img.dl().text(
        "Confirmation scanning in progress",
        (70,img.height/3),
        # (img.width, img.width),
        color=Color.WHITE)
    img.dl().text(
        "Please wait",
        (340,img.height - 150),
        # (img.width, img.width),
        color=Color.WHITE)

    screen.show_till_press_enter(img)

# After multiple scanning - final one
def end_multiple_scanning_results(final_result, angle_average):
    img = BACKGROUND_IMAGE
    if final_result == "Closed":
        text_colour = Color.RED
        handle_position = "Closed"
    elif final_result == "Open":
        text_colour = Color.YELLOW
        handle_position = "Open"
    else:
        text_colour = Color.BLUE
        handle_position = "Not found"

    img.dl().setFontSize(70)
    img.dl().text(
    "End of scanning",
    (285,50),
    color=Color.WHITE)

    img.dl().setFontSize(40)
    img.dl().text(
        ("Valve handle is: %s" %
         (handle_position)),
        (125,300),
        # (img.width, img.width),
        color=text_colour)

    img.dl().text(
        ("Valve handle is: %s degrees away from fully %s" %
         (angle_average,handle_position)),
        (125,350),
        # (img.width, img.width),
        color=text_colour)

    screen.show_till_press_enter(img)


if __name__ == '__main__':
    while True:
        img = BACKGROUND_IMAGE
        start_multiple_scanning()
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
