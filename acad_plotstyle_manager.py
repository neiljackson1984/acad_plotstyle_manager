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
import operator
import functools


parser = argparse.ArgumentParser(description="Generate a human-readable json representation of an autocad pen table (stb or ctb) file.")
parser.add_argument("--input_acad_pen_table_file", action='store', nargs=1, required=True, help="the .stb or .ctb file to be converted into human readable format")
parser.add_argument("--output_human_readable_pen_table_file", action='store', nargs=1, required=False, help="the human readable pen table file to be created.")
args, unknownArgs = parser.parse_known_args()
input_acad_pen_table_file_path = (pathlib.Path(args.input_acad_pen_table_file[0]).resolve() if args.input_acad_pen_table_file and args.input_acad_pen_table_file[0] else None)
output_human_readable_pen_table_file_path = (pathlib.Path(args.output_human_readable_pen_table_file[0]).resolve() if args.output_human_readable_pen_table_file and args.output_human_readable_pen_table_file[0] else None)
print("input_acad_pen_table_file_path is " + str(input_acad_pen_table_file_path))
print("output_human_readable_pen_table_file_path is " + str(output_human_readable_pen_table_file_path))



myPentable = AcadPentable(input_acad_pen_table_file_path)
json.dump(myPentable.toHumanReadableDictionary(), open(output_human_readable_pen_table_file_path, "w"), indent=4)
json.dump(myPentable.toRawDictionary(), open(output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.name).with_suffix(input_acad_pen_table_file_path.suffix + ".raw.json")  , "w"), indent=4)

# myPentable.plot_style['white'].color_policy = ColorPolicy(0)


 
##  if 'white' not in myPentable.plot_style:
##    myPentable.plot_style['white'] = AcadPlotstyle(owner = myPentable, name = "white")
##           
##  myPentable.plot_style['white'].color = testColor
##  myPentable.plot_style['white'].mode_color = testColor
##    
##  myPentable.writeToFile(output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.stem + "-modified" + input_acad_pen_table_file_path.suffix))      
##  json.dump(myPentable.toHumanReadableDictionary(),   open(output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.stem + "-modified" + input_acad_pen_table_file_path.suffix + ".json"), "w"), indent=4)
##  json.dump(myPentable.toRawDictionary(),             open(output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.stem + "-modified" + input_acad_pen_table_file_path.suffix + ".raw.json"), "w"), indent=4)



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
    'black': PentableColor(0, 0,   0),
    'blue':  PentableColor(0, 0, 255)
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

