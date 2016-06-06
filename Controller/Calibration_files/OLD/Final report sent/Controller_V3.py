# Scanning software has to be in "Controller folder"
# Calibration files have to be in  "Controller folder/Calibration_files".

# For communications
import smbus
import time
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
from Hot_Spot_Detection_Controlled_V5 import do_hot_spot_detection

# Function to wait for a time period
def wait_for_scan(time_delay):
    print "Waiting for %i seconds" % time_delay
    time.sleep(time_delay)

# Function to read communications output
def read_comms_output(I2C_DEVICE_ADDR):
    #Receive:


    RECEIVED_DATA_LENGTH = 9                                    # How long is the message
    received_number = bus.read_i2c_block_data(I2C_DEVICE_ADDR, 0x01)
                                                                # Read the received things in numbers format
    number_used = received_number[0:RECEIVED_DATA_LENGTH]       # Truncate the sequence to only used numbers
    string_used = "".join([chr(i) for i in number_used])        # Convert sequence of numbers to ASCII string
                                                                # In format of #$F(fault_bit)I(idle_bit)S(stop_bit)%

    #string_used = "#$F3S0%"  # ONLY FOR TESTING

    print "Trying to read the message..."

    comms_output = interpret_comms_output(string_used)          # interpret the raw comms output to get the real message

    print "Message received:", comms_output # ONLY FOR TESTING

    # Return dictionary in format of comms_output ['fault_bit'] ['stop_bit'] ['idle_bit']
    return comms_output


# Function to decode comms raw output which is a string in format of #$F(fault_bit)I(idle_bit)S(stop_bit)%
def interpret_comms_output(comms_output_raw):
    fault_bit = int(comms_output_raw[3])                             # Read the fault bit
    idle_bit = int(comms_output_raw[5])                              # Read the idle bit
    stop_bit = int(comms_output_raw[7])                              # Read the stop bit

                                                                # Encode the output in to a dictionary
    comms_output = {"fault_bit": fault_bit, "stop_bit": stop_bit, "idle_bit": idle_bit}
    return comms_output                                         # Return the decoded  sequence


# Function to send the message to communication system.
# Reminder: message_to_comms = {"detection_progress": 0, "fault_result":0, "error": 0}
# Format to send: #$P(detection_progress)F(fault_result)E(error)%
def send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms):
    sent_message = encode_message_to_comms(message_to_comms)    # Put the information in format of
                                                                # #$P(detection_progress)F(fault_result)E(error),%

    #WRITE:
    DATATOSEND = sent_message                                   # Has to be in format of: "#$P0F0S0,%"
    ascii_Send=[]                                               # Initialise the list to be sent
    for i in DATATOSEND:                                        # For every member in DATATOSEND variable
        ascii_Send.append(ord(i))                               # Add a numbers version to list to be sent


    print "String to send is: ", DATATOSEND # DEBUGGING FEEDBACK


    bus.write_i2c_block_data(I2C_DEVICE_ADDR, 0x01, ascii_Send) # Send the data to commms system

    print "String sucesfully sent."

    return


# Function to encode the message to be sent to communication system from the format of
# message_to_comms = {"detection_progress": 0, "fault_result":0, "error": 0} to
# "#$P(detection_progress)F(fault_result)E(error),%"
def encode_message_to_comms(message_to_comms):
                                                                # Add the strings and variables together
    encoded_message = "#$P" + str(message_to_comms["detection_progress"]) + \
                      "F" + str(message_to_comms["fault_result"]) + \
                      "E" + str(message_to_comms["error"]) + ",%"
    print "Encoded message is:", encoded_message                # DEBUGGING FEEDBACK
    return encoded_message


# Function to start orange flap scan and decode its outputs.
# Possible scan outputs: "Error - No flaps found", "Slope position", "Flat position", "Error"
# Decoded outputs - 1 (for "Slope position"), 0 (for "Flat posititon") and "Error" for any error.
def start_and_decode_orange_flap_scan():
    ## Orange flap scanning
    fault_detection_output = do_Orange_Flap_scanning()          # Start the scan
    if fault_detection_output[0] == ("E" or "e"):                 # If output starts with E or e
        return "Error"                                          # Return error
    elif fault_detection_output[0] == ("S" or "s"):               # If output starts with S or s (Slope)
        return "1"                                              # Return that fault was detected
    elif fault_detection_output[0] == ("F" or "f"):               # If output starts with F or f (Flat)
        return "0"                                              # Return that fault was not detected
    return "Error"                                              # Any other option (impossible) - Error


