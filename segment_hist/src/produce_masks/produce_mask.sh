#This is not the final version

#This script takes as input the an image, 
#and use the Felzenszwalb algorithm to produce segmented images, where each
#segment is represented by a distinct randomly selected colour. 
#
#The parameters utilized for the Felzenszwalb algorithm were chosen arbitrarily,
#in order for the background to be detected as a whole segment,
#separate from the tissue slices. Different values are required for different image sizes.
#For more details about them, read the README file inside the 
#Felzenszwalb_algorithm folder. 
#

#read the name of the svs file from the command line argument
svs_file=$1

#set parameters for Felzenszwalb algorithm
sigma=${2:-0.5}
min=${3:-100000}
k=${4:-20000}
level=${5:-1}

image=$(basename $svs_file .svs)
echo $image

#produce edge image
#echo "producing edge file..."
produce_edges.py $svs_file "edges_$image.jpg" $level
convert "edges_$image.jpg" "$image.ppm"

        
#run Felzenszwalb algorithm
#echo "segmenting $image..."
Felzenszwalb_algorithm/segment $sigma $k $min "$image.ppm" "segmented_$image.ppm"

#delete #image.ppm
rm $image.ppm

#echo "ALL DONE"
