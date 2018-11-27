#!/bin/bash
#This is not the final version.
#This will be the final script. It will work as wrapper and will connect the rest of the scripts in a single pipeline.


PROGNAME=$( basename $0 | cut -d'.' -f1 )
[[ -L $0 ]] && PROGNAME=$( readlink -f $0 | cut -d'.' -f1 )
src_dir=${PROGNAME%/*}
PROGNAME=${PROGNAME##*/}
cwd=$( pwd )

#function printing an error message
usage () {
    cat <<-_EOF_
        $PROGNAME: usage: $PROGNAME [test] [ARGS]
        $1
        For more information check the help page: $PROGNAME [-h | --help]
_EOF_
    return
}


#function that print the help page
pleh () {
    less <<- _EOF_
    $PROGNAME
    ===============================================================================

    SYNOPSIS
    --------
    $PROGNAME [ARGS] 
    $PROGNAME test [ARGS]

    DESCRIPTION
    -----------
    $PROGNAME implements a semi-automatic pipeline to segment tissue slices from 
    the background in high resolution whole-slde histopathological images and 
    produce patches of those segments from the full resolution image.

    $PROGNAME can function in test mode. This could assist the user in setting the 
    appropriate parameters for the pipeline. In test mode, $PROGNAME will output
    the segmented version of the input image  with scales indicating the number of
    rows and columns. In that image the background should be separate from the 
    tissue pieces for the pipeline to work properly. 

    ARGUMENTS
    ---------
    -s
    --sigma_F

    -m
    --min_F

    -k
    --k_F

    -l
    --level

    -p
    --save_patches

    -t
    --contour_threshold

    -d
    --patch_size

    -n
    --number_of_lines

    -b
    --borders

    -c
    --corners

    -x
    --save_tilecrossed_image

    -f
    --save_mask

    -e
    --save_edges

    -i
    --image_file

    -h
    --help
_EOF_
    return
}


#check if the required files for the Felzenszwalb algorithm are already set up
if [[ ! (-d "$src_dir/Felzenszwalb_algorithm")  ]]; then
    echo Initial set up...
    cd $src_dir/
    unzip ../Felzenszwalb_algorithm.zip 
    mv segment Felzenszwalb_algorithm
    cd Felzenszwalb_algorithm
    make
    cd $cwd
    echo ...OK
fi

#echo "$@"

#read command line arguments
if [[ $1 == 'test' ]]; then
    test_image='True'
    shift
    while [[ -n $1 ]]; do
        case $1 in
            -s | --sigma_F)                   shift
                                              sigma=$1
                                              ;;
            -m | --min_F)                     shift
                                              min=$1
                                              ;;
            -k | --k_F)                       shift
                                              k=$1
                                              ;;
            -l | --level)                     shift
                                              level=$1
                                              ;;
            -i | --image_file)                shift
                                              svs=$1
                                              ;;
            -h | --help)                      pleh
                                              exit
                                              ;;
            *)                                usage 'Invalid argument!' >&2
                                              exit 1
                                              ;;
        esac
        shift
    done
