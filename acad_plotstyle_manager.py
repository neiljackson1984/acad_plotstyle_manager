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


# lineweightConceptReport()

# thePentable = AcadPentable()
thePentable = myPentable

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

if True:
    
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

    for (lineThicknessDegree, densityDegree, colorKey) in itertools.product(preferredLineThicknessesByDegree, preferredDensitiesByDegree, {**{'unspecified':None}, **preferredColors}):
        # print("working on lineThicknessDegree " + str(lineThicknessDegree) + ", " + "densityDegree " + str(densityDegree) + ", colorKey " + str(colorKey))
        thisPlotstyle = thePentable.addAPlotstyle( 
            name= "thickness{:d}_density{:d}".format(lineThicknessDegree, densityDegree) + ("" if colorKey == 'unspecified' else "_color" + colorKey[0].upper() + colorKey[1:] )
        )
        # print("constructing plot style " + thisPlotstyle.name)

        thisPlotstyle.lineweight = 1 + thePentable.custom_lineweight_table.index(preferredLineThicknessesByDegree[lineThicknessDegree])
        thisPlotstyle.screen = int(100 * preferredDensitiesByDegree[densityDegree])
        if colorKey != 'unspecified' : 
            thisPlotstyle.mode_color = preferredColors[colorKey]
            thisPlotstyle.color_policy |= ColorPolicy.EXPLICIT_COLOR
            # print("thisPlotstyle.color_policy.value: " + str(thisPlotstyle.color_policy.value))
            # thisPlotstyle.color_policy = thisPlotstyle.color_policy & (thisPlotstyle.color_policy & ~ColorPolicy.USE_OBJECT_COLOR)
            # print("thisPlotstyle.color_policy.value: " + str(thisPlotstyle.color_policy.value))


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