if False:
    thisPlotStyle = thePentable.addAPlotstyle(name="tester1")
    thisPlotStyle.color_policy |= ColorPolicy.EXPLICIT_COLOR | ColorPolicy.CONVERT_TO_GRAYSCALE
    thisPlotStyle.color      = PentableColor(red=250 ,  green=100 ,  blue=0   , colorMethod=ColorMethod.BY_ACI    ) 
    thisPlotStyle.mode_color = PentableColor(red=221 ,  green=0   ,  blue=50   , colorMethod=ColorMethod.BY_COLOR  ) 

    thisPlotStyle = thePentable.addAPlotstyle(name='tester2')
    thisPlotStyle.color_policy |= ColorPolicy.EXPLICIT_COLOR | ColorPolicy.CONVERT_TO_GRAYSCALE
    thisPlotStyle.color      = PentableColor(red=0 ,  green=255   ,  blue=0   , colorMethod=ColorMethod.BY_ACI    ) 
    thisPlotStyle.mode_color = PentableColor(red=221 ,  green=0   ,  blue=0   , colorMethod=ColorMethod.BY_ACI    ) 

    thisPlotStyle = thePentable.addAPlotstyle(name='tester3')
    thisPlotStyle.color_policy |= ColorPolicy.EXPLICIT_COLOR | ColorPolicy.CONVERT_TO_GRAYSCALE
    thisPlotStyle.color      = PentableColor(red=0 ,  green=255   ,  blue=0   , colorMethod=ColorMethod.BY_COLOR    ) 
    thisPlotStyle.mode_color = PentableColor(red=221 ,  green=0   ,  blue=0   , colorMethod=ColorMethod.BY_ACI    ) 

    thisPlotStyle = thePentable.addAPlotstyle(name='tester4')
    thisPlotStyle.color_policy |= ColorPolicy.EXPLICIT_COLOR | ColorPolicy.CONVERT_TO_GRAYSCALE
    thisPlotStyle.color      = PentableColor(red=0 ,  green=255   ,  blue=0   , colorMethod=ColorMethod.BY_ACI       ) 
    thisPlotStyle.mode_color = PentableColor(red=221 ,  green=0   ,  blue=0   , colorMethod=ColorMethod.BY_COLOR      ) 

    thisPlotStyle = thePentable.addAPlotstyle(name='tester5')
    thisPlotStyle.color_policy |= ColorPolicy.EXPLICIT_COLOR | ColorPolicy.CONVERT_TO_GRAYSCALE
    thisPlotStyle.color      = PentableColor(red=0 ,  green=255   ,  blue=0   , colorMethod=ColorMethod.BY_COLOR       ) 
    thisPlotStyle.mode_color = PentableColor(red=221 ,  green=0   ,  blue=0   , colorMethod=ColorMethod.BY_COLOR      ) 

    thisPlotStyle = thePentable.addAPlotstyle(name='tester6')
    thisPlotStyle.color_policy |= ColorPolicy.EXPLICIT_COLOR | ColorPolicy.CONVERT_TO_GRAYSCALE
    thisPlotStyle.color      = PentableColor(red=99 ,  green=255   ,  blue=0   , colorMethod=ColorMethod.BY_ACI    ) 
    thisPlotStyle.mode_color = PentableColor(red=221 ,  green=33   ,  blue=0   , colorMethod=ColorMethod.BY_ACI    ) 

    thisPlotStyle = thePentable.addAPlotstyle(name='tester7')
    thisPlotStyle.color_policy |= ColorPolicy.EXPLICIT_COLOR | ColorPolicy.CONVERT_TO_GRAYSCALE
    thisPlotStyle.color      = PentableColor(red=99 ,  green=255   ,  blue=0   , colorMethod=ColorMethod.BY_COLOR    ) 
    thisPlotStyle.mode_color = PentableColor(red=221 ,  green=33   ,  blue=0   , colorMethod=ColorMethod.BY_ACI    ) 

    thisPlotStyle = thePentable.addAPlotstyle(name='tester8')
    thisPlotStyle.color_policy |= ColorPolicy.EXPLICIT_COLOR | ColorPolicy.CONVERT_TO_GRAYSCALE
    thisPlotStyle.color      = PentableColor(red=99 ,  green=255   ,  blue=0   , colorMethod=ColorMethod.BY_ACI       ) 
    thisPlotStyle.mode_color = PentableColor(red=221 ,  green=33   ,  blue=0   , colorMethod=ColorMethod.BY_COLOR      ) 

    thisPlotStyle = thePentable.addAPlotstyle(name='tester9')
    thisPlotStyle.color_policy |= ColorPolicy.EXPLICIT_COLOR | ColorPolicy.CONVERT_TO_GRAYSCALE
    thisPlotStyle.color      = PentableColor(red=99 ,  green=255   ,  blue=0   , colorMethod=ColorMethod.BY_COLOR       ) 
    thisPlotStyle.mode_color = PentableColor(red=221 ,  green=33   ,  blue=0   , colorMethod=ColorMethod.BY_COLOR      ) 



    thisPlotStyle = thePentable.plot_style['Normal']
    thisPlotStyle.color_policy |= ColorPolicy.EXPLICIT_COLOR | ColorPolicy.CONVERT_TO_GRAYSCALE
    thisPlotStyle.color      = PentableColor(red=221 ,  green=0   ,  blue=0   , colorMethod=ColorMethod.BY_ACI       ) 
    thisPlotStyle.mode_color = PentableColor(red=255 ,  green=255   ,  blue=255   , colorMethod=ColorMethod.BY_ACI      ) 



allPossibleColorPolicies = map(
    lambda y : functools.reduce(operator.or_, y),
    itertools.product(  *( (ColorPolicy(0), x) for x in ColorPolicy )   ) 
)

arbitraryNonIndexColor=PentableColor(red=2 ,  green=4   ,  blue=6   , colorMethod=ColorMethod.BY_COLOR       ) 
white=PentableColor(red=255 ,  green=255   ,  blue=255   , colorMethod=ColorMethod.BY_COLOR       ) 

