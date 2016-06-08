# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

import sys                                                  # Only for RPI
sys.path.append('/home/pi/MCS_Software')                    # Only for RPI

from SimpleCV import *
from os.path import exists
from LED_Sequence_scanning_images import LED_scanning_images

demo_images = LED_scanning_images()

cam = None
# prepares, selects the camera
def setup(local_cam):
    global cam
    cam = local_cam
    # if cam == None:
    #     cam = Camera(0, {"width": 1024, "height": 768})    # Only for RPI 2592x1944. For calibration - 1024x768
    # #cam = Camera                                          # Only for laptop
    # time.sleep(1)

# Shows the image until the button is pressed
def show_image_until_pressed(img):
    disp = Display()                                        # Create a display
    while disp.isNotDone():                                 # Loop until display is not needed anymore
        if disp.mouseLeft:                                  # Check if left click was used on display
            disp.done = True                                # Turn off Display
        img.show()                                          # Show the image on Display
    disp.quit()                                        # Exit the display so it does not go to "Not responding"

# Briefly flashes the image
def show_image_briefly(img):
    img.show()                                              # Show the image on Display


# for image acquisition from camera (and flipping)
def GetImage():
    # img = cam.getImage()
    img = cam.getImage()                                    ##ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
    #img = img.flipVertical()
    img = img.flipHorizontal()
    return img


# Debugging function: Shows the pixel value when clicked on the screen:
def debug_pixel_value(img):
    disp = Display()                                            # Create a display
    while disp.isNotDone():                                     # Loop until display is not needed anymore
        img.clearLayers()                                       # Clear old drawings
        if disp.mouseLeft:
            mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
            text = "Pixel value is: " + str(img.getGrayPixel(mouse_coords[0],mouse_coords[1]))
            img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
            img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED, dimensions = [2,2])
        if disp.mouseRight:                                     # If right clicked
            disp.done = True                                    # Turn off Display
        img.save(disp)                                          # Show the image on Display
    Display().quit()                                            # Exit the display so it does not go to "Not responding"
    return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]


# Function to detect the main LED:
def MainLedDetection(img, coords, data):
    # STD_CONSTANT = 5                                          # Define how many standard deviations of saturation to include
    #MIN_BRIGHTNESS = 100 #240 on laptop                         # Minimal illumination threshold
    #BLOBS_MAX_SIZE = 5000                                       # Specify max size of blob
    #BLOBS_MIN_SIZE = 10                                         # Specify min size of blob

    BLOBS_BRIGHTNESS_THRESHOLD = 240  #230 on laptop            # Define how close to the calibrated colour blobs have to be

    # COLOUR FILTER. NOT USEFULL ON RPI AND WITH LONG DISTANCES
    # img = img.toHSV()                                           # Convert image to HSV colour space
    # # minsaturation = (data["avg_sat"]- STD_CONSTANT * data["std_sat"])
    #                                                             # Derive minimum saturation. As a reminder: hsv_data =
    #                                                             # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    #                                                             # Apply filters to the image TODO: calibrate or change the filtering
    # filtered = img.hueDistance(color = data["avg_hue"],
    #                           minvalue = MIN_BRIGHTNESS
    #                            )

    filtered = img.binarize(thresh = BLOBS_BRIGHTNESS_THRESHOLD)
    # filtered.show()
    filtered = filtered.invert()                                # Invert black and white (to have LED as white)
    filtered = filtered.morphOpen()                             # Perform morphOps
    # filtered = filtered.erode(1)

    filtered = filtered.dilate(1)

    #debug_pixel_value(filtered)# TESTING DEBUGGING

    #show_image_briefly(filtered)
                                                                # Look for blobs
    all_blobs = filtered.findBlobs(
                                #maxsize=BLOBS_MAX_SIZE,
                                # minsize= 1,                    # Only for low resolutions
                                #threshval = BLOBS_BRIGHTNESS_THRESHOLD
                                    )

    if all_blobs > 1:                                           # If more than 1 blob found
        all_blobs = all_blobs.sortDistance(point =(coords[0], coords[1]))   # Sort based on distance from mouse click
    elif all_blobs < 1:                                         # If none blobs found
        # print "No blobs found"                                # Print and return that no blobs were found. Not needed
        return "No blobs found"

    m_led = all_blobs[0]                                        # m_led is the closest blob to mouse click

    return m_led


