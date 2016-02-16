from SimpleCV import *
import cv2
import colorsys
"""
b = np.arange((4*4*3))
b = b.reshape(4,4,3)
print b

avg = np.mean(b[:,:,0])
print avg, "AVG"
d = np.std(b[:,:,0])
print d, "STD"
"""

#CORRECT
img = Image("Cropped.jpg")
#hsv = img.toHSV()

hsv = img.getNumpyCv2()
hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)

print hsv[:,:,0], "HUE"
print hsv[:,:,1], "SAT"

avgHue = np.mean(hsv[:,:,0])
print avgHue, "AVG"

avgSat = np.mean(hsv[:,:,1])
stdSat = np.std(hsv[:,:,1])
minSat = np.min(hsv[:,:,1])
print avgSat, "avgSat"
print stdSat, "stdSat"
print minSat, "minSat"

"""
img = Image("Cropped.jpg")
#hsv = img.toHSV()

hsv = img.getNumpyCv2()
hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)

hsvmean = np.mean(hsv, axis = 0)

print hsv.shape


hsvStd = np.std(hsvmean, axis = 0)
hsvmean = np.mean(hsvmean, axis = 0)
print hsvStd, "STD"
print hsvmean, "mean" #correct

meanHue = hsvmean[0]
meanSat = hsvmean[1]
stdSat = hsvStd[1]

print meanHue
print meanSat
print stdSat

"""
