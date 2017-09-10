#!/bin/bash -e

# Create mosaic grid of candidate headshots for campaign list page icon

# Not sure exactly where to put this since it should be run from within the
# citycouncil django app in order to use git ls-files, but belongs more in the
# local-scripts

export size=${1:-50}

# convert all images to same size
for f in $(git ls-files static/headshots); do
    if [ ! -e sprite/$size.${f##*/} ]; then
        convert $f"[$sizex$size]" sprite/$size.${f##*/};
    fi;
done;

rm sprite/$size.blank.png

# combine all images in montage
montage $(ls sprite/$size.*.png | sort -R) -geometry "${size}x${size}"+0+0 -background transparent sprite.$size.png
echo "created sprite.$size.png"
