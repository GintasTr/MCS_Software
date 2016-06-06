# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".
import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
from Demonstration.Hot_spot_detection.temperature_data_acquisition import Temperature_data
from Demonstration.Hot_spot_detection.display_interaction import display_interaction
from Demonstration.Hot_spot_detection.Background_generation import background_operations
from Demonstration.Hot_spot_detection.Hot_spot_scanning_images import hot_spot_scanning_images

demo_images = hot_spot_scanning_images()

# MAIN SOFTWARE FUNCTION
def do_hot_spot_detection(jpeg_streamer_local):
    global jpeg_streamer
    jpeg_streamer = jpeg_streamer_local
    IMAGE_SCALAR = 10 ## 12.8 to get to 1024 x 768, 12 to get 960 x 720, 10 for 800x600
    THERMAL_IMAGE_WIDTH = 80*IMAGE_SCALAR
    THERMAL_IMAGE_HEIGHT = 60*IMAGE_SCALAR
    SPACING_WIDTH = 80
    PALLETE_WIDTH = 80
    HEIGHT = 720
    COMBINED_WIDTH = THERMAL_IMAGE_WIDTH + SPACING_WIDTH + PALLETE_WIDTH
    START_MESSAGE = "Starting hot spot detection"
    TEMPERATURE_THRESHOLD = 50                                      # Threshold temperature for warning
    WARNING_MESSAGE = "WARNING. HOT SPOT DETECTED!"
    REGULAR_MESSAGE = "Hottest spot: temperature of approximately %.1f at %i X and %i Y coordinates"

    temperature_object = Temperature_data()
    display_interaction_object = display_interaction()
    background_object = background_operations(THERMAL_IMAGE_WIDTH,SPACING_WIDTH,
                                              PALLETE_WIDTH,HEIGHT)

    background_image = background_object.get_background()

    Warning = False                                                 # Initializing variables

    print START_MESSAGE                                         # Inform user about scanning

# Collect maximum temperature pixel data from multiple images. Returns dictionary with:
# {"max_raw_pixel": max_raw_pixel,
# "max_pixel_locations_x": max_pixel_locations_x,
# "max_pixel_locations_y": max_pixel_locations_y,
# "max_temperature": max_temperature,
# "raw_values": raw_values}
    max_temperature_information = temperature_object.iterate_for_max_temperature()

    ## TO SHOW THE IMAGE
    RADIUS = 30

    coloured_scalled_image = display_interaction_object.coloured_image_from_raw(
        max_temperature_information["raw_values"], IMAGE_SCALAR)

    if max_temperature_information["max_temperature"] > TEMPERATURE_THRESHOLD:
        Warning = True                                          # If max temp is larger than limit, flag the warning
        print WARNING_MESSAGE                                   # Print message


    hot_spots_layer = DrawingLayer((960,720))

                                                                # Print regular message either way
    for i in range (0, len(max_temperature_information["max_pixel_locations_x"])):
        print REGULAR_MESSAGE % (max_temperature_information["max_temperature"],
                                 max_temperature_information["max_pixel_locations_x"][i],
                                 max_temperature_information["max_pixel_locations_y"][i])


        ## TO SHOW THE IMAGE
        hot_spots_layer.circle(((max_temperature_information["max_pixel_locations_x"][i]*IMAGE_SCALAR),
                                (max_temperature_information["max_pixel_locations_y"][i]*IMAGE_SCALAR +
                                 (HEIGHT - THERMAL_IMAGE_HEIGHT)/2)),
                                RADIUS, color=Color.BLACK,
                                width = 5, filled = False, alpha = 255)


    ## TO SHOW THE IMAGE
    legend_layer = background_object.get_legends_layer(
        max_temperature_information["max_temperature"],
        max_temperature_information["min_temperature"])


    fault_detection_feedback = ("%f" % round(max_temperature_information["max_temperature"],3))[0:5]
    hottest_spot_x = "%02i" % max_temperature_information["max_pixel_locations_x"][0]
    hottest_spot_y = "%02i" % max_temperature_information["max_pixel_locations_y"][0]
    fault_detection_output= {"fault_detection_feedback": fault_detection_feedback,
                           "max_pixel_locations_x": hottest_spot_x,
                           "max_pixel_locations_y": hottest_spot_y}

    img = display_interaction_object.combine_image(coloured_scalled_image, legend_layer,
                                                       background_image, hot_spots_layer)

    img.save(jpeg_streamer)


    # if Warning:
    #     return "Hot spot detected"
    # else:
    #     return "No hot spots detected"

    return fault_detection_output

# If called by itself:
if __name__ == '__main__':
    print do_hot_spot_detection()