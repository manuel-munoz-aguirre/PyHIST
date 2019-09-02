from PIL import Image
import openslide
import numpy as np
import cv2
import warnings
from matplotlib import pyplot as plt
import subprocess
import sys


def produce_edges(in_img, out_img, level):
    '''
    Takes as input an image and uses Canny edge detector from opencv
    library to produce an image in which the detected edges are marked.
    '''

    # read the image
    svs = openslide.OpenSlide(in_img)
    img = svs.read_region((0, 0), level, svs.level_dimensions[level])
    img = np.array(img.convert('RGB'))
    img = img[..., ::-1]

    # run Canny edge detector
    edges = cv2.Canny(img, 100, 200)

    # save the produced image in a ppm format
    edges = Image.fromarray(edges)
    warnings.filterwarnings("ignore")

    edges = edges.convert('RGB')
    edges.save(out_img, 'PPM')
    warnings.filterwarnings("default")


def produce_test_image(image, out_folder):
    '''
    Produces a PNG version of the segmented PPM image using matplotlib.
    '''
    warnings.filterwarnings("ignore")

    mask = cv2.imread(out_folder + "segmented_" + image + ".ppm")
    plt.imshow(mask)
    plt.savefig(out_folder + "test_" + image + ".png")

    warnings.filterwarnings("default")


def produce_segmented_image(sample_id, out_folder, sigma, k_const, min):
    '''
    Invokes a shell to run Felzenszwalb's algorithm with the PPM
    image containing the edges from the Canny detector.
    '''
    bashCommand = "src/Felzenszwalb_algorithm/segment " + str(sigma) + " " + \
        str(k_const) + " " + str(min) + " " + out_folder + \
        "edges_" + sample_id + ".ppm" + " " + \
        out_folder + "segmented_" + sample_id + ".ppm"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error is not None:
        print(error)
        sys.exit(1)