# Function to start LED sequence detection and decode its outputs.
# Possible scan outputs: "Error - <...>", "Faster - <...>", "Slower - <...>"
# Decoded outputs - 1 (for "Faster"), 0 (for "Slower") and "Error" for any error.
def start_and_decode_LED_sequence_scan():
    ## LED Scanning
    fault_detection_output = do_LED_scanning()
    if fault_detection_output[0] == ("E" or "e"):                 # If output starts with E or e
        return "Error"                                          # Return error
    elif fault_detection_output[0] == ("F" or "f"):               # If output starts with F or f (Faster)
        return "1"                                              # Return that fault was detected
    elif fault_detection_output[0] == ("S" or "s"):               # If output starts with S or s (Slower)
        return "0"                                              # Return that fault was not detected
    return "Error"                                              # Any other option (impossible) - Error

# Function to start coolant valve handle position detection and decode its outputs.
# Possible scan outputs: "Error - <...>", "Open", "Closed"
# Decoded outputs - 1 (for "Closed"), 0 (for "Open") and "Error" for any error.
def start_and_decode_coolant_valve_scan():
    ## Valve handle scanning
    fault_detection_output = do_Valve_Handle_scanning()
    if fault_detection_output[0] == ("E" or "e"):                 # If output starts with E or e
        return "Error"                                          # Return error
    elif fault_detection_output[0] == ("C" or "c"):               # If output starts with C or c (Closed)
        return "1"                                              # Return that fault was detected
    elif fault_detection_output[0] == ("O" or "o"):               # If output starts with O or o (Open)
        return "0"                                              # Return that fault was not detected
    return "Error"                                              # Any other option (impossible) - Error


# Function to start foreign object detection and decode its outputs.
# Possible scan outputs: "Error - <...>", "Not found", "Object is present"
# Decoded outputs - 1 (for "Object is present"), 0 (for "Not found") and "Error" for any error.
def start_and_decode_foreign_object_scan():
    FOREIGN_OBJECT = "Green_breadboard"                         # Default name for foreign object
    ## Foreign object scanning
    fault_detection_output = detect_foreign_object(FOREIGN_OBJECT)
    if fault_detection_output[0] == ("E" or "e"):                 # If output starts with E or e
        return "Error"                                          # Return error
    elif fault_detection_output[0] == ("O" or "o"):               # If output starts with O or o (Object is present)
        return "1"                                              # Return that fault was detected
    elif fault_detection_output[0] == ("N" or "n"):               # If output starts with N or n (Not found)
        return "0"                                              # Return that fault was not detected
    return "Error"                                              # Any other option (impossible) - Error


# Function to start foreign Hot spot detection and decode its outputs.
# Possible scan outputs: "Error - <...>", "Hot spot detected", "No hot spots detected"
# Decoded outputs - 1 (for "Hot spot detected"), 0 (for "No hot spots detected") and "Error" for any error.
def start_and_decode_hot_spots_scan():
    ## Hot spots scanning
    fault_detection_output = do_hot_spot_detection()
    print "Output of Hot spot detection is: ", fault_detection_output
    print fault_detection_output[0]
    if fault_detection_output[0] == ("E" or "e"):                 # If output starts with E or e
        return "Error"                                          # Return error
    elif fault_detection_output[0] == ("H" or "h"):               # If output starts with H or h (Hot spot detected)
        return "1"                                              # Return that fault was detected
    elif fault_detection_output[0] == ("N" or "n"):               # If output starts with N or n (No hot spots detected)
        return "0"                                              # Return that fault was not detected
    return "Error"                                              # Any other option (impossible) - Error