for (color, colorPolicy) in itertools.product((arbitraryNonIndexColor, white), allPossibleColorPolicies):    
    d = bool(colorPolicy & ColorPolicy.ENABLE_DITHERING)
    g = bool(colorPolicy & ColorPolicy.CONVERT_TO_GRAYSCALE)
    e = bool(colorPolicy & ColorPolicy.EXPLICIT_COLOR)

    predictedValueOfTheColorFieldInTheUserInterface               = {
        True:",".join(map(str,(color.red,color.green,color.blue))),
        False:"Use object color"
     }[(e ^ g) & (not (color is white)) ] 

    predictedValueOfTheDitheringFieldInTheUserInterface           = {
        True:"On",
        False:"Off"
    }[d | ( g & e )]

    predictedValueOfTheConvertToGrayscaleFieldInTheUserInterface  = {
        True:"On",
        False:"Off"
    }[g & (not e)]
 
    colorPolicyCuteString = ("D" if d else "d") + ("G" if g else "g") + ("E" if e else "e")
    
    thisPlotstyle = thePentable.addAPlotstyle(name=color.htmlCode + " " + colorPolicyCuteString)
    thisPlotstyle.color_policy = colorPolicy
    thisPlotstyle.mode_color = color

    thisPlotstyle.description = (
        ""
        + colorPolicyCuteString
        + "\t\t" 
        + predictedValueOfTheColorFieldInTheUserInterface 
        + " " + predictedValueOfTheDitheringFieldInTheUserInterface 
        + " " + predictedValueOfTheConvertToGrayscaleFieldInTheUserInterface
        # + "\t\t" + thisPlotstyle.mode_color.htmlCode 
        + "\t"*6
        + str(colorPolicy)
    )

    

if False:
    for (lineThicknessDegree, densityDegree, colorKey) in itertools.product(preferredLineThicknessesByDegree, preferredDensitiesByDegree, {**preferredColors, **{'unspecified':None}}):
        # print("working on lineThicknessDegree " + str(lineThicknessDegree) + ", " + "densityDegree " + str(densityDegree) + ", colorKey " + str(colorKey))
        thisPlotStyle = AcadPlotstyle(owner=thePentable,
            name= "thickness{:+d}_density{:+d}".format(lineThicknessDegree, densityDegree) + ("" if colorKey == 'unspecified' else "_color" + colorKey[0].upper() + colorKey[1:] )
        )
        # print("constructing plot style " + thisPlotStyle.name)


        thisPlotStyle.lineweight = 1 + thePentable.custom_lineweight_table.index(preferredLineThicknessesByDegree[lineThicknessDegree])
        thisPlotStyle.screen = int(100 * preferredDensitiesByDegree[densityDegree])
        if colorKey != 'unspecified' : 
            thisPlotStyle.color = copy.deepcopy(preferredColors[colorKey]) 
            thisPlotStyle.mode_color = copy.deepcopy(preferredColors[colorKey])

            # print("thisPlotStyle.color_policy.value: " + str(thisPlotStyle.color_policy.value))
            # thisPlotStyle.color_policy = thisPlotStyle.color_policy & (thisPlotStyle.color_policy & ~ColorPolicy.USE_OBJECT_COLOR)
            # print("thisPlotStyle.color_policy.value: " + str(thisPlotStyle.color_policy.value))

        thePentable.plot_style[thisPlotStyle.name] = thisPlotStyle


thePentable.writeToFile(output_human_readable_pen_table_file_path.parent.joinpath("good.stb"))
json.dump(thePentable.toHumanReadableDictionary(),   open(output_human_readable_pen_table_file_path.parent.joinpath("good.stb").with_suffix(input_acad_pen_table_file_path.suffix + ".json"), "w"), indent=4)
json.dump(thePentable.toRawDictionary(),             open(output_human_readable_pen_table_file_path.parent.joinpath("good.stb").with_suffix(input_acad_pen_table_file_path.suffix + ".raw.json"), "w"), indent=4)


