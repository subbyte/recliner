#!/usr/bin/env python3

""" Automatic Eclipse Photo Alignment for Timelapse
"""

__author__ = "Xiaokui Shu"
__copyright__ = "Copyright 2019, Xiaokui Shu"
__license__ = "Apache"
__version__ = "1.0.0"
__maintainer__ = "Xiaokui Shu"
__email__ = "xiaokui.shu@ibm.com"
__status__ = "Prototype"

import argparse
import os
import magic
import numpy
import cv2
import time
import multiprocessing.pool
import operator
import collections

default_hough_param1 = 100
default_hough_param2 = 30
default_min_distance_between_circles = 600
default_min_radius = 275
default_max_radius = 290
default_output_canvas_width = -1
default_output_canvas_height = -1
default_output_resize_ratio = 1

debug_mode = False

def retrieve_photo_paths (d, r):
    ps = []
    for root, dirs, files in os.walk (d):
        if root == d or root + "/" == d or r:
            for f in files:
                p = os.path.join(root, f)
                if "jpeg" in magic.detect_from_filename(p).mime_type:
                    ps.append (p)
    return ps

def calculate_min_length_to_edge (c, img):
    x, y = c
    width = img.shape[1]
    height = img.shape[0]
    mle = -1
    if x > 0 and y > 0 and width > x and height > y:
        mle = min (x, y, width - x, height - y)
    return mle

def gen_detect_sun (cirD, minR, maxR, houghparam1, houghparam2, is_dryrun, ddir):
    def detect_sun (p):
        pb = os.path.basename(p)
        print("[Info] processing %s ..." % (pb))
        img = cv2.imread(p)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles (img_gray
                                   ,cv2.HOUGH_GRADIENT
                                   ,1
                                   ,cirD
                                   ,param1=houghparam1
                                   ,param2=houghparam2
                                   ,minRadius=minR
                                   ,maxRadius=maxR
                                   )
        if not circles is None:
            circles = numpy.uint16(numpy.around(circles))[0,:]
            if len(circles) > 1:
                print("[Warning] %d Sun detected in photo %s\nConsider rerun with different parameters, especially larger CIRD." % (len(circles[0,:]), p))
            else:
                sun_circle   = circles[0]
                sun_center_x = sun_circle[0]
                sun_center_y = sun_circle[1]
                sun_radius   = sun_circle[2]
                if is_dryrun:
                    if debug_mode:
                        print("[Info] %s: Sun center (%d, %d), radius %d." % (sun_center_x, sun_center_y, sun_radius))
                    cv2.circle(img, (sun_center_x, sun_center_y), sun_radius, (0,255,0), 2)
                    cv2.circle(img, (sun_center_x, sun_center_y), 2, (0,0,255), 3)
                    po = os.path.join(ddir, pb)
                    cv2.imwrite(po, img)
            mle = calculate_min_length_to_edge((sun_center_x, sun_center_y), img)
            return p, sun_radius, (sun_center_x, sun_center_y), mle
        else:
            print("[Warning] no Sun detected in photo %s\nConsider rerun with different parameters." % (p))
    return detect_sun

def gen_align_sun (fp_detect_sun, ddir, ocw, och, r):
    def align_sun (p):
        pb = os.path.basename(p)
        sun = fp_detect_sun(p)
        if sun:
            _, _, (x, y), mle = sun
            charray = [mle]
            charray.extend([] if ocw<0 else [ocw//2])
            charray.extend([] if och<0 else [och//2])
            ch = min(charray)
            w = ocw if ocw>0 else mle*2
            h = och if och>0 else mle*2
            img = cv2.imread(p)
            suncrop = img[y-ch:y+ch, x-ch:x+ch]
            ch_r = int(ch*r)
            sunresize = cv2.resize(suncrop, (ch_r*2, ch_r*2))
            imgo = numpy.zeros((h,w,3), numpy.uint8)
            imgo[h//2-ch_r:h//2+ch_r, w//2-ch_r:w//2+ch_r] = sunresize[:,:]
            po = os.path.join(ddir, pb)
            cv2.imwrite(po, imgo)
    return align_sun

def main ():
    parser = argparse.ArgumentParser(description="Recognize, crop and align the Sun (normal Sun, partial/total eclipse) in photos (jpeg).")
    parser.add_argument("sdir", metavar="SDIR", help="source directory of eclipse photos")
    parser.add_argument("ddir", metavar="DDIR", help="destination directory to write the output")
    parser.add_argument("-r", "--recursive", help="load photos in subdirectories recursively", action="store_true")
    parser.add_argument("-d", "--dryrun", help="only try to recognize the Sun, output green circles on photos to DDIR, not align photos", action="store_true")
    parser.add_argument("--circlediff", metavar="CIRD", help="Int: minimal distance (pixels) between detected circles", default=default_min_distance_between_circles, type=int)
    parser.add_argument("--minradius", metavar="MINR", help="Int: minimal radius (pixels) of the Sun for detection", default=default_min_radius, type=int)
    parser.add_argument("--maxradius", metavar="MAXR", help="Int: maximum radius (pixels) of the Sun for detection", default=default_max_radius, type=int)
    parser.add_argument("--houghparam1", metavar="HPM1", help="Int: param1 in HoughCircles()", default=default_hough_param1, type=int)
    parser.add_argument("--houghparam2", metavar="HPM2", help="Int: param2 in HoughCircles()", default=default_hough_param2, type=int)
    parser.add_argument("--outputwidth", metavar="OCW", help="Int: output canvas width", default=default_output_canvas_width, type=int)
    parser.add_argument("--outputheight", metavar="OCH", help="Int: output canvas height", default=default_output_canvas_height, type=int)
    parser.add_argument("--outputresize", metavar="R", help="Float: output resize ratio in (0, 1]", default=default_output_resize_ratio, type=float)

    args = parser.parse_args()
    try:
        os.mkdir(args.ddir)
    except FileExistsError:
        print("[Error] %s exists, please choose a new one." % (args.ddir))
    except FileNotFoundError:
        print("[Error] oops, recliner does not do `mkdir -p`, specify DDIR under existing path.")
    else:
        photos = retrieve_photo_paths(args.sdir, args.recursive)
        if photos:
            func_rcg_sun = gen_detect_sun(args.circlediff, args.minradius, args.maxradius, args.houghparam1, args.houghparam2, args.dryrun, args.ddir)
            if args.dryrun:
                with multiprocessing.pool.ThreadPool() as workers:
                    results = workers.map(func_rcg_sun, photos)
                results = list(filter(None, results))
                radiuses = list(map(operator.itemgetter(1), results))
                if radiuses:
                    print("[Info] radiuses detected for tuning parameters in the next run:")
                    for k, v in collections.Counter(radiuses).items():
                        print("radius: %d pixels, count: %d" % (k, v))
                        if v <= 5:
                            for p, r, _, _ in results:
                                if r == k:
                                    print("- " + p)
                    print("[Info] circle center to edge (pixels):")
                    mles = list(map(operator.itemgetter(3), results))
                    mles.sort()
                    print(mles)
                else:
                    print("[Error] no Sun found in any photos")
            else:
                func_align_sun = gen_align_sun(func_rcg_sun, args.ddir, args.outputwidth, args.outputheight, args.outputresize)
                with multiprocessing.pool.ThreadPool() as workers:
                    workers.map(func_align_sun, photos)
        else:
            print("[Error] no JPEG file found in %s" % (args.sdir))

if __name__== "__main__":
    main()
