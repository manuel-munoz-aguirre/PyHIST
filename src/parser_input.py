import itertools as it
import logging
import warnings

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from src import utility_functions


description_str = '''
    PyHIST is a semi-automatic pipeline to produce tiles from a high resolution histopathological image.
'''

epilog_str = '''
    Examples: See the documentation at https://pyhist.readthedocs.io/
    '''


def build_parser():

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
                            description=description_str,
                            epilog=epilog_str)

    # Calculate 4-bit permutations for options that need it
    perms = list(set(
        it.permutations(['0', '0', '0', '0', '1', '1', '1', '1'], 4)))
    combs = []
    for perm in perms:
        combs.append(''.join(perm))

    # Mandatory arguments
    parser.add_argument("svs",
                        type=str,
                        help='The whole slide image input file',
                        metavar='input_image')

    # Optional argument group: execution settings
    group_exec = parser.add_argument_group('Execution')
    group_exec.add_argument(
        '--patch-size',
        type=int,
        default=512,
        help='Integer indicating the size of the produced tiles. A value of P will produce tiles of size P x P.')
    group_exec.add_argument(
        '--method',
        help='Method to perform the segmentation.',
        choices=['randomsampling', 'graph', 'graphtestmode', 'otsu', 'adaptive'],
        default='graph'
    )
    group_exec.add_argument(
        "--format",
        help='Format to save the tiles.',
        choices=["png", "jpg"],
        default="png")
    group_exec.add_argument(
        '--content-threshold',
        type=float,
        default=0.5,
        help='''Threshold parameter indicating the proportion of the tile area that
        should be foreground (tissue content) in order to be selected. It should
        range between 0 and 1. Not applicable for random sampling.''',
        metavar='CONTENT_THRESHOLD',
        dest='thres')

    group_exec.add_argument(
        "--info",
        help='Show status messages at each step of the pipeline.',
        choices=["silent", "default", "verbose"],
        default="default")

    # Optional argument group: output
    group_output = parser.add_argument_group('General output')
    group_output.add_argument(
        '--output',
        help="Output directory",
        type=str,
        default="output/")
    group_output.add_argument(
        '--save-patches',
        action='store_true',
        default=False,
        help='Save the tiles with an amount of foreground above the content threshold.')
    group_output.add_argument(
        '--save-blank',
        action='store_true',
        default=False,
        help='If enabled, background tiles will be saved (i.e. those that did not meet the content threshold.).')
    group_output.add_argument(
        '--save-nonsquare',
        action='store_true',
        default=False,
        help='''By default, only square tiles are saved, discarding the regions
        towards the edges of the WSI that do not fit a complete tile. If this
        flag is enabled, these non-square tiles will be saved as well.''')
    group_output.add_argument(
        '--save-tilecrossed-image',
        action='store_true',
        default=False,
        help='Produce a thumbnail of the original image, in which the selected tiles are marked with a cross.')
    group_output.add_argument(
        '--save-mask',
        action='store_true',
        default=False,
        help='Keep the mask used to perform tile selection.')


    # Optional argument group: downsampling
    group_downsampling = parser.add_argument_group('Downsampling')
    group_downsampling.add_argument(
        '--output-downsample',
        help='Downsampling factor for the output image. Must be a power of 2.',
        type=int,
        default=16)
    group_downsampling.add_argument(
        "--mask-downsample",
        help='''Downsampling factor to calculate the image mask. A higher number will speed up the tiling evaluation process at the expense of
        tile evaluation quality. Must be a power of 2.''',
        type=int,
        default=16)
    group_downsampling.add_argument(
        "--tilecross-downsample",
        help='''Downsampling factor to generate the tilecrossed overview image. Must be a power of 2.''',
        type=int,
        default=16)
    group_downsampling.add_argument(
        "--test-downsample",
        help='''Downsampling factor to generate the test image in graph test mode. Must be a power of 2.''',
        type=int,
        default=16)


    # Optional argument group: sampling settings
    group_sampling = parser.add_argument_group('Random sampling')
    group_sampling.add_argument(
        '--npatches',
        help='Number of tiles to extract in random sampling mode.',
        type=int,
        default=100)


    # Optional argument group: segmentation
    group_segmentation = parser.add_argument_group('Graph segmentation')
    group_segmentation.add_argument(
        '--save-edges',
        action='store_true',
        default=False,
        help='Keep the image produced by the Canny edge detector.')

    group_segmentation.add_argument(
        '--borders',
        type=str,
        default='1111',
        help='''
        A four digit string. Each digit represents a border of the image in the
        following order: left, bottom, right, top. If the digit is 1, then the
        corresponding border will be taken into account to define background.
        For instance, with 1010 the algorithm will look at the left
        and right borders of the segmented image, in a window of width defined by
        the --percentage-bc argument, and every segment identified will be set as background.
        This argument is mutually exclusive with --corners. If --borders is set
        to be different from 0000, then --corners must be 0000.''',
        choices=combs)

    group_segmentation.add_argument(
        '--corners',
        type=str,
        default='0000',
        help='''
        A four digit string. Each digit represents a corner of the image in the
        following order: top left, bottom left, bottom right, top right. If the
        digit is equal to 1, then the corresponding corner will be taken
        into account to define background. For instance, with 0101, the
        bottom left and top right corners of the segmented image will be considered,
        with a square window of size given by the --percentage-bc argument,
        and every segment identified will be set as background. This argument is
        mutually exclusive with --borders. If --corners is set to be different from
        0000, then --borders must be 0000.''',
        choices=combs)

    group_segmentation.add_argument(
        '--k-const',
        type=int,
        default=10000,
        help='''
        Parameter used by the segmentation algorithm to threshold regions in the image. 
        This value controls the degree to which the difference between two segments must be 
        greater than their internal differences in order for them not to be merged. 
        Lower values result in finer region segmentation, while higher values are better 
        to detect large chunks of tissue. Larger images require higher values.''')

    group_segmentation.add_argument(
        '--minimum_segmentsize',
        type=int,
        default=10000,
        help='''Parameter required by the segmentation algorithm. 
        Minimum segment size enforced by post-processing.''',
        metavar='MINIMUM_SEGMENTSIZE')

    group_segmentation.add_argument(
        '--percentage-bc',
        type=int,
        default=5,
        help='''Integer [0-100] indicating the percentage of the image (width
        and height) that will be considered as border/corner in order to define
        the background.''',
        metavar='PERCENTAGE_BC',
        dest='pct_bc')

    group_segmentation.add_argument(
        '--sigma',
        type=float,
        default=0.5,
        help='''Parameter required by the segmentation algorithm.
        Used to smooth the input image with a Gaussian kernel before segmenting it.''')

    return parser


