import copy, numpy, os, sys
from simpleDXFlib import getDist, getAngle, getIncludedAngle

EOF = "M2"
class tool_result(object):
    """Meant to be like the linixcnc tool_result class. Needs work
    Would rather use linuxcnc but I do not want to have to deal with
    path information and have linixcnc running to do so."""
    def __init__(self):
        self.id = 1
        self.yoffset=0.0
        self.zoffset=0.0
        self.aoffset=0.0
        self.boffset=0.0
        self.coffset=0.0
        self.uoffset=0.0
        self.voffset=0.0
        self.woffset=0.0
        self.diameter=0.125
        self.frontangle=0.0
        self.backangle=0.0
        self.orientation=0    
    def __getitem__(self):
        return(self)

class FeedRate(object):
    def __init__(self):
        self.format = "G94 F%f	  ;feed/minute mode"
        self.feedRate = 35
    def put(self, rate):
        self.feedRate = rate
    def get(self):
        line = self.format % self.feedRate
        return(line)


class Cut(object):
    def __init__(self):
        self.onOff = 0
        self.startPt = None
        self.endPt = None
        self.formatX = " X %f"
        self.formatY = " Y %f"
        self.formatZ = " Z %f"
        self.axis = "XYZ"
        self.dims = None
    def flat_to3D(self, l):
        if len(l) == 2:
            l.append(0)
        return(l)
    def get(self, axis = None):
        if axis == None:
            axis = self.axis
        """Returns G code.
        axis : returns G code axis 
               "X" : only X axis
               "XY" : only XY axis
               ect."""
        line = self.format
        if axis.find("X") != -1:
            line = line + self.formatX % self.endPt[0]
        if axis.find("Y") != -1:        
            line = line + self.formatY % self.endPt[1]
        if axis.find("Z") != -1:            
            line = line + self.formatZ % self.endPt[2]
        line = self.getMore(axis, line)
        return(line)
    def put(self, endPt = None, startPt = None, dims = None):
        if endPt != None:
                self.endPt = self.flat_to3D(endPt)        
        if startPt != None:
                self.startPt = self.flat_to3D(startPt)            
        if dims:
                self.dims = dims
    def getMore(self, axis, line):
        return(line)
                        
class RapidMotion(Cut):
    def __init__(self):
        Cut.__init__(self)
        self.type = "rapidMotion"
        self.format = "G0"
        self.comment = " ; "


class StraightFeed(Cut):
    """G1 operations"""
    def __init__(self):
        Cut.__init__(self)
        self.type = "straightFeed"
        self.format = "G1"
        self.comment = " ; "


                
class Arc(Cut):
    def __init__(self):
        Cut.__init__(self)  
        self.type = "arc"      
        self.format = "G%s"
        self.startPt = None
        self.endPt = None
        self.centerPt = None
        self.direction = "2" # 2 CW , 3 CCW        
        self.formatI = " I %f"
        self.formatJ = " J %f"
        self.formatK = " K %f"
        self.offset = [0.0, 0.0, 0.0]
        self.radius = None
        self.axis = "XYZIJ"
        self.comment = " ; "        
    def put(self, endPt = None, offset = None, startPt = None, centerPt =None, direction = None):
        if endPt != None:
                self.endPt = self.flat_to3D(endPt)
        if startPt != None:
            self.startPt = self.flat_to3D(startPt)
        if offset:
            self.offset = self.flat_to3D(offset)
        if (centerPt != None) and (startPt != None):
            self.offset = numpy.array(self.flat_to3D(centerPt)) - numpy.array(self.flat_to3D(startPt))
            self.centerPt = numpy.array(self.startPt) + numpy.array(self.offset)
            self.radius = getDist(self.startPt, self.centerPt)
        if direction:
            self.direction = direction
    def getMore(self, axis, line):
        line = line % self.direction
        if axis.find("I") != -1:
            line = line + self.formatI % self.offset[0]
        if axis.find("J") != -1:
            line = line + self.formatJ % self.offset[1]
        if axis.find("K") != -1:
            line = line + self.formatK % self.offset[2]
        return(line)

class Offset(object):
    def __init__(self, offsetType, tool = None, shape = None):
        """offset types:
        right
        left
        none"""        
        self.offsetType = offsetType
        if tool != None:
            self.tool = tool
        else:
            self.tool = 0
        if shape != None:
            self.shape = shape
    def get(self):
        if (self.offsetType == "none") or (self.offsetType == None):
            off = "G40"
        elif self.offsetType == "left":                            
            off = "G41 D%i ; left offset" % self.tool
        elif self.offsetType == "right":
            off = "G42 D%i ; right offset" % self.tool
        return(off)


