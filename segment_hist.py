import os
import platform
import sys
import time
from src import utility_functions, patch_selector, parser_input
import subprocess

def check_compilation():
    if not os.path.isfile("src/Felzenszwalb_algorithm/segment"):

        # If Windows, the user must compile the script manually, otherwise
        # we attempt to compile it
        if platform.system() == "Windows":
            print(
                "Please compile Felzenszwalb's algorithm before running this script. Exiting."
            )
            sys.exit(1)
        else:
            print("Compiling Felzenszwalb's algorithm...")
            try:
                subprocess.check_call(["make"],
                                      stdout=subprocess.PIPE,
                                      cwd="src/Felzenszwalb_algorithm/")
            except:
                print(
                    "Compilation of Felzenszwalb's algorithm failed. Please compile it before running this script. Exiting."
                )
                sys.exit(1)


def check_arguments(args):

    # Borders and Corners
    if (args.borders == '0000'
            and args.corners == '0000') or (args.borders != '0000'
                                            and args.corners != '0000'):
        print("Invalid borders and corners parameters! Exiting.")
        sys.exit(1)

    # Content threshold
    if args.thres > 1 or args.thres < 0:
        print(
            "CONTENT_THRESHOLD should be a float number between 0 and 1! Exiting."
        )
        sys.exit(1)

    # Check if the mask downsampling factor is a power of two
    # TODO: add this check for all downsampling factors
    if not utility_functions.isPowerOfTwo(args.downsample_mask):
        print("Downsampling factor for the mask must be a power of two.")
        sys.exit(1)


def main():

    # Read arguments
    parser = parser_input.build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    # Argument checker
    check_arguments(args)

    # Check if the segmentation algorithm is compiled
    check_compilation()

    sample_id = args.svs.split('/')[-1]
    sample_id = sample_id.split('.')[0]

    # Create output folder
    img_outpath = args.output
    if not os.path.exists(img_outpath):
        os.makedirs(img_outpath)
    img_outpath = img_outpath + sample_id + "/"
    if not os.path.exists(img_outpath):
        os.makedirs(img_outpath)

    # Produce edge image
    utility_functions.produce_edges(args.svs,
                                    img_outpath + "edges_" + sample_id + ".ppm",
                                    args.downsample_mask,
                                    args.verbose)

    # Run the segmentation algorithm
    utility_functions.produce_segmented_image(sample_id, img_outpath,
                                              args.sigma, args.k_const,
                                              args.minimum_segmentsize,
                                              args.verbose)

    # test mode
    if args.test_mode:
        utility_functions.produce_test_image(sample_id,
                                             img_outpath,
                                             args)
        sys.exit(0)

    # Generate image tiles
    patch_selector.run(sample_id, args.thres,
                       args.patch_size, args.lines,
                       args.borders, args.corners,
                       args.save_tilecrossed_image, args.save_patches,
                       args.svs,
                       args.output_downsample, args.downsample_mask,
                       img_outpath, args.verbose)

    # # Delete segmented and edge images
    # if (not args.save_mask):
    #     os.remove(output + "segmented_" + sample_id + ".ppm")
    # if (not args.save_edges):
    #     os.remove(output + "edges_" + sample_id + ".ppm")
    # print('ALL DONE!')


if __name__ == "__main__":
    main()
