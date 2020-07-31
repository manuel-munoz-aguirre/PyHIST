import logging
import openslide
import os
import sys

from src import utility_functions, parser_input
from src.slide import PySlide, TileGenerator


def main():
    
    # Read parser arguments
    parser = parser_input.build_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    # Configure logger
    loglevel = {"default": logging.INFO, "verbose": logging.DEBUG, "silent": logging.CRITICAL}
    logging.basicConfig(level=loglevel[args.info], format='%(asctime)s [%(levelname)s]: %(message)s', datefmt="%d-%m-%Y %H:%M:%S")

    # Checking correct arguments and compilation of segmentation algorithm
    parser_input.check_arguments(args)
    utility_functions.check_image(args.svs)

    # Extract tiles
    slide = PySlide(vars(args))
    tile_extractor = TileGenerator(slide)
    tile_extractor.execute()

    # Clean-up
    utility_functions.clean(slide)


if __name__ == "__main__":
    main()