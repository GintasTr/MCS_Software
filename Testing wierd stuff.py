from SimpleCV import *
import cv2

"""
cam = Camera()
time.sleep(1)
img = cam.getImage()
img = cam.getImage()
display = Display()
#pressed = pg.key.get_pressed()
print "I launched a window"
while display.isNotDone():
    #if(pressed[13] == True): #CODE FOR ESC. CAN BE USED FOR OTHER??
    #    display.done = True

    if display.mouseRight:
        display.done = True
    img.show()
Display().quit()
while True:
    None
"""

""" CODE TO FIND THE PRESSED KEY CODE
import cv2
img = cv2.imread('Lenna.png') # load a dummy image
while(1):
    cv2.imshow('img',img)
    k = cv2.waitKey(33)
    if k==27:    # Esc key to stop
        break
    elif k==-1:  # normally -1 returned,so don't print it
        continue
    else:
        print k # else print its value
"""





cam = Camera()
time.sleep(1)
img = cam.getImage()
img = cam.getImage()

print "In the shown image, left click on the orange flap in the image to calibrate" \
      " its colour and then Escape or Right click to turn off the image"
disp = Display()  # Create a display
while disp.isNotDone(): # Loop until display is not needed anymore
    img.clearLayers()
    if disp.mouseLeft:  #   Show coords on screen
        mouse_coords = [disp.mouseX, disp.mouseY]
        text = "X:" + str(mouse_coords[0]) + " Y:" + str (mouse_coords[1])
        img.dl().text(text, (mouse_coords[0] + 10, mouse_coords[1] + 10), color=Color.RED)
        img.dl().circle((mouse_coords[0], mouse_coords[1]), color = Color.RED, radius = 26)
    if disp.mouseRight: # Turn off the screen
        disp.done = True    # Turn off Display
    img.save(disp)  # Show the image on Display
Display().quit()    # Exit the display so it does not go to "Not responding"