if False:
    #=======================================
    # sussing out how the Flag enum works:
    #=======================================
    x = ColorPolicy.EXPLICIT_COLOR | ColorPolicy.ENABLE_DITHERING
    y = ColorPolicy.EXPLICIT_COLOR & ColorPolicy.ENABLE_DITHERING
    # x = ColorPolicy.EXPLICIT_COLOR | ColorPolicy.ENABLE_DITHERING
    # y = ColorPolicy.EXPLICIT_COLOR
    # print("type(x): " + str(type(x)))
    print("repr(ColorPolicy.EXPLICIT_COLOR & ColorPolicy.ENABLE_DITHERING): " + repr(ColorPolicy.EXPLICIT_COLOR & ColorPolicy.ENABLE_DITHERING))
    print("repr(ColorPolicy.EXPLICIT_COLOR | ColorPolicy.ENABLE_DITHERING): " + repr(ColorPolicy.EXPLICIT_COLOR | ColorPolicy.ENABLE_DITHERING)) 
    print("repr(ColorPolicy.ENABLE_DITHERING | ColorPolicy.EXPLICIT_COLOR): " + repr(ColorPolicy.ENABLE_DITHERING | ColorPolicy.EXPLICIT_COLOR)) 
    print("repr(ColorPolicy(ColorPolicy.ENABLE_DITHERING)): " + repr(ColorPolicy(ColorPolicy.ENABLE_DITHERING))) 
    print("repr(~ColorPolicy.ENABLE_DITHERING): " + repr(~ColorPolicy.ENABLE_DITHERING)) 
    print("repr(ColorPolicy(~ColorPolicy.ENABLE_DITHERING)): " + repr(ColorPolicy(~ColorPolicy.ENABLE_DITHERING))) 
    print("x.EXPLICIT_COLOR: " + repr(x.EXPLICIT_COLOR))
    print("y.EXPLICIT_COLOR: " + repr(y.EXPLICIT_COLOR))
    print(repr(PentableColor(10,11,12))) 


    print([x for x in ColorPolicy ]) 
    print("===============")

    # # print("\n".join([str(x) for x in itertools.product(ColorPolicy) ])) 
    # print(
    #     "\n".join(
    #         str(x) for x in ( (ColorPolicy(0), x) for x in ColorPolicy )
    #     )
    # )

    # print("===============")


    print("===============")
    print(
        "\n".join(
                str(x) 
                for x in 
                map(
                    lambda y : y,
                    itertools.product(  *( (0, x) for x in "abc" )   ) 
                )
            )
        )

    print("===============")
    print(
        "\n".join(
                str(x) 
                for x in 
                map(
                    lambda y : y,
                    itertools.product(  *( (ColorPolicy(0), x) for x in ColorPolicy )   ) 
                )
            )
        )

    print("===============")
    print(
        "\n".join(
                str(x) 
                for x in 
                map(
                    lambda y : functools.reduce(operator.or_, y),
                    itertools.product(  *( (ColorPolicy(0), x) for x in ColorPolicy )   ) 
                )
            )
        ) 


    print("===============")
    allPossibleColorPolicies = map(
        lambda y : functools.reduce(operator.or_, y),
        itertools.product(  *( (ColorPolicy(0), x) for x in ColorPolicy )   ) 
    )
    print(
        "\n".join(
                map(str,  
                    allPossibleColorPolicies
                )
            )
        ) 

if False:
    x = PentableColor()
    print("repr(x.colorMethod): " + repr(x.colorMethod))
    x.colorMethod = 198
    print("repr(x.colorMethod): " + repr(x.colorMethod))

    y = ColorMethod.BY_ACI
    print("repr(y): " + repr(y))
    y = 198
    print("repr(y): " + repr(y))
    print("type(y): " + str(type(y)))


    x = PentableColor(-1006632961)
    print("repr(x.colorMethod): " + repr(x.colorMethod))
    x.colorMethod = 198
    print("repr(x.colorMethod): " + repr(x.colorMethod))
    print("repr(PentableColor(-1006632961).colorMethod): " + repr(PentableColor(-1006632961).colorMethod))
    print("repr(PentableColor(-1006632962 + 1*2**24).colorMethod): " + repr(PentableColor(-1006632962 +  1*2**24).colorMethod))
    print("repr(PentableColor(-1006632962 + 19*2**24).colorMethod): " + repr(PentableColor(-1006632962 +  19*2**24).colorMethod))
    
if False:    
    x = PentableColor()
    print("x.htmlCode: " + x.htmlCode )


# generate a test drawing containing a sample of each plotstyle.
import decimal
def drange(x, y, jump):
  while x < y:
    yield float(x)
    x = decimal.Decimal(x) + decimal.Decimal(jump)

samplerScript = ""

insertionPoint = (1,11,0)
stationIntervalX = 2.5
stationIntervalY = 0.1
nominalTextWidth = 0.5
lineLength = 0.5

stationIncrementDirectionX = 1
stationIncrementDirectionY = -1

xRange = (1,7.5)
yRange = (1,10)


xValues = drange( xRange[0], xRange[1] + stationIntervalX, stationIntervalX )
yValues = drange( yRange[0], yRange[1] + stationIntervalY, stationIntervalY )

yValues = reversed(list(yValues))

stations = tuple(itertools.product(xValues, yValues))