# Function to measure average illumination around LEDs TODO: Think about implementing threshold filter instead
def GetLight(img, coords, hsv_data, dist):
    dist_scalar = 3                                            # Margin of distance to include both LEDs
    crop_length = int(round(dist_scalar*dist))
    main_blob = MainLedDetection(img,coords,hsv_data)           # Get main led blob. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}
    if main_blob == "No blobs found":                           # Check whether blobs were found
        return "No blobs found"                                 # If no blobs found return string
    blob_coordinates = main_blob.coordinates()                  # Main blob coordinates
    cropped = img.crop(blob_coordinates[0],                     # Crop around the main blob
                        blob_coordinates[1], crop_length,
                        crop_length, centered=True)
    cropped = cropped.toGray()                                  # Convert to Gray scale colour space
    #cropped.show()                                              # DEBUGGING
    cropped = cropped.getGrayNumpy()                            # Convert to NumPy array
    light_value = np.mean(cropped)                              # Get average grayscale colour
    # print light_value                                         # For debugging TODO: Check for more efficient methods
    return light_value




# Function to get number_of_blobs
def BlobsNumber(img, coords, hsv_data, dist):
    #MINIMUM_BLOB_SIZE = 100
    dist_scalar = 2.5                                           # Margin of distance to include both LEDs
    crop_length = int(round(dist_scalar*dist))

    main_blob = MainLedDetection(img,coords,hsv_data)           # Get main led blob. As a reminder: hsv_data =
                                                                # {"avg_hue": meanHue, "avg_sat": meanSat, "std_sat": stdSat}

    if main_blob == "No blobs found":                           # Check whether blobs were found


        result_to_return = {"number_of_blobs": "No blobs found",
                            "main_LED_blob": 0,
                            "filtered_img_with_LEDs": 0,
                            "crop_length": crop_length
                            }
        return result_to_return


    blob_coordinates = main_blob.coordinates()                  # Main blob coordinates
    cropped = img.crop(blob_coordinates[0],                     # Crop around the main blob
                        blob_coordinates[1], crop_length,
                        crop_length, centered=True)
    cropped = cropped.toGray()                                  # Convert to Grayscale Image
    cropped_num = cropped.getGrayNumpy()                        # Convert to NumPy array
    bin_thresh = (np.max(cropped_num) + np.mean(cropped_num))/2   # Set the threshold as half of the max to average
    cropped = cropped.binarize(thresh=bin_thresh)               # Binarize the cropped image
    cropped = cropped.invert()                                  # Invert so that light areas are white
    cropped = cropped.morphOpen()
    # cropped = cropped.erode(iterations = 1)                     # FOR BIGGER RANGE
    # filtered = cropped.erode(1)

    cropped = cropped.dilate(iterations = 1)                    # If from close - change to 1


    all_blobs = cropped.findBlobs(
                                #minsize = 1        # Only for low resolutions
                                 )
    if all_blobs<1:                           # Check whether blobs were found


        result_to_return = {"number_of_blobs": "No blobs found",
                            "main_LED_blob": 0,
                            "filtered_img_with_LEDs": 0,
                            "crop_length": crop_length
                            }
        return result_to_return
                                                                # Find ALL blobs in the image
    all_blobs.draw(color = Color.GREEN,width=2)      # For debugging - draw all blobs
    # show_image_briefly(cropped)                                # DEBUGGING
    cropped = cropped.applyLayers()
    number_of_blobs = len(all_blobs)                            # Return the number of found blobs

    result_to_return = {"number_of_blobs": number_of_blobs,
                        "main_LED_blob": main_blob,
                        "filtered_img_with_LEDs": cropped,
                        "crop_length": crop_length
                        }
    return result_to_return



