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



##########################################################################
###   BEGIN PEN TABLE LIBRARY (TO DO: make this a standalone module)  
##########################################################################
# color_policy bitmask values:
colorPolicies = {
    'enableDithering': 1,
    'convertToGrayscale': 2,
    'useObjectColor': 4
}
# bit 2 (use object color) is allowed to be high only when bit 1 (convert to grayscale) is low.

#end-style enum:
endStyles = {
    'butt': 0,
    'square': 1,
    'round': 2,
    'diamond':3,
    'useObjectEndStyle': 4
}

# The butt and square end styles are similar; both result in a straight edge perpendicular to the line.
# The difference is the location, along the line, of the edge.  With the 'butt' end style, the edge intersects the endpoint of the line.
# With the 'square' end style, the edge lies a distance lineThickness/2 beyond the endpoint of the line.
# Just as the 'round' end style can be conceived of as starting with the 'butt' end style and then adding a disc
# centered on the endpoint with the diameter of the disk being the line thickness, similarly, the 'square' 
# end style can be conceived as starting with the 'butt' end style and then adding a square, centered on the endpoint,
# with the inscribed diameter of the square being the line thickness, and with the square being oriented so that 
# (at least) one of its sides is parallel with the line.

#join-style enum
joinStyles = {
    'miter': 0,
    'bevel': 1,
    'round': 2,
    'diamond': 3,
    'useObjectJoinStyle':5
}

fillStyles = {
    'solid':64,
    'checkerboard':65,
    'crosshatch':66,
    'diamonds':67,
    'horizontalBars':68,
    'slantLeft':69,
    'slantRight':70,
    'squareDots':71,
    'verticalBars':72,
    'useObjectFillStyle':73
}

#the 'lineweight' property is as follows:
# 0 means "useObjectLineweight"
# any other integer n is a reference to custom_linewight_table[n-1]

# I include the defaultLineweightTable here as a descriptive reference (not prescriptive).
# AutoCAD will reconstruct the below values if the custom_lineweight_table property of the plot
# style is absent or if the custom_lineweight_table property has fewer than the standard number of entries.
defaultLineweightTable = [
        0.0,    #  0                 
        0.05,   #  1          
        0.09,   #  2          
        0.1,    #  3         
        0.13,   #  4          
        0.15,   #  5          
        0.18,   #  6          
        0.2,    #  7         
        0.25,   #  8          
        0.3,    #  9         
        0.35,   # 10          
        0.4,    # 11         
        0.45,   # 12          
        0.5,    # 13         
        0.53,   # 14          
        0.6,    # 15         
        0.65,   # 16          
        0.7,    # 17         
        0.8,    # 17         
        0.9,    # 18         
        1.0,    # 19         
        1.06,   # 20          
        1.2,    # 21         
        1.4,    # 22         
        1.58,   # 23          
        2.0,    # 24         
        2.11    # 25         
] 


# for reference, here is the LineWeight enum definition from the relevant oarx c++ header file:
# The integers that appear in the symbol names are in units of 10 microns.
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



lineTypes = {
    'solid'                              : 0 ,
    'dashed'                             : 1 ,
    'dotted'                             : 2 ,
    'dash_dot'                           : 3 ,
    'short_dash'                         : 4 ,
    'medium_dash'                        : 5 ,
    'long_dash'                          : 6 ,
    'short_dash_x2'                      : 7 ,
    'medium_dash_x2'                     : 8 ,
    'long_dash_x2'                       : 9 ,
    'medium_long_dash'                   : 10,
    'medium_dash_short_dash_short_dash'  : 11,
    'long_dash_short_dash'               : 12,
    'long_dash_dot_dot'                  : 13,
    'long_dash_dot'                      : 14,
    'medium_dash_dot_short_dash_dot'     : 15,
    'sparse_dot'                         : 16,
    'iso_dash'                           : 17,
    'iso_dash_space'                     : 18,
    'iso_long_dash_dot'                  : 19,
    'iso_long_dash_double_dot'           : 20,
    'iso_long_dash_triple_dot'           : 21,
    'iso_dot'                            : 22,
    'iso_long_dash_short_dash'           : 23,
    'iso_long_dash_double_short_dash'    : 24,
    'iso_dash_dot'                       : 25,
    'iso_double_dash_dot'                : 26,
    'iso_dash_double_dot'                : 27,
    'iso_double_dash_double_dot'         : 28,
    'iso_dash_triple_dot'                : 29,
    'iso_double_dash_triple_dot'         : 30,
    'use_object_linetype'                : 31
}

def getPenTableData(penTableFile):
    headerBytes = penTableFile.read(60)
    global payloadBytes
    compressedBytes=penTableFile.read()
    payloadBytes = zlib.decompress(compressedBytes)
    payloadString = payloadBytes.decode("ascii")

    nameAndPrimitiveValuePattern = re.compile(r"^\s*(?P<identifier>\w+)\s*=\s*(?P<rawvalue>.*)$")
    nameAndSubObjectPattern = re.compile(r"^\s*(?P<identifier>\w+)\s*{\s*$")
    subObjectTerminationPattern = re.compile(r"^\s*(}\s*)+$")


    data = payloadStringToPenTableObject(payloadString)

    # headerString = headerBytes.decode("raw_unicode_escape")
    # if headerString.encode("raw_unicode_escape") == headerBytes:
    #     print("original header was preserved.")
    # else:
    #     print("original header was corrupted.")

    #include the header of the original file as an item in the dictionary, with the special key "_header"
    data['_header'] = headerBytes.decode("raw_unicode_escape")

    mysteryBytes = headerBytes[headerBytes.find(b'\n') + 1 + len("pmzlibcodec"):]

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
    if 'plot_style' in data: data['plot_style'] = list(data['plot_style'].values())
    if 'custom_lineweight_table' in data: data['custom_lineweight_table'] = list(data['custom_lineweight_table'].values())

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