if False:  
    # add a sequence of plotStyles to test the effect of the various values of color_policy and to experiment
    # with the weird white-implies-no-override behavior.
    allPossibleColorPolicies = map(
        lambda y : functools.reduce(operator.or_, y),
        itertools.product(  *( (ColorPolicy(0), x) for x in reversed(ColorPolicy) )   ) 
    )

    brightGreen  = PentableColor(red=0   ,  green=250   ,  blue=0     , colorMethod=ColorMethod.BY_COLOR      ) 
    darkRed      = PentableColor(red=195 ,  green=0     ,  blue=0     , colorMethod=ColorMethod.BY_COLOR      )
    brightOrange = PentableColor(red=245 ,  green=145   ,  blue=50    , colorMethod=ColorMethod.BY_COLOR      )
    white        = PentableColor(red=255 ,  green=255   ,  blue=255   , colorMethod=ColorMethod.BY_COLOR      ) 
    black        = PentableColor(red=0   ,  green=0     ,  blue=0     , colorMethod=ColorMethod.BY_COLOR      ) 

    colorExplicitlyDefinedInThePentable =   brightGreen
    for (color, colorPolicy) in itertools.product((colorExplicitlyDefinedInThePentable, white), allPossibleColorPolicies):    
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
    
        colorPolicyCuteString = ("E" if e else "e") +  ("G" if g else "g") + ("D" if d else "d")
        # oops, plot style names are supposed to be case insensitive (i.e. two names that differe only in capitalization are regarded by AutoCAD to be equivalent.
        # could case-sensitiviy be the root of all my confusion, since I have been naming my plot styles names that differ only in capitalization.
        # To overcome case insensitivity, I have appended  str(int(colorPolicy))  to the plot style name, below:
        
        thisPlotstyle = thePentable.addAPlotstyle(name=color.htmlCode + " " + colorPolicyCuteString + " " + str(int(colorPolicy)) )
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
            + "thisPlotstyle.explicitlyOverrideTheColor: " + str(thisPlotstyle.explicitlyOverrideTheColor) + "  "
            + "thisPlotstyle.grayscale: " + str(thisPlotstyle.grayscale) + "  "
            + "thisPlotstyle.dither: " + str(thisPlotstyle.dither) + "  "

            + str(colorPolicy)
        )
    
    # generate a test drawing (or rather an autolisp script that populates the test drawing) containing a sample of each plotstyle
    import decimal
    def drange(x, y, jump):
        while x < y:
            yield float(x)
            x = decimal.Decimal(x) + decimal.Decimal(jump)

    samplerScript = ""
    # colorExplicitlyDefinedInThePentable is defined above.  that and white are the two colors that we are attempting to override to.
    lineColor = darkRed 

    textColor = black
    stationIntervalX = 2.5
    stationIntervalY = 0.1
    nominalTextWidth = 0.5
    lineLength = 0.5



    xRange = (1,7.5)
    yRange = (1,10)
    xValues = drange( xRange[0], xRange[1] + stationIntervalX, stationIntervalX )
    yValues = drange( yRange[0], yRange[1] + stationIntervalY, stationIntervalY )
    yValues = reversed(list(yValues))
    stations = tuple(itertools.product(xValues, yValues))

    textHeight = 0.04
    textAngle = 0
    textAlignment = "MR" # the sttring to be passed as the "Justify" option to the "Text" command.  must be one of Left Center Right Align Middle Fit TL TC TR ML MC MR BL BC BR 
    # note the "Align" keyword launches into more point selection and changes the subsequent syntaz of the Text command .

    # positions relative to insertionPoint, which we will move for each subsequent sample.
    anchors = {}
    anchors['textPosition']   = (nominalTextWidth ,0,0)
    anchors['lineStartPoint'] =   tuple(map(operator.add, anchors['textPosition']   ,  (2 * textHeight ,0,0)  ))
    anchors['lineEndPoint']   =   tuple(map(operator.add, anchors['lineStartPoint'] ,  (lineLength     ,0,0)  ))

    #returns an autolisp expression that will evaluate to the specified string
    def escapeStringForAutolisp(x: str) -> str:
        # using conversion via list of character codes -- crude and inefficient, but effective and reliable.
        return "(vl-list->string '(" + " ".join(map(str,x.encode())) + "))"

    def toAutolispExpression(x) -> str:
        if isinstance(x, str): return escapeStringForAutolisp(x)
        elif isinstance(x, tuple): return "'(" + " ".join(map(toAutolispExpression, x)) + ")"
        elif isinstance(x, PentableColor): return toAutolispExpression(x.sysvarString)
        else: return str(x)

    # first, erase all existing entities.
    samplerScript += '(command "._erase" (ssget "A") "")' + "\n"

    stationIndex =  0
    stationsRolloverCount = 0
    lastEncounteredRolloverCount = 0
    for plotStyle in thePentable.plot_style.values():
        lastEncounteredRolloverCount = stationsRolloverCount

        #add commands to the samplerScript to draw the sample of this plotSTyle.
        #the sample will consist of a text object containing the name of the plot style,
        # then a line with the line's plotstyleName set to the name of the plotstyle.
        #the script is intended to be run in a dwg file that is configured to use the 
        # pen table file corresponding to thePentable
        thisStation = stations[stationIndex]
        # print("thisStation: " + str(thisStation))

        localAnchors = {key: tuple(map(operator.add, stations[stationIndex], value)) for (key,value) in anchors.items()}

        annotationTextForThisSample = plotStyle.name

        defaultDesiredSysvarState = {
            'CLAYER'         :'0',
            'CELTYPE'        :'Continuous',
            'CETRANSPARENCY' : 0,
            'CELTSCALE'      : 0.9,
            'TEXTSTYLE'      : 'Standard',
        }

        desiredSysvarStateForInsertingTheText = {
            'CECOLOR'       : textColor,
            'CPLOTSTYLE'    : "Normal",
            'CELWEIGHT'     : 0,
        }

        desiredSysvarStateForInsertingTheLine = {
            'CECOLOR'       : lineColor,
            'CPLOTSTYLE'    : plotStyle.name,
            'CELWEIGHT'     : 211,
        }

        # The CPLOTSTYLE variable is not case sensitive, which is really a problem because plot style names are, in gneral, case sensitive.

        samplerScript += (
            ""



            + " ".join( '(setvar ' + toAutolispExpression(sysvarName) + " "   + toAutolispExpression(sysvarValue)   + ')' for (sysvarName, sysvarValue) in defaultDesiredSysvarState.items() ) 


            + " ".join( '(setvar ' + toAutolispExpression(sysvarName) + " "   + toAutolispExpression(sysvarValue)   + ')' for (sysvarName, sysvarValue) in desiredSysvarStateForInsertingTheLine.items() ) 
            + "(command " 
            +   '"._line"' + " " 
            +   toAutolispExpression(localAnchors['lineStartPoint']) + " "
            +   toAutolispExpression(localAnchors['lineEndPoint']) + " "
            +   '""' 
            + ")"  


            + " ".join( '(setvar ' + toAutolispExpression(sysvarName)    + toAutolispExpression(sysvarValue)   + ')' for (sysvarName, sysvarValue) in desiredSysvarStateForInsertingTheText.items() ) 
            + "(command " 
            +   '"text"'  
            +   toAutolispExpression('Justify') 
            +   toAutolispExpression(textAlignment)
            +   toAutolispExpression(localAnchors['textPosition']) + " "
            +   toAutolispExpression(textHeight) + " "
            +   toAutolispExpression(textAngle) + " "
            +   toAutolispExpression(annotationTextForThisSample) + " "
            + ")" + "\n"
        )

        # for each sample, it will be obvious to distinguish visually whether the line's 
        # final graphical color is lineColor (dark red, or if convered to grayscale, dark grey) 
        # (which means that "use object color" has actually happened.
        # or colorExplicitlyDefinedInThePentable (either bright green (or, if converted to 
        # grayscale, light gray) or white) (whcih means thaat "use object color" has not happened.)
        # 
        # Thus, we can determine visually whether AutoCAD is doing an explicit color override 
        # and whetehr it is doing conversion to grayscale for each test case.


        stationIndex = (stationIndex + 1) % len(stations)
        if stationIndex == 0: stationsRolloverCount += 1
    # print(samplerScript)
    if lastEncounteredRolloverCount > 0:
        print("warning: re-used stations up to " + str(lastEncounteredRolloverCount) + "times.")

    with open(output_human_readable_pen_table_file_path.parent.joinpath("sampler.lsp"), "w") as f:
        f.write(samplerScript)