else
    while [[ -n $1 ]]; do
        if [[ ${#1} -gt 2 && ${1:0:2} != '--' ]]; then
            #echo "in the if: $1"
            for (( i=1; i<${#1}; ++i )); do
                arg=${1:$i:1}
                case $arg in
                    s) shift
                       sigma=$1
                       ;;
                    m) shift
                       min=$1
                       ;;
                    k) shift
                       k=$1
                       ;;
                    l) shift
                       level=$1
                       ;;
                    p) save_patches='True'
                       ;;
                    t) shift
                       thres=$1
                       ;;
                    d) shift
                       patch_size=$1
                       ;;
                    n) shift
                       lines=$1
                       ;;
                    b) shift
                       borders=$1
                       ;;
                    c) shift
                       corners=$1
                       ;;
                    x) save_tilecrossed='True'
                       ;;
                    i) shift
                       svs=$1
                       ;;
                    h) pleh
                       exit
                       ;;
                    f) save_mask='True'
                       ;;
                    e) save_edges='True'
                       ;;
                    *) usage 'Invalid argument!' >&2
                       exit 1
                       ;;
                esac
                unset arg
            done
            shift
        else
            case $1 in
                -s | --sigma_F)                   shift
                                                  sigma=$1
                                                  ;;
                -m | --min_F)                     shift
                                                  min=$1
                                                  ;;
                -k | --k_F)                       shift
                                                  k=$1
                                                  ;;
                -l | --level)                     shift
                                                  level=$1
                                                  ;;
                -p | --save_patches)              save_patches='True'
                                                  ;;
                -t | --contour_threshold)         shift
                                                  thres=$1
                                                  ;;
                -d | --patch_size)                shift
                                                  patch_size=$1
                                                  ;;
                -n | --number_of_lines)           shift
                                                  lines=$1
                                                  ;;
                -b | --borders)                   shift
                                                  borders="$1"
                                                  ;;
                -c | --corners)                   shift
                                                  corners="$1"
                                                  ;;
                -x | --save_tilecrossed_image)    save_tilecrossed='True'
                                                  ;;
                -h | --help)                      pleh
                                                  exit
                                                  ;;
                -f | --save_mask)                 save_mask='True'
                                                  ;;
                -e | --save_edges)                save_edges='True'
                                                  ;;
                -i | --image_file)                shift
                                                  svs=$1
                                                  ;;
                *)                                usage 'Invalid argument!' >&2
                                                  exit 1
                                                  ;;
            esac
            shift
        fi
    done
fi

#check for the image input
[[ -n $svs ]] || { usage 'Invalid or absent input!' >&2; exit 1; }


#set default values for parameters
sigma=${sigma:-0.5}
min=${min:-100000}
k=${k:-20000}
level=${level:-1}
save_patches=${save_patches:-'False'}
thres=${thres:-0.5}
patch_size=${patch_size:-512}
lines=${lines:-100}
borders=${borders:-'1111'}
corners=${corners:-'0000'}
save_tilecrossed=${save_tilecrossed:-'False'}
save_mask=${save_mask:-'False'}
save_edges=${save_edges:-'False'}

#check errors in borders and corners input
[[ $borders == '0000' ]] && [[ $corners == '0000' ]] && { usage 'Invalid borders and corners parameters!' >&2; exit 1; }
[[ $borders != '0000' ]] && [[ $corners != '0000' ]] && { usage 'Invalid borders and corners parameters!' >&2; exit 1; }

image=$( cut -d '.' -f1 <<< $svs )
echo $image

#create a temporary folder
temp=".$PROGNAME-$image.$$_$RANDOM"
mkdir $temp

#produce edge image
echo 'Producing edge image...'
python "$src_dir/produce_edges.py" $svs "$temp/edges_$image.jpg" $level
convert "$temp/edges_$image.jpg" "$temp/$image.ppm"
echo OK

#run Felzenszwalb algorithm
echo 'Segmenting image...'
$src_dir/Felzenszwalb_algorithm/segment $sigma $k $min "$temp/$image.ppm" "$temp/segmented_$image.ppm"
echo OK

#delete image.ppm
rm $temp/$image.ppm

#test mode
[[ $test_image == 'True' ]] && { echo "Producing test image..."; python $src_dir/test_image.py $temp $image; mv "$temp/test_$image.png" $cwd; rm -r $temp; echo "ALL DONE!"; exit; }


#produce and select tiles
echo 'Extracting tiles...'
python $src_dir/patch_selector.py $temp $image $thres $patch_size $lines $borders $corners $save_tilecrossed $save_patches

#delete mask and edge images
[[ $save_mask == 'False' ]] && rm "$temp/segmented_$image.ppm"
[[ $save_edges == 'False' ]] && rm "$temp/edges_$image.jpg"

#turn the results visible
mv "$cwd/$temp" "$cwd/${image}_${PROGNAME}_output"
echo 'ALL DONE!'
