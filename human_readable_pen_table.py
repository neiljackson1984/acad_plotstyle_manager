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

import * from acad_pentable




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


json.dump(penTableData, open(output_human_readable_pen_table_file_path.with_suffix(".new.json"), "w"), indent=4)

open(output_human_readable_pen_table_file_path.with_suffix(".initialPayload"), 'wb').write(payloadBytes)
#to do: make payloadBytes local (not global) -- was only global for debugging
writePenTableDataToFile(data=penTableData, penTableFile=open(output_human_readable_pen_table_file_path.with_suffix(".new.stb") ,"wb"))
open(output_human_readable_pen_table_file_path.with_suffix(".finalPayload"), 'wb').write(payloadBytes)


exit()