# thePentable.writeToFile(output_human_readable_pen_table_file_path.parent.joinpath("good.stb"))
thePentable.writeToFile(output_human_readable_pen_table_file_path.parent.joinpath(input_acad_pen_table_file_path.name))
json.dump(thePentable.toHumanReadableDictionary(),   open(output_human_readable_pen_table_file_path.parent.joinpath("good.stb").with_suffix(input_acad_pen_table_file_path.suffix + ".json"), "w"), indent=4)
json.dump(thePentable.toRawDictionary(),             open(output_human_readable_pen_table_file_path.parent.joinpath("good.stb").with_suffix(input_acad_pen_table_file_path.suffix + ".raw.json"), "w"), indent=4)

thePentable.writeSamplerToFile(output_human_readable_pen_table_file_path.parent.joinpath("sampler.lsp"))
import tabulate
import pprint
collectedRgbValues = (
    tuple(
        map(
            lambda i: sorted(set(x[i] for x in aciToRgb.values())),
            range(len(tuple(aciToRgb.values())[0]))
        )
    )
)

print("Here is the complete list of red, green and blue values (respectively) among all the aci colors: " + "\n"
    + tabulate.tabulate(collectedRgbValues)
)




prettyPrinter = pprint.PrettyPrinter(indent=4, depth = 4, width=24)

# prettyPrinter.pprint(
#     tuple(
#         (
#             redValue, 
#             sorted(
#                 tuple(
#                     (greenValue, blueValue)
#                     for (r, greenValue, blueValue) in aciToRgb.values()
#                     if r == redValue
#                 )
#             )
#         ) 
#         for redValue in collectedRgbValues[0] 
#     )
# )


#each member of each rgb value is replaced with the index at which that member appears in the list of standard values
standardMagnitudes=sorted(collectedRgbValues[0])
indexifiedRgbValues = tuple(map(
    lambda x:
        tuple(map(
            lambda y: standardMagnitudes.index(y),
            x
        )),
    aciToRgb.values()
))
uniqueIndexifiedRgbValues = set(indexifiedRgbValues)

deOrderedIndexifiedRgbValues = tuple(
    sorted(
        set(
            tuple(
                map(tuple, map(sorted, 
                    indexifiedRgbValues
                ))
            )
        )
    )
)


