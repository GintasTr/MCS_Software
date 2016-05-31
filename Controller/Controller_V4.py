# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

# For communications
import smbus
import time
import sys
# TESTING DEBUGGING


from SimpleCV import *

# Foreign object detection
from Foreign_Object_Detection_Controlled_V3 import detect_foreign_object
# LED sequence detection
from LED_Sequence_Controlled_V8 import do_LED_scanning
# Orange flap position detection
from Orange_Flap_V5 import do_Orange_Flap_scanning
# Valve handle position detection
from Valve_Handle_Controlled_V7 import do_Valve_Handle_scanning
# Hot spot detection
from Hot_Spot_Detection_Controlled_V4 import do_hot_spot_detection

# Function to wait for a time period
def wait_for_scan(time_delay):
    print "Waiting for %i seconds" % time_delay
    time.sleep(time_delay)

# Function to read communications output
def read_comms_output(I2C_DEVICE_ADDR):
    #Receive:
    RECEIVED_DATA_LENGTH = 9                                    # How long is the message

    try:
        received_number = bus.read_i2c_block_data(I2C_DEVICE_ADDR, 0x01)
                                                                # Read the received things in numbers format
    except IOError as detail:
        print "Handling IO error:", detail                      # Report IOError
        faulty_transmission = True
        string_used = "#$S0L0I0%"                               # Record place holder for message (not used)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:                                                     # Rerport unexpected error
        print "Unexpected error while reading comms: ", sys.exc_info()[0]
        faulty_transmission = True
        string_used = "#$S0L0I0%"                               # Record place holder for message (not used)
    else:
        faulty_transmission = False
        number_used = received_number[0:RECEIVED_DATA_LENGTH]       # Truncate the sequence to only used numbers
        string_used = "".join([chr(i) for i in number_used])        # Convert sequence of numbers to ASCII string
                                                                    # In format of
                                                            # "#$S(fault_selection_byte)L(location_byte)I(idle_byte)%"
        print "Received message properly:", string_used

    #string_used = "$S0L0I0%"  # ONLY FOR TESTING

    print "Trying to interpret the message..."

    # Interpret the raw comms output to get the real message or identify faulty transmission in format of:
    # comms_output ['fault_selection_byte'] ['location_byte'] ['idle_byte'] ['faulty_transmission']
    comms_output = interpret_comms_output(string_used, faulty_transmission)
                            # Interpret the raw comms output to get the real message or identify faulty transmission

    print "Message received:", comms_output # ONLY FOR TESTING

    # Return dictionary in format of:
    # comms_output ['fault_selection_byte'] ['location_byte'] ['idle_byte'] ['faulty_transmission']
    return comms_output


# Function to decode comms raw output which is a string in format of
# "#$S(fault_selection_byte)L(location_byte)I(idle_byte)%"
def interpret_comms_output(comms_output_raw, faulty_transmission):

    try:
        fault_selection_byte = int(comms_output_raw[3])             # Read the fault selection byte
        location_byte = int(comms_output_raw[5])                    # Read the location_byte
        idle_byte = int(comms_output_raw[7])                        # Read the idle_byte
    except ValueError as detail:                                    # If unable to convert to ints
        print "Commands received were not convertible to int:", detail
        faulty_transmission = True
        fault_selection_byte, location_byte, idle_byte = 0, 0, 0    # Record place holder for message (not used)
    except (KeyboardInterrupt, SystemExit):                         # If user wants to exit software
        raise
    except:                                                         # Rerport unexpected error
        print "Unexpected error while interpreting comms: ", sys.exc_info()[0]
        faulty_transmission = True
        fault_selection_byte, location_byte, idle_byte = 0, 0, 0    # Record place holder for message (not used)

                                                                    # Encode the output in to a dictionary
    comms_output = {"faulty_transmission": faulty_transmission,
                    "fault_selection_byte": fault_selection_byte,
                    "location_byte": location_byte,
                    "idle_byte": idle_byte}

    if not(                                                         # If data is not within defined limits
            (0 <= comms_output["fault_selection_byte"] <= 5) and
            (0 <= comms_output["location_byte"] <= 9) and
            (0 <= comms_output["idle_byte"] <= 2)
    ):
        comms_output["faulty_transmission"] = True                    # Mark transmission as faulty
    return comms_output                                             # Return the decoded  sequence


