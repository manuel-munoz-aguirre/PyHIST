from wand.image import Image as wImage
from PIL import Image
import openslide
import numpy as np
import cv2
import warnings
from matplotlib import pyplot as plt
import subprocess

def convert_to_ppm(infile):
    img = wImage(filename=infile)
    converted_img = img.convert('ppm')
    converted_img.save(filename='ppmout.ppm') 

def produce_edges(in_img, out_img, level):
    '''
    Takes as input an image and uses Canny edge detector from opencv
    library to produce an image in which the detected edges are marked.
    '''

    #read the image
    svs = openslide.OpenSlide(in_img)
    img = svs.read_region((0,0), level, svs.level_dimensions[level])
    img = np.array(img.convert('RGB'))
    img = img[...,::-1]

    #run Canny edge detector
    edges = cv2.Canny(img, 100, 200)

    #save the produced image
    cv2.imwrite(out_img, edges)
    

def produce_test_image(image):
    warnings.filterwarnings("ignore")

    mask = cv2.imread("segmented_" + image + ".ppm")
    test_image = plt.imshow(mask)
    plt.savefig("test_" + image + ".png")

    warnings.filterwarnings("default")

def produce_segmented_image(sample_id, sigma, k_const, min):
    bashCommand = "src/Felzenszwalb_algorithm/segment " + str(sigma) + " " + \
    str(k_const) + " " + str(min) + " ppmout.ppm" + " segmented_" + sample_id + \
    ".ppm"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error is not None: eprint(error); sys.exit(1)
