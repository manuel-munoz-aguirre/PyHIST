#!/usr/bin/env python

import os
import argparse
import subprocess
import platform
from argparse import ArgumentParser
import sys
from src import produce_edges, utility_functions

def build_parser():

    parser = ArgumentParser(description='Semi-automatic pipeline to segment tissue slices from\
    the background in high resolution whole-slide histopathological images and\
    extracts patches of tissue segments from the full resolution image')
    
    # TODO: Fill arguments

    return parser


def check_compilation():
    if not os.path.isfile("src/Felzenszwalb_algorithm/segment"): 

        # If Windows, the user must compile the script manually, otherwise 
        # we attempt to compile it
        if platform.system() == "Windows":
            print("Please compile Felzenszwalb's algorith before running this script. Exiting.")
            sys.exit(1)
        else:
            print("Compiling Felzenszwalb's algorithm...")
            try:
                subprocess.check_call(["make"], stdout=subprocess.PIPE, cwd="src/Felzenszwalb_algorithm/")
            except:
                print("Compilation of Felzenszwalb's algorithm failed. Please compile it before running this script. Exiting.")
                sys.exit(1)


if __name__ == "__main__":
    
    # Read arguments
    # parser = build_parser()
    # if len(sys.argv)==1:        # TODO: Modify this with the minimal number of arguments
    #     parser.print_help()
    #     sys.exit(1)
    # args = parser.parse_args()

    # Check if the segmentation algorithm is compiled
    check_compilation()

    # Continue with the rest ...
    produce_edges.run("FILE.svs", "test.jpg", 1)

    # Convert to ppm
    utility_functions.convert_to_ppm("test.jpg")