# Function to send the message to communication system. REMINDER:
#     message_to_comms["detection_progress"] = 1              # Set the progress bit
#     message_to_comms["sensing_selection"] = 1               # Set the location bit
#     message_to_comms["fault_result"] = "111111111"          # Set feedback bit
#     message_to_comms["error"] = 1                           # Set error bit
# Format to send: #$P(detection_progress)S(sensing_selection)F(fault_result)E(error),%
def send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms):
    sent_message = encode_message_to_comms(message_to_comms)    # Put the information in format of
                                                                # #$P(detection_progress)F(fault_result)E(error),%
    DATATOSEND = sent_message                                   # Has to be in format of: "#$P0F0S0,%"
    ascii_Send=[]                                               # Initialise the list to be sent
    for i in DATATOSEND:                                        # For every member in DATATOSEND variable
        ascii_Send.append(ord(i))                               # Add a numbers version to list to be sent

    print "String to send is: ", DATATOSEND # DEBUGGING FEEDBACK

    try:
        bus.write_i2c_block_data(I2C_DEVICE_ADDR, 0x01, ascii_Send) # Send the data to commms system
    except IOError as detail:
        print "IO error while sending data:", detail            # Report IOError
        print "Failed to send data."
    except (KeyboardInterrupt, SystemExit):                     # User wants to exit software
        raise
    except:                                                     # Rerport unexpected error
        print "Unexpected error while sending data: ", sys.exc_info()[0]
        print "Failed to send data."
    else:
        print "String successfully sent."

    return


# Function to encode the message to be sent to communication system from the format of
#     message_to_comms["detection_progress"] = 1              # Set the progress bit
#     message_to_comms["sensing_selection"] = 1               # Set the location bit
#     message_to_comms["fault_result"] = "111111111"          # Set feedback bit
#     message_to_comms["error"] = 1                           # Set error bit
# Format to send: #$P(detection_progress)S(sensing_selection)F(fault_result)E(error),%
def encode_message_to_comms(message_to_comms):
                                                                # Add the strings and variables together
    encoded_message = "#$P" + str(message_to_comms["detection_progress"]) + \
                      "S" + str(message_to_comms["sensing_selection"]) + \
                      "F" + str(message_to_comms["fault_result"]) + \
                      "E" + str(message_to_comms["error"]) + ",%"
    return encoded_message


# Function to start orange flap scan and decode its outputs.
# Output is a dictionary of: {"location_byte", "fault_detection_feedback"} -NOT REALLY
# Possible fault_detection_feedback: "Error - No flaps found", "Slope position", "Flat position", "Error"
# Decoded outputs - 11111 (for "Slope position"), 00000 (for "Flat posititon") and "Error" for any error.
def start_and_decode_orange_flap_scan(location_byte):
    ## Orange flap scanning
    #fault_detection_output = do_Orange_Flap_scanning(location_byte)    # Start the scan
    fault_detection_output = "Error" #"Flat position" #"Slope position" # "Error"              # DEBUGGING
    if fault_detection_output[0] == ("E" or "e"):                       # If output starts with E or e
        return "Error"                                                  # Return error
    elif fault_detection_output[0] == ("S" or "s"):                     # If output starts with S or s (Slope)
        feedback = str(location_byte) + "11111111"
        return feedback                                                 # Return that fault was detected
    elif fault_detection_output[0] == ("F" or "f"):                     # If output starts with F or f (Flat)
        feedback = str(location_byte) + "00000000"
        return feedback                                                 # Return that fault was not detected
    return "Error"                                                      # Any other option (impossible) - Error


# Function to start LED sequence detection and decode its outputs.
# Possible scan outputs: "Error - <...>", or frequency in 4 bytes (0.00-999.)
# Decoded outputs - "Error" for error, first byte - location, other 4 - frequency, last 4 - DO NOT CARE
def start_and_decode_LED_sequence_scan(location_byte):
    ## LED Scanning
    fault_detection_output = "12.2" #"1.42"  #"Error"         # DEBUGGING
    #fault_detection_output = do_LED_scanning(location_byte)
    if fault_detection_output[0] == ("E" or "e"):               # If output starts with E or e
        return "Error"                                          # Return error
    else:
        feedback = str(location_byte) + str(fault_detection_output) + "0000"
        return feedback                                         # Return that fault was detected