class Entry(object):
    def __init__(self):
        self.offset = None
        self.tool = None
        self.inside = None
    def put(self, cut = None, safeHeight = None, offset = None, tool = None, inside = None):
        """offset and tool optional"""
        if cut != None:
            self.cut = cut
        if safeHeight != None:
            self.safeHeight = safeHeight
        if offset != None:
            self.offset = Offset(offsetType = offset, tool = tool.id)
            if cut.type == "straightFeed":
                dist = getDist(self.cut.startPt, self.cut.endPt)
                self.offsetVector = -1 * numpy.array([(self.cut.endPt[0] - self.cut.startPt[0]) / dist,
                                                      (self.cut.endPt[1] - self.cut.startPt[1]) / dist,
                                                      0])
            elif cut.type == "arc":
                dist = getDist(self.cut.startPt, self.cut.endPt)
                self.offsetVector = -1 * numpy.array([-1 * (self.cut.startPt[1] - self.cut.centerPt[1]) / dist,
                                                      (self.cut.startPt[0] - self.cut.centerPt[0]) / dist,
                                                      0])

        if tool != None:
            self.tool = tool
        if self.tool != None:
            self.toolDiaOffset = [tool.diameter, tool.diameter, 0]
        else:
            self.toolDiaOffset = [0, 0, 0]

    def get(self):
        if self.offset == None:
            xySafe = list(self.cut.startPt)
            xySafe[2] = self.safeHeight
            one = RapidMotion()
            one.put(endPt = xySafe)
            two = RapidMotion()
            two.put(endPt = [None, None, self.cut.startPt[2]])
            entryMove = one.get() + "\n"
            entryMove = entryMove + two.get("Z")
        else:
            xySafe = numpy.array(self.cut.startPt) + (numpy.array(self.toolDiaOffset) * self.offsetVector)
            xySafe[2] = self.safeHeight
            one = RapidMotion()
            one.put(endPt = xySafe)
            two = self.offset.get()
            xySafe = list(self.cut.startPt) 
            xySafe[2] = self.safeHeight

            three = RapidMotion()
            three.put(endPt = xySafe)
            four = RapidMotion()
            four.put(endPt = [None, None, self.cut.startPt[2]])
            entryMove = one.get() + "\n"
            entryMove = entryMove + two + "\n"
            entryMove = entryMove + three.get() + "\n"
            entryMove = entryMove + four.get("Z")
            
        return(entryMove)
        # safeHeight move to start XY + offset
        # offset G code
        # safeHeight move to start XY
        # Z move to start of cut

class Exit(object):
    def __init__(self):
        self.offset = None
        self.tool = None
        self.inside = None
    def put(self, cut = None, safeHeight = None, offset = None, tool = None, inside = None):
        """offset and tool optional"""
        if cut != None:
            self.cut = cut
        if safeHeight != None:
            self.safeHeight = safeHeight
        if offset != None:
            self.offset = Offset(offsetType = offset, tool = tool.id)
            if cut.type == "straightFeed":
                dist = getDist(self.cut.startPt, self.cut.endPt)
                self.offsetVector = -1 * numpy.array([(self.cut.endPt[0] - self.cut.startPt[0]) / dist,
                                                      (self.cut.endPt[1] - self.cut.startPt[1]) / dist,
                                                      0])
            if cut.type == "arc":
                dist = getDist(self.cut.startPt, self.cut.endPt)
                self.offsetVector = -1 * numpy.array([(self.cut.endPt[0] - self.cut.startPt[0]) / dist,
                                                      (self.cut.endPt[1] - self.cut.startPt[1]) / dist,
                                                      0])
                
        if tool != None:
            self.tool = tool
        if self.tool != None:
            self.toolDiaOffset = [tool.diameter, tool.diameter, 0]
        else:
            self.toolDiaOffset = [0, 0, 0]
            
    def get(self):
        if self.offset == None:
            two = RapidMotion()
            two.put(endPt = [None, None, self.safeHeight])
            exitMove = two.get("Z")
        else:
            xySafe = numpy.array(self.cut.startPt) + (numpy.array(self.toolDiaOffset) * self.offsetVector)
            if self.cut.type == "straightFeed":
                one = StraightFeed()
                one.put(startPt = self.cut.startPt, endPt = self.cut.endPt)
                exitMove = one.get() + "\n"
            else:
                one = Arc()
                one.put(startPt = self.cut.startPt, endPt = self.cut.endPt, 
                        centerPt = self.cut.centerPt, direction = self.cut.direction)                
                exitMove = one.get() + "\n"
            two = RapidMotion()
            two.put(endPt = [0.0,0.0, self.safeHeight])

            exitMove = exitMove + two.get("Z")

        return(exitMove)