# Function to perform the main sequence scanning
# Reminder: cal_data = {"max_light": max_light, "min_light": min_light,"m_led_coords": m_led_coords,
                      #"m_led_data": m_led_data, "dist_led": dist_led,"seq_time": seq_time, "scan_type": scan_type}
def SequenceScanning(cal_data):
    FIRST_DETECTION_LIMIT = 10                              # Time to wait for first LED to get detected
    # RENAMING CALIBRATION VARIABLES EASIER ACCESS:
    m_led_coord_x = cal_data['m_led_coord_x']
    m_led_coord_y = cal_data['m_led_coord_y']
    avg_hue = cal_data['avg_hue']
    avg_sat = cal_data['avg_sat']
    std_sat = cal_data['std_sat']
    seq_time = cal_data['seq_time']
    dist_led = cal_data['dist_led']
    scan_type = cal_data['scan_type']
    max_light = cal_data['max_light']
    min_light = cal_data['min_light']


    m_led_coords = (m_led_coord_x, m_led_coord_y)
    m_led_data = {"avg_hue": avg_hue,
                   "avg_sat": avg_sat,
                   "std_sat": std_sat}

    scan_done = False                                            # Initiate scanning loop
    start1 = time.time()                                        # Mark the start scanning

    elapsed_time1 = time.time() - start1                        # Obtain value for checking loop to not show error
    while not scan_done:                                         # Perform while scanning is not done
        led_sequence = []                                        # Create empty list to store sequence
        live_img = GetImage()                                    # Get live camera image
        if MainLedDetection(live_img ,m_led_coords,m_led_data) == "No blobs found":
                                                                 # Check if there is a main LED
            elapsed_time1 = time.time() - start1                # Check how long main LED is not detected

            not_used = demo_images.looking_for_LED(live_img)

            if elapsed_time1 > FIRST_DETECTION_LIMIT:            # If it is longer than limit
                return "Error - first LED not found"             # Return error
            continue                                             # Start from the top of the loop
        print "LED found, starting sequence scanning"            # Notify user about sequence scanning
        start2 = time.time()                                    # Mark the start of sequence
        elapsed_old = 0                                          # Initialise for delta T acquisition
        previous_state = "SCN"                               # Initialise previous LED state variable
        # elapsed_time = time.time() - start2                     # Obtain value for while loop to not show error
        delta_t = 0.0
        show_scanning_demo = True

        last_change_time = time.time()
        time_of_current_state = time.time() - last_change_time
        while show_scanning_demo:
        # while(elapsed_time < seq_time):              # Loop while sequence is not finished

            live_img = GetImage()                                # Obtain live image

            if scan_type == "number_of_blobs":           # If scanning is performed based on number_of_blobs

                blobs_result = BlobsNumber(live_img, m_led_coords,
                                              m_led_data, dist_led)
                number_of_blobs = blobs_result["number_of_blobs"]

                if number_of_blobs == "No blobs found":              # If no blobs were found

                    show_scanning_demo = demo_images.looking_for_LED(live_img)

                    led_state = "Not_found"
                    if previous_state == led_state:
                        # elapsed_time = (time.time() - start2)            # Update elapsed time for the loop
                        time_of_current_state = time.time() - last_change_time
                        continue                                         # Loop again

                    last_change_time = time.time()
                    previous_state = led_state

                    elapsed_time = (time.time() - start2)            # Get elapsed time for the list
                    delta_t = elapsed_time - elapsed_old              # Calculate Delta T
                    elapsed_old = elapsed_time                        # Update Old time for delta T calculations
                    led_sequence.append("No blobs found at %.4f.  Delta T from last state: %.4f"
                                        % (elapsed_time, delta_t))
                    print ("No blobs found at %.4f. Delta T from last state: %.4f"
                                        % (elapsed_time, delta_t))
                    continue                                         # Start from the top of the loop

                if number_of_blobs > 1:                              # Check if more than 1 LED is on
                    led_state = "ON"
                else:
                    led_state = "OFF"

                if previous_state == led_state:                      # If current state is the same as previous, do nothing
                    time_of_current_state = time.time() - last_change_time
                    # elapsed_time = (time.time() - start2)            # Update elapsed time for the loop

                    show_scanning_demo = demo_images.sequence_scanning_image_shown(live_img, blobs_result["main_LED_blob"],
                                              blobs_result["filtered_img_with_LEDs"],
                                              blobs_result["crop_length"],
                                              time_of_current_state,
                                              delta_t, number_of_blobs)

                    continue                                         # Loop again


                last_change_time = time.time()
                previous_state = led_state                           # Update the previous state
                elapsed_time = (time.time() - start2)                # Calculate elapsed time
                delta_t = elapsed_time - elapsed_old                 # Calculate Delta T
                elapsed_old = elapsed_time                           # Update Old time for delta T calculations
                                                                     # Add new values to sequence list

                show_scanning_demo = demo_images.sequence_scanning_image_shown(live_img, blobs_result["main_LED_blob"],
                          blobs_result["filtered_img_with_LEDs"],
                          blobs_result["crop_length"],
                          time_of_current_state,
                          delta_t, number_of_blobs)
                led_sequence.append("LED state: %s at %.4f. Delta T from last state: %.4f" % \
                      (led_state, elapsed_time, delta_t))
                                                                     # Print new values for debugging
                print "LED state: %s at %.4f. Delta T from last state: %.4f" % \
                      (led_state, elapsed_time, delta_t)





                                                                 # Notify user about end of scanning
        print "END OF SCANNING. \n Sequence is:"                 # Nicely print the sequence

        for i in led_sequence:
            print i
        #again = GetConfirmation("Scan again? Y/N")               # Ask if scan again
        #if again:
            continue                                             # Start from the top loop
        return led_sequence

