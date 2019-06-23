#!/usr/bin/env python3

import sys
import cv2 as cv
import numpy

thresholdx = 50

src = cv.imread(cv.samples.findFile(sys.argv[1]))
cv.imshow("Source", src)
src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
_, area = cv.threshold(src_gray, thresholdx, 255, cv.THRESH_BINARY)
# cv.imshow("Active Area", area)
contours, _ = cv.findContours(area, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

areac = numpy.zeros((src.shape[0], src.shape[1], 3), dtype=numpy.uint8)
if not contours is None:
    if len(contours) > 1:
        print("enlarge thresholdx to get only one contour")
    else:
        hull = cv.convexHull(contours[0])
        cv.drawContours(areac, [hull], 0, (255,255,255), thickness=cv.FILLED)

areac_gray = cv.cvtColor(areac, cv.COLOR_BGR2GRAY)
cv.imshow("Convex", areac_gray)

circles = cv.HoughCircles(areac_gray, cv.HOUGH_GRADIENT, 1, 200, param1=100, param2=5, minRadius=65, maxRadius=75)

if not circles is None:
    circles = numpy.uint16(numpy.around(circles))[0,:]
    print("How many circles? %d" %(len(circles)))
    for circle in circles:
        center_x = circle[0]
        center_y = circle[1]
        radius   = circle[2]
        cv.circle(areac, (center_x, center_y), radius, (0,255,0), 1)
        cv.circle(areac, (center_x, center_y), 2, (0,0,255), 3)
    cv.imshow("Detected", areac)
else:
    print("No circle")

cv.waitKey()