class Operation(object):
    def __init__(self):
        self.cuts = []
        self.name = None
        self.safeHeight = None
        self.offset = None
        self.tool = None
    def putCut(self, cut):
        self.cuts.append(cut)
    def get(self):
        # entry
        if self.name:
            ops = "; %s\n" % self.name
        else:
            ops = ""
        cuts = list(self.cuts) # make a temp copy to modify
        # start op in center of first cut (if closed shape)
        if cuts[0].startPt == cuts[-1].endPt:
         if cuts[0].type == "straightFeed":
             mid = (numpy.array(cuts[0].startPt) + numpy.array(cuts[0].endPt)) / 2
             endCut = copy.copy(cuts[0])
             endCut.put(endPt = mid)
             cuts[0].put(startPt = mid)
             cuts.append(endCut)
         elif cuts[0].type == "arc":
             a = getIncludedAngle(startPt = cuts[0].startPt,
                                  endPt = cuts[0].endPt,
                                  centerPt = cuts[0].centerPt)
             startAngle = getAngle(startPt = cuts[0].startPt,
                                   centerPt = cuts[0].centerPt)
             midAngle = (startAngle + (a / 2)) % 360
             midX = cuts[0].radius * numpy.cos(numpy.radians(midAngle))
             midY = cuts[0].radius * numpy.sin(numpy.radians(midAngle))
             midPt = copy.copy(cuts[0].centerPt)
             midPt[0] = midPt[0] + midX
             midPt[1] = midPt[1] + midY
             lastCut = copy.copy(cuts[0])
             lastCut.put(startPt = cuts[0].startPt, endPt = midPt, centerPt = cuts[0].centerPt, direction = cuts[0].direction)
             cuts[0].put(startPt = midPt, endPt = cuts[0].endPt, centerPt = cuts[0].centerPt, direction = cuts[0].direction)
             cuts.append(lastCut)


        
        entry = Entry()
        exit = Exit()
        if self.offset:
            entry.put(cut = cuts[0], safeHeight = self.safeHeight, 
                      offset = self.offset, tool = self.tool)
            exit.put(cut = cuts[-1], safeHeight = self.safeHeight, 
                      offset = self.offset, tool = self.tool)
        else:
            entry.put(cut = self.cuts[0], safeHeight = self.safeHeight)
            exit.put(cut = self.cuts[0], safeHeight = self.safeHeight)
        ops = ops + entry.get() + "\n"

        if self.offset:
            for c in cuts[0 : -1]:
                ops = ops + c.get() + "\n"
        else:
            for c in cuts:
                ops = ops + c.get() + "\n"
        ops = ops + exit.get() + "\n"
        # radius comp off just in case
        comp = Offset(None)
        ops = ops + comp.get() + "\n"
        return(ops)

if __name__ == "__main__":

    line01 = StraightFeed()
    line01.put(startPt = [1.0, 1.0, 0.0], endPt = [1.0, 2.0, 0.0])
    line02 = StraightFeed()
    line02.put(startPt = [1.0, 2.0, 0.0], endPt = [2.0, 2.0, 0.0])
    line03 = StraightFeed()
    line03.put(startPt = [2.0, 2.0, 0.0], endPt = [2.0, 1.0, 0.0])
    line04 = StraightFeed()
    line04.put(startPt = [2.0, 1.0, 0.0], endPt = [1.0, 1.0, 0.0])

    operationLines01 = [line01, line02, line03, line04]

    ops = Operation()
    ops.name = "One"
    ops.safeHeight = 0.25
    for o in operationLines01:
        ops.putCut(o)
    print ops.get()

    # box offset right
    ops = Operation()
    ops.name = "Two"
    ops.safeHeight = 0.25
    ops.offset = "right"
    ops.tool = tool_result()
    for o in operationLines01:
        ops.putCut(o)
    print ops.get()
