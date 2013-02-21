import numpy

EOF = "M2"

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
        self.startDeptht = 0.0
        self.endDepth = -0.25
        self.cutDepth = 0.0625
        self.toolDia = 0.0
        self.feedRate = 0.0
        self.offset = "G40" # -1 left, 0 none , 1 right (which side of cut tool is on)
        self.cuts = []
        self.onOff = 0

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
        self.direction = "2" # 2 CW , 3 CCW
        self.format = "G%s"
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
if __name__ == "__main__":
    one =  RapidMotion()
    one.put([1.0, 1.0])
    print one.get()

    two = StraightFeed()
    two.put([0.1, 4.4])
    print two.get()
