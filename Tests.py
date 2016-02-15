from SimpleCV import *
import cv2
import colorsys

img = Image("Cropped.jpg")
#hsv = img.toHSV()

hsv = img.getNumpyCv2()
hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)
print hsv

hsvmean = np.mean(hsv, axis = 0)
hsvStd = np.std(hsv, axis = 0)

print hsvmean
print hsvStd


hsvStd = np.std(hsvStd, axis = 0)
hsvmean = np.mean(hsvmean, axis = 0)

print hsvStd
print hsvmean

meanHue = hsvmean[0]
meanSat = hsvmean[1]
stdSat = hsvStd[1]

print meanHue
print meanSat
print stdSat