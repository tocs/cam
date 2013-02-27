import numpy, os, sys

# http://gnipsel.com/linuxcnc/gui/gui03b.html
# set up paths to files
#BASE = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
BASE = "/home/tocs/Desktop/git/linuxcnc"
libdir = os.path.join(BASE, "lib", "python")
sys.path.insert(0, libdir)
datadir = os.path.join(BASE, "share", "linuxcnc")
xmlname = os.path.join(datadir,"gui3.glade")

import linuxcnc

EOF = "M2"
# the panel header text is temporary stuff that goes at the top of the NGC file.
# it will be handeled better in the Panel class later.
panelHeaderText = """; Modal settings
G17	  ;XY plane
G20	  ;inch mode
G40	  ;cancel diameter compensation
G49	  ;cancel length offset
G54	  ;coordinate system 1
G80	  ;cancel motion
G90 F#1	  ;non-incremental motion
"""


class Panel(object):
    def __init__(self):
        self.safeHeight = 0.025
        self.operations = []
        self.onOff = 0
        
    def loadDXF(self, filename):
        """get all the separate objects in dxf and make an
        operation out of each one"""
        DXF = DXF()
        DXF.open(filename)

class Operation(object):
    # made up of cut objects
    # tool
    # offset
    # cut direction
    # init position
    # entry
    # cuts
    #    rapid motion
    #    straight feed
    #    arc
    # tabs
    # exit
    def __init__(self):
        self.name = ""
        self.safeHeight = 0.25
        self.startDepth = 0.0
        self.endDepth = -0.25
        self.cutDepth = -0.0625
        self.cutDepths = list(numpy.arange(self.startDepth, self.endDepth + self.cutDepth, self.cutDepth))

        self.startPt = None
        self.endPt = None
        
        self.entry = None
        self.exit = None

        self.tool = None
        self.straightFeedRate = 0.0
        self.plungeFeedRate = 0.0        
        self.offset = Offset("none") # -1 left, 0 none , 1 right (which side of cut tool is on)
        self.cuts = []
        self.onOff = 1
    def setCutDepths(self, lst = None):
        if lst:
            cutDepths = lst
        else:
            cutDepths = list(numpy.arange(self.startDepth, self.endDepth + self.cutDepth, self.cutDepth))
    def put(self, name = None, safeHeight = None, startDepth = None, endDepth = None, cutDepth = None,
               tool = None, startPt = None, offset = None, endPt = None):
        if name != None:
            self.name = name
        if safeHeight != None:
            self.safeHeight = safeHeight
        if startDepth != None:
            self.startDepth = startDepth
        if endDepth != None:
            self.endDepth = endDepth
        if cutDepth != None:
            self.cutDepth
        if tool != None:
            self.tool = tool
        if startPt != None:
            self.startPt = startPt
        if endPt != None:
            self.endPt
        if startDepth or endDepth or cutDepth:
            pass
        if startPt != None or (endDepth != None):
            entry = entryMove()
            if e.get("layer").find("offset") != -1:
                if e.get("layer").find("right") != -1:  
                    entry.put(startPt, offset = "right", tool = tool, safeHeight = safeHeight)
                elif e.get("layer").find("left") != -1:  
                    entry.put(startPt, offset = "left", tool = tool, safeHeight = safeHeight)
                else:
                    entry.put(startPt, safeHeight = safeHeight)
        print entry.get()
    
    def addCut(self):
        pass
class Cut(object):
    def __init__(self):
        self.onOff = 0
        self.endPt = [0.0, 0.0, 0.0]
        self.formatX = " X %f"
        self.formatY = " Y %f"
        self.formatZ = " Z %f"
    def flat_to3D(self, l):
        if len(l) == 2:
            l.append(0)
        return(l)
    def get(self, axis = "XYZ"):
        line = self.format
        if axis.find("X") != -1:
            line = line + self.formatX % self.endPt[0]
        if axis.find("Y") != -1:        
            line = line + self.formatY % self.endPt[1]
        if axis.find("Z") != -1:            
            line = line + self.formatZ % self.endPt[2]
        line = self.getMore(axis, line)
        return(line)
    def getMore(self, axis, line):
        return(line)
        
class RapidMotion(Cut):
    def __init__(self):
        Cut.__init__(self)
        self.format = "G0"
        self.comment = " ; "
    def put(self, endPt):
        self.endPt = self.flat_to3D(endPt)

