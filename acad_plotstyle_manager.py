import argparse
import os
import json
import pathlib
import sys
import math
import copy
import uuid

from acad_pentable import *
import itertools



parser = argparse.ArgumentParser(description="Generate a human-readable json representation of an autocad pen table (stb or ctb) file.")
parser.add_argument("--input_acad_pen_table_file", action='store', nargs=1, required=True, help="the .stb or .ctb file to be converted into human readable format")
parser.add_argument("--output_human_readable_pen_table_file", action='store', nargs=1, required=False, help="the human readable pen table file to be created.")
args, unknownArgs = parser.parse_known_args()
input_acad_pen_table_file_path = (pathlib.Path(args.input_acad_pen_table_file[0]).resolve() if args.input_acad_pen_table_file and args.input_acad_pen_table_file[0] else None)
output_human_readable_pen_table_file_path = (pathlib.Path(args.output_human_readable_pen_table_file[0]).resolve() if args.output_human_readable_pen_table_file and args.output_human_readable_pen_table_file[0] else None)
print("input_acad_pen_table_file_path is " + str(input_acad_pen_table_file_path))
print("output_human_readable_pen_table_file_path is " + str(output_human_readable_pen_table_file_path))


# round trip file consistency test.
myPentable = AcadPentable(input_acad_pen_table_file_path)
pathOfRoundTripGeneration0 = input_acad_pen_table_file_path
pathOfRoundTripGeneration1 = output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.stem + "-roundTrip1").with_suffix(input_acad_pen_table_file_path.suffix)
pathOfRoundTripGeneration2 = output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.stem + "-roundTrip2").with_suffix(input_acad_pen_table_file_path.suffix)
pathOfRoundTripGeneration3 = output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.stem + "-roundTrip3").with_suffix(input_acad_pen_table_file_path.suffix)

AcadPentable(pathOfRoundTripGeneration0).writeToFile(pathOfRoundTripGeneration1)
AcadPentable(pathOfRoundTripGeneration1).writeToFile(pathOfRoundTripGeneration2)
AcadPentable(pathOfRoundTripGeneration2).writeToFile(pathOfRoundTripGeneration3)



# How does a pentable file change as it takes a (nominally non-modifying) round trip through
# this script or through the autoCAD pentable editor.
# "==T==>" means "open in the AutoCAD pen table editor, then click "save and close"".  (a round trip through the auTocad (T) editor)
# "==N==>" (right-pointing arrow) or "\N/" (down-pointing arrow) means a round trip through this (Neil's (N)) python script.
# the hashes I use below are a truncation of the sha1 hash, keeping the first few bytes as needed to ensure uniqueness.

# a06627d8: the factory-original acad.stb file
# b04bd8fe: the factory-original acad.ctb file
# 1c03a1ea: an arbitrary stb file from an arbitrary project

#  a06627d8 ==T==> 02503499 ==T==> a002fca8 ==T==> a002fca8
#    \N/
#  4b3f061a ==T==> 02503499 ==T==> a002fca8 ==T==> a002fca8
#    \N/
#  4b3f061a ==T==> 02503499 ==T==> a002fca8
#    \N/
#  4b3f061a ==T==> 02503499 ==T==> a002fca8

#  b04bd8fe ==T==> d59c374a ==T==> e044dfd4 ==T==> e044dfd4
#    \N/
#  b2a316e6 ==T==> d59c374a ==T==> e044dfd4 ==T==> e044dfd4
#    \N/
#  b2a316e6 ==T==> d59c374a ==T==> e044dfd4

#  1c03a1ea ==T==> 1c03a1ea ==T==> 1c03a1ea ==T==> 1c03a1ea
#    \N/
#  e0d21e21 ==T==> 1c03a1ea ==T==> 1c03a1ea ==T==> 1c03a1ea
#    \N/
#  e0d21e21 ==T==> 1c03a1ea ==T==> 1c03a1ea

# very, very strange.  It is not hugely surprising that a round trip through this script is not entirely equivalent to a round 
# trip throught he autocad pen table editor
# (I think I remember noticing an extra null byte on the end of the payload that acad adds and this script does not (or vice versa))
# it is also not hugely surprising (although rather bad practice) that some of the factory-original pen table files
# might have been composed in an earlier/non-standard version of the pentable editor, and therefore require a single trip through the 
# acad editor to settle down.
# But, what is very weird is a06627d8 (the factory original acad.stb file), which only settles down after TWO trips through the 
# acad editor.  This means that there exists at least one input that requires more than one round trip through the acad editor before
# settling down -- what is the acad editor doing that would require more than one trip to settle down?