# Function to start coolant valve handle position detection and decode its outputs.
# Output from scanning is a dictionary of: {"angle_information", "fault_detection_feedback"}
# Possible fault_detection_feedback outputs: "Error - <...>", "Open", "Closed", angle_information: 00-99
# Decoded outputs - 1 (for "Closed"), 0 (for "Open") and "Error" for any error.
def start_and_decode_coolant_valve_scan():
    ## Valve handle scanning
    fault_detection_output = {"angle_information": "1.",        # DEBUGGING
                              "fault_detection_feedback": "Open"#"Closed" #"Open" #"Error"
                              }
    #fault_detection_output = do_Valve_Handle_scanning()
    if fault_detection_output["fault_detection_feedback"][0] == ("E" or "e"):
                                                                # If output starts with E or e
        return "Error"                                          # Return error
    elif fault_detection_output["fault_detection_feedback"][0] == ("C" or "c"):
        feedback = str(fault_detection_output["angle_information"]) + "1111111"
                                                                # If output starts with C or c (Closed)
        return feedback                                         # Return that fault was detected
    elif fault_detection_output["fault_detection_feedback"][0] == ("O" or "o"):
        feedback = str(fault_detection_output["angle_information"]) + "0000000"
                                                                # If output starts with C or c (Closed)
        return feedback                                         # Return that fault was detected
    return "Error"                                              # Any other option (impossible) - Error


# Function to start foreign object detection and decode its outputs.
# Output from scanning is a dictionary of: {"object_coord_x", "object_coord_y", "fault_detection_feedback"}
# Possible fault_detection_feedback outputs: "Error - <...>", "Not found", "Object is present"
# Outputs - "Error" for any error, object_selection and x(4bytes)y(4bytes)coords for object detected, 0 and DO NOT CARE for not.
def start_and_decode_foreign_object_scan(object_selection):
    if object_selection == 1:                                   # Selection of foreign objects. If 1 - Green_breadboard
        FOREIGN_OBJECT = "Green_breadboard"
    if object_selection == 2:                                   # Selection of foreign objects. If 2 - Red_Glue
        FOREIGN_OBJECT = "Red_Glue"
    if object_selection == 3:                                   # Selection of foreign objects. Undefined yet.
        FOREIGN_OBJECT = "3"
    if object_selection == 4:                                   # Selection of foreign objects. Undefined yet.
        FOREIGN_OBJECT = "4"
    if object_selection == 5:                                   # Selection of foreign objects. Undefined yet.
        FOREIGN_OBJECT = "5"

    ## Foreign object scanning
    #fault_detection_output = detect_foreign_object(FOREIGN_OBJECT)
    fault_detection_output = {"fault_detection_feedback": "Error", #"Object found", #"Error"
                              "object_coord_x": "0001",
                              "object_coord_y": "9999"}

    if fault_detection_output["fault_detection_feedback"][0] == ("E" or "e"):
                                                                # If output starts with E or e
        return "Error"                                          # Return error
    elif fault_detection_output["fault_detection_feedback"][0] == ("O" or "o"):
                                                                # If output starts with O or o (Object is present)
        feedback = str(object_selection) + \
                   str(fault_detection_output["object_coord_x"]) + \
                   str(fault_detection_output["object_coord_y"])

        return feedback                                         # Return that fault was detected
    elif fault_detection_output["fault_detection_feedback"][0] == ("N" or "n"):
                                                                # If output starts with N or n (Not found)
        feedback = "000000000"
        return feedback                                         # Return that fault was not detected
    return "Error"                                              # Any other option (impossible) - Error


