#!/usr/bin/env python3

import sys
import numpy
import cv2

def recognize_circles(p):
    img = cv2.imread(p)
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(imgray, cv2.HOUGH_GRADIENT, 1, 100, param1=50, param2=30, minRadius=270, maxRadius=290)
    circles = numpy.uint16(numpy.around(circles))
    for circle in circles[0,:]:
        cv2.circle(img, (circle[0], circle[1]), circle[2], (0,255,0), 2)
        cv2.circle(img, (circle[0], circle[1]), 2        , (0,0,255), 3)
    cv2.imshow("Detected Circles", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__== "__main__":
    recognize_circles(sys.argv[1])