def check_arguments(args):

    # Argument checking for graph segmentation
    if (args.borders == '0000' and args.corners == '0000') or (args.borders != '0000' and args.corners != '0000'):
        raise ValueError("Invalid borders and corners parameters. Only one of either should be specified.")
    if args.thres > 1 or args.thres < 0:
        raise ValueError("CONTENT_THRESHOLD should be a floating point number between 0 and 1.")
    if args.pct_bc < 0 or args.pct_bc > 100:
        raise ValueError("PERCENTAGE_BC should be an integer number between 0 and 100.")
    if not utility_functions.isPowerOfTwo(args.output_downsample):
        raise ValueError("Downsampling factor for output image must be a power of two.")
    if not utility_functions.isPowerOfTwo(args.mask_downsample):
        raise ValueError("Downsampling factor for the mask must be a power of two.")
    if not utility_functions.isPowerOfTwo(args.tilecross_downsample):
        raise ValueError("Downsampling factor for the tilecrossed image must be a power of two.")

    # If random sampling, ignore flags
    if args.method == "randomsampling":
        if args.npatches <= 0:
            raise ValueError("Number of patches to extract must be greater than zero.")

        x = [args.save_blank, args.save_nonsquare, args.save_tilecrossed_image,
        args.save_mask, args.save_edges]
        strs = ["--save-blank", "--save-nonsquare", "--save-tilecrossed-image",
                 "--save-mask", "--save-edges"]

        if sum(x) >= 1:
            invalid_flags = str([strs[x] for x in [i for i, y in enumerate(x) if y]])
            logging.info('The following flags and their group parameters will be ignored' \
                ' since they are not used in random sampling mode: ' + invalid_flags)

    if args.method in ["otsu", "adaptive"]:
        x = [args.save_edges]
        strs = ["--save-edges"]

        if sum(x) >= 1:
            invalid_flags = str([strs[x] for x in [i for i, y in enumerate(x) if y]])
            logging.info('The following flags and their group parameters will be ignored' \
                ' since they are not used in thresholding modes: ' + invalid_flags)
