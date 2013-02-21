import numpy
# ToDo:
#     - deal with layer information
#     - argument with get method to get only items wanted (string eg. "startPt", or list eg. ["startPt", "endPt"]
# main DXF object class
class DXF(object):
    def __init__(self):
        self.filename = ""
        
    def new(self):
        self.HEADER = HEADER()
        self.CLASSES = CLASSES()
        self.TABLES = TABLES()
        self.BLOCKS = BLOCKS()
        self.ENTITIES = ENTITIES()
        self.OBJECTS = OBJECTS() 
    def open(self, filename):
        self.new()
        self.filename = filename
        dxfTxt = open(self.filename, 'r').readlines()
        self.load(dxfTxt)
    def load(self, dxfText):
        """DXF.load(dxfTxt)
        dxfTxt : A string containing a dxf file (or possably sections of a dxf).
        """
        currentSection = ""
        section = []
        for l in xrange(len(dxfText) - 1):
            if (dxfText[l].rstrip() == "  0") and (dxfText[l + 1].rstrip() == "SECTION"):
                # is there a way to refrence self.HEADER (etc) 
                currentSection = dxfText[l + 3].strip()
                section.append(dxfText[l].rstrip())
            elif (dxfText[l].rstrip() == "ENDSEC") and (dxfText[l - 1].rstrip() == "  0"):
                section.append(dxfText[l].rstrip())
                if currentSection == "HEADER":
                    self.HEADER.parse(section)
                if currentSection == "CLASSES":
                    self.CLASSES.parse(section)
                if currentSection == "TABLES":
                    self.TABLES.parse(section)
                if currentSection == "BLOCKS":
                    self.BLOCKS.parse(section)
                if currentSection == "ENTITIES":
                    self.ENTITIES.parse(section)
                if currentSection == "OBJECTS":
                    self.OBJECTS.parse(section)
                section = []
            else:
                section.append(dxfText[l].rstrip())

                
# section classes
class SECTIONS(object):
    def __init__(self):
        self.data = []
        # have a get and some sort of get all (maybe option in get).
    def parse(self, dxfText):
        currentSection = ""
        section = []
        for l in xrange(4, len(dxfText) - 1):
            if (dxfText[l].rstrip() == "  0"):
                if section == []:
                    currentSection = dxfText[l + 1].strip()
                    section.append(dxfText[l].rstrip())
                else:
                    
                    self.put(currentSection, section)
                    section = []
                    currentSection = dxfText[l + 1].strip()
                    section.append(dxfText[l].rstrip())                    
            else:
                section.append(dxfText[l].rstrip())
        
    def put(self, typ, d):
        """put apropreate dxf data into subsectio
        typ : a type that goes into the classes sectio (ie. LINE into Entities)
        d : list of strings in the proper dxf format
        """
        self.data.append([typ, d[2:]])
            
class HEADER(SECTIONS):
    def __init__(self):
        SECTIONS.__init__(self)    

class CLASSES(SECTIONS):
    def __init__(self):
        SECTIONS.__init__(self)

class TABLES(SECTIONS):
    def __init__(self):
        SECTIONS.__init__(self)    

class BLOCKS(SECTIONS):
    def __init__(self):
        SECTIONS.__init__(self)

class ENTITIES(SECTIONS):
    def __init__(self):
        SECTIONS.__init__(self)    
    def put(self, typ, d):
        if typ == "LINE":
            self.data.append(Line())
        if typ == "LWPOLYLINE":
            self.data.append(LWPolyline())            
        if typ == "CIRCLE":
            self.data.append(Circle())
        if typ == "ARC":
            self.data.append(Arc())
        if typ == "POINT":
            self.data.append(Point())
        if typ == "Polyline":
            self.data.append((Polyline()))                                    
        if typ == "Image":
            self.data.append(Image())                                    
        if typ == "Insert":
            self.data.append(Insert())                                    
        if typ == "MText":
            self.data.append(MText())                                    
        if typ == "Text":
            self.data.append(Text())      
        # print self.data[-1]
        self.data[-1].load(d)

        
class OBJECTS(SECTIONS):
    def __init__(self):
        SECTIONS.__init__(self)

