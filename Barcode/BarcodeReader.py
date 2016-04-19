import csv
from SimpleCV import *


img = Image("QR_code.jpg")
barcode = img.findBarcode()
if barcode: # if we have a barcode
    data = str(barcode.data)
    img.dl().text(data, (img.width/2, img.height/2), color= Color.RED)
else:
    img.dl().text("NOT RECOGNISED", (img.width/2, img.height/2), color= Color.RED)

img.save("QR_Detected") #display