def payloadStringToPenTableObject(payloadString: str):
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

# penTableObject can be a dict or a list.  If it's a list, the result will be the same as passing
# a dict whose keys are the stringified int's 0,1,...,len(penTableObject)-1
def penTableObjectToPayloadString(penTableObject) -> str:
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

##########################################################################
###   END PEN TABLE LIBRARY
##########################################################################




######################################################################################
##  BEGIN  BUSINESS LOGIC
######################################################################################

parser = argparse.ArgumentParser(description="Generate a human-readable json representation of an autocad pen table (stb or ctb) file.")
parser.add_argument("--input_acad_pen_table_file", action='store', nargs=1, required=True, help="the .stb or .ctb file to be converted into human readable format")
parser.add_argument("--output_human_readable_pen_table_file", action='store', nargs=1, required=False, help="the human readable pen table file to be created.")
args, unknownArgs = parser.parse_known_args()
input_acad_pen_table_file_path = (pathlib.Path(args.input_acad_pen_table_file[0]).resolve() if args.input_acad_pen_table_file and args.input_acad_pen_table_file[0] else None)
output_human_readable_pen_table_file_path = (pathlib.Path(args.output_human_readable_pen_table_file[0]).resolve() if args.output_human_readable_pen_table_file and args.output_human_readable_pen_table_file[0] else None)
print("input_acad_pen_table_file_path is " + str(input_acad_pen_table_file_path))
print("output_human_readable_pen_table_file_path is " + str(output_human_readable_pen_table_file_path))






penTableData = getPenTableData(open(input_acad_pen_table_file_path, "rb"))
json.dump(penTableData, open(output_human_readable_pen_table_file_path, "w"), indent=4)



# insert my experimental plotStyle as the second item of the list
# myPlotStyle=copy.deepcopy(penTableData['plot_style'][0])
# myPlotStyle['name']                  = "standby--" + 
# myPlotStyle['localized_name']        = myPlotStyle['name']
# myPlotStyle['description']           = ""
# myPlotStyle['color']                 = -1006632961
# myPlotStyle['mode_color']            = -1006632961
# myPlotStyle['color_policy']          = colorPolicies['useObjectColor']
# myPlotStyle['physical_pen_number']   = 0     
# myPlotStyle['virtual_pen_number']    = 0      
# myPlotStyle['screen']                = 100  
# myPlotStyle['linepattern_size']      = 0.5
# myPlotStyle['linetype']              = lineTypes['use_object_linetype']
# myPlotStyle['adaptive_linetype']     = True                         
# myPlotStyle['lineweight']            = penTableData['custom_lineweight_table'].index(1.4) + 1     
# myPlotStyle['fill_style']            = fillStyles['useObjectFillStyle']    
# myPlotStyle['end_style']             = endStyles['butt']     
# myPlotStyle['join_style']            = joinStyles['useObjectJoinStyle']   
# penTableData['plot_style'].append(myPlotStyle)






# for i in range(32):
#     newPlotStyle = copy.deepcopy(penTableData['plot_style'][0])
#     newPlotStyle['name'] = "linetype " + str(i)
#     newPlotStyle['localized_name'] = newPlotStyle['name']
#     newPlotStyle['linetype'] = i
#     penTableData['plot_style'].append(newPlotStyle)

# for key in endStyles:
#     newPlotStyle = copy.deepcopy(penTableData['plot_style'][0])
#     newPlotStyle['name']              = "end_style " + str(key)
#     newPlotStyle['localized_name']    = newPlotStyle['name']
#     newPlotStyle['end_style']         = endStyles[key]     
#     newPlotStyle['lineweight']        = penTableData['custom_lineweight_table'].index(2.0) + 1 
#     penTableData['plot_style'].append(newPlotStyle)

# for key in endStyles:
#     penTableData['plot_style'].pop()



# this is a hack to add some new entries to the plot style table, which the autocad plot style editor GUI
# will not let us do in the case when a color-mapping table is present (but we want to keep the color mapping table and 
# do not understand why the presence of a color mapping table ought to preclude adding a new plot style)
numberOfStandbyPlotstylesToAdd = 1
for i in range(numberOfStandbyPlotstylesToAdd):
    myPlotStyle=copy.deepcopy(penTableData['plot_style'][0])
    myPlotStyle['name']                  = "standby--" + uuid.uuid4().hex
    myPlotStyle['localized_name']        = myPlotStyle['name']
    penTableData['plot_style'].append(myPlotStyle)





json.dump(penTableData, open(output_human_readable_pen_table_file_path.with_suffix(".new.json"), "w"), indent=4)

open(output_human_readable_pen_table_file_path.with_suffix(".initialPayload"), 'wb').write(payloadBytes)
#to do: make payloadBytes local (not global) -- was only global for debugging
writePenTableDataToFile(data=penTableData, penTableFile=open(output_human_readable_pen_table_file_path.with_suffix(".new.stb") ,"wb"))
open(output_human_readable_pen_table_file_path.with_suffix(".finalPayload"), 'wb').write(payloadBytes)


exit()