class StraightFeed(Cut):
    def __init__(self):
        Cut.__init__(self)
        self.format = "G1"
        self.comment = " ; "
    def put(self, endPt):
        self.endPt = self.flat_to3D(endPt)        

                
class Arc(Cut):
    def __init__(self):
        Cut.__init__(self)        
        self.format = "G%s"
        self.direction = "2" # 2 CW , 3 CCW        
        self.formatI = " I %f"
        self.formatJ = " J %f"
        self.formatK = " K %f"
        self.offset = [0.0, 0.0, 0.0]
        self.comment = " ; "        
    def put(self, endPt = None, offset = None, 
            startPt = None, centerPt =None, direction = None):
        self.endPt = self.flat_to3D(endPt)
        if offset:
            self.offset = self.flat_to3D(offset)
        if (centerPt != None) and (startPt != None):
            self.offset = numpy.array(self.flat_to3D(centerPt)) - numpy.array(self.flat_to3D(startPt))
        if direction:
            self.direction = direction
    def putStartCenter(self, startPt, centerPt):
        startPt = numpy.array(flat_to3D(startPt))
        centerPt = numpy.array(flat_to3D(centerPt))
        self.offset = centerPt = startPt
    def putDirection(self, d):
        self.direction = str(d)
    def getMore(self, axis, line):
        line = line % self.direction
        if axis.find("I") != -1:
            line = line + self.formatI % self.offset[0]
        if axis.find("J") != -1:
            line = line + self.formatJ % self.offset[1]
        if axis.find("K") != -1:
            line = line + self.formatK % self.offset[2]
        return(line)


# Other G code objects
# feed rate
class FeedRate(object):
    def __init__(self):
        self.format = "G94 F%f	  ;feed/minute mode"
        self.feedRate = 35
    def put(self, rate):
        self.feedRate = rate
    def get(self):
        line = self.format % self.feedRate
        return(line)

class ExitMove(RapidMotion):
    def __init__(self, height):
        RapidMotion.__init__(self)
        self.endPt = [0.0, 0.0, height]
    def get(self, axis = "Z"):
        line = self.format
        if axis.find("X") != -1:
            line = line + self.formatX % self.endPt[0]
        if axis.find("Y") != -1:        
            line = line + self.formatY % self.endPt[1]
        if axis.find("Z") != -1:            
            line = line + self.formatZ % self.endPt[2]
        line = self.getMore(axis, line)
        return(line)


class Offset(object):
    def __init__(self, offsetType, tool = None):
        """offset types:
        right
        left
        none"""
        
        self.offsetType = offsetType
        if tool != None:
            self.tool = tool
        else:
            self.tool = 0
        
    def get(self):
        if self.offsetType == "none":
            off = "G40"
        elif self.offsetType == "left":                            
            off = "G41 D%i ; left offset" % self.tool
        elif self.offsetType == "right":
            off = "G42 D%i ; right offset" % self.tool

        return(off)
        
class entryMove(object):
    def __init__(self):
        self.startPt = None 
        self.tool = None
        self.toolID = None
        self.toolDia = None
        self.offset = Offset("none")
        self.safeHeight = None
    def put(self, startPt = None, tool = None, offset = None, safeHeight = None):
        if startPt != None:
            self.startPt = startPt
        if safeHeight != None:
            self.safeHeight = safeHeight
        if offset != None and tool != None:
            self.tool = tool
            self.toolID = tool.id
            self.toolDia = numpy.array([tool.diameter, tool.diameter, 0])
            self.offset = Offset(offsetType = offset, tool = tool.id)
        
    def get(self):
        # calc start
        # moveto xy offset safe
        # offset
        # start xy safe
        # z
        move = ""
        offsetStart = RapidMotion()
        if (self.offset != None) and (self.offset.offsetType) != "none":
            offsetPt = numpy.array(self.startPt)
            offsetPt[2] = self.safeHeight
            offsetPt = offsetPt + self.toolDia 
            offsetStart.put(offsetPt)
            move = move + offsetStart.get() + "\n"
            move = move + self.offset.get() + "\n"
        else:
            offsetPt = numpy.array(self.startPt)
            offsetPt[2] = self.safeHeight
            offsetStart.put(offsetPt)
            move = move + offsetStart.get() + "\n"
            move = move + "G40\n"

        offsetStart.put(endPt = self.startPt)
        move = move + offsetStart.get()



        
        return(move)
if __name__ == "__main__":
    one =  RapidMotion()
    one.put([1.0, 1.0])
    print one.get()

    two = StraightFeed()
    two.put([0.1, 4.4])
    print two.get()
