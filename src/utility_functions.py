from wand.image import Image

# Modify this function to write to correct paths
def convert_to_ppm(infile):
    img = Image(filename=infile)
    converted_img = img.convert('ppm')
    converted_img.save(filename='ppmout.ppm') 