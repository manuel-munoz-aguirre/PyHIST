import os
import platform
import sys
import openslide
import subprocess
import warnings
from src import utility_functions, patch_selector, parser_input


def check_compilation():

    if not os.path.isfile("src/graph_segmentation/segment"):

        # If Windows, the user must compile the script manually, otherwise
        # we attempt to compile it
        if platform.system() == "Windows":
            print("Please compile the segmentation algorithm before"
                  "running this script. Exiting.")
            sys.exit(1)
        else:
            print("Compiling the graph segmentation algorithm...")
            try:
                subprocess.check_call(["make"],
                                      stdout=subprocess.PIPE,
                                      cwd="src/graph_segmentation/")
            except Exception:
                print("Compilation of the segmentation algorithm failed."
                      "Please compile it before running this script. Exiting.")
                sys.exit(1)


def check_arguments(args):
      
    if (args.borders == '0000' and args.corners == '0000') or \
       (args.borders != '0000' and args.corners != '0000'):
        raise ValueError("Invalid borders and corners parameters. Only one"
                         "of either should be specified.")

    if args.thres > 1 or args.thres < 0:
        raise ValueError("CONTENT_THRESHOLD should be a floating point number"
                         "between 0 and 1.")

    if args.pct_bc < 0 or args.pct_bc > 100:
        raise ValueError("PERCENTAGE_BC should be an integer number"
                         "between 0 and 100. Exiting.")
    
    if not utility_functions.isPowerOfTwo(args.output_downsample):
        raise ValueError("Downsampling factor for output image must"
                         "be a power of two.")

    if not utility_functions.isPowerOfTwo(args.mask_downsample):
        raise ValueError("Downsampling factor for the mask must"
                         "be a power of two.")

    if not utility_functions.isPowerOfTwo(args.tilecross_downsample):
        raise ValueError("Downsampling factor for the tilecrossed"
                         "image must be a power of two.")

    # If random sampling, ignore other flags
    def simple_formatwarning(message, *args, **kwargs):
        return str(message) + '\n'
    warnings.formatwarning = simple_formatwarning

    if args.sampling:
        x = [args.save_edges, args.save_mask, args.save_patches,
             args.save_tilecrossed_image, args.test_mode, args.exclude_blank]
        strs = ["--save-edges", "--save-mask", "--save-patches",
                "--save-tilecrossed-image", "--test-mode", "--exclude-blank"] 
        
        if sum(x) >= 1:
            invalid_flags = str([strs[x] for x in [i for i, y in enumerate(x) if y]])
            warnings.warn("The following flags and their related parameters will be"
                          "ignored since they are not used in random sampling mode." +
                          invalid_flags, RuntimeWarning)
                
    # Check if the image can be read
    try:
        _ = openslide.OpenSlide(args.svs)
    except Exception:
        raise TypeError("Unsupported format, or file not found.")

    
def main():
    
    # Read arguments
    parser = parser_input.build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    # Checking correct arguments and compilation of segmentation algorithm
    check_arguments(args)
    check_compilation()

    # Create output folder
    sample_id = args.svs.split('/')[-1]
    sample_id = sample_id.split('.')[0]

    img_outpath = args.output
    if not os.path.exists(img_outpath):
        os.makedirs(img_outpath)
    img_outpath = img_outpath + sample_id + "/"
    if not os.path.exists(img_outpath):
        os.makedirs(img_outpath)

    # Do random sampling if requested, otherwise
    # run the normal pipeline
    if args.sampling:
        utility_functions.randomSampler(args, img_outpath)
    else:
        # Produce edge image
        utility_functions.produce_edges(args,
                                        img_outpath + "edges_" + sample_id +
                                        ".ppm")

        # Run the segmentation algorithm
        utility_functions.produce_segmented_image(sample_id,
                                                  img_outpath,
                                                  args)

        # Test mode
        if args.test_mode:
            utility_functions.produce_test_image(sample_id,
                                                 img_outpath,
                                                 args)
            sys.exit(0)

        # Generate image tiles
        patch_selector.run(sample_id,
                           img_outpath,
                           args)

        # Delete segmented and edge images
        if not args.save_mask:
            os.remove(img_outpath + "segmented_" + sample_id + ".ppm")
        if not args.save_edges:
            os.remove(img_outpath + "edges_" + sample_id + ".ppm")


if __name__ == "__main__":
    main()
