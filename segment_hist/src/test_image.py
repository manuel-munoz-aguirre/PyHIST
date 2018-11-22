#load the required libraries
import cv2
from matplotlib import pyplot as plt
import sys
import warnings

warnings.filterwarnings("ignore")
folder = str(sys.argv[1])
image = str(sys.argv[2])

mask = cv2.imread(folder + "/segmented_" + ".ppm")
test_image = im.show(mask)
plt.savefig(folder + "/test_" + image + ".png")
