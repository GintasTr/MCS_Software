import time
from SimpleCV import *

c = Camera(0, {"width": 1024, "height": 768})    # Only for RPI 2592x1944. For calibration - 1024x768
time.sleep(1)
js = JpegStreamer("0.0.0.0:8080")

while(1):
  c.getImage().save(js)
  time.sleep(0.1)