import argparse
import os
import re
import json
import pathlib
import sys
import math
import copy
import zlib
import json
import uuid
import enum




# color_policy bitmask values:
class ColorPolicy(enum.IntFlag):
    ENABLE_DITHERING        = 1   # bit 0
    CONVERT_TO_GRAYSCALE    = 2   # bit 1
    USE_OBJECT_COLOR        = 4   # bit 2

# bit 2 (use object color) is allowed to be high only when bit 1 (convert to grayscale) is low.

class EndStyle(enum.IntEnum):
        BUTT                 = 0 
        SQUARE               = 1 
        ROUND                = 2 
        DIAMOND              = 3 
        USE_OBJECT_ENDSTYLE  = 4

# The butt and square end styles are similar; both result in a straight edge perpendicular to the line.
# The difference is the location, along the line, of the edge.  With the 'butt' end style, the edge intersects the endpoint of the line.
# With the 'square' end style, the edge lies a distance lineThickness/2 beyond the endpoint of the line.
# Just as the 'round' end style can be conceived of as starting with the 'butt' end style and then adding a disc
# centered on the endpoint with the diameter of the disk being the line thickness, similarly, the 'square' 
# end style can be conceived as starting with the 'butt' end style and then adding a square, centered on the endpoint,
# with the inscribed diameter of the square being the line thickness, and with the square being oriented so that 
# (at least) one of its sides is parallel with the line.

class JoinStyle(enum.IntEnum):
    MITER= 0
    BEVEL= 1
    ROUND= 2
    DIAMOND= 3
    USE_OBJECT_JOINSTYLE=5


class FillStyle(enum.IntEnum):
    SOLID=64
    CHECKERBOARD=65
    CROSSHATCH=66
    DIAMONDS=67
    HORIZONTAL_BARS=68
    SLANT_LEFT=69
    SLANT_RIGHT=70
    SQUARE_DOTS=71
    VERTICAL_BARS=72
    USE_OBJECT_FILL_STYLE=73

class LineType(enum.IntEnum):
    USE_OBJECT_LINETYPE                = 31
    SOLID                              = 0 
    DASHED                             = 1 
    DOTTED                             = 2 
    DASH_DOT                           = 3 
    SHORT_DASH                         = 4 
    MEDIUM_DASH                        = 5 
    LONG_DASH                          = 6 
    SHORT_DASH_X2                      = 7 
    MEDIUM_DASH_X2                     = 8 
    LONG_DASH_X2                       = 9 
    MEDIUM_LONG_DASH                   = 10
    MEDIUM_DASH_SHORT_DASH_SHORT_DASH  = 11
    LONG_DASH_SHORT_DASH               = 12
    LONG_DASH_DOT_DOT                  = 13
    LONG_DASH_DOT                      = 14
    MEDIUM_DASH_DOT_SHORT_DASH_DOT     = 15
    SPARSE_DOT                         = 16
    ISO_DASH                           = 17
    ISO_DASH_SPACE                     = 18
    ISO_LONG_DASH_DOT                  = 19
    ISO_LONG_DASH_DOUBLE_DOT           = 20
    ISO_LONG_DASH_TRIPLE_DOT           = 21
    ISO_DOT                            = 22
    ISO_LONG_DASH_SHORT_DASH           = 23
    ISO_LONG_DASH_DOUBLE_SHORT_DASH    = 24
    ISO_DASH_DOT                       = 25
    ISO_DOUBLE_DASH_DOT                = 26
    ISO_DASH_DOUBLE_DOT                = 27
    ISO_DOUBLE_DASH_DOUBLE_DOT         = 28
    ISO_DASH_TRIPLE_DOT                = 29
    ISO_DOUBLE_DASH_TRIPLE_DOT         = 30
    

class CustomLineweightDisplayUnit(enum.IntEnum):
    MILLIMETER  = 0
    INCH        = 1

#the 'lineweight' property is as follows:
# 0 means "useObjectLineweight"
# any other integer n is a reference to custom_linewight_table[n-1]

