import numpy, sys
from simpleDXFlib import *
from simpleCAMlib02 import *
# these comments are just some notes for me
# operations
# entry
#   move to start XY
#   move down to first cut Z
# depths
# cuts
#     bulk
#     tabs
# exit

# Print sort of a header

# set following parameters
# filename = sys.argv[1]
filename = "/home/tocs/4gary/play/cam/CTH.dxf" # Change to your dxf file
safeHeight = 0.25 # positive hieghts are above the work piece.
straightFeedRate = 65.0 # set to a resonable feed rate. Inches/Minute

dxf = DXF()
dxf.open(filename)
print "; filename:", dxf.filename


# print initial modal settings and set cut feed rate
print """
; Modal settings
G17	  ;XY plane
G20	  ;inch mode
G40	  ;cancel diameter compensation
G49	  ;cancel length offset
G54	  ;coordinate system 1
G80	  ;cancel motion
G90 F#1	  ;non-incremental motion
G94 F%f	  ;feed/minute mode

G0 Z %f   ;move to safe height
""" % (straightFeedRate, safeHeight)


# each dxf entity ("e")  will be an operation (lwpolylines for operations with more than one cut)
# need to make lwpolylines more like other entities
# need to add arc entity
print "; ENTITIES:"

for e in dxf.ENTITIES.data:    # step through each entity (e)
    # for now each operation cuts full depth.
    # for now now cutter offset
    # ui should allow for changes in depth and deal with such things as pockets, offsets, tool diameter, ect

    # Change values to suite your needs. Negative values are generaly below the top of the work piece.
    startDepth = 0.0
    endDepth = -0.25
    stepDepth = -0.0625
    cutDepths = numpy.arange(startDepth, endDepth + stepDepth, stepDepth)    
    initMove = e.get()

    # initial cutter position
    line = RapidMotion()
    line.put([0.0, 0.0, safeHeight])
    print line.get("Z")

    line = RapidMotion()
    line.put([e.get("startPt")[0], e.get("startPt")[1], safeHeight])
    print line.get("XYZ")    

    # define cut acording to type of dxf entity
    if e.type == "Circle":
        for d in cutDepths:
            # all the circle are going to be cut counter clock wise for now
            # move to Z depth
            line = StraightFeed()
            line.put([0.0, 0.0, d])
            print line.get("Z")
            # cut circle
            arc = Arc()
            e.endPt[2] = d # set the dxf ent Z value
            arc.put(endPt = e.get("endPt"),
                    startPt = e.get("startPt"),
                    centerPt = e.get("centerPt"),
                    direction = "3")
            print arc.get("XYZIJ")
            
    if e.type == "Line":
        # cut from startPt to endPt, 
        # raise cutter and move back to start pt (always same cut direction to lessen cutter offset issues)
        for d in cutDepths:
            # move to Z depth
            line = StraightFeed()
            line.put([0.0, 0.0, d])
            print line.get("Z")
            # cut line
            straightFeed = StraightFeed()
            pt = e.get("endPt")[0:2] + [d] # set the dxf ent Z value
            straightFeed.put(pt)
            print straightFeed.get()
            if d != cutDepths[-1]:
                # raise cutter and move to next start point
                line = StraightFeed()
                line.put([0.0, 0.0, safeHeight])
                print line.get("Z")

                line = RapidMotion()
                line.put([e.get("startPt")[0], e.get("startPt")[1], safeHeight])
                print line.get("XYZ")                

                line = StraightFeed()
                line.put([0.0, 0.0, d])
                print line.get("Z")


    if e.type == "LWPolyline":
        # right now LWPolyline behave diferently that other ents
        # will change from dealing with separate verts to line and arc ents
        # move to Z depth
        for d in cutDepths:
            line = StraightFeed()
            line.put([0.0, 0.0, d])
            print line.get("Z")
            # check type of vert and cut section of polyline (will change from cutting verts to cutting lines and arcs)
            for linesArcs in e.asLinesArcs():
                if linesArcs[0] == "LINE":
                    line = StraightFeed()
                    line.put([linesArcs[2][0], linesArcs[2][1], d])
                    print line.get("XYZ")
                elif linesArcs[0] == "ARC":
                    arc = Arc()
                    linesArcs[2][2] = d
                    linesArcs[1][2] = d
                    linesArcs[3][2] = d
                    e.endPt[2] = d # set the dxf ent Z value
                    if linesArcs[4] > 0:
                        direction = "3"
                    elif linesArcs[4] < 0:
                        direction = "2"

                    arc.put(endPt = linesArcs[2][0 : 3],
                            startPt = linesArcs[1][0 : 3],
                            centerPt = linesArcs[3][0 : 3],
                            direction = direction)
                    print arc.get("XYZIJ")

            if (e.get()["closed"] == 0) and (d != cutDepths[-1]):
                    line = RapidMotion()
                    line.put([0.0, 0.0, safeHeight])
                    print line.get("Z")

                    line = RapidMotion()
                    line.put([e.get("startPt")[0], e.get("startPt")[1], safeHeight])
                    print line.get("XYZ")

                    line = StraightFeed()
                    line.put([0.0, 0.0, d])
                    print line.get("Z")
    print
# done cutting raise cutter and move to origin
line = RapidMotion()
line.put([0.0, 0.0, safeHeight])
print line.get("Z")    
print line.get("XYZ")    
print

print EOF