print("indexifiedRgbValues: ")
print(tabulate.tabulate(
    map(
        lambda a,b: (str(a)+":", *b),
        *((lambda x: (range(len(x)), x))(indexifiedRgbValues))
    )
))

print("sorted(indexifiedRgbValues): ")
print(tabulate.tabulate(
    map(
        lambda a,b: (str(a)+":", *b),
        *((lambda x: (range(len(x)), x))(sorted(indexifiedRgbValues) ))
    )
))

print("sorted(set(indexifiedRgbValues)) with frequencies, sorted by frequency: ")
print(tabulate.tabulate(
    map(
        lambda a,b: (str(a)+":", *b),
        *((lambda x: (range(len(x)), x))(
            tuple(sorted(
                map(
                    lambda x: ( 
                        len(
                            tuple(
                                0 for y in indexifiedRgbValues
                                if y==x 
                            )
                        ),
                        *x
                    ),
                    sorted(set(indexifiedRgbValues)) 
                )
            ))
        ))
    )
))

print("deOrderedIndexifiedRgbValues: ")
print(tabulate.tabulate(
    map(
        lambda a,b: (str(a)+":", *b),
        *((lambda x: (range(len(x)), x))(deOrderedIndexifiedRgbValues))
    )
))

deOrderedIndexifiedRgbValuesWithCounts = tuple(map(
    lambda x:
        (
            len(tuple(
                0 for y in set(indexifiedRgbValues)
                if sorted(y) == sorted(x)
            )),
            *x
        ),
    deOrderedIndexifiedRgbValues
))


print("lengths of colledctedRgbValues: " + str(tuple(map(len, collectedRgbValues))))

indexifiedMagnitudeCombinationsCollectedByFrequency = tuple(
    (
        frequency,
        tuple(x[1:] 
            for x in deOrderedIndexifiedRgbValuesWithCounts
            if x[0] == frequency
        )    
    ) 
    for frequency in set(
        tuple(map(
            lambda x: x[0],
            deOrderedIndexifiedRgbValuesWithCounts
        ))
    )
)

print("indexifiedMagnitudeCombinationsCollectedByFrequency: ")
print(
    "\n".join(
        map(
            lambda x:
                "magnitude combinations that appear " + str(x[0]) + " times: " + "\n"
                + "\t" +  "There are " + str(len(x[1])) + " such magnitude combinations:" + "\n" 
                + "\t" + "and they use " + str(len(set(itertools.chain(*x[1])))) + " of the magnitudes, namely " 
                + str(
                    sorted(
                        set(itertools.chain(*x[1]))
                    )
                ) +  "\n"
                + "\t" + "\n\t".join(
                    map(str, x[1])
                ),
            indexifiedMagnitudeCombinationsCollectedByFrequency
        )
    )
)


print("indexifiedMagnitudeCombinationsCollectedByFrequency, with different inner sorting: ")
print(
    "\n".join(
        map(
            lambda x:
                "magnitude combinations that appear " + str(x[0]) + " times: " + "\n"
                + "\t" +  "There are " + str(len(x[1])) + " such magnitude combinations:" + "\n" 
                + "\t" + "and they use " + str(len(set(itertools.chain(*x[1])))) + " of the magnitudes, namely " 
                + str(
                    sorted(
                        set(itertools.chain(*x[1]))
                    )
                ) +  "\n"
                + "\t" 
                # + "\n\t".join(map(str, 
                #     sorted(
                #         x[1],
                #         key= lambda x: (x[0], x[2], x[1])
                #     )
                # ))
                + tabulate.tabulate(
                    sorted(
                        x[1],
                        key= lambda x: (x[0], x[2], x[1])
                    )
                )
                ,
            indexifiedMagnitudeCombinationsCollectedByFrequency
        )
    )
)

import ezdxf;
doc = ezdxf.new(dxfversion="R2010")
modelSpace = doc.modelspace()

inch = 1.0
millimeter = inch/25.4

gridInterval = 0.1 * inch