# Function to start Hot spot detection and decode its outputs.
# Scanning output is a dictionary of: {"max_pixel_locations_x", "max_pixel_locations_y", "fault_detection_feedback"}
# Possible scan outputs: "Error - <...>", temperature in form of: 000.0-999.9
# Decoded outputs - 000.0-999.9 for hottest spot temperature in the image, x coords 0-80, y cords 0-60.
def start_and_decode_hot_spots_scan():
    ## Hot spots scanning
    fault_detection_output= {"fault_detection_feedback": "12.53", #"000.0" #"Error"
                           "max_pixel_locations_x": "00",
                           "max_pixel_locations_y": "99"}
    #fault_detection_output = do_hot_spot_detection()
    if fault_detection_output["fault_detection_feedback"][0] == ("E" or "e"):
                                                                # If output starts with E or e
        return "Error"                                          # Return error
    else:                                                       # If there was no error
        feedback = str(fault_detection_output["fault_detection_feedback"]) + \
                   str(fault_detection_output["max_pixel_locations_x"]) + \
                   str(fault_detection_output["max_pixel_locations_y"])
        return feedback
    return "Error"                                              # If it got here, there was an error


# Function to start specific piece of fault detection softaware.
# Output has to be in the form of:  1 (fault detected), 0 (fault not detected) or "error"
# Encoding is: 1-flap position,
# 2 - LED sequence, 3 - coolant valve, 4 - foreign object, 5 - hot spot detection
# 6 - not allocated (possibly QR code scanning or any oter foreign objects, 7 - shut down (not possible)
def initiate_fault_detection(fault_selection_byte, location_byte):
    # If 1 - detect flap position.
    if fault_selection_byte == 1:
        decoded_detection_output = start_and_decode_orange_flap_scan(location_byte) # Start and decode orange flap scan
    # If 2 - detect LED sequence.
    elif fault_selection_byte == 2:
        decoded_detection_output = start_and_decode_LED_sequence_scan(location_byte)# Start and decode LED sequence scan
    # If 3 - detect coolant valve handle position.
    elif fault_selection_byte == 3:
        decoded_detection_output = start_and_decode_coolant_valve_scan()         # Start and decode coolant valve scan
    # If 4 - run foreign object detection for pre-defined foreign object
    elif fault_selection_byte == 4:
        decoded_detection_output = start_and_decode_foreign_object_scan(location_byte)# Start and decode foreign object scan
    # If 5 - run hot-spot detection
    elif fault_selection_byte == 5:
        decoded_detection_output = start_and_decode_hot_spots_scan()             # Start and decode hot spots scan
    # If anything else - "Error", because they are not allocated currently
    else:
        print "Message received is invalid"
        decoded_detection_output = "Error"
    return decoded_detection_output                                      # Return the output as "1", "0" or "Error"


# Function to check if message received was in valid format of  0 <= ['fault_selection_byte'] < 8,  0 <= ['stop_bit'] < 2.
def was_meesage_invalid(comms_output):
    if ((0 <= comms_output['fault_selection_byte']) and
            (comms_output['fault_selection_byte'] < 8) and
            (0 <=comms_output['stop_bit']) and
            (comms_output['stop_bit'] < 2) and
            (0 <= comms_output['idle_bit']) and
            (comms_output['idle_bit'] < 2)
        ):
        return False
    else:
        return True