# entity classes
class Entity(object):
    """Base class for objects found in ENTITIES section class."""
    def __init__(self):
        self.type = str(type(self)).split('.')[-1].replace("'>", "")
        self.tmp = []
        self.data = []
        self.startPt = [None, None, None]
        self.endPt = [None, None, None]
        self.centerPt = [None, None, None]
        self.radius = None
        self.startAngle = None
        self.endAngle = None
        self.verts = []
        self.closed = None
        self.layer = None
        self.color = None
    def new(self):
        pass
    def load(self, dxfText):
        """load dxf text"""
        # print self.type, "no entity specific load code."
        #for line in xrange(2, len(dxfText)):
        #    print line, '"' + dxfText[line] + '"'            
    def put(self):
        """ 
        use ent.get(option)
        options : startPt,
        endPt,
        centerPt,
        startAngle,
        endAngle
        """
        pass
    def get(self, arg = None):
        """ use ent.get(option)
        options : "startPt",
                  "endPt",
                  "centerPt",
                  "startAngle",
                  "endAngle"
        """
        d = {"type" : self.type, 
             "startPt" : self.startPt, 
             "endPt" : self.endPt, 
             "centerPt" : self.centerPt,
             "radius" : self.radius,
             "verts" : self.verts,
             "startAngle" : self.startAngle,
             "endAngle" : self.endAngle,
             "closed" : self.closed,
             "layer" : self.layer,
             "color" : self.color}

        if arg == None:
            return(d)
        elif type(arg) == type("string"):
            return(d[arg])
        elif type(arg) == type(["List"]):
            pass 
                
            
    def move(self):
        pass
    def copy(self):
        pass
    def rotate(self):
        pass
    def scale(self):
        pass
    def mirror(self):
        pass


class Line(Entity):
    def __init__(self):
        Entity.__init__(self)
    def load(self, dxfText):
        """load dxf text
        dxfText : list of string out of dxf file."""
        for line in xrange(2, len(dxfText)):
            # print  '"' + dxfText[line] + '"'
            if dxfText[line].rstrip() == " 10":
                self.startPt[0] = float(dxfText[line + 1])
            if dxfText[line].rstrip() == " 20":
                self.startPt[1] = float(dxfText[line + 1])
            if dxfText[line].rstrip() == " 30":
                self.startPt[2] = float(dxfText[line + 1])
            if dxfText[line].rstrip() == " 11":
                self.endPt[0] = float(dxfText[line + 1])
            if dxfText[line].rstrip() == " 21":
                self.endPt[1] = float(dxfText[line + 1])
            if dxfText[line].rstrip() == " 31":
                self.endPt[2] = float(dxfText[line + 1])
            if dxfText[line].rstrip() == "  8":
                self.layer = dxfText[line + 1]
            if dxfText[line].rstrip() == " 62":
                self.color = int(dxfText[line + 1])
            if dxfText[line].rstrip() == " 31":
                self.endPt[2] = float(dxfText[line + 1])                                                
        self.centerPt = list((numpy.array(self.startPt) + numpy.array(self.endPt)) / 2)
        # startAngle
        # endAngle

