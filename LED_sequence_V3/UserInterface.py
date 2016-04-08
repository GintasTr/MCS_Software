from SimpleCV import *


class UserInterface():

    YES_KEY = "y"

    def __init__(self, cam):
        self.cam = cam

    def GetConfirmation(self, confirmationText):
        while True:                                                     # Loop until valid response
            print confirmationText                                      # Ask for confirmation
            try:                                                        # Catch Index error in case of too fast response
                userInput = raw_input()                                 # Check user input
                userInput = userInput.lower()                           # Make it lower case
                if userInput[0] == UserInterface.YES_KEY:                                 # Check if it is y, n, or something else
                    return True                                         # Return respective values
                elif userInput[0] == "n":
                    return False
            except(IndexError):                                         # In case of Index error (too fast response)
                print "Something is wrong, try again."
            else:
                print "Incorrect value entered."

    # Function for getting the correct image
    def RequestConfirmedImage(self, RequestText, ConfirmationText1, ConfirmationText2, disp):
        confirmation = False                                        # Initialise the confimation loop
        while not confirmation:                                     # Loop until confirmation = True
            raw_input(RequestText)                                  # Show the request to put camera nicely.
            img = self.cam.GetImage()                                        # Get image from camera
            print ConfirmationText1                                 # Ask to close the image and then answer
            disp = Display()
            while disp.isNotDone():                                 # Loop until display is not needed anymore
                if disp.mouseLeft:                                  # Check if left click was used on display
                    disp.done = True                                # Turn off Display
                img.show()                                          # Show the image on Display
            disp.quit()                                        # Exit the display so it does not go to "Not responding"
            confirmation = self.GetConfirmation(ConfirmationText2)       # Ask whether LED was clearly visible and confirm.
        return img

    # Function for getting mLedCoords:
    def GetClickCoords(self, img, RequestText, disp):
        print RequestText                                           # Ask user to click on display
        while disp.isNotDone():                                     # Loop until display is not needed anymore
            img.clearLayers()                                       # Clear old drawings
            if disp.mouseLeft:
                mouse_coords = [disp.mouseX, disp.mouseY]           # Show coords on screen with modifiable square size
                text = "X:" + str(mouse_coords[0]) + " Y:" + str(mouse_coords[1])
                img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color= Color.RED)
                img.dl().centeredRectangle(center = [mouse_coords[0], mouse_coords[1]], color = Color.RED, dimensions = [20,20])
            if disp.mouseRight:                                     # If right clicked
                disp.done = True                                    # Turn off Display
            img.save(disp)                                          # Show the image on Display
        disp.quit()                                            # Exit the display so it does not go to "Not responding"
        return mouse_coords                                         # Return mouseX and mouseY as mouse_coords[0] and [1]