# Function to read calibration file
# Reminder: calibration_data = {"max_light": max_light, "min_light:": min_light,"m_led_coords": m_led_coords,
# "m_led_data": m_led_data, "dist_led": dist_led,"seq_time": seq_time}
def read_calibration_data(STORAGE_FILE):

    with open(STORAGE_FILE, "r") as storage:
        m_led_coord_x = int(storage.readline().split()[1])
        m_led_coord_y = int(storage.readline().split()[1])
        avg_hue = float(storage.readline().split()[1])
        avg_sat = float(storage.readline().split()[1])
        std_sat = float(storage.readline().split()[1])
        dist_led = float(storage.readline().split()[1])
        seq_time = int(storage.readline().split()[1])
        scan_type = (storage.readline().split()[1])
        max_light = float(storage.readline().split()[1])
        min_light = float(storage.readline().split()[1])


    scan_type = "number_of_blobs"
    # SCALE COORDINATES DUE TO RESOLUTION DIFFERENCE BETWEEN CALIBRATION (1024x768) and scanning (2592x1944)
    #m_led_coord_x = m_led_coord_x * 2592/1024
    #m_led_coord_y = m_led_coord_y * 1944/768


    calibration_data = {"m_led_coord_x": m_led_coord_x,
                        "m_led_coord_y": m_led_coord_y,
                        "avg_hue": avg_hue,
                        "avg_sat": avg_sat,
                        "std_sat": std_sat,
                        "dist_led": dist_led,
                        "seq_time": seq_time,
                        "scan_type": scan_type,
                        "max_light": max_light,
                        "min_light": min_light
                        }

    demo_images.reading_from_file_image(m_led_coord_x, m_led_coord_y,
                                        dist_led, seq_time,
                                        avg_hue, avg_sat)

    print calibration_data
    return calibration_data

