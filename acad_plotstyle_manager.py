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

from acad_pentable import *




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

myPentable = AcadPentable(open(input_acad_pen_table_file_path, "rb"))
myPentable.writeToFile(penTableFile=open(output_human_readable_pen_table_file_path.with_suffix(".new.stb") ,"wb"))
json.dump(myPentable.toRawDictionary(), open(output_human_readable_pen_table_file_path, "w"), indent=4)
json.dump(myPentable.toHumanReadableDictionary(), open(output_human_readable_pen_table_file_path.with_suffix(".humanReadable.json"), "w"), indent=4)
    
