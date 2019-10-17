import os
import platform
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
import itertools as it
import time
from src import utility_functions, patch_selector
import subprocess

description_str = '''
    Segment_hist implements a semi-automatic pipeline to segment tissue slices from
    the background in high resolution whole-slde histopathological images and
    extracts patches of tissue segments from the full resolution image. 

    Whole slide histological images are very large in terms of size, making it
    difficult for computational pipelines to process them as single units, thus, 
    they have to be divided into patches. Moreover, a significant portion of each 
    image is background, which should be excluded from downstream analyses. 
    
    In order to efficiently segment tissue content from each image, $PROGNAME 
    utilizes a Canny edge detector and a graph-based segmentation method. A lower 
    resolution version of the image, extracted from the whole slide image file,
    is segmented. The background is defined as the segments that can be found at the
    borders or corners of the image (for more details check -b and -c arguments 
    documentation). Finally, patches are extracted from the full size image ,while
    the corresponding patches are checked in the segmented image. Patches with a 
    "tissue content" greater than a threshold value (-t) are selected.

    Moreover, segment_hist can function in test mode. This could assist the user in 
    setting the appropriate parameters for the pipeline. In test mode, segment_hist 
    will output the segmented version of the input image with scales indicating 
    the number of rows and columns. In that image the background should be separate 
    from the tissue pieces for the pipeline to work properly. 
    '''

epilog_str = '''
    EXAMPLES
    --------
    
    Keep segmented image, save patches, produce a thumbnail with marked the
    selected patches, use a content threshold of 0.1 for patch selection.
    
    segment_hist -pfxt 0.1 input_image
    
    segment_hist -p -f -x -t 0.1 input_image

    Do not save patches, produce thumbnail, use different than the default values
    for k and m parameters.
    
    segment_hist -xk 10000 -m 1000 input_image

    Do not save patches, produce thumbnail, use a content threshold of 0.1 for
    patch selection, for background identification use bottom_left and top_right
    corners.
    
    segment_hist -xt 0.1 -b 0000 -c 0101 input_image
 
    Function in test mode, use different than the default values for k and m 
    parameters.
    
    segment_hist --test -k 1000 -m 1000 input_image

    
    REFERENCES
    ----------
    Felzenszwalb, P.F., & Huttenlocher, D.P. (2004). Efficient Graph-Based Image 
    Segmentation. International Journal of Computer Vision, 59, 167-181.
    '''