# Function to get average blinking period
# Single value in led_sequence is: LED state: ON at 14.6632 Delta T from last state: 0.4788
def get_average_period(led_sequence):
    sum = 0                                                         # Initialize sum
    for i in range(0, (len(led_sequence)-2)):                       # For whole length of sequence
        if led_sequence[i].split()[0] !="No":                       # Only if first word is not equal to "No"
            sum += float(led_sequence[(i+2)].split()[-1])           # Sum the Delta T of next item
                                                                    # to get how long the state was constant
    average = sum/(len(led_sequence)-2)                             # Calculate average frequency
    print "Average period is:", average                             # For debugging
    return average


# Function to compare set frequency to some pre-defined values.
# Single value in led_sequence is: LED state: ON at 14.6632 Delta T from last state: 0.4788
def compare_frequency(led_sequence):
    THRESHOLD_FREQUENCY = 1.0                                         # Threshold blinking frequency (in Hz)

    threshold_period = 1.0/THRESHOLD_FREQUENCY                        # Calculate threshold Delta T

    sequence_period = get_average_period(led_sequence)                # Get average period
    print "Threshold period is:", threshold_period
    if sequence_period < threshold_period:
        return "Faster - LED is blinking faster than threshold frequency"
    else:
        return "Slower - LED is blinking slower than threshold frequency"
    return "Error - strange error in frequency check"


# Funtion to check whether main LED was gone for more than certain amount of time
# Single value in led_sequence is: LED state: ON at 14.6632 Delta T from last state: 0.4788
def check_validity(led_sequence, seq_time):
    VALIDITY_THRESHOLD = float(seq_time)/2                               # Amount of time required to make sequence invalid
    sum = 0                                                       # Initialize sum
    for i in range(0, (len(led_sequence)-1)):                     # For whole length of sequence
        if led_sequence[i].split()[0] == "No":                    # If first word in sequence member is "No"
            sum += float(led_sequence[(i+1)].split()[-1])         # Sum the Delta T of next items
    if sum < VALIDITY_THRESHOLD:
        return False                                              # Results are valid
    else:
        return True                                               # Results are not valid
    return "Error - strange error in validity check"


### Main scanning software:
def do_LED_scanning(local_cam, location_byte):
    STORAGE_FILE = "LED_sequence_calibration_data.txt"

    setup(local_cam)

    demo_images.scanning_start()

    #ONLY USED FOR WINDOWS
    #calibration_data_location = os.path.join(os.path.dirname(__file__), 'Calibration_files\\', STORAGE_FILE)
    calibration_data_location = os.path.join(os.path.dirname(__file__), STORAGE_FILE)

    print "Reading from: " + calibration_data_location

    if not exists(calibration_data_location):
        print ("Calibration data for this object has not been found. "
               "Please do the calibration first and store its data to "
               "Calibration_files folder before running the scan")
        return "Error"                                      # If error occurs - only used when called by other software

    calibration_data = read_calibration_data(calibration_data_location)          # Extract calibration data

    led_sequence = SequenceScanning(calibration_data)             # Start sequence scanning based on calibration data

    if type(led_sequence) != list:
        if led_sequence.split()[0] == "E" or "e":                     # Check if LED sequence was actually found
            return "Error - first LED not found"

    # Check if LED was gone for more than half of the sequence time
    results_are_not_valid = check_validity(led_sequence, calibration_data["seq_time"])

    if results_are_not_valid:                                     # If results were not valid
        demo_images.non_valid_scan()
        return "Error - results are not valid because main LED was lost for too long"

    #result = compare_frequency(led_sequence)                # Only for binary results
    result = get_average_period(led_sequence)                # Get average period
    result = ("%f" % round(result,2))[0:4]
    demo_images.scanning_done_image(led_sequence, result)
    return result

# If called by itself:
if __name__ == '__main__':
    cam = Camera(0, {"width": 960, "height": 720})
    location_byte = 1
    print do_LED_scanning(cam, location_byte)