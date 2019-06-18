# Eclipse Photo Alignment for Timelapse

The Sun/Moon moves during an eclipse. If you do not have a tracker but have hundreds of photos with the Sun/Moon at all places, you may want a tool to align the Sun/Moon (and partial Sun/Moon) for creating a timelapse. This is the tool to do it.

### The Challenge

Object recognition is not enough. Finding the smallest contour works for the full Sun/Moon, but it does not help to align the partial Sun/Moon. All photos should be aligned at the center of the full/partial Sun/Moon. The only solution is to embed the knowledge into the program that the object it tries to recognize is part of a circle. The program should try to match the full/partial edge of a circle, and derive the center and radius of the circle.

Even assuming the contrast of the photo is good and the program can recognize a circle based on part of its edge, the program may find two circles in the instance of a solar eclipse -- one for the Sun (yellow region) and one for the Moon (blackout region). We need to tell the program to only return the one we need.

### The Magic Employed by recliner

1. cv::HoughCircles() in openCV

2. parameters tuning based on your photos

### How to Use recliner

1. export your photos (containing only the Sun/Moon) into a directory.

2. estimate the radius of the Sun/Moon in pixel.

3. run `./recliner -d --minradius MINR --maxradius MAXR SDIR DDIR` It will output the circle recognition results in `DDIR` with green circle and red center dot. recliner will output suggestions if any to fine-tune the parameters.

4. rerun recliner with tuned parameters.

5. when you are satisfied with the recognition results, run `./recliner --outputwidth=1920 --outputheight=1080 SDIR DDIR` to output to fullHD photos. If the Sun/Moon is too large, run with `--outputresize=0.5`.
