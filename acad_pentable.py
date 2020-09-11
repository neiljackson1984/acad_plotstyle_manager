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
import collections
from typing import IO, Any, AnyStr, Union

def set_bit(v, index, x):
  """Set the index:th bit of v to 1 if x is truthy, else to 0, and return the new value."""
  mask = 1 << index   # Compute mask, an integer with just bit 'index' set.
  returnValue = v & ~mask          # Clear the bit indicated by the mask (if x is False)
  if x: returnValue |= mask         # If x was True, set the bit indicated by the mask.
  return returnValue            # Return the result, we're done.

def get_bit(v, index):
    mask = 1 << index
    return (1 if (v & mask) else 0)

# to do: figure out how to escape double quotes and newlines in the string values in the pentable payload (would mainly be used in the description field).

# color_policy bitmask values:
# class ColorPolicy(enum.IntFlag):
#     ENABLE_DITHERING        = 1   # bit 0
#     CONVERT_TO_GRAYSCALE    = 2   # bit 1
#     USE_OBJECT_COLOR        = 4   # bit 2

# bit 2 (use object color) is allowed to be high only when bit 1 (convert to grayscale) is low.
# oops, USE_OBJECT_COLOR should be relabled "DO_NOt_USE_OBJECT_COLOR" (aka (explciitly override tyhe color))

class ColorPolicy(enum.IntFlag):
    ENABLE_DITHERING        = 1   # bit 0
    CONVERT_TO_GRAYSCALE    = 2   # bit 1
    EXPLICIT_COLOR          = 4   # bit 2  # this bit goes low when the user in the ui selects "use object color" from the color dropdown box.

#this is a duplicate of the AcCmEntityColor::ColorMethod definfed in the oarx c++ header file dbcolor.h
class ColorMethod(enum.IntEnum):
    BY_LAYER        = 192 # 0xc0 
    BY_BLOCK        = 193 # 0xc1
    BY_COLOR        = 194 # 0xc2
    BY_ACI          = 195 # 0xc3
    BY_PEN          = 196 # 0xc4
    FOREGROUND      = 197 # 0xc5
    LAYER_OFF       = 198 # 0xc6
    LAYER_FROZEN    = 199 # 0xc7
    NONE            = 200 # 0xc8

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


stbConstantHeader = b'PIAFILEVERSION_2.0,STBVER1,compress\r\npmzlibcodec'
ctbConstantHeader = b'PIAFILEVERSION_2.0,CTBVER1,compress\r\npmzlibcodec'
ttbConstantHeader = b'PIAFILEVERSION_2.0,TTBVER1,compress\r\npmzlibcodec'
# a file having the ttbConstantHeader is what AutoCAD gneerates when you run convertctb to convert a ctb file into an stb file with a contained 
# conversion table.. I do not understand why containing the conversion table is such a special case as to merit having its own special header.
# I think for my purposes, I will interpret the ttb header as meaning that we are dealing with a NAMED_PLOT_STYLES pentable (rather than interoduce a third PentableType value,
# which would be ridiculous)

#thanks to https://softwareengineering.stackexchange.com/questions/262346/should-i-pass-in-filenames-to-be-opened-or-open-files
# for a flexible way to have a fucntion that accepts either a path-like object or a file-like object:
Pathish = Union[AnyStr, pathlib.Path]  # in lieu of yet-unimplemented PEP 519
FileSpec = Union[IO, Pathish]


class PentableType(enum.Enum):
    NAMED_PLOT_STYLES            = enum.auto()
    COLOR_DEPENDENT_PLOT_STYLES  = enum.auto()