class LWPolyline(Entity):
    def __init__(self):
        Entity.__init__(self)
    def load(self, dxfText):
        """load dxf text
        dxfText : list of string out of dxf file."""
        x1 = None
        y1 = None
        self.elevation = 0.0
        for line in xrange(2, len(dxfText)):
            # print  '"' + dxfText[line] + '"'
            if dxfText[line].rstrip() == " 10":
                x1 = float(dxfText[line + 1])
            if dxfText[line].rstrip() == " 20":
                y1 = float(dxfText[line + 1])
            if dxfText[line].rstrip() == "  8":
                self.layer = dxfText[line + 1]
            if dxfText[line].rstrip() == " 62":
                self.color = int(dxfText[line + 1])
            if dxfText[line].rstrip() == " 38":
                self.elevation = float(dxfTxt[l + 1])
            if dxfText[line].rstrip() == " 42":
                self.bulge = float(dxfText[line + 1])                
            if dxfText[line].rstrip() == " 70":
                self.closed = int(dxfText[line + 1])
            if (x1 != None) and (y1 != None):
                pt = [x1, y1, self.elevation]
                if len(dxfText) >= line + 3:
                    if dxfText[line + 2].rstrip() == " 42":
                        pt.append(float(dxfText[line + 3]))
                    else:
                        pt.append(0)
                else:
                    pt.append(0)                                                
                self.verts.append(pt)
                x1 = None
                y1 = None
        self.startPt = self.verts[0]
        self.endPt = self.verts[-1]
        c = numpy.array([0,0,0])
        for v in self.verts:
            # print v
            c = c + numpy.array(v[0:3])
        self.centerPt = list(c / len(self.verts))
    def asLinesArcs(self):
        """Returns a list of lines and arcs in the polyline
        format:
        ["LINE", [start point xyz], [end point xyz]]
        or 
        ["ARC", [[start point xyz], [end point xyz], [center point xyz], cw/ccw]
        cw  : 1 (clockwise)
        ccw : -1 (counterclock wise)
        only supports closed polylines for now
        """
        ents = []
        if self.closed == 1:
            count = len(self.verts)
        else:
            count = len(self.verts) - 1
        for e in xrange(count):
            # for lines
            if (self.verts[e][3] == 0.0):
                nextPoint = (e + 1) % len(self.verts)
                ents.append(["LINE", 
                             self.verts[e][0:3],
                             self.verts[nextPoint][0:3]])
            else:
                nextPoint = (e + 1) % len(self.verts)
                # get center using bulge factor
                bulge = self.verts[e][3]
                angle = 4 * numpy.arctan(bulge) # included angle for center and 2 end points
                startPt = numpy.array(self.verts[e][0:3])
                endPt = numpy.array(self.verts[nextPoint][0:3])
                cordCenter = (endPt + startPt) / 2.0
                sP2cCVector = cordCenter - startPt
                sP2cCMag = numpy.sqrt(sum(pow(sP2cCVector, 2.0)))
                cC2CircleCMag = sP2cCMag / numpy.tan(angle / 2.0)
                cC2CircleCUnitV = numpy.array([-1 * sP2cCVector[1], sP2cCVector[0], 0])  / sP2cCMag
                center = cordCenter + (cC2CircleCUnitV * cC2CircleCMag)
                if bulge > 0:
                    direction = 1
                elif bulge < 0:
                    direction = -1
                else:
                    direction = 0
                ents.append(["ARC", 
                             list(startPt),
                             list(endPt),
                             list(center),
                             direction])
                

                        
        # got to be better ways to do this
        # get rid of single point at end if last move is an arc 
        if ents[-1][1] == ents[-1][2]:
            ents.pop(-1)

        return(ents)

class Circle(Entity):
    def __init__(self):
        Entity.__init__(self)
    def load(self, dxfText):
        """load dxf text
        dxfText : list of string out of dxf file."""
        for line in xrange(2, len(dxfText)):
            # print  '"' + dxfText[line] + '"'
            if dxfText[line].rstrip() == " 10":
                self.centerPt[0] = float(dxfText[line + 1])
            if dxfText[line].rstrip() == " 20":
                self.centerPt[1] = float(dxfText[line + 1])
            if dxfText[line].rstrip() == " 30":
                self.centerPt[2] = float(dxfText[line + 1])
            if dxfText[line].rstrip() == " 40":
                self.radius = float(dxfText[line + 1])
            if dxfText[line].rstrip() == "  8":
                self.layer = dxfText[line + 1]
            if dxfText[line].rstrip() == " 62":
                self.color = int(dxfText[line + 1])
            if dxfText[line].rstrip() == " 31":
                self.endPt[2] = float(dxfText[line + 1])                                                
        self.startAngle = 0
        self.endAngle = 0
        self.startPt = [self.centerPt[0] + self.radius, self.centerPt[1], self.centerPt[2]]
        self.endPt = self.startPt


        
class Arc (Entity):
    def __init__(self):
        Entity.__init__(self)

class Point(Entity):
    def __init__(self):
        Entity.__init__(self)



class Polyline(Entity):
    def __init__(self):
        Entity.__init__(self)

class Image(Entity):
    def __init__(self):
        Entity.__init__(self)

class Insert(Entity):
    def __init__(self):
        Entity.__init__(self)

class MText(Entity):
    def __init__(self):
        Entity.__init__(self)

class Text(Entity):
    def __init__(self):
        Entity.__init__(self)