# I include the defaultLineweightTable here as a descriptive reference (not prescriptive).
# AutoCAD will reconstruct the below values if the custom_lineweight_table property of the plot
# style is absent.  If the custom_lineweight_table property has fewer than the standard number (27, I think) of entries,
# autoCAD will either fill in the 'missing' entries with values from the "defaultLineweights" or will completely overwrite the 
# custom_lineweight_table with the defaultLineweights (I can't remember which)
defaultLineweights = [
        0.00,    #  0  *classic             
        0.05,    #  1  *classic     
        0.09,    #  2  *classic       
        0.10,    #  3         
        0.13,    #  4  *classic        
        0.15,    #  5  *classic        
        0.18,    #  6  *classic        
        0.20,    #  7  *classic       
        0.25,    #  8  *classic        
        0.30,    #  9  *classic       
        0.35,    # 10  *classic        
        0.40,    # 11  *classic       
        0.45,    # 12          
        0.50,    # 13  *classic       
        0.53,    # 14  *classic        
        0.60,    # 15  *classic       
        0.65,    # 16          
        0.70,    # 17  *classic       
        0.80,    # 17  *classic       
        0.90,    # 18  *classic       
        1.00,    # 19  *classic       
        1.06,    # 20  *classic        
        1.20,    # 21  *classic        
        1.40,    # 22  *classic        
        1.58,    # 23  *classic         
        2.00,    # 24  *classic       
        2.11     # 25  *classic       
] 


# for reference, here is the LineWeight enum definition from the relevant oarx c++ header file:
# The integers that appear in the symbol names are in units of 10 microns.
# the below lineweights are what I amc alling the "classic" lineweights.
#   enum LineWeight        { kLnWt000          =   0,
#                            kLnWt005          =   5,
#                            kLnWt009          =   9,
#                            kLnWt013          =  13,
#                            kLnWt015          =  15,
#                            kLnWt018          =  18,
#                            kLnWt020          =  20,
#                            kLnWt025          =  25,
#                            kLnWt030          =  30,
#                            kLnWt035          =  35,
#                            kLnWt040          =  40,
#                            kLnWt050          =  50,
#                            kLnWt053          =  53,
#                            kLnWt060          =  60,
#                            kLnWt070          =  70,
#                            kLnWt080          =  80,
#                            kLnWt090          =  90,
#                            kLnWt100          = 100,
#                            kLnWt106          = 106,
#                            kLnWt120          = 120,
#                            kLnWt140          = 140,
#                            kLnWt158          = 158,
#                            kLnWt200          = 200,
#                            kLnWt211          = 211,
#                            kLnWtByLayer      = -1,
#                            kLnWtByBlock      = -2,
#                            kLnWtByLwDefault  = -3,
#                            kLnWtByDIPs       = -4 };    // for internal use only

classicLineweights = [
    0.00,
    0.05,
    0.09,
    0.13,
    0.15,
    0.18,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.50,
    0.53,
    0.60,
    0.70,
    0.80,
    0.90,
    1.00,
    1.06,
    1.20,
    1.40,
    1.58,
    2.00,
    2.11
]



class AcadPlotstyle (object):
    def __init__(
        name                  ="Normal",
        localized_name        = None,
        description           = "",
        color                 = -1006632961,
        mode_color            = -1006632961,
        color_policy          = ColorPolicy(),
        physical_pen_number   = 0,     
        virtual_pen_number    = 0,      
        screen                = 100,  
        linepattern_size      = 0.5,
        linetype              = LineType(),
        adaptive_linetype     = True,                         
        lineweight            = 0,
        fill_style            = FillStyle(), 
        end_style             = EndStyle(),   
        join_style            = JoinStyle()
    ):
        self.description           = str(description)
        self.color                 = int(color)
        self.mode_color            = int(mode_color)           
        self.color_policy          = ColorPolicy(color_policy)
        self.physical_pen_number   = int(physical_pen_number)
        self.virtual_pen_number    = int(virtual_pen_number)   
        self.screen                = int(screen)               
        self.linepattern_size      = float(linepattern_size)
        self.linetype              = LineType(linetype)
        self.adaptive_linetype     = bool(adaptive_linetype)
        self.lineweight            = int(lineweight)   
        self.fill_style            = FillStyle(fill_style)        
        self.end_style             = EndStyle(end_style)
        self.join_style            = JoinStyle(join_style)