def build_parser(desc, epi):

    parser = ArgumentParser(formatter_class=RawTextHelpFormatter,
                            description=desc,
                            epilog=epi)

    # Calculate 4-bit permutations for options that need it
    perms = list(
        set(it.permutations(['0', '0', '0', '0', '1', '1', '1', '1'], 4)))
    combs = []
    for perm in perms:
        combs.append(''.join(perm))

    parser.add_argument('-b',
                        '--borders',
                        type=str,
                        default='1111',
                        help='''
    A four digit string. Each digit represents a border of the image in the 
    following order: left, bottom, right, top. If the digit is equal to 1 and
    not 0, then the corresponding border will be taken into account to define
    background. For instance, with -b 1010 the algorithm will look at the left
    and right borders of the segmented image, in a window of width defined by
    the -n argument, and every segment identified will be set as background. 
    If this argument is not equal to 0000, then -c should be 0000. 
    Default value is 1111.
    ''',
                        choices=combs)

    parser.add_argument('-c',
                        '--corners',
                        type=str,
                        default='0000',
                        help='''
    A four digit string. Each digit represents a corner of the image in the 
    following order: top_left, bottom_left, bottom_right, top_right. If the 
    digit is equal to 1 and not 0, then the corresponding corner will be taken
    into account to define background. For instane, with -c 0101 the algorithm
    will look at the bottom_left and top_right corners of the segmented image,
    in a square window of size given by the -n argument, and every segment
    identified will be set as background. If this argument is not equal to 0000,
    then -b should be 0000. Default value is 0000.
    ''',
                        choices=combs)

    parser.add_argument('-d',
                        '--patch-size',
                        type=int,
                        default=512,
                        help='''
    Integer indicating the size of the produced patches. A value of D
    will produce patches of size D x D. Default value is 512.
    ''')

    parser.add_argument('-e',
                        '--save-edges',
                        action='store_true',
                        default=False,
                        help='''
    Keep the image produced by the Canny edge detector. 
    By default, segment_hist will delete it.
    ''')

    parser.add_argument('-f',
                        '--save-mask',
                        action='store_true',
                        default=False,
                        help='''
    Keep the produced segmented image. By default, segment_hist will delete it.
    ''')

    parser.add_argument('-k',
                        '--k-const',
                        type=int,
                        default=10000,
                        help='''
    Parameter required by the segmentation algorithm.
    Value for the threshold function. The threshold function controls the 
    degree to which the difference between two segments must be greater than
    their internal differences in order for them not to be merged. Lower values
    result in finer segmentation. Larger images require higher values.
    Default value is 10000.
    ''')

    parser.add_argument('-m',
                        '--minimum_segmentsize',
                        type=int,
                        default=10000,
                        help='''
    Parameter required by the segmentation algorithm. 
    Minimum segment size enforced by post-processing.
    Larger images require higher values.
    Default value is 10000.
    ''')

    parser.add_argument('-n',
                        '--number-of-lines',
                        type=int,
                        default=100,
                        help='''
    Integer indicating the number of lines from the borders or the corners of
    the segmented image that the algorithm should take into account to define
    background. Default value is 100.
    ''',
                        metavar='NUMBER_OF_LINES',
                        dest='lines')

    parser.add_argument('-p',
                        '--save-patches',
                        action='store_true',
                        default=False,
                        help='''
    Save the produced patches of the full resolution image. By default, 
    segment_hist will not save them.                       
    ''')

    parser.add_argument('-s',
                        '--sigma',
                        type=float,
                        default=0.5,
                        help='''
    Parameter required by the segmentation algorithm. 
    Used to smooth the input image before segmenting it.
    Default value is 0.5.
    ''')

    parser.add_argument("svs",
                        type=str,
                        help='The whole slide image input file',
                        metavar='input_image')

    parser.add_argument('-t',
                        '--content-threshold',
                        type=float,
                        default=0.5,
                        help='''
    Threshold parameter indicating the proportion of a patch content that 
    should not be covered by background in order to be selected. It should
    range between 0 and 1. Default value is 0.5.
                          ''',
                        metavar='CONTENT_THRESHOLD',
                        dest='thres')

    parser.add_argument('-o',
                        '--output',
                        help="Output directory",
                        type=str,
                        default="output/")

    parser.add_argument('-v',
                        "--verbose",
                        help='''
    Print status messages at each step of the procedure with information''',
                        action='store_true',
                        default=False)

    parser.add_argument("-w",
                        "--downsample-mask",
                        help='''
    Downsampling factor to calculate image mask''',
                        type=int,
                        default=16)

    parser.add_argument('-x',
                        '--save-tilecrossed-image',
                        action='store_true',
                        default=False,
                        help='''
    Produce a thumbnail of the original image, in which the selected patches
    are marked with a blue cross. By default, segment_hist will not do this.
    ''')

    parser.add_argument('-y',
                        '--test-mode',
                        help='''
    Function in test mode''',
                        action='store_true',
                        default=False)

    parser.add_argument('-z',
                        '--output-downsample',
                        help='''
    Downsampling factor for the output image.''',
                        type=int,
                        default=16)

    return parser


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
    if not utility_functions.isPowerOfTwo(args.downsample_mask):
        print("Downsampling factor for the mask must be a power of two.")
        sys.exit(1)


def main():

    # Read arguments
    parser = build_parser(description_str, epilog_str)
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