def drawIcon(modelSpace, center, iconType="square"):
    size = gridInterval*0.5
    numberOfNestedCopies = 1
    nonSquareSizeAdjustmentFactor = 0.65

    squareVertices =[            
        (-1/2, -1/2),
        (1/2, -1/2),
        (1/2, 1/2),
        (-1/2,1/2)
    ]

    #close it:
    squareVertices.append(squareVertices[0])
    
    for i in range(numberOfNestedCopies):
        scaledSize = size*(1 - i/numberOfNestedCopies)

        if iconType=="square":
            #scale by size and move to center
            scaledVertices = tuple(
                tuple(map(operator.add, center,
                    (
                        coordinate*scaledSize
                        for coordinate in vertex
                    )
                ))
                for vertex in squareVertices
            )
            # for i in range(len(scaledVertices) - 1):
            #     modelSpace.add_line(scaledVertices[i], scaledVertices[i+1])

            hatch = modelSpace.add_hatch()
            hatch.paths.add_polyline_path(scaledVertices)
        else:
            scaledSize *= nonSquareSizeAdjustmentFactor
            # modelSpace.add_circle(center=center, radius=scaledSize/2)
            hatch = modelSpace.add_hatch()
            hatch.paths.add_polyline_path([
                (scaledSize/2 + center[0],0+center[1],1),(-scaledSize/2+center[0],0+center[1],1),(scaledSize/2+center[0],0+center[1])
            ])
        



rowIndex = 0


# partitionsOfThree = ((1,1,1), (1,2), (3))  <-- this is really hoaw we are categrozing the combinations.  the fact the each combination appears in
# every possible permutation in the acad color set means that the (3)-pattern combinations appear once, the (1,2)-pattern combinations appear 3 times,
# and the (1,1,1)-pattern combinations appear 6 times.

magnitudes = range(len(standardMagnitudes))
# magnitudes = standardMagnitudes


for (frequency, combinations) in indexifiedMagnitudeCombinationsCollectedByFrequency:
        if frequency == 1:
            #in this case, we are dealing with combinations of the form (a,a,a)
            for combination in combinations:
                rowY = -gridInterval * rowIndex
                drawIcon(modelSpace, ( magnitudes[combination[0]]*gridInterval , rowY))
                rowIndex += 1
        elif frequency == 3:
            #in this case, we are dealing with a combination of the form (a, b, b) (order irrrelevant)
            for (singleElement, doubleElement) in sorted(
                (
                    tuple(sorted(
                    set(combination),
                    key=lambda x: combination.count(x)                    
                    ))
                    for combination in combinations
                ), 
                key=sorted
            ):
                rowY = -gridInterval * rowIndex
                squareIconPosition = (magnitudes[doubleElement] * gridInterval, rowY)
                circleIconPosition = (magnitudes[singleElement] * gridInterval, rowY)
                drawIcon(modelSpace, squareIconPosition)
                drawIcon(modelSpace, circleIconPosition, "circle")
                modelSpace.add_line(start=squareIconPosition, end=circleIconPosition)
                rowIndex += 1            
  
        elif frequency == 6:
            #in this case, we are dealing with a combination of the form (a, b, c)

            # group the combinations by (smallestElement, largestElement)
            for (smallestElement, largestElement), middleElements in (
                (
                    (smallestElement, largestElement), 
                    #middle elements:
                    tuple(map(
                        lambda x: sorted(x)[1],
                        group
                    ))
                )
                for (smallestElement, largestElement), group in
                itertools.groupby(
                    sorted(
                        combinations,
                        key=lambda x: (min(x), max(x))
                    ),
                    key=lambda x: (min(x), max(x))
                )
            ):
                rowY = -gridInterval * rowIndex
                leftSquarePosition  = (magnitudes[smallestElement]*gridInterval , rowY)
                rightSquarePosition = (magnitudes[largestElement]*gridInterval , rowY)
                drawIcon(modelSpace, leftSquarePosition)
                drawIcon(modelSpace, rightSquarePosition)
                for middleElement in middleElements:
                    drawIcon(modelSpace, (magnitudes[middleElement]*gridInterval , rowY), "circle")
                modelSpace.add_line(start=leftSquarePosition, end=rightSquarePosition)
                rowIndex += 1





doc.saveas(output_human_readable_pen_table_file_path.parent.joinpath('colorspace.dxf'))


