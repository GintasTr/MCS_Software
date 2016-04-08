
class CameraWrapper():


    def __init__(self, cam):
        self.cam = cam

    # Function to get the image from camera
    def GetImage(self):
        img = self.cam.getImage()                                            # Get image from camera
        img = self.cam.getImage()                                            # ONLY FOR LAPTOP DUE TO FRAME BUFFERS?
        img = img.flipHorizontal()                                      # Flip image (has to be tested on PI)
        return img