json.dump(myPentable.toHumanReadableDictionary(), open(output_human_readable_pen_table_file_path, "w"), indent=4)
json.dump(myPentable.toRawDictionary(), open(output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.name).with_suffix(input_acad_pen_table_file_path.suffix + ".raw.json")  , "w"), indent=4)

# myPentable.plot_style['white'].color_policy = ColorPolicy(0)

# testColor = int.from_bytes( [195, 254, 255, 255], byteorder='big', signed=True)
testColor = int.from_bytes( [100, 254, 255, 255], byteorder='big', signed=True)


 
if 'white' not in myPentable.plot_style:
    myPentable.plot_style['white'] = AcadPlotstyle(parent = myPentable, name = "white")
         
myPentable.plot_style['white'].color = testColor
myPentable.plot_style['white'].mode_color = testColor



myPentable.writeToFile(output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.stem + "-modified").with_suffix(input_acad_pen_table_file_path.suffix))      
json.dump(myPentable.toHumanReadableDictionary(), open(output_human_readable_pen_table_file_path, "w"), indent=4)
json.dump(myPentable.toRawDictionary(), open(output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.name).with_suffix(input_acad_pen_table_file_path.suffix + ".raw.json")  , "w"), indent=4)

# print(str(input_acad_pen_table_file_path.name) + "-new")
# print("pathOfModifiedPentableFile: " + str(pathOfModifiedPentableFile))


# lineweightConceptReport()

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

#similarly, we have the following 4 preferred degrees of density (a.k.a. "screening" in AutoCAD plotstyle parlance)
preferredDensitiesByDegree = {
    -3: 0.353,
    -2: 0.500,
    -1: 0.707,
     0: 1.000
}

preferredColors = {
    'black': (0, 0, 0),
    'blue':(0,0,255)
}

# we want to consturct a pen table having a nicely-named plot style for each member of the cartesian prodcut of our 
# series of preferred property values (along with an "unspecified") value added to each series of preferred property values
# so that, for any combination of properties that we choose to enforce and preferred values for those properties, we can find a corresponding
# plot style.  I am tempted not to have an "unspecified" value for the line thicknesses, because I want to strictly adhere to the
# chosen few (and there is always the required "Normal" plot style -- which leaves every property unspecified).  Perhaps the only property
# which I want the user to be able to leave "unspecified" by choosing a plot style is the color.  Even this is only a convenience, a hack to
# avoid having to think carefully about colors in the same way that I have thought carefully about line thickness and density.
# ideally, we should be able to parameterize the space of styles however we see fit, and then present the chosen parameterization to the user
# as knobs to turn in the ui (along the lines of css), but given AuotCAD's relatively primitive concept of combining styles, explicitly constructing
# each choice ahead-of-time, as we are doing here, is the coses we can come to giving the user the knobs that we would like to give him.

thePentable = AcadPentable()

for (lineThicknessDegree, densityDegree, colorKey) in itertools.product(preferredLineThicknessesByDegree, preferredDensitiesByDegree, {**preferredColors, **{'unspecified':None}}):
    # print("working on lineThicknessDegree " + str(lineThicknessDegree) + ", " + "densityDegree " + str(densityDegree) + ", colorKey " + str(colorKey))
    thisPlotStyle = AcadPlotstyle(parent=thePentable,
        name= "thickness{:+d}_density{:+d}".format(lineThicknessDegree, densityDegree) + ("" if colorKey == 'unspecified' else "_color" + colorKey[0].upper() + colorKey[1:] )
    )
    # print("constructing plot style " + thisPlotStyle.name)


    thisPlotStyle.lineweight = 1 + thePentable.custom_lineweight_table.index(preferredLineThicknessesByDegree[lineThicknessDegree])
    thisPlotStyle.screen = int(100 * preferredDensitiesByDegree[densityDegree])
    if colorKey != 'unspecified' : 
        thisPlotStyle.color = int.from_bytes( (195,) + preferredColors[colorKey], byteorder='big', signed=True)
        thisPlotStyle.mode_color = thisPlotStyle.color

        # print("thisPlotStyle.color_policy.value: " + str(thisPlotStyle.color_policy.value))
        thisPlotStyle.color_policy = thisPlotStyle.color_policy & (thisPlotStyle.color_policy & ~ColorPolicy.USE_OBJECT_COLOR)
        # print("thisPlotStyle.color_policy.value: " + str(thisPlotStyle.color_policy.value))

    thePentable.plot_style[thisPlotStyle.name] = thisPlotStyle


thePentable.writeToFile(output_human_readable_pen_table_file_path.parent.joinpath("good.stb"))