interval = (0,-0.3,0)
textHeight = 0.04
textAngle = 0
textAlignment = "MR" # the sttring to be passed as the "Justify" option to the "Text" command.  must be one of Left Center Right Align Middle Fit TL TC TR ML MC MR BL BC BR 
# note the "Align" keyword launches into more point selection and changes the subsequent syntaz of the Text command .

# positions relative to insertionPoint, which we will move for each subsequent sample.
anchors = {
    'textPosition': (nominalTextWidth ,0,0), 
    'lineStartPoint': (nominalTextWidth + 3 * textHeight,0,0),
    'lineEndPoint': (nominalTextWidth + 3 * textHeight + lineLength,0,0)
}

#returns an autolisp expression that will evaluate to the specified string
def escapeStringForAutolisp(x: str) -> str:
    # using conversion via list of character codes -- crude and inefficient, but effective and reliable.
    return "(vl-list->string '(" + " ".join(map(str,x.encode())) + "))"

def toAutolispExpression(x) -> str:
    if isinstance(x, str): return escapeStringForAutolisp(x)
    elif isinstance(x, tuple): return "'(" + " ".join(map(toAutolispExpression, x)) + ")"
    else: return str(x)

samplerScript += '(command "._erase" (ssget "A") "")' + "\n"

stationIndex =  0
stationsRolloverCount = 0
for plotStyle in thePentable.plot_style.values():
    if stationsRolloverCount > 0: print("warning: re-used stations .")
    #add commands to the samplerScript to draw the sample of this plotSTyle.
    #the sample will consist of a text object containing the name of the plot style,
    # then a line with the line's plotstyleName set to the name of the plotstyle.
    #the script is intended to be run in a dwg file that is configured to use the 
    # pen table file corresponding to thePentable
    thisStation = stations[stationIndex]
    print("thisStation: " + str(thisStation))


    localAnchors = {key: tuple(map(operator.add, stations[stationIndex], value)) for (key,value) in anchors.items()}

    annotationTextForThisSample = plotStyle.name

    # all strings:


    defaultDesiredSysvarState = {
        'CLAYER'         :'0',
        'CELTYPE'        :'Continuous',
        'CETRANSPARENCY' : 0,
        'CELTSCALE'      : 0.9,
        'TEXTSTYLE'      : 'Standard',
    }

    desiredSysvarStateForInsertingTheText = {
        'CECOLOR'       : '0,0,0',
        'CPLOTSTYLE'    : "Normal",
        'CELWEIGHT'     : 0,
    }

    desiredSysvarStateForInsertingTheLine = {
        'CECOLOR'       : '66,77,88',
        'CPLOTSTYLE'    : plotStyle.name,
        'CELWEIGHT'     : 211,
    }


    samplerScript += (
        ""



        + "\n".join( '(setvar ' + toAutolispExpression(sysvarName) + " "   + toAutolispExpression(sysvarValue)   + ')' for (sysvarName, sysvarValue) in defaultDesiredSysvarState.items() ) + "\n"


        + "\n".join( '(setvar ' + toAutolispExpression(sysvarName) + " "   + toAutolispExpression(sysvarValue)   + ')' for (sysvarName, sysvarValue) in desiredSysvarStateForInsertingTheLine.items() ) + "\n"
        + "(command " 
        +   '"._line"' + " " 
        +   toAutolispExpression(localAnchors['lineStartPoint']) + " "
        +   toAutolispExpression(localAnchors['lineEndPoint']) + " "
        +   '""' + " " 
        + ")" + "\n"


        + "\n".join( '(setvar ' + toAutolispExpression(sysvarName) + " "   + toAutolispExpression(sysvarValue)   + ')' for (sysvarName, sysvarValue) in desiredSysvarStateForInsertingTheText.items() ) + "\n"
        + "(command " 
        +   '"text"' + " " 
        +   toAutolispExpression('Justify') 
        +   toAutolispExpression(textAlignment)
        +   toAutolispExpression(localAnchors['textPosition']) + " "
        +   toAutolispExpression(textHeight) + " "
        +   toAutolispExpression(textAngle) + " "
        +   toAutolispExpression(annotationTextForThisSample) + " "
        + ")" + "\n"
    )

    insertionPoint = tuple(map(operator.add, insertionPoint,interval))

    stationIndex = (stationIndex + 1) % len(stations)
    if stationIndex == 0: stationsRolloverCount += 1
# print(samplerScript)


with open(output_human_readable_pen_table_file_path.parent.joinpath("sampler.lsp"), "w") as f:
    f.write(samplerScript)