# Function to start specific piece of fault detection softaware.
# Output has to be in the form of:  1 (fault detected), 0 (fault not detected) or "error"
# Encoding is: 1-flap position,
# 2 - LED sequence, 3 - coolant valve, 4 - foreign object, 5 - hot spot detection
# 6 - not allocated (possibly QR code scanning or any oter foreign objects, 7 - shut down (not possible)
def initiate_fault_detection(fault_bit):
    # If 1 - detect flap position.
    if fault_bit == 1:
        decoded_detection_output = start_and_decode_orange_flap_scan()   # Start and decode orange flap scan
    # If 2 - detect LED sequence.
    elif fault_bit == 2:
        decoded_detection_output = start_and_decode_LED_sequence_scan()  # Start and decode LED sequence scan
    # If 3 - detect coolant valve handle position.
    elif fault_bit == 3:
        decoded_detection_output = start_and_decode_coolant_valve_scan() # Start and decode coolant valve scan
    # If 4 - run foreign object detection for pre-defined foreign object
    elif fault_bit == 4:
        decoded_detection_output = start_and_decode_foreign_object_scan()# Start and decode foreign object scan
    # If 5 - run hot-spot detection
    elif fault_bit == 5:
        decoded_detection_output = start_and_decode_hot_spots_scan()     # Start and decode hot spots scan
    # If anything else - "Error", because they are not allocated currently
    else:
        print "Message received is invalid"
        decoded_detection_output = "Error"
    return decoded_detection_output                                      # Return the output as "1", "0" or "Error"


# Function to check if message received was in valid format of  0 <= ['fault_bit'] < 8,  0 <= ['stop_bit'] < 2.
def was_meesage_invalid(comms_output):
    if ((0 <= comms_output['fault_bit']) and
            (comms_output['fault_bit'] < 8) and
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
    message_to_comms = {"detection_progress": 0, "fault_result":0, "error": 0}
                                                                # Initialise message_to_comms variable
    repeat = True

    while repeat:                                               # Repeat while it is needed
        wait_for_scan(time_delay)                               # Wait for a given period of time
        comms_output = read_comms_output(I2C_DEVICE_ADDR)       # Get the decoded output of the comms system
                                                                # in format of comms_output
                                                                # ['fault_bit'] ['idle_bit'] ['stop_bit']
        if was_meesage_invalid(comms_output):                   # Check whether message received is valid.
            print "Message received is invalid"
            continue

        if comms_output["stop_bit"] == 1:                       # If stop is set:
            repeat = False                                      # Terminate the software
            continue                                            # Start from the while loop (will get out of it)

        if comms_output["idle_bit"] == 1:                       # If idle is set
            print "Idle mode initiated"         # ONLY FOR DEBBUGING

            message_to_comms["detection_progress"] = 0              # Clear the progress bit
            message_to_comms["fault_result"] = 0                    # Clear result bit
            message_to_comms["error"] = 0                           # Clear error bit
                                                                    # Put the message to comms in propper format for comms
            send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms)# Send the message to communication system

                                                                # If idle == 1
            time_delay = TIME_DELAY_IDLE                        # Set comms frequency to be slower
            continue                                            # Go back to while loop

        time_delay = TIME_DELAY_ACTIVE                          # If stop is not set, scanning frequency increases

        if comms_output["fault_bit"] == 0:                      # If fault detection was not initialised
            continue                                            # Continue from while loop start
                                                                # If fault detection was requested:
        message_to_comms["detection_progress"] = 1              # Set the progress bit
        message_to_comms["fault_result"] = 0                    # Clear result bit
        message_to_comms["error"] = 0                           # Clear error bit
                                                                # Put the message to comms in propper format for comms
        send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms)# Send the message to communication system

        # Start the specific fault detection. Possible outputs - 1 (fault detected), 0 (fault not detected) or "error"
        fault_result = initiate_fault_detection(comms_output["fault_bit"])

        if fault_result == "Error":                              # If result was error
            message_to_comms["detection_progress"] = 0           # Clear the progress bit
            message_to_comms["error"] = 1                        # Set error bit
        else:
            message_to_comms["detection_progress"] = 0           # Clear the progress bit
            message_to_comms["fault_result"] = fault_result      # Select appropriate output
            message_to_comms["error"] = 0                        # Clear error bit

        send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms) # Send the message to communication system

    message_to_comms["detection_progress"] = 1              # Clear the progress bit
    message_to_comms["fault_result"] = 1                    # Clear result bit
    message_to_comms["error"] = 1                           # Clear error bit
                                                            # Put the message to comms in propper format for comms
    send_message_to_comms(I2C_DEVICE_ADDR, message_to_comms)# Send the message to communication system

    print SHUT_DOWN_NOTIFICATION                                 # If got out of loop, print notification


# If called by itself, just so that it does not show error when something is returned
if __name__ == '__main__':
    start_communications()