class AcadPentable (object):

    def __init__(self, pentableFile=None):
        self._pentableType = PentableType.NAMED_PLOT_STYLES
        self._conservedHeaderBytes = {PentableType.NAMED_PLOT_STYLES: stbConstantHeader, PentableType.COLOR_DEPENDENT_PLOT_STYLES: ctbConstantHeader}[self._pentableType]
        self.description = ""
        self.aci_table_available = False
        self.scale_factor = 1.0
        self.apply_factor = False
        self.custom_lineweight_display_units =  CustomLineweightDisplayUnit.MILLIMETER
        self.custom_lineweight_table = copy.deepcopy(defaultLineweights)
        self.plot_style = collections.OrderedDict()
        normalPlotStyle = AcadPlotstyle(owner=self)
        self.plot_style[ normalPlotStyle.name ] = normalPlotStyle
        self.aci_table = None
        # it is possible to construct a pentable file in whcih there are multiple plot_style entries with the same name 
        # (the pentable file stored this internally as an ordered-list rather than a dictionary-like-structure.
        # However, clearly the intent (which I think the AutoCAD pen table editor UI gnerally enforces) is that the name property of each plot_style entry
        # is a unique key.
        # the pentable does store the order of the entries, therefore I am using OrderedDict to represent this, rather than a (plain-old) dict.
        # it might make more sense to store the polt_style list as a list, and do our own lookup function; this would be a more faithful hewing to autoCAD's own representation.


        #when we read in a pentable file, we will record the path of the source file, if available, in this variable
        # self._pathOfSourceFile = None  ## not yet implemented
        
        #when we read in a pentable file, we will store the _headerBytes for subsequent use during write-out (TO DO: if possible, store the constant header bytes as a constant in this code rather than dynamically reading them each time)
        self._headerBytes = None

        if pentableFile: self.loadFromFile(pentableFile)


    #the private version of _loadFromFile expects an open file handle as an argument (hopefully one that is opened in binary mode)
    def _loadFromFile(self, pentableFile):
        # to do: allow passing either a file-like object or a path-like object (e.g. a string)
        headerBytes = pentableFile.read(60)
        self._conservedHeaderBytes = headerBytes[:headerBytes.find(b'\n') + 1 + len("pmzlibcodec")] #I suspect that this is a fixed magic string that we could store as a constant.
        # print("self._conservedHeaderBytes: " + repr(self._conservedHeaderBytes))
        # to do: verify the checksums.

        #set the pentableType based on the header.
        self._pentableType = {
            stbConstantHeader: PentableType.NAMED_PLOT_STYLES,
            ttbConstantHeader: PentableType.NAMED_PLOT_STYLES,
            ctbConstantHeader: PentableType.COLOR_DEPENDENT_PLOT_STYLES
        }.get(self._conservedHeaderBytes)
        
        #to do: handle the case of an unrecognized header (probably should cause a result similar to a bad checksum)

        # it is perhaps a bit redundant to hang on to self._conservedHeaderBytes and self._pentableType, however I still do not totally trust that the
        # header will always be one of the three "known" constant headers (because the idea that those three constant header values are consistent or
        # complete is merely the result of empirical investigation - Autodesk could change things on a whim.)

        compressedBytes=pentableFile.read()
        payloadBytes = zlib.decompress(compressedBytes)
        payloadString = payloadBytes.decode("ascii")

        #debugging only:
        #print(payloadString)



        self.fromRawDictionary(AcadPentable._payloadStringToRawDictionary(payloadString))
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

        


     #the private version of _writeToFile expects an open file handle as an argument, and we will be writing to the file handle, so hopefully it is opened in write mode..
    
    #the public version of loadFromFile can take either an open file handle or a path-ish object (a string or a pathlib.Path)
    def loadFromFile(self, pentableFile: FileSpec):
        if isinstance(pentableFile, (str, bytes, pathlib.Path)):
            with open(pentableFile, 'rb') as f:
                return self._loadFromFile(f)
        else:
            return self._loadFromFile(pentableFile)

    def _writeToFile(self, pentableFile):
        #to do: accept file-like object or a path-like object (current;y , we are only accepting a file-like object.


        # print("conservedHeaderBytes: " + conservedHeaderBytes.decode("unicode_escape"))
        # print("len(conservedHeaderBytes): " + str(len(conservedHeaderBytes)))
        # print("conservedHeaderBytes: " + repr(conservedHeaderBytes))
        # print("test: " + str(list("\n\n\t".encode("UTF-8"))))
        # print("test2: " + "|" + ("\n\n\t".encode("utf-8").decode("unicode_escape")) + "|")
        # print("test2: " + "|" + repr("\n\n\t") + "|")
        

        payloadString = AcadPentable._penTableObjectToPayloadString(self.toRawDictionary())
        payloadBytes = payloadString.encode('ascii')
        compressedBytes = zlib.compress(payloadBytes)



        # the header consists of the original header up to and including "pmzlibcodec"
        # followed by a 4-byte little-endian unsigned integer representation of the adler32 checksum of the compressed payload
        # followed by a 4-byte little-endian unsigned integer representation of the count of bytes in the uncompressed payload
        # followed by a 4-byte little-endian unsigned integer representation of the count of bytes in the compressed payload.

        # conservedHeaderBytes = originalHeaderBytes[:originalHeaderBytes.find(b'\n') + 1 + len("pmzlibcodec")]
        
        # checksumBytes = originalHeaderBytes[len(conservedHeaderBytes): len(conservedHeaderBytes)+4]
        # I am cheating by pulling the checksum bytes from the original header -- this may not work.
        # actually, AutoCAD does not seem to mind having a bogus checksum.  However, by playing around and googling, I
        # have discoverd that, evidently, the checksumBytes are the 4-byte little-endian unsigned integer representation 
        # of the adler32 checksum of the compressed payload
        checksumBytes = zlib.adler32(compressedBytes).to_bytes(length=4,byteorder='little')
        payloadBytesCountBytes = len(payloadBytes).to_bytes(length=4,byteorder='little')
        compressedBytesCountBytes = len(compressedBytes).to_bytes(length=4,byteorder='little')


        # print("len(conservedHeaderBytes): " + str(len(conservedHeaderBytes)))

        pentableFile.write(
            self._conservedHeaderBytes 
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

    #the public version of writeToFile can take either an open file handle or a path-ish object (a string or a pathlib.Path)
    def writeToFile(self, pentableFile: FileSpec):
        if isinstance(pentableFile, (str, bytes, pathlib.Path)):
            with open(pentableFile, 'wb') as f:
                return self._writeToFile(f)
        else:
            return self._writeToFile(pentableFile)


    def toRawDictionary(self) -> dict:
        return {
            **{
                                            
                'description'                       : self.description                             ,    
                'aci_table_available'               : self.aci_table_available                     ,            
                'scale_factor'                      : self.scale_factor                            ,     
                'apply_factor'                      : self.apply_factor                            ,     
                'custom_lineweight_display_units'   : self.custom_lineweight_display_units         ,                       
                'custom_lineweight_table'           : copy.deepcopy(self.custom_lineweight_table)  , 
                # TO DO: deal with the case of having an ACI table

                'plot_style'                        :  [ self.plot_style[i].toRawDictionary() for i in self.plot_style ] 
            },  
            **( {} if self.aci_table == None else  {'aci_table': self.aci_table})
        }

    def toHumanReadableDictionary(self) -> dict:
        return {
            **{
                # '_conservedHeaderBytes'             : repr(self._conservedHeaderBytes), 
                '_conservedHeaderBytes'             : self._conservedHeaderBytes.decode('ascii')    , 
                '_pentableType'                     : repr(self._pentableType)                      ,

                'description'                       : self.description                              ,          
                'aci_table_available'               : self.aci_table_available                      ,                  
                'scale_factor'                      : self.scale_factor                             ,           
                'apply_factor'                      : self.apply_factor                             ,           
                'custom_lineweight_display_units'   : repr(self.custom_lineweight_display_units)    ,                                   
                'custom_lineweight_table'           : copy.deepcopy(self.custom_lineweight_table)   ,       
                # TO DO: deal with the case of having an ACI table

                'plot_style'                        :  [ self.plot_style[i].toHumanReadableDictionary() for i in self.plot_style ] 
            },
            **( {} if self.aci_table == None else  {'aci_table': self.aci_table})
        }

    def fromRawDictionary(self, data: dict):
        # AutoCAD stores the list of plot styles as an associative array, whose keys are always the integers 0...n
        # Therefore, it would make sense not to represent the list of plot styles as an associative array, but instead as an 
        # ordered list.  Probably, AutoCAD's serialization format does not have a way to encode a list, but our serialization format (probably json) does.

        #just for debugging, so we can keep track of which keys we have processed
        data = copy.deepcopy(data)
        #to undo the debugging, replace .pop with .get below

        self.plot_style = collections.OrderedDict(
                {
                    plotStyleEntry['name'] : AcadPlotstyle.createNewFromOwnerAndRawDictionary(owner = self, rawDictionary = plotStyleEntry)
                    for plotStyleEntry in data.pop('plot_style',[]).values()  # I am trusting .values() (and all the preceeding construction of data) to have preserved the order present in the orignal file.
                }
            )
            #we are double-representing the name here, both as the key to the self.plot_style dictionary and as a property of thisPlotStyle -- not sure the best way to resolve this.

        self.custom_lineweight_table = list(data.pop('custom_lineweight_table', {}).values())  # I am trusting .values() (and all the preceeding construction of data) to have preserved the order present in the orignal file.

        self.description                        = str(data.pop('description'))
        self.aci_table_available                = bool(data.pop('aci_table_available'))
        self.scale_factor                       = float(data.pop('scale_factor'))
        self.apply_factor                       = bool(data.pop('apply_factor'))
        self.custom_lineweight_display_units    = CustomLineweightDisplayUnit(data.pop('custom_lineweight_display_units'))
        self.aci_table = ( list(data.pop('aci_table').values()) if 'aci_table' in data else None)  # I am trusting .values() (and all the preceeding construction of data) to have preserved the order present in the orignal file. 

        # print("unprocessed data: " + json.dumps(data, indent=4)) 

        #I have made the _penTableObjectToPayloadString() function so that a list results in exactly the same output as a dictionary whose keys
        # are the stringified sequential integers starting with "0"
        # thus, I do not need to bother converting data['plot_style'] back into a dictionary before writing to the stb file.

        #To do: deal with the case of having an aci table.

        #perhaps we should store the "plot_style" entry as a dictionary with the keys being names, but this would remove the order of plot_style list, which is 
        # somewhat important because the order of the list controls the order in which the plot styles are presented to the user in the ui.

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
                # return "\"" + x

                # Although the pentable editor ui appears to support having newlines in the description of a plot style, 
                # upon saving and re-opening, the newlines have been replaced with spaces.
                # that is very crappy design (both to not support newlines in the first place, and, in the second place, knowing that newlines are not supported, 
                # to have the user interface give the user the impression that they are supported (but actually unceremoneously replacing the user's (carefully placed) newlines with spaces when the uses saves the pen table file)
                # Once again, Autodesk, you should be embarassed.
                # Even crappier, for the pentable description field (the description for the entire pentable, not the per-plotstyle description), the user interface gives the impression that nbewlines are supported,
                # but if the user enters some newlines and saves, upon repopening, the pentable editor throws a popup message saying "Error syntax", followed by another popup error message saying "File Error Could not load file", 
                # and refuses to open the file (the same thing that happens when we 
                # insert newlines programmtically in the payload string).
                # For the hapless user who just so happened to add a newline to the description field of his precious pentable file (which he has not bothered to back up) and save, his pentable file is rendered useless,
                # and he will only find out that there is a problem the next time he opens the pentable file in the pentable editor (or, presumably, trys to plot with it -- I am not sure what AutoCAD will do when you 
                # attempt to plot with the newline-plagued pentable file.  
                # This is REALLY, REALLY bad, careless software design.
                # the plotstyle name field has the same problem -- the ui will let you insert newlines and save and close with no indication of a problem, and the file is then completey broken and unusable.
                # let me not make the same mistake.  Even though I cannot do anything to magically support newlines,
                # I can at least consistently sanitize newlines (and carriage returns, which cause the same problems as linefeeds.)
                # from all string values (both the plotstyle description and the pen table description (and any other strings that happen to be in the data (names for instance)) that I write into the payloadString.
                return "\"" + x.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")

            elif isinstance(x, bool):
                return ("TRUE" if x else "FALSE")
            elif isinstance(x, enum.IntEnum) or isinstance(x, enum.IntFlag) :
                return str(int(x))
            else:
                return str(x)

        payloadString = ""
        keys = penTableObject.keys() if isinstance(penTableObject, dict) else range(len(penTableObject))
        for key in keys:
            # print("now processing key " + str(key))
            payloadString += str(key)
            value = penTableObject[key]
            if isinstance(value, dict) or isinstance(value, list):
                payloadString += (
                    "{\n" 
                    + "\n".join(map(lambda y: " " + y, AcadPentable._penTableObjectToPayloadString(value).splitlines())) 
                    + "\n"
                    + "}\n"
                )
            else:
                payloadString += "=" + encodeAsPenTablePrimitive(value) + "\n"
        return payloadString

    def addAPlotstyle(self, name: str) -> 'AcadPlotstyle':
        newPlotstyle = AcadPlotstyle(owner=self, name=name)
        self.plot_style[str(name)] = newPlotstyle
        # caution: this overwrites an existing plot style at the specified dictionary key, if one already exists.
        return newPlotstyle

class PentableColor (object):    
    def __init__(self, *args, **kwargs):
        #the constructor accepts any of the following argument signatures:
        #   (byte or float) red, (byte or float) green, (byte or float) blue, (byte or ColorMethod) colorMethod
        #   (byte or float) red, (byte or float) green, (byte or float) blue
        #   int pentableRgbqColorInt
        # a float value for red, green, or blue, will be inerpreted as a ratio: a real number in the range [0,1], which we will map onto [0, 255]
        # an int value for red, green, or blue will be interpreted as the byte to be stored in the rgbQ data structure (i.e. the traditional 0..255 int color component value)
        # the acadRgbqColorInt is the signed integer representation of color that is the 'native' type of the 'color' and 'mode_color' 
        # properties that appear in the pen table.
        if len(args) == 1 and len(kwargs)==0: 
            # a single non-keyword argument will be interpreted as acadRgbqColorInt or as a PenTablColor object, if appropriate.
            self.acadRgbqColorInt = (args[0].acadRgbqColorInt if isinstance(args[0], PentableColor) else int(args[0]))
        else:
            red              =  (kwargs['red'              ] if 'red'               in kwargs else (args[0] if len(args) >= 1 else 255 ))
            green            =  (kwargs['green'            ] if 'green'             in kwargs else (args[1] if len(args) >= 2 else 255 ))
            blue             =  (kwargs['blue'             ] if 'blue'              in kwargs else (args[2] if len(args) >= 3 else 255 ))
            colorMethod      =  (kwargs['colorMethod'      ] if 'colorMethod'       in kwargs else (args[3] if len(args) >= 4 else ColorMethod.BY_ACI ))
            acadRgbqColorInt =  (kwargs['acadRgbqColorInt' ] if 'acadRgbqColorInt'  in kwargs else None)
            if acadRgbqColorInt != None:
                self.acadRgbqColorInt = int(acadRgbqColorInt)
            else: 
                self.colorMethod = colorMethod
                self.setRgb( red, green, blue)
            
            # to do maybe: detect invalid argument combinations and throw an exception if encountered. something like   raise Exception("invalid arguments")
            # to do maybe: setters for red, green, and blue

    @property
    def colorMethod(self) -> int:
        return self._colorMethod 

    @colorMethod.setter
    def colorMethod(self, x) -> ColorMethod:
        self._colorMethod = ColorMethod(int(x))
        return self.colorMethod

    @property
    def acadRgbqColorInt(self) -> int:
        return int.from_bytes( (self.blue, self.green, self.red, self.colorMethod), byteorder='little', signed=True)

    @acadRgbqColorInt.setter
    def acadRgbqColorInt(self, x: int) -> int:
        (self.blue, self.green, self.red, self.colorMethod) = tuple(int(x).to_bytes(length=4,byteorder='little', signed=True))
        return self.acadRgbqColorInt # are setters supposed/allowed to return a value?  perhaps the "@...setter" annotation automatically adds such a return statement.

    def setRgb(self, red, green, blue):
        self.red         = int( red    * 255 if isinstance(red   , float) else red    )
        self.green       = int( green  * 255 if isinstance(green , float) else green  )
        self.blue        = int( blue   * 255 if isinstance(blue  , float) else blue   )
    
    def getRgbTuple(self):
        return (self.red, self.green, self.blue)

    @property
    def humanReadableString(self) -> str:
        # return "red: {:3d}, green: {:3d}, blue: {:3d}, colorMethod: {:s} (acadRgbqColorInt: {:d})".format(self.red, self.green, self.blue, repr(self.colorMethod), self.acadRgbqColorInt)
        return "red: {:d}, green: {:d}, blue: {:d}, colorMethod: {:s} (acadRgbqColorInt: {:d})".format(self.red, self.green, self.blue, repr(self.colorMethod), self.acadRgbqColorInt)

    @property 
    def htmlCode(self) -> str:
        return "{:02X}{:02X}{:02X}".format(self.red, self.green, self.blue)        

    @property 
    #This returns a string suitable for setting as the value of the CECOLOR system variable in autocad
    
    def sysvarString(self) -> str:
        # #descriptinf of the CECOLOR system variable from the AutoCAD documentation:
        # Sets the color of new objects as you create them.
        # 
        # Valid values include the following:
        # * BYLAYER or BYBLOCK
        # * AutoCAD Color Index (ACI): integer values from 1 to 255, or a color name from the first seven colors
        # * True Colors: RGB or HSL values from 000 to 255 in the form "RGB:130,200,240"
        # * Color Books: Text from standard PANTONE or custom color books, the DIC color guide, or RAL color sets, for example "DIC COLOR GUIDE(R)$DIC 43"
        # 
        # Note: this is not yet fully implemented to be fully faithful to the CECOLOR variable's description in the documentation; I am blindly emitting the rgb form 
        # of the string rather than properly emitting the colr index or color books pecification as applicable.
        return "RGB:{:d},{:d},{:d}".format(self.red, self.green, self.blue)        

class NullableColor(object):
    def __init__(red: int, green: int, blue: int, isNull: bool = False):
        self.red    = red
        self.green  = green
        self.blue   = blue
        self.isNull = isNull

class AcadPlotstyle (object):
    def __init__(self, owner: AcadPentable,
        name                  = "Normal",
        localized_name        = None,
        description           = "",
        color                 = PentableColor(red=255, green=255, blue=255, colorMethod=195), #-1006632961,
        mode_color            = PentableColor(red=255, green=255, blue=255, colorMethod=195), #-1006632961,
        color_policy          = ColorPolicy.ENABLE_DITHERING,
        physical_pen_number   = 0,     
        virtual_pen_number    = 0,      
        screen                = 100,  
        linepattern_size      = 0.5,
        linetype              = LineType.USE_OBJECT_LINETYPE,
        adaptive_linetype     = True,                         
        lineweight            = 0,
        fill_style            = FillStyle.USE_OBJECT_FILL_STYLE, 
        end_style             = EndStyle.USE_OBJECT_ENDSTYLE,   
        join_style            = JoinStyle.USE_OBJECT_JOINSTYLE
        ):
        self.owner = owner

        self.name                  = str(name)
        self.localized_name        = str(localized_name if localized_name else self.name) 
        self.description           = str(description)
        self.color                 = PentableColor(color)
        self.mode_color            = ( None if mode_color == None else PentableColor(mode_color))           
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

        self._explicitColor = NullableColor( *((self.color if self.mode_color == None else self.mode_color).getRgbTuple()), isNull=self.colorOverride ) 


    )


        # the 'color' property is an signed 32-bit integer, which we interpret by converting it into a list of byte values (assuming little-endian and 2's complement)
        # the bytes are of the form [b, g, r, 195], where r, g, b are integers in the range [0,255] representing the usual rgb components.
        # the "use object color" value for color that is pickable in the AutoCAD user interface corresponds to [255, 255, 255, 195].
        # This means that, as far as I can tell, there is no way to specify literally red=255, green=255, blue=255 (Come on now, Autodesk -- you should be embarassed.  White lives matter too.)
        # the Oarx c++ header file dbcolor.h seems like it is probably related to the way that color is represented in the pentable files. 
        # The "195" value (aka 0xc3) is probably related to the AcCmEntityColor::ColorMethod.kByACI enum value that is decalred in that header file.
        # the 4-byte representation of color that we are seeing in the pentable file is likely the same as the AcCmEntityColor::mRGBM .  (whose type is a rather complicated union of ints and enums.)
        # 

    @staticmethod
    def createNewFromOwnerAndRawDictionary(owner: AcadPentable, rawDictionary: dict):
        return AcadPlotstyle(owner = owner,
            name                  = rawDictionary['name'                 ],
            localized_name        = rawDictionary['localized_name'       ],
            description           = rawDictionary['description'          ],
            color                 = rawDictionary['color'                ],
            mode_color            = rawDictionary.get('mode_color' , None),
            color_policy          = rawDictionary['color_policy'         ],
            physical_pen_number   = rawDictionary['physical_pen_number'  ],
            virtual_pen_number    = rawDictionary['virtual_pen_number'   ],
            screen                = rawDictionary['screen'               ],
            linepattern_size      = rawDictionary['linepattern_size'     ],
            linetype              = rawDictionary['linetype'             ],
            adaptive_linetype     = rawDictionary['adaptive_linetype'    ],
            lineweight            = rawDictionary['lineweight'           ],
            fill_style            = rawDictionary['fill_style'           ],
            end_style             = rawDictionary['end_style'            ],
            join_style            = rawDictionary['join_style'           ]
        )

    # for dealing with the PlotStyle.control_policy property and whether or not we make mode_color white,
    # we have to take pains, because the mapping from these four controllable 1-bit levers
    # to the observable behaviors which those bits control is non-intuitive, to say the least,
    # and there are even some (easily) conceivable behaviors that are (infuriatingly) unacheivable.

    # a control state is a 4-bit number encoding the four bits that we can control directly, namely:
    # (modeColorIsWhite, EXPLICIT_OVERRIDE bit of color_policy (a.k.a. the eBit) , CONVERT_TO_GRAYSCALE bit of color_policy (aka gBit), ENABLE_DITHERING bit of color_policy (aka dBit))
    # the bits of the ColorPolicy enum values are only very loosely related to the behaviors for which they are named 
    # -- hence the need for this elaborate mapping system.
    # We assign unique integer index i to each member of the control state space, constructed 
    # thus: i = modeColorIsWhite*8 + eBit*4 + gBit*2 + dBit*1
    # (note: each of these dimensions has 2 possible values, which we encode as 0 or 1, in the usual way)

    # a behavior state is a member of the cartesian product between three dimensions:
    #   colorOverride: this has three possible (imaginable) values: 
    #       0: don't override
    #       1: override to some color other than white
    #       2: override to white
    #   grayscale:
    #       0: no
    #       1: yes
    #   dither:
    #       0:no
    #       1:yes
    #
    # We assign a unique integer index i to each member of the behavior state space, constructed 
    # thus: i = colorOverride*4 + grayscale*2 + dither*1

    # here is a map between controlStates and behaviorStates, worked out empirically.
    # this is intended to be const
    # notice that behavior states 8, 9, 10, and 11 (which correspond to colorOverride == 2), are unreachable (AutoCAD won't let you override to white)
    colorControlStatesToColorBehaviorStates = {
        0  : 4 ,
        1  : 1 ,
        2  : 6 ,
        3  : 7 ,
        4  : 4 ,
        5  : 5 ,
        6  : 1 ,
        7  : 1 ,
        8  : 0 ,
        9  : 1 ,
        10 : 2 ,
        11 : 3 ,
        12 : 0 ,
        13 : 1 ,
        14 : 1 ,
        15 : 1 
    } 

    def toRawDictionary(self) -> dict:
        return {
            **{
                'name'                  : self.name                    ,
                'localized_name'        : self.localized_name          ,
                'description'           : self.description             ,
                'color'                 : self.color.acadRgbqColorInt               
            }, 
            **({} if self.mode_color == None else {'mode_color': self.mode_color.acadRgbqColorInt }),
            **{
                'color_policy'          : self.color_policy        ,
                'physical_pen_number'   : self.physical_pen_number ,
                'virtual_pen_number'    : self.virtual_pen_number  ,
                'screen'                : self.screen              ,
                'linepattern_size'      : self.linepattern_size    ,
                'linetype'              : self.linetype            ,
                'adaptive_linetype'     : self.adaptive_linetype   ,
                'lineweight'            : self.lineweight          ,
                'fill_style'            : self.fill_style          ,
                'end_style'             : self.end_style           ,
                'join_style'            : self.join_style          
            }
        }

    def toHumanReadableDictionary(self) -> dict:
        # we convert some of the hard-to-interpret values (like the enums) into strings that are meaningful to the human reader
        return {
            **{
                'name'                  : self.name                      ,
                'localized_name'        : self.localized_name            ,
                'description'           : self.description               ,
                'color'                 : self.color.humanReadableString  
            },  
            **({} if self.mode_color == None else {'mode_color': self.mode_color.humanReadableString}),
            **{
                'color_policy'          : repr(self.color_policy)   ,
                'physical_pen_number'   : self.physical_pen_number ,
                'virtual_pen_number'    : self.virtual_pen_number  ,
                'screen'                : self.screen              ,
                'linepattern_size'      : self.linepattern_size    ,
                'linetype'              : repr(self.linetype)      ,
                'adaptive_linetype'     : self.adaptive_linetype   ,
                'lineweight'            : ("(use object lineweight)" if self.lineweight == 0 else "custom_lineweight_table[" + str(self.lineweight - 1) + "], which is " + str(self.owner.custom_lineweight_table[self.lineweight - 1])) ,
                'fill_style'            : repr(self.fill_style)    ,
                'end_style'             : repr(self.end_style)     ,
                'join_style'            : repr(self.join_style)         
            }
        }

    


























    @property
    def colorControlState(self) -> int:
        # returnValue = 0
        # returnValue = set_bit(returnValue, 3, self.modeColorIsWhite                                )
        # returnValue = set_bit(returnValue, 2, self.color_policy & ColorPolicy.EXPLICIT_COLOR       )
        # returnValue = set_bit(returnValue, 1, self.color_policy & ColorPolicy.CONVERT_TO_GRAYSCALE )
        # returnValue = set_bit(returnValue, 0, self.color_policy & ColorPolicy.ENABLE_DITHERING     )
        # return returnValue

        #or, equivalently:
        return (
               ( 8 if self.modeColorIsWhite                                 else 0 )
            +  ( 4 if self.color_policy & ColorPolicy.EXPLICIT_COLOR        else 0 )
            +  ( 2 if self.color_policy & ColorPolicy.CONVERT_TO_GRAYSCALE  else 0 )
            +  ( 1 if self.color_policy & ColorPolicy.ENABLE_DITHERING      else 0 )
        )


    @colorControlState.setter
    def colorControlState(self, x):
        
        self.color_policy = (
              (ColorPolicy.EXPLICIT_COLOR        if get_bit(x,2) else ColorPolicy(0))
            | (ColorPolicy.CONVERT_TO_GRAYSCALE  if get_bit(x,1) else ColorPolicy(0))
            | (ColorPolicy.ENABLE_DITHERING      if get_bit(x,0) else ColorPolicy(0))
        )

        if bool(self.modeColorIsWhite) != bool(get_bit(x, 3)):
            print("warning: in order to achieve the requested colorControl

        










    @property
    def modeColorIsWhite(self) -> bool:
        return (
            (self.mode_color.red == 255) 
            and (self.mode_color.green == 255) 
            and (self.mode_color.blue == 255 )
        )

    def setModeColorToWhite(self):
        self.mode_color.setRgb(255,255,255)

    def setModeColorRgb(self, *args):
        self.mode_color.setRgb(*args)

    

    @property 
    def explicitlyOverrideTheColor(self) -> bool:
        

    @explicitlyOverrideTheColor.setter
    def explicitlyOverrideTheColor(self, x: bool):





    @property 
    def grayscale(self) -> bool:
        # a lookup table for all possible values of self.color_policy, 
        # which seems to be the only part of a plotStyle that has any bearing on whether AutoCAD performs the "convert to grayscale" behavior.
        # return (
        #     {
        #        (ColorPolicy.EXPLICIT_COLOR & 0 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 0 )|(ColorPolicy.ENABLE_DITHERING & 0 ): False,
        #        (ColorPolicy.EXPLICIT_COLOR & 0 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 0 )|(ColorPolicy.ENABLE_DITHERING & 1 ): False,
        #        (ColorPolicy.EXPLICIT_COLOR & 0 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 1 )|(ColorPolicy.ENABLE_DITHERING & 0 ): True,
        #        (ColorPolicy.EXPLICIT_COLOR & 0 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 1 )|(ColorPolicy.ENABLE_DITHERING & 1 ): True,
        #        (ColorPolicy.EXPLICIT_COLOR & 1 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 0 )|(ColorPolicy.ENABLE_DITHERING & 0 ): False,
        #        (ColorPolicy.EXPLICIT_COLOR & 1 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 0 )|(ColorPolicy.ENABLE_DITHERING & 1 ): False,
        #        (ColorPolicy.EXPLICIT_COLOR & 1 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 1 )|(ColorPolicy.ENABLE_DITHERING & 0 ): False,
        #        (ColorPolicy.EXPLICIT_COLOR & 1 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 1 )|(ColorPolicy.ENABLE_DITHERING & 1 ): False
        #     }
        # )[self.color_policy]
        return ( 
            {
                (False , False , False): False ,
                (False , False , True ): False ,
                (False , True  , False): True  ,
                (False , True  , True ): True  ,
                (True  , False , False): False ,
                (True  , False , True ): False ,
                (True  , True  , False): False ,
                (True  , True  , True ): False

            }[(
                bool(self.color_policy & ColorPolicy.EXPLICIT_COLOR         ),
                bool(self.color_policy & ColorPolicy.CONVERT_TO_GRAYSCALE   ),
                bool(self.color_policy & ColorPolicy.ENABLE_DITHERING       )
            )]
        )

    @grayscale.setter
    def grayscale(self, x: bool) -> bool:

        return self.grayscale


    @property 
    def dither(self) -> bool:
        # a lookup table for all possible values of self.color_policy, 
        # which seems to be the only part of a plotStyle that has any bearing on whether the AutoCAD does the "dither" behavior.
        # My only observable for deciding whether "AutoCAD does the "dither" behavior" is the On/Off readout in the pen table editor ui.
        # In my tests, niether the ENABLE_DITHERING bit nor the value of the On/Off "Dither" readout in the pentable ui
        # had any coprrespondence with anything in autoCAD on the screen or in the pdf plot.
        # therefore, I have designed this function to return the "Dither" status that the pentable editor ui would show the user,
        # which (if the other prperties are any guide) might not be quite the same thing as the "dither" behavior that AutoCAD would do while plotting
        # (which, I imagine, only happens with certain special plotter configurations and plotter drivers, but does not happen with the default AutoCAD pdf printer drivers.)
        #
        # return (
        #     {
        #        (ColorPolicy.EXPLICIT_COLOR & 0 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 0 )|(ColorPolicy.ENABLE_DITHERING & 0 ): False,
        #        (ColorPolicy.EXPLICIT_COLOR & 0 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 0 )|(ColorPolicy.ENABLE_DITHERING & 1 ): True,
        #        (ColorPolicy.EXPLICIT_COLOR & 0 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 1 )|(ColorPolicy.ENABLE_DITHERING & 0 ): False,
        #        (ColorPolicy.EXPLICIT_COLOR & 0 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 1 )|(ColorPolicy.ENABLE_DITHERING & 1 ): True,
        #        (ColorPolicy.EXPLICIT_COLOR & 1 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 0 )|(ColorPolicy.ENABLE_DITHERING & 0 ): False,
        #        (ColorPolicy.EXPLICIT_COLOR & 1 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 0 )|(ColorPolicy.ENABLE_DITHERING & 1 ): True,
        #        (ColorPolicy.EXPLICIT_COLOR & 1 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 1 )|(ColorPolicy.ENABLE_DITHERING & 0 ): True,
        #        (ColorPolicy.EXPLICIT_COLOR & 1 )|(ColorPolicy.CONVERT_TO_GRAYSCALE & 1 )|(ColorPolicy.ENABLE_DITHERING & 1 ): True
        #     }

        # )[self.color_policy]
        return ( 
            {
                (False , False , False): False ,
                (False , False , True ): True  ,
                (False , True  , False): False ,
                (False , True  , True ): True  ,
                (True  , False , False): False ,
                (True  , False , True ): True  ,
                (True  , True  , False): True  ,
                (True  , True  , True ): True

            }[(
                bool(self.color_policy & ColorPolicy.EXPLICIT_COLOR         ),
                bool(self.color_policy & ColorPolicy.CONVERT_TO_GRAYSCALE   ),
                bool(self.color_policy & ColorPolicy.ENABLE_DITHERING       )
            )]
        )
    
    @dither.setter
    def dither(self, x: bool) -> bool:
        if x != self.dither:
            

        return self.dither




# It seems that the AutoCAD pentable editor acts so as to keep plotStyle.color set to the index color that is nearest to the selected
# rgb color (i.e. autoCAD sets the rgb values of plotStyle.color to the rgb values that match some index color, and AutoCAD sets plotStyle.color.colorMethod = ColorMethod.BY_ACI)
# 
#  The user interface logic for selecting color seems to be as follows: 
# the result of the user picking a color from the color dropdown box 
# (including the case where the user clicks  the "select color" item in the dropdown and goes through the color selection dialog) is a 
# triple of bytes: the red, green, blue values, which we will call r, g, and b, below, and a boolean choice of whether or not to "use object color"
# AutoCAD then does the following:
# 1: plotStyle.mode_color.setRgb(r,g,b)
# 2: if the user chose use_object_color=true or if the user chose r=g=b=255, then clear the EXPLICIT_COLOR bit of plotStyle.color_policy, else set the EXPLICIT_COLOR bit of plotStyle.color_policy.
#       in our python-based domain-specific-language, this would look like:
#       plotStyle.color_policy = (plotStyle.color_policy  & ~ColorPolicy.EXPLICIT_COLOR) | (0 if <the user chose "use object color"> else ColorPolicy.EXPLICIT_COLOR) 
# 3: plotStyle.mode_color.colorMethod = ( <does the triple of bytes exactly match some index color> ? ColorMethod.BY_ACI : ColorMethod.BY_COLOR );
# 4: if <does the triple of bytes exactly match some index color> { 
#   display the color in the interface as "Color 112", for instance, or "Red", etc. ;
# } else { 
#   display the color in the interface as "132,87,66" (or the like) ;
# }
# 5: plotStyle.color = <index color that most closely matches the triple of bytes> ; // the 'index color', here, always has colorMethod == BY_ACI
# 
# Based on what the interface shows when I open a specially-contrived pen table that has some plot styles that whose color and mode_color values are other
# than how the pentable editor would have made them, I suspect the following hypothesis:
# The complete set of information that the user perceives to be controlled by and displayed in the "color" dropdown box in the ui
# (naively: byte red, byte blue, byte green, bool USE_OBJECT_COLOR (where the red, green, and blue bytes being relevant only when USE_OBJECT_COLOR is false)
# is entirely represented by the following:
# the 'EXPLICIT_COLOR' bit of plotStyle.color_policy  (low corresponds with the user seeing "use object color" in the ui)
# plotStyle.mode_color.red
# plotStyle.mode_color.green
# plotStyle.mode_color.blue
# 
# I suspect that we could exercise effectively complete programmatic control of the 'color' property of a plot style 
# (i.e. acheive every functional outcome that could be acheived with the ui)
# by attending only to plotStyle.mode_color.red, plotStyle.mode_color.green, plotStyle.mode_color.blue, and the EXPLICIT_COLOR bit of 
# plotStyle.color_policy, and that we could completely ignore plotStyle.color and plotStyle.mode_color.colorMethod.
#
# In other words, I suspect that our mission of being able to do complte programmatic manipulation of a pentable file 
# does not require us to reproduce all 5 steps of the ui's color-setting logic that I described above.
# Rather, we can get away doing only steps 1 and 2, and ignore the rest of the steps, whose only purpose is 
# to update plotStyle.color and  plotStyle.mode_color.colorMethod according to the user's choice.
#
# One quirk to the way AutoCAD displays the color (as text) in the interface is that the index colors that 
# do not have names (e.g. color 12, whose rgb representation is 221,0,0) are displayed in rgb format when the 
# plot style editor first opens.  Only after you manipulate the plot style's 'color' dropdown box does AutoCAD "realize"
# that the color is an index color and so changes the display from "221,0,0" to "Color 12" (for instance).
#
#  The result of the "or if the user chose r=g=b=255" expression in the above pseudo-code is that it is impossible in the ui to explcitly specify an
# explicit color that is pure white (i.e. r=g=b=255).
# if we attempt to speicify pure white programmataically and then open the resulting pentable file in that autoCAD pen table editor,
# the pen table editor ui shows "use object color" just as it does when we attempted to make the change in the ui, which suggests
# (but further testing is still in order) that the end result when plotting will be to "use object color".



# programattically setting color_policy to each possible ColorPolicy (with the color set to an arbitrary non-index RGB color
# (red=2,green=4,blue=6)
# to ensure that the weirdness with an rgb color of 255,255,255 corresponding to "use object color" doesn't obscure the 
# action of the EXPLICIT_COLOR bit), we have the following observed in the user interface:

# e for (E)xplicit color
# g for convert to (G)rayscale
# d for (D)ithering.
# uppercase means the bit is high.  lowercase means the bit is low.
#
#                              ||---------------------------------------||--------------------------------------------------------|
#                              || displayed in the pentable editor's    || visible result on the screen                           |
#                              || user interface                        || in AutoCAD, with bright green/light                    |
#                              ||                                       || gray corresponding to NOT "use object                  |
#                              ||                                       || color"                                                 |
#                              ||                                       || and dark red/dark gray corresponding                   |
#                              ||                                       || to "use object color"                                  |
#                              ||                                       || and gray of any intensity                              |
#                              ||                                       || corrsponding to                                        |
#                              ||                                       || "convert to grayscale:on"                              |
#   |===========|==============||==================|========|===========||==================|========|===========||===============|
#   | rgb color | color_policy || Color            | Dither | Grayscale || color was over-  | Dither | Grayscale || subjectively  |               
#   |           |              ||                  |        |           || ridden by the    |        |           || appreciated   |               
#   |           |              ||                  |        |           || plot style       |        |           || color         |        
#   |-----------|--------------||------------------|--------|-----------||------------------|--------|-----------||---------------|
#   | 00FA00    | egd          || Use object color | Off    | Off       || overridden       | ???    | Off       || bright green  |                
#   | 00FA00    | egD          || Use object color | On     | Off       || use object color | ???    | Off       || dark red      |                   
#   | 00FA00    | eGd          || 0,250,0          | Off    | On        || overridden       | ???    | On        || light gray    |              
#   | 00FA00    | eGD          || 0,250,0          | On     | On        || overridden       | ???    | On        || light gray    |                                                          
#   | 00FA00    | Egd          || 0,250,0          | Off    | Off       || overridden       | ???    | Off       || bright green  |                                       
#   | 00FA00    | EgD          || 0,250,0          | On     | Off       || overridden       | ???    | Off       || bright green  |                              
#   | 00FA00    | EGd          || Use object color | On     | Off       || use object color | ???    | Off       || dark red      |                                                                        
#   | 00FA00    | EGD          || Use object color | On     | Off       || use object color | ???    | Off       || dark red      |                   
#   |-----------|--------------||------------------|--------|-----------||------------------|--------|-----------||---------------|  
#   | FFFFFF    | egd          || Use object color | Off    | Off       || use object color | ???    | Off       || dark red      |                   
#   | FFFFFF    | egD          || Use object color | On     | Off       || use object color | ???    | Off       || dark red      |                   
#   | FFFFFF    | eGd          || Use object color | Off    | On        || use object color | ???    | On        || dark gray     |                   
#   | FFFFFF    | eGD          || Use object color | On     | On        || use object color | ???    | On        || dark gray     |                                                   
#   | FFFFFF    | Egd          || Use object color | Off    | Off       || use object color | ???    | Off       || dark red      |                                     
#   | FFFFFF    | EgD          || Use object color | On     | Off       || use object color | ???    | Off       || dark red      |                                      
#   | FFFFFF    | EGd          || Use object color | On     | Off       || use object color | ???    | Off       || dark red      |                                                         
#   | FFFFFF    | EGD          || Use object color | On     | Off       || use object color | ???    | Off       || dark red      |                                                
#   |===========|==============||==================|========|===========||==================|========|===========||===============|   
#
#
#   | unachievable  :                              |                     |                                          
#   |===========|==============||==================|========|===========||  
#   | 00FA00    |              || Use object color | Off    | On        ||
#   | 00FA00    |              || Use object color | On     | On        ||
#   |-----------|              ||------------------|--------|-----------||
#   | FFFFFF    |              || 255,255,255      | Off    | Off       ||                                    
#   | FFFFFF    |              || 255,255,255      | Off    | On        ||                                                                                    
#   | FFFFFF    |              || 255,255,255      | On     | Off       ||                                  
#   | FFFFFF    |              || 255,255,255      | On     | On        || 
#   |-----------|--------------||------------------|--------|-----------||
#
# the user interface states marked "unachievable" above cannot be acheived
# by programmatically manipulating the plotStyle.color_policy value
# and cannot be achieved by manually manipulating controls in the user interface.
#
# The basic conept is: the d and g bits behave exactly as expected (affecting the Dither
# and Grayscale field values in the naive, expected way) except when:
# e is high and g is high, 
# in which case the Grayscale field shows "Off" (despite the g bit being high)
# and the Dither field shows "On" (even when the d bit is low)

# I am beginning to think that the e bit is not exactly an "EXPLICIT_COLOR" bit.
# it is more like a "user has attempted to set the color explicitly" bit -- no not quite nevermind.


# Here's the deal:
# all the color policy bits work exactly as expected except for the following exceptions:

# If I want to explicitly set the color (which, naively means set e high)
# and want convert_to_grayscale to be on, then I must, counterintuitevly, set e low.  Bizarre!
#
# If I want to leave color unspecified (i.e. I want 'Use object color')
# (which, naively, means set e low), and want convert_to_grayscale to be on,
# then I must change the color to 255,255,255
#
# Said another way: all the color policy bits work as expected with the following exceptions:
# 1: If I want to explcitly set the color to white (r=255,b=255,g=255), then I am out of luck (niether programmatically nor using the ui will cause 'white' or 255,255,255 to appear in the UI)
# 2: If want convert_to_grayscale to be on, in which case:
# to achieve an explicitly set color, I must (counter-intuitively) set the e bit low (even though, naively, I would think I should set e high)
# to achieve an inherited color (i.e. "Use object color"), I must set the rgb color value to 255,255,255 (even though, naively, I would think that if I am inheriting 
# a color value, then the rgb color value would be irrelevant).
# 
# That is annoying and bizarre, but tolerable, so far as it goes.  What I am having a really hard time
# understanding are the results of violating rule 2; if I want convert_to_grayscale to be on, but I forget the rule and naively set the G bit high, then
# if I am attempting to have an explicitly set color (i.e. e high), the actual result will be that convert_to_grayscale 
# will be off and color will be shown as "use object color" and "Dither" will be "On" (even if I set d low),
# and if, instead, I am attempting to have an inherited color (a.k.a "use object color")(i.e. e low), the actual result will 
# be that the rgb values of my color will appear in the "color" field of the user interface
#  (unless of course my color happens to be 255,255,255).
#
# What is going on under the hood in the AutoCAD pen table editor (and presumably in other parts of AutoCAD) that would cause this bizarre behavior?
# Even if there is something screwed up about the case where the user wants to explicitly set a white color, how does the "white" weirdness
# disrupt the connection between the d bit and the "Dither" user interface setting?
# It is almost as if, in the process of displaying a given plotstyle in the user interface, AutoCAD first throws up a default display (which has dithering on)
# Then, AutoCAD starts reading through the plotstyle data in the file.  When AutoCAD sees that the e bit is low but the color is not 255,255,255, AutoCAD "freaks out" and 
# decides to stop reading the rest of the plotstyle data and simply leaves the default display (including the "dithering:on" readout) up on the screen.... or something like that
# OR, alternatively, is there some legitimate reason why dithering and grayscale should have any interaction with one another? 
#
# If we suppose that AutoCAD encodes the "explcitly_override_the_color" flag by putting exactly 1 high bit in the pair of slots (g and e)
# and that AutoCAD encodes whether to "convert_to_grayscale" by deciding WHICH of the two slots the 1 high bit goes into (put the high bit in g to mean "convert_to_grayscale",
# and put the high bit in e to mean "don't convert to grayscale"), then, under that account, it seems that what really makes autocad freak out is having both the G and the E bits being high.
# If they are both high, autoCAD "freaks out" (as suggested above) and leaves the "default" vlaues displayed: "use object color", "dither:on", "grayscale:off".
#  
# That account starts to make sense.  
# continuing to think along those lines, autoCAD has no way to encode simultaneously "grayscale:on" and "use object color".
# So, (as if it were someone's half-baked work-around to an edge case, or to maintain backward compatibility somewhere), they adopted 
# the convention that a color of 255,255,255 (because who is ever going to want to explicitly set a white color? (admittedly, it is perhaps the least likely color that
# one would want to explicitly set)) will force a meaning of "use object color", so that we can now encode both  "grayscale:on" and "use object color" 
# by instead encoding "grayscale:on" and "explicitly override the color to white".
# That is perhaps the most reasonable explanation that I can come up with, but still, what nonsense!


# this function is more annotational than functional.
def lineweightConceptReport():
    # reason about lineweights chosen in a geometric series (which the autocad lineweights and the iso standard linewights are based on)
    baseLineThickness = 0.25
    #0.01*25.4 # 0.25 # 0.13 # units are millimeters
    # the errors for indices 0..6 are all 0.0 steps when we take baseLineThickness to be 0.25.  This suggests that AutoCAD's original "preference" was to use 0.25 millimeters as the base line width.
    stepFactorJumpSize = 1 
    stepFactor = 2**(1/2 * stepFactorJumpSize)
    indices = range(-10,11)
    arbitraryLineThicknessFormat="{:6.3f}"
    standardLineThicknessFormat="{:6.2f}"
    logErrorFormat="{:+4.1f}"
    indexFormat="{:>3d}"

    print("preferred line thickness series:")
    print("stepFactor: " + "{:12.6f}".format(stepFactor))

    # positiveStandardLineThicknesses = list(filter( lambda x: x>0, defaultLineweightTable  ))
    positiveStandardLineThicknesses = list(filter( lambda x: x>0, classicLineweights  ))

    for i in indices:
        thisLineThickness = baseLineThickness * stepFactor ** i
        # nearestStandardThickness = min(defaultLineweightTable, key= lambda standardThickness: abs(math.log(standardThickness) - math.log(thisLineThickness))  ) # would it be equivalent to simply look at the abs of the (plain-old) difference between standardThickness and thisLineThickness? (no, because the "half-way point" between two adjacent standard thicknesses is different in the log differnece vs. plain-old difference cases.  of course, for very small differences, it wouldn't make much  of a difference (so to speak))
        nearestStandardThickness = min( 
            positiveStandardLineThicknesses, 
            key= lambda standardThickness: abs(math.log(standardThickness) - math.log(thisLineThickness))  # would it be equivalent to simply look at the abs of the (plain-old) difference between standardThickness and thisLineThickness? (no, because the "half-way point" between two adjacent standard thicknesses is different in the log differnece vs. plain-old difference cases.  of course, for very small differences, it wouldn't make much  of a difference (so to speak))  
        ) 
        logError = math.log(nearestStandardThickness, stepFactor) - math.log(thisLineThickness, stepFactor)
        
        print(
            "\t" + indexFormat.format(i) + ": " 
            # + arbitraryLineThicknessFormat.format(thisLineThickness) + " --> " 
            +  ( standardLineThicknessFormat.format(nearestStandardThickness)  + " (error: " + logErrorFormat.format(logError) + " steps)" 
                if abs(logError)<0.5 else 
                "unachievable among the standard line thicknesses"
            )
        )

    print("standard line thickness series:")
    for standardThickness in positiveStandardLineThicknesses:
        degree = math.log(standardThickness, stepFactor) -  math.log(baseLineThickness, stepFactor) 
        print( "\t" + standardLineThicknessFormat.format(standardThickness) + " is degree " + "{:+4.2f}".format(degree))


    # with:
    #   baseLineThickness = 0.25 millimeter
    #   stepFactorJumpSize = 1
    #   stepFactor = 2**(1/2 * stepFactorJumpSize)
    # we say that the degree i line thickness is the value in classicLineweights that is nearest (in a log sense) to
    # baseLineThickness * stepFactor**i
    # the set of classicLineweights contains reasonably close matches for degrees -4, ..., 6
    # The goal is to restrict ourselves to using only the following 11 lineweights, and, even within this limited list,
    # we should try to prefer lineweights of even degree, only reseorting to odd-degree lineweights in special cases where an intermediate thickness is needed.
    # By sticking to this scheme (which can be adjusted if needed by starting with a different baseLineThickness value), we will produce drawings 
    # with a small finite number of visually-distinct lineweights.
    # the idea is that the perceived psychometric change from one degree of thickness to the next should be roughly uniform for all degrees.
    preferredLineThicknessesByDegree = {
        -4:   0.05,
        -3:   0.09, 
        -2:   0.13,  
        -1:   0.18,  
        0:   0.25,  
        1:   0.35,  
        2:   0.50,  
        3:   0.70,  
        4:   1.00,  
        5:   1.40,  
        6:   2.00  
    }



###   # round trip file consistency test.
###   pathOfRoundTripGeneration0 = input_acad_pen_table_file_path
###   pathOfRoundTripGeneration1 = output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.stem + "-roundTrip1").with_suffix(input_acad_pen_table_file_path.suffix)
###   pathOfRoundTripGeneration2 = output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.stem + "-roundTrip2").with_suffix(input_acad_pen_table_file_path.suffix)
###   pathOfRoundTripGeneration3 = output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.stem + "-roundTrip3").with_suffix(input_acad_pen_table_file_path.suffix)
###   
###   AcadPentable(pathOfRoundTripGeneration0).writeToFile(pathOfRoundTripGeneration1)
###   AcadPentable(pathOfRoundTripGeneration1).writeToFile(pathOfRoundTripGeneration2)
###   AcadPentable(pathOfRoundTripGeneration2).writeToFile(pathOfRoundTripGeneration3)
###   
###   
###   # How does a pentable file change as it takes a (nominally non-modifying) round trip through
###   # this script or through the autoCAD pentable editor.
###   # "==T==>" means "open in the AutoCAD pen table editor, then click "save and close"".  (a round trip through the auTocad (T) editor)
###   # "==N==>" (right-pointing arrow) or "\N/" (down-pointing arrow) means a round trip through this (Neil's (N)) python script.
###   # the hashes I use below are a truncation of the sha1 hash, keeping the first few bytes as needed to ensure uniqueness.
###   
###   # a06627d8: the factory-original acad.stb file
###   # b04bd8fe: the factory-original acad.ctb file
###   # 1c03a1ea: an arbitrary stb file from an arbitrary project
###   
###   #  a06627d8 ==T==> 02503499 ==T==> a002fca8 ==T==> a002fca8
###   #    \N/
###   #  4b3f061a ==T==> 02503499 ==T==> a002fca8 ==T==> a002fca8
###   #    \N/
###   #  4b3f061a ==T==> 02503499 ==T==> a002fca8
###   #    \N/
###   #  4b3f061a ==T==> 02503499 ==T==> a002fca8
###   
###   #  b04bd8fe ==T==> d59c374a ==T==> e044dfd4 ==T==> e044dfd4
###   #    \N/
###   #  b2a316e6 ==T==> d59c374a ==T==> e044dfd4 ==T==> e044dfd4
###   #    \N/
###   #  b2a316e6 ==T==> d59c374a ==T==> e044dfd4
###   
###   #  1c03a1ea ==T==> 1c03a1ea ==T==> 1c03a1ea ==T==> 1c03a1ea
###   #    \N/
###   #  e0d21e21 ==T==> 1c03a1ea ==T==> 1c03a1ea ==T==> 1c03a1ea
###   #    \N/
###   #  e0d21e21 ==T==> 1c03a1ea ==T==> 1c03a1ea
###   
###   # very, very strange.  It is not hugely surprising that a round trip through this script is not entirely equivalent to a round 
###   # trip throught he autocad pen table editor
###   # (I think I remember noticing an extra null byte on the end of the payload that acad adds and this script does not (or vice versa))
###   # it is also not hugely surprising (although rather bad practice) that some of the factory-original pen table files
###   # might have been composed in an earlier/non-standard version of the pentable editor, and therefore require a single trip through the 
###   # acad editor to settle down.
###   # But, what is very weird is a06627d8 and b04bd8fe (the factory original acad.stb and acad.ctb files, respectively), which only settles down after TWO trips through the 
###   # acad editor.  This means that there exists at least one input that requires more than one round trip through the acad editor before
###   # settling down -- what is the acad editor doing that would require more than one trip to settle down?
###  In the factory-original stb file, the 'color' property of each plotstyle is [255, 255, 255, 255] and there is no mode_color property.
# On the first round-trip through the autocad pentable editor, the 'coolor' properties are changed to [255, 255, 255, 195] and a mode_color = [255, 255, 255, 255] property is added to each plot style.
# On the second round-trip through the acad pen table editor, the 'mode color properties are changed to [255, 255, 255, 195].
# There appear to be no other changes to the data occuring while taking the factory-original acad.stb round-tripping throuigh the acad editor.
# it seems, therefore, that when the acad editor needs to add a new color or mode_color property, it uses a value of [255, 255, 255, 255], and
# that, upon encountering an exiting color or mode_color properrty value in which the first byte is 255 (and, probably, anything other than 195), acad changes the first byte to 195.
# that theory explains (but does not excuse) why it takes two round-trips through the acad pentable eitor for the factory-originalacad.stb file to settle down.
#  The exact same thing is happening with the factory-original ctb file.
#
#  Perhaps the "mode_color" property is a relatively new invention that was not included with the factory-original pentable files, which are probably ancient 
# (the factory-original acad.stb and acad.ctb have a filesystem timestamp of 1999 and 2016, respectively, on my computer,
# but that could be meaningless)
# the "195" (aka 0xc3) is probably related to the AcCmEntityColor::colorMethod enum (see http://help.autodesk.com/view/OARX/2021/ENU/?guid=OARX-RefGuide-AcCmEntityColor__colorMethod_const)
# ( and the related .NET enum Autodesk.AutoCAD.Colors.ColorMethod (see http://help.autodesk.com/view/OARX/2021/ENU/?guid=OARX-ManagedRefGuide-Autodesk_AutoCAD_Colors_ColorMethod)).  
# Notably, Autodesk.AutoCAD.Colors.ColorMethod.ByAci is 0xc3.
# I think "ACI" stand for "Auotcad color index"

# the C# code that defines the .NET enum is :
#  public enum ColorMethod {
#    ByAci = 0xc3,
#    ByBlock = 0xc1,
#    ByColor = 0xc2,
#    ByLayer = 0xc0,
#    ByPen = 0xc4,
#    Foreground = 0xc5,
#    LayerFrozen = 0xc7,
#    LayerOff = 0xc6,
#    None = 200
#  }

#from the Oarx header file dbcolor.h: 
# class AcCmEntityColor
# {
# public:
#     enum Color { kRed,
#                  kGreen,
#                  kBlue
#     };
# 
#     // Color Method.
#     enum ColorMethod {   kByLayer =0xC0, 
#                          kByBlock,
#                          kByColor,
#                          kByACI,
#                          kByPen,
#                          kForeground,
#                          kLayerOff,
#                          // Run-time states
#                          kLayerFrozen,
#                          kNone
#     };
# 
#     enum ACIcolorMethod {kACIbyBlock    = 0,
#                          kACIforeground = 7,
#                          kACIbyLayer    = 256,
#                          // Run-time states
#                          kACIclear      = 0,    
#                          kACIstandard   = 7,
#                          kACImaximum    = 255,
#                          kACInone       = 257,
#                          kACIminimum    = -255,
#                          kACIfrozenLayer= -32700
#     };
# ............
# private:
#     // Blue, green, red, and Color Method (byBlock, byLayer, byColor).
#     // Is stored that way for better performance. 
#     // This is an RGBQUAD layout
#     // https://docs.microsoft.com/en-us/windows/desktop/api/wingdi/ns-wingdi-tagrgbquad
#     //
#     // Note that color chanels in RGBQUAD are reversed from COLORREF (0x00bbggrr) 
#     // Note the dependency on struct layout: we assume that indirect does not
#     // overlap with colorMethod!
#     //
#     union {
#         Adesk::UInt32    whole;
#         Adesk::Int16     indirect;
#         struct {
#             Adesk::UInt8 blue,
#                          green,
#                          red,
#                          colorMethod;
#         } mdata;
#         Adesk::Int32    mnIndirect32;
#     } mRGBM;

