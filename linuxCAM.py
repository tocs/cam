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

# starting to learn about the linuxcnc moduel
try:
    s = linuxcnc.stat() # create a connection to the status channel
    s.poll() # get current values
except linuxcnc.error, detail:
    print "error", detail
    sys.exit(1)
toolTable = s.tool_table


# set following parameters
# filename = sys.argv[1]
filename = "/home/tocs/4gary/play/3dSheetCam/cam/NONAME_0.dxf" # Change to your dxf file
# filename = "/home/tocs/4gary/play/3dSheetCam/cam/CTH.dxf" # Change to your dxf file

safeHeight = 0.25 # positive hieghts are above the work piece.
straightFeedRate = 65.0 # set to a resonable feed rate. Inches/Minute



dxf = DXF()
dxf.open(filename)
print "; filename:", dxf.filename


# print initial modal settings and set cut feed rate
print panelHeaderText

feed = FeedRate()
feed.put(60)
print feed.get()
print
print ExitMove(safeHeight).get()

# each dxf entity ("e")  will be an operation (lwpolylines for operations with more than one cut)
# need to make lwpolylines more like other entities
# need to add arc entity
print "; ENTITIES:"

for e in dxf.ENTITIES.data:    # step through each entity (e)
    # for now each operation cuts full depth.
    print "; %s" % e.get("type")

    # Change values to suite your needs. Negative values are generaly below the top of the work piece.
    tool = toolTable[1] 
    startDepth = 0.0
    endDepth = -0.25
    stepDepth = -0.0625
    cutDepths = list(numpy.arange(startDepth, endDepth + stepDepth, stepDepth))
    initMove = e.get()

    # put entry move things here
    startPt = e.get("startPt")
    entry = entryMove()
    if e.get("layer").find("offset") != -1:
        if e.get("layer").find("right") != -1:  
            print "; Right"
            entry.put(startPt, offset = "right", tool = tool, safeHeight = safeHeight)
        elif e.get("layer").find("left") != -1:  
            print "; Left"
            entry.put(startPt, offset = "left", tool = tool, safeHeight = safeHeight)
    else:
        entry.put(startPt, safeHeight = safeHeight)
    print entry.get()
    
    # define cut acording to type of dxf entity
    if (e.type == "Circle") or (e.type == "Arc"):
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

            if (e.type == "Arc") and (d != cutDepths[-1]):
                print ExitMove(safeHeight).get()
                
                line = RapidMotion()
                line.put([e.get("startPt")[0], e.get("startPt")[1], safeHeight])
                print line.get("XYZ")

                line = StraightFeed()
                line.put([0.0, 0.0, d])
                print line.get("Z")
        print ExitMove(safeHeight).get()
            
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
                print ExitMove(safeHeight).get()

                line = RapidMotion()
                line.put([e.get("startPt")[0], e.get("startPt")[1], safeHeight])
                print line.get("XYZ")                
        print ExitMove(safeHeight).get()



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
                if linesArcs.type == "Line":
                    line = StraightFeed()
                    line.put(linesArcs.get("endPt"))
                    line.endPt[2] = d
                    print line.get("XYZ")
                elif linesArcs.type == "Arc":
                    arc = Arc()
                    # start here

                    if linesArcs.get("direction") > 0:
                        direction = "3"
                    else:
                        direction = "2"
                    arc.put(endPt = linesArcs.get("endPt"),
                            startPt = linesArcs.get("startPt"),
                            centerPt = linesArcs.get("centerPt"),
                            direction = direction)
                    arc.endPt[2] = d
                    print arc.get("XYZIJ")

            if (e.get()["closed"] == 0) and (d != cutDepths[-1]):
                    print ExitMove(safeHeight).get()

                    line = RapidMotion()
                    line.put([e.get("startPt")[0], e.get("startPt")[1], safeHeight])
                    print line.get("XYZ")

                    line = StraightFeed()
                    line.put([0.0, 0.0, d])
                    print line.get("Z")
        print ExitMove(safeHeight).get()
    print
# done cutting raise cutter and move to origin
print ExitMove(safeHeight).get()
print Offset("none").get()        
line = RapidMotion()
line.put([0.0, 0.0, safeHeight])
print line.get("XYZ")
print

print EOF