## MAIN SOFTWARE WHICH STARTS AND PERFORMS COMMUNICATIONS PERIODICALLY
def start_communications():
    I2C_DEVICE_BUS = 1                                          # Which I2C bus is used by comms
    I2C_DEVICE_ADDR = 0x04                                      # Which address is used by comms
    SHUT_DOWN_NOTIFICATION = "Shut down command was issued (or horrible error occured), stopping the software"
    TIME_DELAY_INITIAL = 1                                      # Initial time delay
    TIME_DELAY_ACTIVE = 1                                       # Active scanning time delay
    TIME_DELAY_IDLE = 60                                        # Idle scanning time delay

    #setup()
                                                                # Info to user about shutdown
    global bus
    bus = smbus.SMBus(I2C_DEVICE_BUS)                           # Initialise I2C bus


    time_delay = TIME_DELAY_INITIAL
    message_to_comms = {"detection_progress": 0,
                        "sensing_selection": 0,
                        "fault_result": "000000000",
                        "error": 0}
                                                                # Initialise message_to_comms variable
    repeat = True

    while repeat:                                               # Repeat while it is needed
        wait_for_scan(time_delay)                               # Wait for a given period of time


        # Get the decoded output of the comms system in format of
        # comms_output ["fault_selection_byte"] ["location_byte"] ["idle_byte"] ["faulty_transmission"]
        comms_output = read_comms_output(I2C_DEVICE_ADDR)

        if comms_output["faulty_transmission"] == True:         # Check whether message received is valid.
            print "Message received is invalid, waiting for the valid message"
            message_to_comms["detection_progress"] = 0          # Clear the progress bit
            message_to_comms["sensing_selection"] = 0           # Clear the location bit
            message_to_comms["fault_result"] = "000000000"      # Clear result bit
            message_to_comms["error"] = 1                       # Set error bit
                                                                # Put the message to comms in propper format for comms
            # send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms)# Send the message to communication system
            continue

        if comms_output["idle_byte"] == 2:                      # If idle byte is 2 - signal to stop the software
            repeat = False                                      # Terminate the software
            continue                                            # Start from the while loop (will get out of it)

        if comms_output["idle_byte"] == 1:                      # If idle is set to 1 - signal to start idle mode
            print "Idle mode initiated"         # ONLY FOR DEBBUGING

            message_to_comms["detection_progress"] = 0          # Clear the progress bit
            message_to_comms["sensing_selection"] = 0           # Clear the location bit
            message_to_comms["fault_result"] = "000000000"      # Clear result bit
            message_to_comms["error"] = 0                       # Clear error bit
                                                                # Put the message to comms in propper format for comms
            send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms)# Send the message to communication system

                                                                # If idle == 1
            time_delay = TIME_DELAY_IDLE                        # Set comms frequency to be slower
            continue                                            # Go back to while loop

        time_delay = TIME_DELAY_ACTIVE                          # If stop is not set, scanning frequency increases

        if comms_output["fault_selection_byte"] == 0:               # If fault detection was not initialised
            #send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms)# Send the message to communication system
            continue                                            # Continue from while loop start
                                                                # If fault detection was requested:
        message_to_comms["detection_progress"] = 1              # Set the progress bit
                                                                # Indicate which fault is being detected
        message_to_comms["sensing_selection"] = comms_output["fault_selection_byte"]
        message_to_comms["fault_result"] = "000000000"          # Clear result bit
        message_to_comms["error"] = 0                           # Clear error bit
                                                                # Put the message to comms in propper format for comms
        send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms)# Send the message to communication system

        try:
            # Start the specific fault detection.
            fault_result = initiate_fault_detection(comms_output["fault_selection_byte"], comms_output["location_byte"])
        except (KeyboardInterrupt, SystemExit):                 # If user wants to exit the software
            raise
        except:                                                 # Unexpected fault issue
            print "Unexpected issue while scanning for fault"
            fault_result = "Error"


        if fault_result == "Error":                              # If result was error
            message_to_comms["detection_progress"] = 0           # Clear the progress bit
                                                                 # Indicate which fault was being detected
            message_to_comms["sensing_selection"] = comms_output["fault_selection_byte"]
            message_to_comms["fault_result"] = "000000000"       # Clear result bit
            message_to_comms["error"] = 1                        # Set error bit
        else:
            message_to_comms["detection_progress"] = 0           # Clear the progress bit
                                                                 # Indicate which fault was being detected
            message_to_comms["sensing_selection"] = comms_output["fault_selection_byte"]
            message_to_comms["fault_result"] = fault_result      # Select appropriate output
            message_to_comms["error"] = 0                        # Clear error bit

        send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms) # Send the message to communication system

    message_to_comms["detection_progress"] = 1              # Set the progress bit
    message_to_comms["sensing_selection"] = 1               # Set the location bit
    message_to_comms["fault_result"] = "111111111"          # Set feedback bit
    message_to_comms["error"] = 1                           # Set error bit
                                                            # Put the message to comms in propper format for comms and
    send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms)# Send the message to communication system

    print SHUT_DOWN_NOTIFICATION                                 # If got out of loop, print notification


# If called by itself, just so that it does not show error when something is returned
if __name__ == '__main__':
    start_communications()