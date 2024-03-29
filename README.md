# Robust Eclipse Photo Alignment for Timelapse

The Sun/Moon moves during an eclipse. If you do not have a tracker but have hundreds of photos with the Sun/Moon at all places, you may want a tool to align the Sun/Moon (and partial Sun/Moon) for creating a timelapse. This is the tool to do it. And it parallelizes photo processing on multi-core CPUs (one image per core).

![Circle Original 1][o1]
![Circle Origianl 2][o2]
![Circle Original 3][o3]
![Circle Original 4][o4]

![Circle Edge 1][e1]
![Circle Edge 2][e2]
![Circle Edge 3][e3]
![Circle Edge 4][e4]

![Circle Recognition 1][r1]
![Circle Recognition 2][r2]
![Circle Recognition 3][r3]
![Circle Recognition 4][r4]

### How to Use recliner

1. export your photos (containing only the Sun/Moon) into a directory.

2. estimate the radius of the Sun/Moon in pixel.

3. run `./recliner -a --minradius MINR --maxradius MAXR SDIR DDIR` It will output the edge and circle recognition results in `DDIR` with green circle and red center dot. recliner will output suggestions if any to fine-tune the parameters.

4. rerun recliner with tuned parameters iteratively.

5. when you are satisfied, run `./recliner --outputwidth=1920 --outputheight=1080 SDIR DDIR` to output photos on Full HD canvas. The Sun/Moon will be aligned at the center.

[o1]: analyzed/01.jpg
[o2]: analyzed/02.jpg
[o3]: analyzed/03.jpg
[o4]: analyzed/04.jpg
[e1]: analyzed/01.edges.jpg
[e2]: analyzed/02.edges.jpg
[e3]: analyzed/03.edges.jpg
[e4]: analyzed/04.edges.jpg
[r1]: analyzed/01.circles.jpg
[r2]: analyzed/02.circles.jpg
[r3]: analyzed/03.circles.jpg
[r4]: analyzed/04.circles.jpg