class AcadPentable (object):

    def __init__(self, penTableFile=None):
        self._description = ""
        self.aci_table_available = False
        self.scale_factor = 1.0
        self.apply_factor = False
        self.custom_lineweight_display_units =  CustomLineweightDisplayUnit()
        self.custom_lineweight_table = copy.deepcopy(defaultLineweights)
        self.plot_style = OrderedDict()
        normalPlotStyle = AcadPlotstyle()
        self.plot_style[ normalPlotStyle.name ] = normalPlotStyle
        # it is possible to construct a pentable file in whcih there are multiple plot_style entries with the same name 
        # (the pentable file stored this internally as an ordered-list rather than a dictionary-like-structure.
        # However, clearly the intent (which I think the AutoCAD pen table editor UI gnerally enforces) is that the name property of each plot_style entry
        # is a unique key.
        # the pentable does store the order of the entries, therefore I am using OrderedDict to represent this, rather than a (plain-old) dict.
        # it might make more sense to store the polt_style list as a list, and do our own lookup function; this would be a more faithful hewing to autoCAD's own representation.


        #when we read in a pentable file, we will record the path of the source file, if available, in this variable
        # self._pathOfSourceFile = None  ## not yet implemented
        if penTableFile: self.loadFromFile(penTableFile)




    def loadFromFile(penTableFile):
        # to do: allow passing either a file-like object or a path-like object (e.g. a string)
        self._headerBytes = penTableFile.read(60)
        self._compressedBytes=penTableFile.read()
        self._payloadBytes = zlib.decompress(compressedBytes)
        payloadString = payloadBytes.decode("ascii")

        nameAndPrimitiveValuePattern = re.compile(r"^\s*(?P<identifier>\w+)\s*=\s*(?P<rawvalue>.*)$")
        nameAndSubObjectPattern = re.compile(r"^\s*(?P<identifier>\w+)\s*{\s*$")
        subObjectTerminationPattern = re.compile(r"^\s*(}\s*)+$")

        data = AcadPentable._payloadStringToRawDictionary(payloadString)

        # headerString = headerBytes.decode("raw_unicode_escape")
        # if headerString.encode("raw_unicode_escape") == headerBytes:
        #     print("original header was preserved.")
        # else:
        #     print("original header was corrupted.")

        #include the header of the original file as an item in the dictionary, with the special key "_header"
        #data['_header'] = headerBytes.decode("raw_unicode_escape")

        #mysteryBytes = headerBytes[headerBytes.find(b'\n') + 1 + len("pmzlibcodec"):]

        # # checksumOfPayload = zlib.crc32(payloadBytes)
        # checksumOfPayload = zlib.adler32(payloadBytes)
        # checksumOfCompressed = zlib.adler32(compressedBytes)

        # data['_mysteryBytes'] = list(mysteryBytes)
        # # data['_checksumOfPayload'] = list(checksumOfPayload.to_bytes(length=4,byteorder='little'))
        # # # data['_checksumOfPayload'] = list(
        # # #         map(
        # # #             lambda x: int('{:08b}'.format(x)[::-1], 2),
        # # #             list(checksumOfPayload.to_bytes(length=4,byteorder='little'))
        # # #         )
        # # #     )
        # data['_checksumOfCompressed'] = list(checksumOfCompressed.to_bytes(length=4,byteorder='little'))
        # # data['_checksumOfCompressed'] = list(
        # #         map(
        # #             lambda x: int('{:08b}'.format(x)[::-1], 2),
        # #             list(checksumOfCompressed.to_bytes(length=4,byteorder='little'))
        # #         )
        # #     )
        # data['_payloadBytesCount'] = len(payloadBytes)
        # data['_payloadBytesCountBytes'] = list(len(payloadBytes).to_bytes(length=4,byteorder='little'))
        # data['_compressedBytesCount'] = len(compressedBytes)
        # data['_compressedBytesCountBytes'] = list(len(compressedBytes).to_bytes(length=4,byteorder='little'))



        # now, we are going to go a bit further, and clean up the representation of the stb/ctb data.

        # AutoCAD stores the list of plot styles as an associative array, whose keys are always the integers 0...n
        # Therefore, it would make sense not to represent the list of plot styles as an associative array, but instead as an 
        # ordered list.  Probably, AutoCAD's serialization format does not have a way to encode a list, but our serialization format (probably json) does.
        if 'plot_style' in data: 
            for i in data['plot_style']:
                thisPlotStyle = AcadPlotStyle(
                    name                  = data['plot_style'][i]['name'],
                    localized_name        = data['plot_style'][i]['localized_name'],       
                    description           = data['plot_style'][i]['description'],          
                    color                 = data['plot_style'][i]['color'],                
                    mode_color            = data['plot_style'][i]['mode_color'],           
                    color_policy          = data['plot_style'][i]['color_policy'],         
                    physical_pen_number   = data['plot_style'][i]['physical_pen_number'],  
                    virtual_pen_number    = data['plot_style'][i]['virtual_pen_number'],   
                    screen                = data['plot_style'][i]['screen'],               
                    linepattern_size      = data['plot_style'][i]['linepattern_size'],     
                    linetype              = data['plot_style'][i]['linetype'],             
                    adaptive_linetype     = data['plot_style'][i]['adaptive_linetype'],                 
                    lineweight            = data['plot_style'][i]['lineweight'],           
                    fill_style            = data['plot_style'][i]['fill_style'],           
                    end_style             = data['plot_style'][i]['end_style'],            
                    join_style            = data['plot_style'][i]['join_style'],           
                )
                self.plot_style[thisPlotStyle.name] = thisPlotStyle
                #we are double-representing the name here, both as the key to the self.plot_style dictionary and as a property of thisPlotStyle -- not sure the best way to resolve this.

        if 'custom_lineweight_table' in data: self.custom_lineweight_table = list(data['custom_lineweight_table'].values())

        self._description = str(data['description'])
        self.aci_table_available = bool(data['aci_table_available'])
        self.scale_factor = float(data['scale_factor'])
        self.apply_factor = bool(data['apply_factor'])
        self.custom_lineweight_display_units =  CustomLineweightDisplayUnit(data['custom_lineweight_display_units'])

        #I have made the penTableObjectToPayloadString() function so that a list results in exactly the same output as a dictionary whose keys
        # are the stringified sequential integers starting with "0"
        # thus, I do not need to bother converting data['plot_style'] back into a dictionary before writing to the stb file.


        #perhaps we should store the "plot_style" entry as a dictionary with the keys being names, but this would remove the order of plot_style list, which is 
        # somewhat important because the order of the list controls the order in which the plot styles are presented to the user in the ui.

        return data


    def writePenTableDataToFile(data: dict, penTableFile):
        global payloadBytes
        data = copy.deepcopy(data)
        originalHeaderBytes =  data['_header'].encode("raw_unicode_escape")

        data.pop('_header',None)
        data.pop('_mysteryBytes',None)
        data.pop('_checksumOfPayload',None)
        data.pop('_checksumOfCompressed',None)
        data.pop('_payloadBytesCount',None)
        data.pop('_payloadBytesCountBytes',None)
        data.pop('_compressedBytesCount',None)
        data.pop('_compressedBytesCountBytes',None)

        payloadString = penTableObjectToPayloadString(data)
        payloadBytes = payloadString.encode('ascii')
        compressedBytes = zlib.compress(payloadBytes)



        # the header consists of the original header up to and including "pmzlibcodec"
        # followed by a 4-byte little-endian unsigned integer representation of the adler32 checksum of the compressed payload
        # followed by a 4-byte little-endian unsigned integer representation of the count of bytes in the uncompressed payload
        # followed by a 4-byte little-endian unsigned integer representation of the count of bytes in the compressed payload.

        conservedHeaderBytes = originalHeaderBytes[:originalHeaderBytes.find(b'\n') + 1 + len("pmzlibcodec")]
        
        # checksumBytes = originalHeaderBytes[len(conservedHeaderBytes): len(conservedHeaderBytes)+4]
        # I am cheating by pulling the checksum bytes from the original header -- this may not work.
        # actually, AutoCAD does not seem to mind having a bogus checksum.  However, by playing around and googling, I
        # have discoverd that, evidently, the checksumBytes are the 4-byte little-endian unsigned integer representation 
        # of the adler32 checksum of the compressed payload
        checksumBytes = zlib.adler32(compressedBytes).to_bytes(length=4,byteorder='little')
        payloadBytesCountBytes = len(payloadBytes).to_bytes(length=4,byteorder='little')
        compressedBytesCountBytes = len(compressedBytes).to_bytes(length=4,byteorder='little')


        # print("len(conservedHeaderBytes): " + str(len(conservedHeaderBytes)))

        penTableFile.write(
            conservedHeaderBytes 
            + checksumBytes
            + payloadBytesCountBytes
            + compressedBytesCountBytes
            + compressedBytes
        )




        # mysteryBytes = headerBytes[headerBytes.find(b'\n') + 1 + len("pmzlibcodec"):]

        # data['_mysteryBytes'] = list(mysteryBytes)
        # data['_payloadBytesCount'] = len(payloadBytes)
        # data['_payloadBytesCountBytes'] = list(len(payloadBytes).to_bytes(length=4,byteorder='little'))
        # data['_compressedBytesCount'] = len(compressedBytes)
        # data['_compressedBytesCountBytes'] = list(len(compressedBytes).to_bytes(length=4,byteorder='little'))

    @staticmethod
    def _payloadStringToRawDictionary(payloadString: str):
        nameAndPrimitiveValuePattern = re.compile(r"^\s*(?P<identifier>\w+)\s*=\s*(?P<rawvalue>.*)$")
        nameAndSubObjectPattern = re.compile(r"^\s*(?P<identifier>\w+)\s*{\s*$")
        subObjectTerminationPattern = re.compile(r"^\s*(}\s*)+$")

        # we will pay attention to each line that matches one of the above three patterns, and will ignore any other lines.
        #this is a bit crude, in that it probably won't parse all possible valid payloadStrings,
        # but I am trusting that autoCAD is fairly regular in the way it serializes these data structures.

        data = {}
        objectNestingStack = []
        currentObject = data
        for line in payloadString.splitlines():
            nameAndPrimitiveValueMatch = nameAndPrimitiveValuePattern.match(line)
            nameAndSubObjectMatch = nameAndSubObjectPattern.match(line)
            subObjectTerminationMatch = subObjectTerminationPattern.match(line)

            if nameAndPrimitiveValueMatch: 
                identifier = nameAndPrimitiveValueMatch.group('identifier')
                rawvalue = nameAndPrimitiveValueMatch.group('rawvalue')
                if rawvalue.startswith("\""):
                    # a leading double-quote character indicates that the type of this value is string
                    value = rawvalue[1:]
                elif rawvalue.strip().lower() in ("true","false"):
                    #the keywords "TRUE" and "FALSE" indicate a boolean (I am allowing mixed case)
                    value = (rawvalue.strip().lower() == "true")
                else:
                    # in this case, we will attempt to interpret rawvalue as a number
                    try:
                        # value = int(rawvalue) if int(rawvalue) == float(rawvalue) else float(rawvalue)
                        
                        if "." in rawvalue: value = float(rawvalue)
                        else: value = int(rawvalue)

                    except ValueError as exception:
                        # hopefully, we never get here.
                        print("encountered an exception while attempting to decode rawvalue " + rawvalue +  ": " + str(exception) )
                        value=rawvalue
                currentObject[identifier] = value
            elif nameAndSubObjectMatch:
                identifier = nameAndSubObjectMatch.group('identifier')
                newObject = {}
                currentObject[identifier] = newObject
                objectNestingStack.append(currentObject)
                currentObject = newObject
            elif subObjectTerminationMatch:
                for i in range(subObjectTerminationMatch.group().count("}")):
                    currentObject = objectNestingStack.pop()
        # at this point, we have parsed payloadString as if it were a generic expression in (my concept of) the serialization format that AutoCAD uses.
        return data

    @staticmethod
    # penTableObject can be a dict or a list.  If it's a list, the result will be the same as passing
    # a dict whose keys are the stringified int's 0,1,...,len(penTableObject)-1
    def _penTableObjectToPayloadString(penTableObject) -> str:
        def encodeAsPenTablePrimitive(x) -> str:
            if isinstance(x,str):
                return "\"" + x
            elif isinstance(x, bool):
                return ("TRUE" if x else "FALSE")
            else:
                return str(x)

        payloadString = ""
        keys = penTableObject.keys() if isinstance(penTableObject, dict) else range(len(penTableObject))
        for key in keys:
            # print("now processing key " + key)
            payloadString += str(key)
            value = penTableObject[key]
            if isinstance(value, dict) or isinstance(value, list):
                payloadString += (
                    "{\n" 
                    + "\n".join(map(lambda y: " " + y, penTableObjectToPayloadString(value).splitlines())) 
                    + "\n"
                    + "}\n"
                )
            else:
                payloadString += "=" + encodeAsPenTablePrimitive(value) + "\n"
        return payloadString

